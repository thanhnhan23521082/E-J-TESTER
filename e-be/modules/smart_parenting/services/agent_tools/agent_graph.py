"""LangGraph workflow for Smart Parenting parent chatbot."""

from __future__ import annotations

import json
import logging
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.ext.asyncio import AsyncSession

from shared.clients.llm_client import call_json, call_text
from shared.model import Conversation
from modules.smart_parenting.services.agent_tools.prompt_loader import load_parent_agent_prompt
from modules.smart_parenting.services.agent_tools.tools import (
    LANGGRAPH_TOOLS,
    reset_tool_runtime_context,
    set_tool_runtime_context,
)

logger = logging.getLogger(__name__)


class AgentState(TypedDict, total=False):
    db: AsyncSession
    student_id: str
    parent_id: int
    question: str
    selected_tools: list[str]
    tool_outputs: dict[str, Any]
    final_answer: str
    escalated: bool
    orchestration_trace: list[dict[str, Any]]


class ToolSelectionDecision(BaseModel):
    selected_tools: list[str] = Field(default_factory=list)
    reasons: dict[str, str] | list[str] | str = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize_reasons(self) -> "ToolSelectionDecision":
        if isinstance(self.reasons, dict):
            return self
        if isinstance(self.reasons, str):
            self.reasons = {
                tool_name: self.reasons
                for tool_name in self.selected_tools
            }
            return self
        normalized: dict[str, str] = {}
        if isinstance(self.reasons, list):
            for idx, reason in enumerate(self.reasons):
                if idx >= len(self.selected_tools):
                    break
                if isinstance(reason, str) and reason.strip():
                    normalized[self.selected_tools[idx]] = reason.strip()
        self.reasons = normalized
        return self


def _contains_any(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def _is_target_school_question(question: str) -> bool:
    q = question.lower()
    target_markers = [
        "trường mục tiêu",
        "target school",
        "deadline",
        "hạn nộp",
        "phù hợp với con",
        "phù hợp với bé",
        "trường của con",
        "trường của bé",
    ]
    # Keep this intent strict so generic ranking/worldwide questions do not get trapped in DB-only flow.
    return _contains_any(q, target_markers)


def _is_global_school_info_question(question: str) -> bool:
    q = question.lower()
    markers = [
        "top",
        "tốt nhất",
        "xếp hạng",
        "ranking",
        "trên thế giới",
        "toàn cầu",
        "ở úc",
        "australia",
        "qs",
        "times higher education",
    ]
    return _contains_any(q, markers)


def _is_school_fit_question(question: str) -> bool:
    q = question.lower()
    markers = [
        "phù hợp học ở đâu",
        "phu hop hoc o dau",
        "khả năng đậu",
        "kha nang dau",
        "đủ ielts",
        "du ielts",
        "học bổng",
        "hoc bong",
        "apply học bổng",
        "apply hoc bong",
        "hướng ngoại",
        "huong ngoai",
        "hướng nội",
        "huong noi",
        "sáng tạo",
        "sang tao",
        "phân tích",
        "phan tich",
        "tính cách",
        "tinh cach",
    ]
    return _contains_any(q, markers)


def _normalize_school_names(
    schools: Any,
) -> list[str]:
    names: list[str] = []
    if isinstance(schools, dict):
        schools = list(schools.values())

    if not isinstance(schools, list):
        return names

    for item in schools:
        if isinstance(item, str):
            if item.strip():
                names.append(item.strip())
            continue

        if not isinstance(item, dict):
            continue

        raw_name = item.get("name")
        if not isinstance(raw_name, str) or not raw_name.strip():
            continue

        names.append(raw_name.strip())

    # Preserve order and remove duplicates
    deduped: list[str] = []
    seen: set[str] = set()
    for name in names:
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(name)
    return deduped


def _build_personalized_web_query(question: str, profile: dict[str, Any]) -> str:
    q = question.strip()
    ielts = profile.get("ielts_score")
    program = profile.get("program")
    target_schools = _normalize_school_names(profile.get("target_schools") or [])

    school_intent_markers = [
        "truong",
        "university",
        "top",
        "xep hang",
        "ranking",
        "hoc bong",
        "scholarship",
        "ielts",
    ]
    q_lower = q.lower()
    has_school_intent = any(marker in q_lower for marker in school_intent_markers)
    if not has_school_intent:
        return q

    context_bits: list[str] = []
    if isinstance(program, str) and program.strip():
        context_bits.append(f"program {program}")
    if ielts is not None:
        context_bits.append(f"IELTS {ielts}")
    if target_schools:
        context_bits.append(f"target schools {', '.join(target_schools[:2])}")

    if context_bits:
        return f"{q} {'; '.join(context_bits)} admission requirements scholarship"
    return f"{q} university ranking admission requirements scholarship"


def _select_tools_with_reasons_fallback(question: str, prompt_cfg: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
    rules = prompt_cfg.get("agent", {}).get("tool_selection_rules", {})
    selected = ["get_student_profile", "get_conversation_history"]
    reasons: dict[str, str] = {
        "get_student_profile": "always include student profile for baseline context",
        "get_conversation_history": "always include conversation history for continuity",
    }

    if _contains_any(question, rules.get("mentor_keywords", [])):
        selected.append("get_mentor_info")
        reasons["get_mentor_info"] = "matched mentor keywords"
    if _contains_any(question, rules.get("behavior_keywords", [])):
        selected.append("get_behavioral_logs")
        reasons["get_behavioral_logs"] = "matched behavior keywords"
    if _contains_any(question, rules.get("milestone_keywords", [])):
        selected.append("get_milestones")
        reasons["get_milestones"] = "matched milestone keywords"
    if _contains_any(question, rules.get("summary_keywords", [])):
        selected.append("get_weekly_digest")
        reasons["get_weekly_digest"] = "matched summary keywords"
    if _contains_any(question, rules.get("course_keywords", [])):
        selected.append("search_courses")
        reasons["search_courses"] = "matched course keywords"
    school_keywords = rules.get("school_keywords", [])
    web_keywords = rules.get("web_keywords", [])
    has_school_topic = _contains_any(question, school_keywords)
    target_school_question = _is_target_school_question(question)
    global_school_question = _is_global_school_info_question(question)
    general_info_question = _contains_any(question, web_keywords) or global_school_question
    school_fit_question = _is_school_fit_question(question)

    if target_school_question:
        selected.append("get_school_info")
        reasons["get_school_info"] = "target school question should use DB data first"
    if _contains_any(question, rules.get("summary_keywords", [])):
        selected.append("get_progress_summary")
        reasons["get_progress_summary"] = "matched summary keywords"
    if general_info_question and (not target_school_question or global_school_question):
        selected.append("web_search")
        reasons["web_search"] = "general information question should use external web context"
    elif has_school_topic and not target_school_question:
        # School-topic question without specific target-school intent defaults to external lookup.
        selected.append("web_search")
        reasons["web_search"] = "school topic appears generic, so use external sources"
    if school_fit_question:
        selected.append("assess_school_fit")
        reasons["assess_school_fit"] = "question needs combined DB profile + external school/scholarship context"
    if _contains_any(question, rules.get("escalate_keywords", [])):
        selected.append("escalate")
        reasons["escalate"] = "matched escalate keywords"

    deduped: list[str] = []
    for tool_name in selected:
        if tool_name not in deduped:
            deduped.append(tool_name)
    return deduped, reasons


async def _select_tools_with_reasons(question: str, prompt_cfg: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
    allowed_tools = [
        "get_student_profile",
        "get_conversation_history",
        "get_mentor_info",
        "get_behavioral_logs",
        "get_milestones",
        "get_weekly_digest",
        "get_progress_summary",
        "search_courses",
        "get_school_info",
        "web_search",
        "assess_school_fit",
        "escalate",
        "chitchat",
    ]
    fallback_selected, fallback_reasons = _select_tools_with_reasons_fallback(question, prompt_cfg)
    system_prompt = (
        "You are an orchestration planner for a parent-support chatbot. "
        "Choose the minimum useful set of tools for the parent's latest message. "
        "Prefer semantic intent over keyword matching. "
        "If the message is a short follow-up fragment like a personality trait or preference, "
        "infer the likely parent intent from that fragment alone. "
        "Use assess_school_fit when the question is about fit, eligibility, top schools, scholarships, "
        "or when the parent gives traits/preferences that should be mapped to school environment. "
        "Use get_school_info only for the student's existing target schools. "
        "Use web_search for general external facts, rankings, or public school information. "
        "Use chitchat only if the message is truly general small-talk and does not need student data."
    )
    prompt = (
        f"Parent message: {question}\n\n"
        f"Allowed tools: {json.dumps(allowed_tools, ensure_ascii=False)}\n"
        f"Fallback suggestion if uncertain: {json.dumps(fallback_selected, ensure_ascii=False)}\n"
        "Return JSON with keys selected_tools and reasons. "
        "selected_tools must be a subset of allowed tools. "
        "Usually include get_student_profile and get_conversation_history unless the message is pure chitchat."
    )

    try:
        decision = await call_json(
            prompt=prompt,
            system_prompt=system_prompt,
            schema=ToolSelectionDecision,
            max_tokens=400,
            temperature=0.1,
        )
        selected = [tool for tool in decision.selected_tools if tool in allowed_tools]
        reasons = {
            tool: reason
            for tool, reason in decision.reasons.items()
            if tool in selected and isinstance(reason, str) and reason.strip()
        }
        if not selected:
            return fallback_selected, fallback_reasons
        deduped: list[str] = []
        for tool_name in selected:
            if tool_name not in deduped:
                deduped.append(tool_name)
        for tool_name in deduped:
            reasons.setdefault(tool_name, "selected by LLM intent analysis")
        return deduped, reasons
    except Exception as exc:
        logger.warning("orchestrator.prepare fallback_to_keyword_routing error=%s", exc)
        return fallback_selected, fallback_reasons


async def prepare_node(state: AgentState) -> AgentState:
    cfg = load_parent_agent_prompt()
    selected, reasons = await _select_tools_with_reasons(state["question"], cfg)

    if len(selected) == 2 and len(state["question"].split()) < 6:
        selected = ["chitchat"]
        reasons = {"chitchat": "short question with no specialized keyword match"}

    trace: list[dict[str, Any]] = [
        {
            "phase": "prepare",
            "question": state["question"],
            "selected_tools": selected,
            "selection_reasons": reasons,
        }
    ]
    logger.info(
        "orchestrator.prepare selected_tools=%s reasons=%s question=%s",
        selected,
        json.dumps(reasons, ensure_ascii=False),
        state["question"],
    )

    return {
        **state,
        "selected_tools": selected,
        "tool_outputs": {},
        "escalated": False,
        "orchestration_trace": trace,
    }


async def tools_node(state: AgentState) -> AgentState:
    db = state["db"]
    student_id = state["student_id"]
    parent_id = state["parent_id"]
    question = state["question"]

    outputs: dict[str, Any] = {}

    trace = list(state.get("orchestration_trace", []))

    def _build_tool_input(tool_name: str) -> tuple[dict[str, Any], str]:
        if tool_name == "chitchat":
            return {"query": question}, "direct answer mode for general question"
        if tool_name == "web_search":
            profile = outputs.get("get_student_profile") or {}
            rewritten_query = _build_personalized_web_query(question, profile)
            return {"query": rewritten_query, "count": 3}, "need realtime web context with student-aware query"
        if tool_name == "escalate":
            return {
                "student_id": student_id,
                "reason": "Auto-escalated by keyword policy",
            }, "question indicates escalation policy"
        if tool_name == "get_school_info":
            profile = outputs.get("get_student_profile") or {}
            schools = profile.get("target_schools") or []
            school_names = _normalize_school_names(schools)
            return {"school_names": school_names}, "derive school names from student profile"
        if tool_name == "search_courses":
            profile = outputs.get("get_student_profile") or {}
            return {
                "student_id": student_id,
                "skill": profile.get("weakest_skill"),
                "program": profile.get("program"),
            }, "derive course filters from student profile"
        if tool_name == "get_behavioral_logs":
            return {"student_id": student_id, "days": 14}, "analyze last 14 days behavior"
        if tool_name == "assess_school_fit":
            return {
                "student_id": student_id,
                "question": question,
            }, "combine profile, learning signals, and web evidence for school-fit answer"
        if tool_name == "get_milestones":
            return {
                "student_id": student_id,
                "status": None,
                "type_filter": None,
                "limit": 10,
            }, "retrieve recent milestones for progress context"
        if tool_name == "get_conversation_history":
            return {"student_id": student_id, "limit": 8}, "preserve recent conversation context without overloading prompt"
        return {"student_id": student_id}, "default student-scoped input"

    token = set_tool_runtime_context(db=db, parent_id=parent_id)
    try:
        selected_tools = state.get("selected_tools", [])
        logger.info("orchestrator.tools start selected_tools=%s", selected_tools)
        for idx, tool_name in enumerate(selected_tools, start=1):
            tool_obj = LANGGRAPH_TOOLS.get(tool_name)
            if tool_obj is None:
                logger.warning("orchestrator.tools skip unknown_tool=%s", tool_name)
                continue
            tool_input, reason = _build_tool_input(tool_name)
            logger.info(
                "orchestrator.tools step=%s/%s tool=%s reason=%s input=%s",
                idx,
                len(selected_tools),
                tool_name,
                reason,
                json.dumps(tool_input, ensure_ascii=False, default=str),
            )
            tool_output = await tool_obj.ainvoke(tool_input)
            outputs[tool_name] = tool_output
            logger.info(
                "orchestrator.tools result tool=%s output=%s",
                tool_name,
                json.dumps(tool_output, ensure_ascii=False, default=str),
            )
            trace.append(
                {
                    "phase": "tool",
                    "step": idx,
                    "total_steps": len(selected_tools),
                    "tool": tool_name,
                    "reason": reason,
                    "input": tool_input,
                    "output": tool_output,
                    "next_tool": selected_tools[idx] if idx < len(selected_tools) else None,
                    "next_tool_decision": (
                        "pre-planned sequence from prepare step"
                        if idx < len(selected_tools)
                        else "tool sequence completed"
                    ),
                }
            )
    finally:
        reset_tool_runtime_context(token)

    return {
        **state,
        "tool_outputs": outputs,
        "escalated": "escalate" in outputs,
        "orchestration_trace": trace,
    }


async def respond_node(state: AgentState) -> AgentState:
    cfg = load_parent_agent_prompt().get("agent", {})
    system_prompt = cfg.get("system_prompt", "You are a helpful educational assistant.")
    style = cfg.get("response_style", [])
    used_tools = state.get("selected_tools", [])
    tool_outputs = state.get("tool_outputs", {})
    web_payload = tool_outputs.get("web_search", {}) if isinstance(tool_outputs, dict) else {}
    web_error = (
        web_payload.get("error")
        if isinstance(web_payload, dict)
        else None
    )
    web_results = (
        web_payload.get("results")
        if isinstance(web_payload, dict)
        else []
    )
    has_web_results = isinstance(web_results, list) and len(web_results) > 0
    profile_payload = tool_outputs.get("get_student_profile", {}) if isinstance(tool_outputs, dict) else {}
    personalization_rule = (
        "Always personalize with student profile fields when available: name, current score, weakest skill, target schools, and concrete next action. "
        "Do not give generic counseling detached from these fields."
    )
    if isinstance(profile_payload, dict) and profile_payload.get("student_id"):
        personalization_rule = (
            "You have student profile data. Start with a student-specific conclusion first, then explain using concrete fields "
            "(IELTS/GPA/target school gap/weakest skill/days left). Avoid asking vague follow-up unless truly missing."
        )

    source_rule = (
        "If web_search was used, include 2-3 source links in markdown bullet format at the end."
        if "web_search" in used_tools
        else "No external source list required."
    )
    web_priority_rule = "No external-web priority constraints."
    if "web_search" in used_tools and has_web_results:
        web_priority_rule = (
            "web_search has usable results. Prioritize external results for factual answer. "
            "Do not claim 'không có dữ liệu' when web results exist."
        )
    elif "web_search" in used_tools and web_error:
        web_priority_rule = (
            "web_search failed. Explicitly tell parent external lookup is temporarily unavailable, "
            "and include the short reason."
        )

    prompt = (
        f"Question from parent: {state['question']}\n\n"
        f"Tool outputs (JSON):\n{json.dumps(tool_outputs, ensure_ascii=False, default=str)}\n\n"
        f"Style rules: {style}\n"
        f"Personalization rule: {personalization_rule}\n"
        f"Source rule: {source_rule}\n"
        f"Web priority rule: {web_priority_rule}\n"
        "Write final answer in Vietnamese for parent."
    )

    logger.info(
        "orchestrator.respond using_tools=%s style_rules=%s",
        used_tools,
        json.dumps(style, ensure_ascii=False, default=str),
    )

    answer = await call_text(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.3,
        max_tokens=900,
    )

    logger.info("orchestrator.respond answer_generated length=%s", len(answer))

    trace = list(state.get("orchestration_trace", []))
    trace.append(
        {
            "phase": "respond",
            "used_tools": state.get("selected_tools", []),
            "answer_length": len(answer),
        }
    )

    return {**state, "final_answer": answer, "orchestration_trace": trace}


async def persist_node(state: AgentState) -> AgentState:
    db = state["db"]
    raw_context_snapshot = {
        "selected_tools": state.get("selected_tools", []),
        "tool_outputs": state.get("tool_outputs", {}),
        "orchestration_trace": state.get("orchestration_trace", []),
    }
    # Ensure JSONB-safe payload (handles time/datetime/Decimal and other non-JSON objects).
    context_snapshot = json.loads(
        json.dumps(raw_context_snapshot, ensure_ascii=False, default=str)
    )

    record = Conversation(
        parent_id=state["parent_id"],
        student_id=state["student_id"],
        question=state["question"],
        ai_response=state.get("final_answer", ""),
        context_snapshot=context_snapshot,
        escalated=bool(state.get("escalated", False)),
    )
    db.add(record)
    await db.commit()
    logger.info(
        "orchestrator.persist saved_conversation parent_id=%s student_id=%s escalated=%s",
        state["parent_id"],
        state["student_id"],
        bool(state.get("escalated", False)),
    )

    return state


def _build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("prepare", prepare_node)
    graph.add_node("run_tools", tools_node)
    graph.add_node("respond", respond_node)
    graph.add_node("persist", persist_node)

    graph.set_entry_point("prepare")
    graph.add_edge("prepare", "run_tools")
    graph.add_edge("run_tools", "respond")
    graph.add_edge("respond", "persist")
    graph.add_edge("persist", END)

    return graph.compile()


_AGENT_GRAPH = _build_graph()


async def run_parent_agent(
    *,
    db: AsyncSession,
    parent_id: int,
    student_id: str,
    question: str,
) -> dict[str, Any]:
    """Execute parent-chat workflow via LangGraph."""
    final_state = await _AGENT_GRAPH.ainvoke(
        {
            "db": db,
            "parent_id": parent_id,
            "student_id": student_id,
            "question": question,
        }
    )

    return {
        "answer": final_state.get("final_answer", ""),
        "tools_used": final_state.get("selected_tools", []),
        "escalated": bool(final_state.get("escalated", False)),
        "tool_outputs": final_state.get("tool_outputs", {}),
    }

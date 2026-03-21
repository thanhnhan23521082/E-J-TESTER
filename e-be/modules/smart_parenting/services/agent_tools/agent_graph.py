"""LangGraph workflow for Smart Parenting parent chatbot."""

from __future__ import annotations

import json
import logging
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from shared.clients.llm_client import call_text
from shared.model import Conversation
from modules.smart_parenting.services.agent_tools.prompt_loader import load_parent_agent_prompt
from modules.smart_parenting.services.agent_tools.tools import (
    LANGGRAPH_TOOLS,
    reset_tool_runtime_context,
    set_tool_runtime_context,
)

logger = logging.getLogger(__name__)


def _sanitize_json(value: Any) -> Any:
    """Ensure value is JSON-serializable for JSONB persistence."""
    return json.loads(json.dumps(value, ensure_ascii=False, default=str))


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


def _contains_any(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def _select_tools_with_reasons(question: str, prompt_cfg: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
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
    if _contains_any(question, rules.get("school_keywords", [])):
        selected.append("get_school_info")
        reasons["get_school_info"] = "matched school keywords"
    if _contains_any(question, rules.get("summary_keywords", [])):
        selected.append("get_progress_summary")
        reasons["get_progress_summary"] = "matched summary keywords"
    if _contains_any(question, rules.get("web_keywords", [])):
        selected.append("web_search")
        reasons["web_search"] = "matched web keywords"
    if _contains_any(question, rules.get("escalate_keywords", [])):
        selected.append("escalate")
        reasons["escalate"] = "matched escalate keywords"

    deduped: list[str] = []
    for tool_name in selected:
        if tool_name not in deduped:
            deduped.append(tool_name)
    return deduped, reasons


async def prepare_node(state: AgentState) -> AgentState:
    cfg = load_parent_agent_prompt()
    selected, reasons = _select_tools_with_reasons(state["question"], cfg)

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
            return {"query": question, "count": 3}, "need realtime web context"
        if tool_name == "escalate":
            return {
                "student_id": student_id,
                "reason": "Auto-escalated by keyword policy",
            }, "question indicates escalation policy"
        if tool_name == "get_school_info":
            profile = outputs.get("get_student_profile") or {}
            schools = profile.get("target_schools") or []
            if isinstance(schools, dict):
                school_names = list(schools.values())
            else:
                school_names = schools
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
        if tool_name == "get_milestones":
            return {
                "student_id": student_id,
                "status": None,
                "type_filter": None,
                "limit": 10,
            }, "retrieve recent milestones for progress context"
        if tool_name == "get_conversation_history":
            return {"student_id": student_id, "limit": 20}, "preserve prior conversation context"
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

    prompt = (
        f"Question from parent: {state['question']}\n\n"
        f"Tool outputs (JSON):\n{json.dumps(state.get('tool_outputs', {}), ensure_ascii=False, default=str)}\n\n"
        f"Style rules: {style}\n"
        "Write final answer in Vietnamese for parent."
    )

    logger.info(
        "orchestrator.respond using_tools=%s style_rules=%s",
        state.get("selected_tools", []),
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
    context_snapshot = _sanitize_json({
        "selected_tools": state.get("selected_tools", []),
        "tool_outputs": state.get("tool_outputs", {}),
        "orchestration_trace": state.get("orchestration_trace", []),
    })

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

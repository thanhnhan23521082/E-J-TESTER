"""LangGraph workflow for Smart Parenting parent chatbot."""

from __future__ import annotations

import json
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


class AgentState(TypedDict, total=False):
    db: AsyncSession
    student_id: str
    parent_id: int
    question: str
    selected_tools: list[str]
    tool_outputs: dict[str, Any]
    final_answer: str
    escalated: bool


def _contains_any(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def _select_tools(question: str, prompt_cfg: dict[str, Any]) -> list[str]:
    rules = prompt_cfg.get("agent", {}).get("tool_selection_rules", {})
    selected = ["get_student_profile", "get_conversation_history"]

    if _contains_any(question, rules.get("mentor_keywords", [])):
        selected.append("get_mentor_info")
    if _contains_any(question, rules.get("behavior_keywords", [])):
        selected.append("get_behavioral_logs")
    if _contains_any(question, rules.get("milestone_keywords", [])):
        selected.append("get_milestones")
    if _contains_any(question, rules.get("summary_keywords", [])):
        selected.append("get_weekly_digest")
    if _contains_any(question, rules.get("course_keywords", [])):
        selected.append("search_courses")
    if _contains_any(question, rules.get("school_keywords", [])):
        selected.append("get_school_info")
    if _contains_any(question, rules.get("summary_keywords", [])):
        selected.append("get_progress_summary")
    if _contains_any(question, rules.get("web_keywords", [])):
        selected.append("web_search")
    if _contains_any(question, rules.get("escalate_keywords", [])):
        selected.append("escalate")

    deduped: list[str] = []
    for tool_name in selected:
        if tool_name not in deduped:
            deduped.append(tool_name)
    return deduped


async def prepare_node(state: AgentState) -> AgentState:
    cfg = load_parent_agent_prompt()
    selected = _select_tools(state["question"], cfg)

    if len(selected) == 2 and len(state["question"].split()) < 6:
        selected = ["chitchat"]

    return {**state, "selected_tools": selected, "tool_outputs": {}, "escalated": False}


async def tools_node(state: AgentState) -> AgentState:
    db = state["db"]
    student_id = state["student_id"]
    parent_id = state["parent_id"]
    question = state["question"]

    outputs: dict[str, Any] = {}

    def _build_tool_input(tool_name: str) -> dict[str, Any]:
        if tool_name == "chitchat":
            return {"query": question}
        if tool_name == "web_search":
            return {"query": question, "count": 3}
        if tool_name == "escalate":
            return {
                "student_id": student_id,
                "reason": "Auto-escalated by keyword policy",
            }
        if tool_name == "get_school_info":
            profile = outputs.get("get_student_profile") or {}
            schools = profile.get("target_schools") or []
            if isinstance(schools, dict):
                school_names = list(schools.values())
            else:
                school_names = schools
            return {"school_names": school_names}
        if tool_name == "search_courses":
            profile = outputs.get("get_student_profile") or {}
            return {
                "student_id": student_id,
                "skill": profile.get("weakest_skill"),
                "program": profile.get("program"),
            }
        if tool_name == "get_behavioral_logs":
            return {"student_id": student_id, "days": 14}
        if tool_name == "get_milestones":
            return {"student_id": student_id, "status": None, "type_filter": None, "limit": 10}
        if tool_name == "get_conversation_history":
            return {"student_id": student_id, "limit": 20}
        return {"student_id": student_id}

    token = set_tool_runtime_context(db=db, parent_id=parent_id)
    try:
        for tool_name in state.get("selected_tools", []):
            tool_obj = LANGGRAPH_TOOLS.get(tool_name)
            if tool_obj is None:
                continue
            tool_input = _build_tool_input(tool_name)
            outputs[tool_name] = await tool_obj.ainvoke(tool_input)
    finally:
        reset_tool_runtime_context(token)

    return {
        **state,
        "tool_outputs": outputs,
        "escalated": "escalate" in outputs,
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

    answer = await call_text(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.3,
        max_tokens=900,
    )

    return {**state, "final_answer": answer}


async def persist_node(state: AgentState) -> AgentState:
    db = state["db"]
    context_snapshot = {
        "selected_tools": state.get("selected_tools", []),
        "tool_outputs": state.get("tool_outputs", {}),
    }

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

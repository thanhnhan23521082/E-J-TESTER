"""
modules/etester/services/llm_service.py
───────────────────────────────────────
LLM-powered AI functions for ETESTER v4.
All calls go through shared/clients/llm_client.py (OpenAI SDK).
"""

import json
import logging

from shared.clients.llm_client import call_text

logger = logging.getLogger(__name__)


async def suggest_trace_links(
    new_milestone_title: str,
    new_milestone_type: str,
    new_milestone_notes: str | None,
    existing_milestones: list[dict],
) -> list[dict]:
    """
    Ask LLM to suggest trace links between a new milestone and existing ones.
    Returns list of { target_milestone_id, relationship_type, evidence, confidence }.
    """
    milestones_text = "\n".join(
        f"  - id={m['id']} | type={m['type']} | title={m['title']} | date={m['date']}"
        for m in existing_milestones
    )

    system = (
        "You are an AI trace engine for ETEST educational platform. "
        "Given a new milestone and a list of existing milestones, suggest causal links. "
        "For each link, provide: target milestone id, relationship type "
        "(experience_source | revision_of | mentor_guided | skill_applied | score_progression | recommends), "
        "evidence text (1 sentence explaining the connection), and confidence (0.0-1.0). "
        "Return JSON array. Max 5 suggestions. Only suggest links with confidence >= 0.7."
    )

    prompt = (
        f"New milestone:\n"
        f"  title: {new_milestone_title}\n"
        f"  type: {new_milestone_type}\n"
        f"  notes: {new_milestone_notes or 'N/A'}\n\n"
        f"Existing milestones:\n{milestones_text}\n\n"
        f"Return JSON array of suggested links."
    )

    try:
        raw = await call_text(prompt=prompt, system_prompt=system, max_tokens=800, temperature=0.3)
        suggestions = json.loads(raw)
        if not isinstance(suggestions, list):
            return []
        return suggestions[:5]
    except Exception as exc:
        logger.warning("Trace link suggestion failed: %s", exc)
        return []


async def score_authenticity_7dim(
    essay_text: str,
    student_writing_level: str,
    essay_history_context: str,
    trace_links_context: str,
    student_notes_context: str,
) -> dict:
    """
    Score essay authenticity across 7 dimensions.
    Returns { auth_score, verdict, dimension_scores, explaining_artifacts,
              explanation_en, explanation_vn }.
    """
    system = (
        "You are an expert authenticity scorer for academic essays. "
        "Score the essay across 7 dimensions (0-100 each):\n"
        "D1: Syntactic Consistency (weight 0.25) - paragraph style matches history\n"
        "D2: Lexical Fingerprint (weight 0.15) - vocabulary density alignment\n"
        "D3: Temporal Coherence (weight 0.15) - timeline of skill development\n"
        "D4: Source Attribution (weight 0.15) - references to known experiences\n"
        "D5: Mentor Alignment (weight 0.10) - matches mentor session feedback\n"
        "D6: Behavioral Consistency (weight 0.10) - study patterns support claims\n"
        "D7: Graph Connectivity (weight 0.10) - artifact connections are logical\n\n"
        "Compute weighted overall score (0-100). "
        "Verdict: justified_growth | consistent | needs_review | suspicious_jump | insufficient_data.\n"
        "Return JSON with: auth_score (int), verdict (str), "
        "dimension_scores (object with d1-d7 each having score, weight, note), "
        "explaining_artifacts (array), explanation_en (str), explanation_vn (str)."
    )

    prompt = (
        f"Student writing level: {student_writing_level}\n"
        f"Essay history:\n{essay_history_context}\n\n"
        f"Trace links:\n{trace_links_context}\n\n"
        f"Student context notes:\n{student_notes_context}\n\n"
        f"Essay text:\n{essay_text[:3000]}\n\n"
        f"Score authenticity. Return JSON."
    )

    try:
        raw = await call_text(prompt=prompt, system_prompt=system, max_tokens=1200, temperature=0.2)
        result = json.loads(raw)
        return {
            "auth_score": min(100, max(0, int(result.get("auth_score", 50)))),
            "verdict": result.get("verdict", "insufficient_data"),
            "dimension_scores": result.get("dimension_scores", {}),
            "explaining_artifacts": result.get("explaining_artifacts", []),
            "explanation_en": result.get("explanation_en"),
            "explanation_vn": result.get("explanation_vn"),
        }
    except Exception as exc:
        logger.warning("7-dim auth scoring failed: %s", exc)
        return {
            "auth_score": 50,
            "verdict": "insufficient_data",
            "dimension_scores": {},
            "explaining_artifacts": [],
            "explanation_en": "Unable to evaluate — please try again.",
            "explanation_vn": "Không thể đánh giá — vui lòng thử lại.",
        }


async def build_narrative(
    student_name: str,
    milestones_text: str,
    core_text: str,
) -> dict:
    """
    Generate EN + VN narrative from student data.
    Returns { narrative_en, narrative_vn }.
    """
    system = (
        "You are an expert personal narrative writer for university applications. "
        "Write 2-4 paragraphs (3-5 sentences each) telling the student's learning journey. "
        "Use specific details from milestones. Voice: authentic, emotional, growth mindset. "
        "No generic language. Master narrative style. "
        "Return JSON: { narrative_en: string, narrative_vn: string }"
    )

    prompt = (
        f"Student name: {student_name}\n"
        f"Milestones:\n{milestones_text}\n\n"
        f"ETESTER Core profile:\n{core_text}\n\n"
        f"Write compelling narratives in both English and Vietnamese."
    )

    try:
        raw = await call_text(prompt=prompt, system_prompt=system, max_tokens=1500, temperature=0.7)
        result = json.loads(raw)
        return {
            "narrative_en": result.get("narrative_en", ""),
            "narrative_vn": result.get("narrative_vn", ""),
        }
    except Exception as exc:
        logger.warning("Narrative generation failed: %s", exc)
        return {"narrative_en": None, "narrative_vn": None}


async def summarize_milestone(
    milestone_type: str,
    title: str,
    score: float | None,
    notes: str | None,
    date: str,
) -> str | None:
    """Generate a short AI summary for a milestone."""
    system = (
        "Bạn là trợ lý AI của ETEST ONE. "
        "Viết bản tóm tắt ngắn gọn (50-150 từ) cho một cột mốc học tập. "
        "Mô tả ngắn gọn thành tích, nhấn mạnh tiến bộ. "
        "Trả lời bằng tiếng Việt, giọng văn tích cực."
    )

    prompt = (
        f"Type: {milestone_type}\nTitle: {title}\n"
        f"Score: {score}\nNotes: {notes or 'Không có'}\nDate: {date}\n\n"
        f"Viết bản tóm tắt:"
    )

    try:
        return await call_text(prompt=prompt, system_prompt=system, max_tokens=256, temperature=0.5)
    except Exception as exc:
        logger.warning("Milestone summarization failed: %s", exc)
        return None

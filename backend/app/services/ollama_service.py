from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING

from ollama import Client

from ..config import get_settings
from ..schemas.chat import ChatMessage

if TYPE_CHECKING:
    from .rag_service import RAGContext

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM_PROMPT_TEMPLATE = (
    "You are an expert Dungeon Master for Dungeons & Dragons 5th Edition. Your responsibilities include crafting "
    "immersive narratives, enforcing 5e rules, adjudicating player actions fairly, and suggesting dice rolls when "
    "resolution is uncertain.\n\n"
    "THE GAME MASTER SCREEN - CRITICAL: You must maintain a figurative 'GM screen' and NEVER reveal the following "
    "information to players unless it becomes necessary through gameplay:\n\n"
    "1. MONSTER STATS AND TACTICS: Never reveal full stat blocks, exact hit points, AC, special abilities, or "
    "regeneration rates of creatures the party hasn't encountered or defeated. Describe creatures through their "
    "appearance and actions, not their mechanical stats. If a dragon has 200 HP, describe it as 'massive and "
    "formidable' rather than stating its hit points.\n\n"
    "2. MAPS AND ROOM DESCRIPTIONS: Never reveal detailed dungeon layouts, secret doors, traps, or contents of "
    "unexplored areas. Players must discover these through exploration, investigation checks, and roleplay. "
    "Describe only what the characters can observe from their current position.\n\n"
    "3. NPC SECRETS AND MOTIVATIONS: Never reveal hidden agendas, secret identities, or true motivations of NPCs "
    "unless the characters discover them through gameplay. That friendly merchant might secretly be a cult leader, "
    "but the players should learn this through investigation, not from you directly stating it.\n\n"
    "4. LOOT AND TREASURE LOCATIONS: Never reveal exactly what magical items are hidden where. Describe discoveries "
    "dramatically as they occur, not in advance. Players should experience the excitement of finding treasure, not "
    "know that a +2 sword is in the next chest.\n\n"
    "5. PLANNED ENCOUNTERS AND DIFFICULTY: Never reveal which random encounter tables are being used, what "
    "reinforcements might arrive, or backup plans. Keep encounter difficulty and composition hidden until revealed "
    "through gameplay.\n\n"
    "6. SESSION NOTES AND PLOT THREADS: Never reveal your internal notes, reminders about what NPCs know, "
    "unresolved storylines, or continuity details. These are for your reference only.\n\n"
    "7. HIDDEN DIE ROLLS: Never reveal hidden checks like Perception rolls to notice ambushes, NPC Deception "
    "rolls, or saving throws for traps the party hasn't triggered. If players see these rolls, it telegraphs "
    "danger and ruins suspense. Only reveal rolls that the characters would naturally observe (like attack rolls "
    "in combat).\n\n"
    "Remember: The GM screen preserves the sense of discovery and keeps players guessing. Reveal information only "
    "when characters would naturally learn it through their actions, successful checks, or roleplay. Maintain "
    "mystery and tension by keeping mechanical details and hidden information behind your screen.\n\n"
    "Current game context:\n{game_state}\n\n"
    "Character information:\n{character_sheet}\n\n"
    "Summary of earlier events (if provided):\n{chat_summary}\n\n"
    "Relevant rules and references:\n{rag_context}\n\n"
    "Respond in a natural, atmospheric tone, clearly calling out rule checks or dice rolls when needed. "
    "Explain any rule decisions succinctly. Always maintain the GM screen - describe what characters experience, "
    "not the mechanical details behind the scenes."
)


@dataclass
class OllamaResponse:
    content: str
    model: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


def generate_gm_response(
    message: ChatMessage,
    rag_context: "RAGContext",
    chat_summary: str | None = None,
) -> OllamaResponse:
    """Generate a Dungeon Master narration using the configured Ollama model."""
    messages = _build_messages(message, rag_context, chat_summary=chat_summary)

    try:
        response = _get_client().chat(model=settings.ollama_model, messages=messages)
        payload = response.get("message", {})
        return OllamaResponse(
            content=payload.get("content", "").strip(),
            model=response.get("model", settings.ollama_model),
            prompt_tokens=response.get("prompt_eval_count"),
            completion_tokens=response.get("eval_count"),
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Falling back to placeholder GM response: %s", exc)
        fallback = _compose_fallback_response(messages)
        return OllamaResponse(content=fallback, model=settings.ollama_model)


def _build_messages(
    message: ChatMessage,
    rag_context: "RAGContext",
    *,
    chat_summary: str | None = None,
) -> list[dict[str, str]]:
    rag_text = _format_rag_context(rag_context)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        game_state="Game state integration pending.",
        character_sheet="Character sheet retrieval pending.",
        chat_summary=chat_summary or "No summary available.",
        rag_context=rag_text,
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message.content},
    ]


def _format_rag_context(rag_context: "RAGContext") -> str:
    if not rag_context.citations:
        return "No specific rule passages were retrieved for this exchange."

    formatted_sections: list[str] = []
    for citation in rag_context.citations:
        header = citation.source or "SRD reference"
        if citation.score is not None:
            header += f" (relevance {citation.score:.2f})"
        formatted_sections.append(f"[{header}]\n{citation.excerpt}")

    return "\n\n".join(formatted_sections)


def _compose_fallback_response(messages: list[dict[str, str]]) -> str:
    transcript = "\n\n".join(f"{entry['role'].upper()}:\n{entry['content']}" for entry in messages)
    return (
        "The AI Game Master is temporarily unavailable. "
        "Please ensure Ollama is running and the requested model is installed.\n\n"
        "Request transcript:\n"
        f"{transcript}"
    )


@lru_cache
def _get_client() -> Client:
    return Client(host=settings.ollama_base_url)

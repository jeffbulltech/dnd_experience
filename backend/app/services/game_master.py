from __future__ import annotations

import json
import logging
from collections.abc import Generator
from typing import Any

from sqlalchemy.orm import Session

from ..models import ChatMessage as ChatLogEntry
from ..schemas.chat import ChatMessage, ChatResponse
from ..schemas.characters import CharacterRead
from ..schemas.game_state import GameStateRead
from . import character_service, chat_service, game_state_service, ollama_service, rag_service

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Context formatting helpers
# ---------------------------------------------------------------------------

ABILITY_NAMES = {
    "str": "Strength", "dex": "Dexterity", "con": "Constitution",
    "int": "Intelligence", "wis": "Wisdom", "cha": "Charisma",
}


def _format_game_state(state: GameStateRead) -> str:
    """Format GameState into a concise prompt section."""
    parts: list[str] = []
    if state.location:
        parts.append(f"Current location: {state.location}")
    if state.active_quests:
        quests = ", ".join(state.active_quests)
        parts.append(f"Active quests: {quests}")
    if state.summary:
        parts.append(f"Narrative summary: {state.summary}")
    return "\n".join(parts) if parts else "The adventure is just beginning — no state recorded yet."


def _format_character(char: CharacterRead) -> str:
    """Format a Character into a concise prompt section."""
    lines: list[str] = [f"Name: {char.name}"]
    if char.race:
        lines.append(f"Species: {char.race}")
    if char.character_class:
        lines.append(f"Class: {char.character_class}")
    lines.append(f"Level: {char.level}")
    if char.background:
        lines.append(f"Background: {char.background}")
    if char.alignment:
        lines.append(f"Alignment: {char.alignment}")
    if char.ability_scores:
        scores = ", ".join(
            f"{ABILITY_NAMES.get(k, k)} {v} ({_modifier(v):+d})"
            for k, v in char.ability_scores.items()
        )
        lines.append(f"Ability scores: {scores}")
    if char.skills:
        skill_list = ", ".join(f"{k} {v:+d}" for k, v in char.skills.items())
        lines.append(f"Skill modifiers: {skill_list}")
    if char.notes:
        lines.append(f"Player notes: {char.notes}")
    return "\n".join(lines)


def _modifier(score: int) -> int:
    return (score - 10) // 2


def _gather_context(db: Session, message: ChatMessage) -> dict[str, str | None]:
    """Fetch game state and character, returning formatted text for each."""
    game_state_text: str | None = None
    character_text: str | None = None

    try:
        state = game_state_service.get_game_state(db, message.campaign_id)
        game_state_text = _format_game_state(state)
    except ValueError:
        logger.debug("No game state for campaign %s", message.campaign_id)

    if message.character_id:
        char = character_service.get_character(db, message.character_id)
        if char:
            character_text = _format_character(char)

    return {"game_state_text": game_state_text, "character_text": character_text}


# ---------------------------------------------------------------------------
# Message handlers
# ---------------------------------------------------------------------------

def handle_player_message(db: Session, message: ChatMessage) -> ChatResponse:
    """Process player input using RAG and Ollama, persisting the exchange."""
    rag_context = rag_service.fetch_relevant_rules(db, message)
    history_entries = chat_service.fetch_chat_history(db, campaign_id=message.campaign_id, limit=120)
    chat_summary = rag_service.summarize_chat_history(history_entries)
    context = _gather_context(db, message)

    gm_reply = ollama_service.generate_gm_response(
        message, rag_context, chat_summary=chat_summary, **context,
    )

    metadata: dict[str, Any] = {"combatActive": False}
    if gm_reply.model:
        metadata["model"] = gm_reply.model
    if gm_reply.prompt_tokens is not None:
        metadata["promptTokens"] = gm_reply.prompt_tokens
    if gm_reply.completion_tokens is not None:
        metadata["completionTokens"] = gm_reply.completion_tokens
    if rag_context.citations:
        metadata["ragCitations"] = [citation.as_dict() for citation in rag_context.citations]
    if rag_context.sources:
        metadata["ragSources"] = rag_context.sources
    if chat_summary:
        metadata["chatSummary"] = chat_summary

    player_entry = ChatLogEntry(
        campaign_id=message.campaign_id,
        character_id=message.character_id,
        role="player",
        content=message.content,
        extra={"user_id": message.user_id} if message.user_id else {},
    )
    gm_entry = ChatLogEntry(
        campaign_id=message.campaign_id,
        character_id=None,
        role="gm",
        content=gm_reply.content,
        rag_context=list(rag_context.context_chunks),
        extra=metadata,
    )

    db.add(player_entry)
    db.add(gm_entry)
    db.commit()

    return ChatResponse(
        response=gm_reply.content,
        rag_sources=rag_context.sources,
        metadata=metadata,
        timestamp=gm_entry.created_at,
    )


def stream_player_message(db: Session, message: ChatMessage) -> Generator[str, None, None]:
    """Stream GM response as Server-Sent Events.

    Yields SSE-formatted lines:
      - ``event: token``  with ``data: <text>`` for each content delta
      - ``event: done``   with ``data: <json metadata>`` when complete
      - ``event: error``  if something goes wrong
    """
    # --- pre-generation work (fast, non-streaming) ---
    rag_context = rag_service.fetch_relevant_rules(db, message)
    history_entries = chat_service.fetch_chat_history(db, campaign_id=message.campaign_id, limit=120)
    chat_summary = rag_service.summarize_chat_history(history_entries)
    context = _gather_context(db, message)

    # Persist the player message immediately so the user sees it in history
    player_entry = ChatLogEntry(
        campaign_id=message.campaign_id,
        character_id=message.character_id,
        role="player",
        content=message.content,
        extra={"user_id": message.user_id} if message.user_id else {},
    )
    db.add(player_entry)
    db.flush()

    # --- stream tokens from Ollama ---
    token_gen, get_final = ollama_service.stream_gm_response(
        message, rag_context, chat_summary=chat_summary, **context,
    )

    for delta in token_gen:
        yield f"event: token\ndata: {json.dumps(delta)}\n\n"

    # --- post-generation: build metadata, persist, send final event ---
    gm_reply = get_final()

    metadata: dict[str, Any] = {"combatActive": False}
    if gm_reply.model:
        metadata["model"] = gm_reply.model
    if gm_reply.prompt_tokens is not None:
        metadata["promptTokens"] = gm_reply.prompt_tokens
    if gm_reply.completion_tokens is not None:
        metadata["completionTokens"] = gm_reply.completion_tokens
    if rag_context.citations:
        metadata["ragCitations"] = [citation.as_dict() for citation in rag_context.citations]
    if rag_context.sources:
        metadata["ragSources"] = rag_context.sources
    if chat_summary:
        metadata["chatSummary"] = chat_summary

    gm_entry = ChatLogEntry(
        campaign_id=message.campaign_id,
        character_id=None,
        role="gm",
        content=gm_reply.content,
        rag_context=list(rag_context.context_chunks),
        extra=metadata,
    )
    db.add(gm_entry)
    db.commit()

    done_payload = json.dumps({
        "response": gm_reply.content,
        "rag_sources": rag_context.sources,
        "metadata": metadata,
        "timestamp": gm_entry.created_at.isoformat(),
    })
    yield f"event: done\ndata: {done_payload}\n\n"

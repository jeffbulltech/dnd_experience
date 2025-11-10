from sqlalchemy.orm import Session


def evaluate_action(db: Session, action_description: str) -> dict:
    """
    Evaluate a player's declared action against D&D 5e rules.

    TODO: Integrate with RAG pipeline and structured rule definitions.
    """
    _ = db, action_description
    raise NotImplementedError("Rules engine not yet implemented.")

"""Factory functions for creating test users."""

import itertools
from sqlalchemy.orm import Session

from app.models import User
from app.services import auth_service
from app.schemas.auth import UserCreate

USER_SEQ = itertools.count()


def create_test_user(session: Session, **overrides) -> User:
    """
    Create a test user with default values.
    
    Args:
        session: Database session
        **overrides: Override default values (email, username, password, display_name)
    
    Returns:
        Created User model instance
    """
    suffix = next(USER_SEQ)
    defaults = {
        "email": f"user{suffix}@test.com",
        "username": f"user{suffix}",
        "password": "testpass123",
        "display_name": f"Test User {suffix}",
    }
    defaults.update(overrides)
    
    user_data = UserCreate(**defaults)
    user_read = auth_service.create_user(session, user_data)
    
    # Return the actual User model instance
    return session.get(User, user_read.id)

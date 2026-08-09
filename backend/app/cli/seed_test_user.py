from __future__ import annotations

import logging

from app.database import SessionLocal
from app.logging_config import setup_logging
from app.models import User
from app.schemas.auth import UserCreate
from app.services import auth_service

logger = logging.getLogger(__name__)

TEST_USERNAME = "newplayer"
TEST_PASSWORD = "newplayer"
TEST_EMAIL = "newplayer@example.com"
TEST_DISPLAY_NAME = "New Player"


def main() -> None:
    setup_logging()
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == TEST_USERNAME).first()
        if existing:
            logger.info("Test user %r already exists, skipping.", TEST_USERNAME)
            return

        auth_service.create_user(
            db,
            UserCreate(
                email=TEST_EMAIL,
                username=TEST_USERNAME,
                password=TEST_PASSWORD,
                display_name=TEST_DISPLAY_NAME,
            ),
        )
        logger.info("Created test user %r.", TEST_USERNAME)
    finally:
        db.close()


if __name__ == "__main__":
    main()

"""Unit tests for auth_service module."""

import pytest

from app.services import auth_service
from app.schemas.auth import LoginRequest, UserCreate
from tests.fixtures.users import create_test_user


class TestAuthService:
    """Unit tests for auth_service functions."""

    def test_create_user_success(self, db_session):
        """Test successful user creation."""
        user_data = UserCreate(
            email="newuser@example.com",
            username="newuser",
            password="securepass123",
            display_name="New User"
        )
        
        result = auth_service.create_user(db_session, user_data)
        
        assert result.id > 0
        assert result.email == "newuser@example.com"
        assert result.username == "newuser"
        assert result.display_name == "New User"
        assert result.is_active is True
        # Password should be hashed, not stored in plain text
        from app.models import User
        user = db_session.get(User, result.id)
        assert user.hashed_password != "securepass123"
        assert user.hashed_password.startswith("$argon2")  # Argon2 hash prefix

    def test_create_user_duplicate_email(self, db_session):
        """Test that creating user with duplicate email raises error."""
        user_data1 = UserCreate(
            email="duplicate@example.com",
            username="user1",
            password="pass12345",
            display_name="User One"
        )
        auth_service.create_user(db_session, user_data1)
        
        user_data2 = UserCreate(
            email="duplicate@example.com",  # Same email
            username="user2",
            password="pass12345",
            display_name="User Two"
        )
        
        with pytest.raises(ValueError, match="already exists"):
            auth_service.create_user(db_session, user_data2)

    def test_create_user_duplicate_username(self, db_session):
        """Test that creating user with duplicate username raises error."""
        user_data1 = UserCreate(
            email="user1@example.com",
            username="duplicate",
            password="pass12345",
            display_name="User One"
        )
        auth_service.create_user(db_session, user_data1)
        
        user_data2 = UserCreate(
            email="user2@example.com",
            username="duplicate",  # Same username
            password="pass12345",
            display_name="User Two"
        )
        
        with pytest.raises(ValueError, match="already exists"):
            auth_service.create_user(db_session, user_data2)

    def test_authenticate_user_success(self, db_session):
        """Test successful user authentication."""
        user_data = UserCreate(
            email="auth@example.com",
            username="authtest",
            password="correctpass",
            display_name="Auth Test"
        )
        created_user = auth_service.create_user(db_session, user_data)
        
        login_request = LoginRequest(username="authtest", password="correctpass")
        token_response = auth_service.authenticate_user(db_session, login_request)
        
        assert token_response.access_token is not None
        assert len(token_response.access_token) > 0

    def test_authenticate_user_invalid_username(self, db_session):
        """Test authentication with non-existent username."""
        login_request = LoginRequest(username="nonexistent", password="anypass")
        
        with pytest.raises(ValueError, match="Invalid username or password"):
            auth_service.authenticate_user(db_session, login_request)

    def test_authenticate_user_invalid_password(self, db_session):
        """Test authentication with incorrect password."""
        user_data = UserCreate(
            email="wrongpass@example.com",
            username="wrongpass",
            password="correctpass",
            display_name="Wrong Pass"
        )
        auth_service.create_user(db_session, user_data)
        
        login_request = LoginRequest(username="wrongpass", password="wrongpassword")
        
        with pytest.raises(ValueError, match="Invalid username or password"):
            auth_service.authenticate_user(db_session, login_request)

    def test_get_current_user_success(self, db_session):
        """Test retrieving current user from valid token."""
        user_data = UserCreate(
            email="token@example.com",
            username="tokentest",
            password="pass12345",
            display_name="Token Test"
        )
        created_user = auth_service.create_user(db_session, user_data)
        
        # Create a token
        login_request = LoginRequest(username="tokentest", password="pass12345")
        token_response = auth_service.authenticate_user(db_session, login_request)
        
        # Get user from token
        user = auth_service.get_current_user(db_session, token_response.access_token)
        
        assert user.id == created_user.id
        assert user.email == "token@example.com"
        assert user.username == "tokentest"

    def test_get_current_user_invalid_token(self, db_session):
        """Test that invalid token raises error."""
        with pytest.raises(ValueError, match="Invalid authentication token"):
            auth_service.get_current_user(db_session, "invalid.token.here")

    def test_get_current_user_expired_token(self, db_session):
        """Test that expired token raises error."""
        from datetime import datetime, timedelta
        import jwt
        from app.config import get_settings
        
        settings = get_settings()
        # Create expired token
        expired_time = datetime.utcnow() - timedelta(hours=1)
        expired_token = jwt.encode(
            {"sub": "1", "exp": expired_time},
            settings.secret_key,
            algorithm="HS256"
        )
        
        with pytest.raises(ValueError, match="Invalid authentication token"):
            auth_service.get_current_user(db_session, expired_token)

    def test_get_current_user_nonexistent_user(self, db_session):
        """Test that token for non-existent user raises error."""
        import jwt
        from datetime import datetime, timedelta
        from app.config import get_settings
        
        settings = get_settings()
        # Create token for user that doesn't exist
        token_expires = datetime.utcnow() + timedelta(hours=6)
        fake_token = jwt.encode(
            {"sub": "99999", "exp": token_expires},
            settings.secret_key,
            algorithm="HS256"
        )
        
        with pytest.raises(ValueError, match="User not found"):
            auth_service.get_current_user(db_session, fake_token)

    def test_password_hashing_different_for_same_password(self, db_session):
        """Test that same password produces different hashes (salt)."""
        user_data1 = UserCreate(
            email="hash1@example.com",
            username="hash1",
            password="samepassword",
            display_name="Hash One"
        )
        user1 = auth_service.create_user(db_session, user_data1)
        
        user_data2 = UserCreate(
            email="hash2@example.com",
            username="hash2",
            password="samepassword",  # Same password
            display_name="Hash Two"
        )
        user2 = auth_service.create_user(db_session, user_data2)
        
        # Hashes should be different due to salt
        from app.models import User
        db_user1 = db_session.get(User, user1.id)
        db_user2 = db_session.get(User, user2.id)
        
        assert db_user1.hashed_password != db_user2.hashed_password
        # But both should verify correctly
        assert auth_service.pwd_context.verify("samepassword", db_user1.hashed_password)
        assert auth_service.pwd_context.verify("samepassword", db_user2.hashed_password)

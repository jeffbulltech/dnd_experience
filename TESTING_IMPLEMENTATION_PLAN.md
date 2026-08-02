# Comprehensive Testing Suite - Implementation Plan

**Target:** 80%+ code coverage for backend services and API endpoints  
**Timeline:** 3-4 weeks for full implementation  
**Priority:** P0 - Critical

---

## Current State Analysis

### Existing Test Infrastructure
- ✅ **Test Framework**: pytest configured
- ✅ **Database Fixtures**: In-memory SQLite database for testing
- ✅ **API Client**: FastAPI TestClient fixture
- ✅ **Basic Tests**: 2 test files with ~10 test cases
- ❌ **Coverage**: Estimated <20% code coverage
- ❌ **Service Tests**: Only partial coverage of character/campaign services
- ❌ **API Tests**: Only health check endpoint tested
- ❌ **Fixtures**: Minimal reusable fixtures

### Gaps Identified
1. **Service Layer**: 19 services, only 3-4 partially tested
2. **API Layer**: 11 routers, ~40 endpoints, only 1 tested
3. **Error Cases**: No negative test cases
4. **Edge Cases**: Limited boundary testing
5. **Mocking**: No mocks for external services (Ollama, ChromaDB)
6. **Fixtures**: No standardized test data factories

---

## Test Structure & Organization

### Proposed Directory Structure

```
backend/tests/
├── conftest.py                    # Shared fixtures (enhanced)
├── fixtures/                       # Test data factories
│   ├── __init__.py
│   ├── users.py                   # User factory
│   ├── campaigns.py               # Campaign factory
│   ├── characters.py              # Character factory
│   └── game_data.py               # Game state, encounters, etc.
├── unit/                          # Unit tests (isolated)
│   ├── services/
│   │   ├── test_adventure_service.py
│   │   ├── test_auth_service.py
│   │   ├── test_campaign_service.py
│   │   ├── test_character_service.py
│   │   ├── test_character_builder_service.py
│   │   ├── test_character_builder_rules.py
│   │   ├── test_chat_service.py
│   │   ├── test_combat_engine.py
│   │   ├── test_dice_service.py
│   │   ├── test_game_master.py
│   │   ├── test_game_state_service.py
│   │   ├── test_inventory_service.py
│   │   ├── test_ollama_service.py
│   │   ├── test_rag_service.py
│   │   └── test_rules_engine.py
│   └── utils/
│       └── test_dice_roller.py
├── integration/                   # Integration tests
│   ├── api/
│   │   ├── test_auth_api.py
│   │   ├── test_campaigns_api.py
│   │   ├── test_characters_api.py
│   │   ├── test_chat_api.py
│   │   ├── test_combat_api.py
│   │   ├── test_dice_api.py
│   │   └── test_inventory_api.py
│   └── services/
│       ├── test_game_master_integration.py
│       └── test_rag_integration.py
└── e2e/                           # End-to-end tests (future)
    └── test_campaign_flow.py
```

---

## Enhanced Test Fixtures

### 1. Enhanced `conftest.py`

**Changes:**
- Add authentication fixtures (authenticated user, JWT tokens)
- Add mock fixtures for external services (Ollama, ChromaDB)
- Add database transaction rollback for isolation
- Add coverage configuration
- Add test data factories

**Implementation:**

```python
# backend/tests/conftest.py (enhanced)

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import User
from app.services.auth_service import create_user
from app.schemas.auth import UserCreate

# Database fixture with transaction rollback
@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    
    connection = engine.connect()
    transaction = connection.begin()
    TestingSession = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session = TestingSession()
    
    try:
        yield session
    finally:
        transaction.rollback()
        connection.close()
        engine.dispose()

# API client fixture
@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# Authenticated user fixture
@pytest.fixture()
def test_user(db_session):
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpass123",
        display_name="Test User"
    )
    return create_user(db_session, user_data)

# Authenticated client fixture
@pytest.fixture()
def authenticated_client(client, test_user):
    # Login to get token
    response = client.post(
        "/api/auth/token",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    
    # Set default headers
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

# Mock Ollama client
@pytest.fixture()
def mock_ollama_client():
    with patch("app.services.ollama_service._get_client") as mock:
        mock_client = Mock()
        mock_client.chat.return_value = {
            "message": {"content": "Test GM response"},
            "model": "mistral",
            "prompt_eval_count": 100,
            "eval_count": 50
        }
        mock.return_value = mock_client
        yield mock_client

# Mock ChromaDB
@pytest.fixture()
def mock_chroma_db():
    with patch("app.services.rag_service._get_vector_store") as mock:
        mock_store = Mock()
        mock_store.similarity_search_with_score.return_value = [
            (Mock(page_content="Test rule content", metadata={"source": "SRD"}), 0.95)
        ]
        mock.return_value = mock_store
        yield mock_store
```

### 2. Test Data Factories

**Create `backend/tests/fixtures/` directory with factory functions:**

```python
# backend/tests/fixtures/users.py
def create_test_user(session, **overrides):
    """Factory for creating test users."""
    defaults = {
        "email": f"user{id(overrides)}@test.com",
        "username": f"user{id(overrides)}",
        "hashed_password": "hashed_password",
        "display_name": "Test User"
    }
    defaults.update(overrides)
    user = User(**defaults)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# backend/tests/fixtures/campaigns.py
def create_test_campaign(session, owner_id, **overrides):
    """Factory for creating test campaigns."""
    from app.models import Campaign
    from app.services import campaign_service
    from app.schemas.campaigns import CampaignCreate
    
    defaults = {
        "name": "Test Campaign",
        "description": "A test campaign",
        "adventure_template_id": None
    }
    defaults.update(overrides)
    
    payload = CampaignCreate(**defaults)
    return campaign_service.create_campaign(session, payload, owner_id=owner_id)

# backend/tests/fixtures/characters.py
def create_test_character(session, user_id, campaign_id=None, **overrides):
    """Factory for creating test characters."""
    from app.services import character_service
    from app.schemas.characters import CharacterCreate
    
    defaults = {
        "name": "Test Character",
        "level": 1,
        "race": "Human",
        "character_class": "Fighter",
        "background": "Soldier",
        "campaign_id": campaign_id
    }
    defaults.update(overrides)
    
    payload = CharacterCreate(**defaults)
    return character_service.create_character(session, payload, user_id=user_id)
```

---

## Unit Test Implementation

### Service Test Patterns

Each service test file should follow this structure:

```python
# Example: backend/tests/unit/services/test_campaign_service.py

import pytest
from app.services import campaign_service
from app.schemas.campaigns import CampaignCreate, CampaignUpdate
from tests.fixtures.campaigns import create_test_campaign
from tests.fixtures.users import create_test_user

class TestCampaignService:
    """Unit tests for campaign_service module."""
    
    def test_create_campaign_success(self, db_session):
        """Test successful campaign creation."""
        user = create_test_user(db_session)
        payload = CampaignCreate(
            name="New Campaign",
            description="Test description"
        )
        
        result = campaign_service.create_campaign(
            db_session, payload, owner_id=user.id
        )
        
        assert result.id > 0
        assert result.name == "New Campaign"
        assert result.owner_id == user.id
        assert result.game_state is not None
    
    def test_create_campaign_with_adventure_template(self, db_session):
        """Test campaign creation with adventure template."""
        user = create_test_user(db_session)
        payload = CampaignCreate(
            name="Adventure Campaign",
            adventure_template_id="lost-mine-of-phandelver"
        )
        
        result = campaign_service.create_campaign(
            db_session, payload, owner_id=user.id
        )
        
        assert result.adventure_template_id == "lost-mine-of-phandelver"
    
    def test_create_campaign_generates_welcome_message(self, db_session, mock_ollama_client):
        """Test that welcome message is generated on campaign creation."""
        user = create_test_user(db_session)
        payload = CampaignCreate(name="Welcome Test")
        
        result = campaign_service.create_campaign(
            db_session, payload, owner_id=user.id
        )
        
        # Verify welcome message was created
        from app.models import ChatMessage
        messages = db_session.query(ChatMessage).filter(
            ChatMessage.campaign_id == result.id,
            ChatMessage.role == "gm"
        ).all()
        
        assert len(messages) == 1
        assert messages[0].extra.get("is_welcome") is True
    
    def test_list_campaigns_filters_by_owner(self, db_session):
        """Test that list_campaigns only returns owner's campaigns."""
        owner1 = create_test_user(db_session, username="owner1")
        owner2 = create_test_user(db_session, username="owner2")
        
        campaign1 = create_test_campaign(db_session, owner1.id, name="Campaign 1")
        campaign2 = create_test_campaign(db_session, owner2.id, name="Campaign 2")
        
        owner1_campaigns = campaign_service.list_campaigns(
            db_session, owner_id=owner1.id
        )
        
        assert len(owner1_campaigns) == 1
        assert owner1_campaigns[0].id == campaign1.id
        assert owner1_campaigns[0].id != campaign2.id
    
    def test_update_campaign_success(self, db_session):
        """Test successful campaign update."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        update = CampaignUpdate(
            name="Updated Name",
            description="Updated description"
        )
        
        result = campaign_service.update_campaign(
            db_session, campaign.id, update, owner_id=user.id
        )
        
        assert result.name == "Updated Name"
        assert result.description == "Updated description"
    
    def test_update_campaign_wrong_owner(self, db_session):
        """Test that non-owners cannot update campaigns."""
        owner = create_test_user(db_session, username="owner")
        other_user = create_test_user(db_session, username="other")
        campaign = create_test_campaign(db_session, owner.id)
        
        update = CampaignUpdate(name="Hacked Name")
        
        with pytest.raises(ValueError, match="not found or access denied"):
            campaign_service.update_campaign(
                db_session, campaign.id, update, owner_id=other_user.id
            )
    
    def test_delete_campaign_cascades(self, db_session):
        """Test that deleting campaign cascades to related data."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        campaign_id = campaign.id
        
        campaign_service.delete_campaign(
            db_session, campaign_id, owner_id=user.id
        )
        
        # Verify campaign is deleted
        from app.models import Campaign, GameState
        assert db_session.get(Campaign, campaign_id) is None
        assert db_session.query(GameState).filter(
            GameState.campaign_id == campaign_id
        ).first() is None
```

### Key Services to Test

#### 1. **adventure_service.py**
- `list_adventure_templates()` - returns all templates
- `get_adventure_template()` - returns specific template
- `get_adventure_seed_content()` - returns seed content
- Error cases: missing files, invalid JSON

#### 2. **auth_service.py**
- `create_user()` - user creation, password hashing
- `verify_password()` - password verification
- `authenticate_user()` - login logic
- Error cases: duplicate email/username, weak passwords

#### 3. **campaign_service.py**
- `create_campaign()` - campaign creation, welcome message generation
- `list_campaigns()` - filtering by owner
- `get_campaign()` - retrieval with access control
- `update_campaign()` - updates with ownership check
- `delete_campaign()` - deletion with cascade
- Error cases: unauthorized access, missing campaign

#### 4. **character_service.py**
- `list_characters()` - filtering by user/campaign
- `create_character()` - character creation
- `get_character()` - retrieval with access control
- `update_character()` - updates
- `delete_character()` - deletion
- Error cases: unauthorized access, invalid data

#### 5. **character_builder_service.py**
- `create_draft()` - draft creation
- `update_step()` - step updates with validation
- `finalize_draft()` - character finalization
- Validation tests for each step (ability scores, origin, class, etc.)
- Error cases: invalid data, missing steps

#### 6. **chat_service.py**
- `fetch_chat_history()` - history retrieval with limits
- `save_message()` - message persistence
- Pagination and ordering tests

#### 7. **combat_engine.py**
- `process_action()` - action processing
- `get_combat_state()` - state retrieval
- `add_participant()` - participant management
- `update_participant()` - participant updates
- `remove_participant()` - participant removal
- Turn order calculation tests

#### 8. **dice_service.py**
- `record_roll()` - roll logging
- `list_rolls()` - roll history with filtering
- Error cases: invalid expressions

#### 9. **game_master.py**
- `handle_player_message()` - message processing flow
- RAG context integration
- Chat summary generation
- Error handling for Ollama failures

#### 10. **ollama_service.py** (with mocks)
- `generate_gm_response()` - response generation
- `_build_messages()` - message formatting
- `_format_rag_context()` - context formatting
- Error cases: Ollama unavailable, empty responses

#### 11. **rag_service.py** (with mocks)
- `fetch_relevant_rules()` - rule retrieval
- `summarize_chat_history()` - summary generation
- Error cases: empty vector store, no matches

---

## Integration Test Implementation

### API Test Patterns

Each API test file should test:
- Successful requests (200, 201)
- Authentication/authorization (401, 403)
- Validation errors (400, 422)
- Not found errors (404)
- Edge cases and boundaries

```python
# Example: backend/tests/integration/api/test_campaigns_api.py

import pytest
from tests.fixtures.campaigns import create_test_campaign
from tests.fixtures.users import create_test_user

class TestCampaignsAPI:
    """Integration tests for /api/campaigns endpoints."""
    
    def test_list_campaigns_requires_auth(self, client):
        """Test that listing campaigns requires authentication."""
        response = client.get("/api/campaigns")
        assert response.status_code == 401
    
    def test_list_campaigns_success(self, authenticated_client, db_session):
        """Test successful campaign listing."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        response = authenticated_client.get("/api/campaigns")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == campaign.id
    
    def test_create_campaign_success(self, authenticated_client, db_session):
        """Test successful campaign creation."""
        payload = {
            "name": "New Campaign",
            "description": "Test description",
            "adventure_template_id": None
        }
        
        response = authenticated_client.post("/api/campaigns", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Campaign"
        assert "id" in data
    
    def test_create_campaign_with_adventure(self, authenticated_client, db_session):
        """Test campaign creation with adventure template."""
        payload = {
            "name": "Adventure Campaign",
            "adventure_template_id": "lost-mine-of-phandelver"
        }
        
        response = authenticated_client.post("/api/campaigns", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["adventure_template_id"] == "lost-mine-of-phandelver"
    
    def test_create_campaign_validation_error(self, authenticated_client):
        """Test campaign creation with invalid data."""
        payload = {"name": ""}  # Empty name
        
        response = authenticated_client.post("/api/campaigns", json=payload)
        
        assert response.status_code == 422
    
    def test_get_campaign_success(self, authenticated_client, db_session):
        """Test successful campaign retrieval."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        response = authenticated_client.get(f"/api/campaigns/{campaign.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == campaign.id
    
    def test_get_campaign_not_found(self, authenticated_client):
        """Test retrieval of non-existent campaign."""
        response = authenticated_client.get("/api/campaigns/99999")
        assert response.status_code == 404
    
    def test_get_campaign_unauthorized(self, authenticated_client, db_session):
        """Test that users cannot access other users' campaigns."""
        owner = create_test_user(db_session, username="owner")
        other_user = create_test_user(db_session, username="other")
        campaign = create_test_campaign(db_session, owner.id)
        
        # Try to access as other_user
        response = authenticated_client.get(f"/api/campaigns/{campaign.id}")
        assert response.status_code == 403
    
    def test_update_campaign_success(self, authenticated_client, db_session):
        """Test successful campaign update."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        payload = {"name": "Updated Name"}
        response = authenticated_client.put(
            f"/api/campaigns/{campaign.id}", json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
    
    def test_delete_campaign_success(self, authenticated_client, db_session):
        """Test successful campaign deletion."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        response = authenticated_client.delete(f"/api/campaigns/{campaign.id}")
        
        assert response.status_code == 204
        
        # Verify deletion
        get_response = authenticated_client.get(f"/api/campaigns/{campaign.id}")
        assert get_response.status_code == 404
```

### API Endpoints to Test

#### `/api/auth/*`
- Registration (success, duplicate email/username, validation)
- Login (success, invalid credentials)
- Token validation
- User info endpoint

#### `/api/campaigns/*`
- List, create, get, update, delete
- Adventure template selection
- Access control

#### `/api/characters/*`
- List, create, get, update, delete
- Campaign filtering
- Access control

#### `/api/chat/*`
- Send message (success, invalid campaign, missing character)
- Get history (pagination, limits)

#### `/api/combat/*`
- Get state, add participant, update participant, remove participant
- Action processing

#### `/api/dice/*`
- Roll dice (success, invalid expression)
- Get history (filtering)

#### `/api/inventory/*`
- List, create, update, delete items
- Character ownership validation

---

## Coverage Goals & Tools

### Coverage Configuration

**Add to `backend/pytest.ini` or `backend/pyproject.toml`:**

```ini
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = """
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=80
    -v
"""
```

### Coverage Targets

- **Overall**: 80%+ code coverage
- **Services**: 85%+ coverage (critical business logic)
- **API Endpoints**: 90%+ coverage (all success and error paths)
- **Utils**: 90%+ coverage (dice roller, etc.)

### Coverage Tools

```bash
# Install coverage tools
pip install pytest-cov coverage

# Run tests with coverage
pytest --cov=app --cov-report=html

# View HTML report
open htmlcov/index.html
```

---

## Implementation Steps

### Phase 1: Infrastructure Setup (Week 1)
1. ✅ Enhance `conftest.py` with authentication and mock fixtures
2. ✅ Create test data factories in `tests/fixtures/`
3. ✅ Set up coverage configuration
4. ✅ Create test directory structure
5. ✅ Add pytest configuration file

### Phase 2: Service Unit Tests (Week 2)
1. ✅ Test `adventure_service.py` (simple, no external deps)
2. ✅ Test `auth_service.py` (password hashing, validation)
3. ✅ Test `campaign_service.py` (CRUD + welcome messages)
4. ✅ Test `character_service.py` (CRUD operations)
5. ✅ Test `character_builder_service.py` (step validation)
6. ✅ Test `dice_service.py` (roll logging)
7. ✅ Test `inventory_service.py` (item management)
8. ✅ Test `game_state_service.py` (state management)

### Phase 3: Complex Service Tests (Week 2-3)
1. ✅ Test `combat_engine.py` (with mocks)
2. ✅ Test `chat_service.py` (message handling)
3. ✅ Test `ollama_service.py` (with Ollama mocks)
4. ✅ Test `rag_service.py` (with ChromaDB mocks)
5. ✅ Test `game_master.py` (integration of services)

### Phase 4: API Integration Tests (Week 3)
1. ✅ Test `/api/auth/*` endpoints
2. ✅ Test `/api/campaigns/*` endpoints
3. ✅ Test `/api/characters/*` endpoints
4. ✅ Test `/api/chat/*` endpoints
5. ✅ Test `/api/combat/*` endpoints
6. ✅ Test `/api/dice/*` endpoints
7. ✅ Test `/api/inventory/*` endpoints
8. ✅ Test `/api/adventures/*` endpoints

### Phase 5: Edge Cases & Error Handling (Week 4)
1. ✅ Add negative test cases
2. ✅ Test boundary conditions
3. ✅ Test error recovery
4. ✅ Test concurrent operations
5. ✅ Verify coverage targets met

---

## Example Test Files

### Complete Service Test Example

See `backend/tests/unit/services/test_campaign_service.py` above for full example.

### Complete API Test Example

See `backend/tests/integration/api/test_campaigns_api.py` above for full example.

---

## Testing Best Practices

### 1. Test Naming
- Use descriptive names: `test_create_campaign_with_adventure_template_success`
- Follow pattern: `test_<action>_<scenario>_<expected_result>`

### 2. Test Organization
- One test class per service/endpoint
- Group related tests together
- Use fixtures for common setup

### 3. Assertions
- One logical assertion per test
- Use specific assertions: `assert result.id == expected_id`
- Test both positive and negative cases

### 4. Test Data
- Use factories for test data creation
- Keep tests independent (no shared state)
- Clean up after tests (fixtures handle this)

### 5. Mocking
- Mock external services (Ollama, ChromaDB)
- Mock file I/O operations
- Don't mock code under test

### 6. Coverage
- Aim for 80%+ overall coverage
- Focus on critical paths first
- Don't obsess over 100% (some code is hard to test)

---

## Continuous Integration

### GitHub Actions Enhancement

Update `.github/workflows/backend-tests.yml`:

```yaml
name: Backend Tests

on:
  push:
    branches: [ "main", "develop" ]
  pull_request:
    branches: [ "main", "develop" ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python 3.11
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"
        cache: "pip"

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r backend/requirements.txt
        pip install pytest-cov

    - name: Run tests with coverage
      env:
        DATABASE_URL: postgresql+psycopg://postgres:postgres@localhost/test_db
      run: |
        cd backend
        pytest --cov=app --cov-report=xml --cov-report=term

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: backend
```

---

## Success Metrics

### Quantitative
- **Code Coverage**: ≥80% overall, ≥85% for services
- **Test Count**: ~200-300 test cases
- **Test Execution Time**: <30 seconds for full suite
- **CI Pass Rate**: >95% on first run

### Qualitative
- All critical paths tested
- Error cases covered
- Edge cases identified and tested
- Tests are maintainable and readable
- Fast feedback loop for developers

---

## Maintenance Plan

### Ongoing
- Run tests before every commit
- Review coverage reports weekly
- Add tests for new features
- Refactor tests when code changes
- Keep fixtures up to date

### Quarterly Reviews
- Review test coverage trends
- Identify untested code paths
- Update test patterns based on learnings
- Remove obsolete tests

---

## Estimated Effort

- **Infrastructure Setup**: 1 day
- **Service Unit Tests**: 5-7 days
- **API Integration Tests**: 4-5 days
- **Edge Cases & Polish**: 2-3 days
- **Total**: 12-16 days (2.5-3 weeks)

---

## Dependencies

### Required Packages
```bash
pip install pytest pytest-cov pytest-mock coverage
```

### Optional but Recommended
```bash
pip install pytest-asyncio pytest-xdist faker  # For async tests, parallel execution, fake data
```

---

This plan provides a comprehensive roadmap for achieving 80%+ test coverage. Start with Phase 1 (infrastructure) and work through each phase systematically.


# Testing Conventions

## Environment Configuration
```bash
# .env.test
PROJECT_NAME=my-awesome-app
STAGE=test
DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_db
SECRET_KEY=test-secret-key-not-for-production
```

## Project Structure
```
tests/
├── conftest.py              # Pytest fixtures
├── unit/                    # Unit tests
├── integration/             # Integration tests
├── e2e/                     # End-to-end tests
├── fixtures/                # Test data
└── performance/             # Performance tests
```

## Pytest Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
addopts = -v --cov=app --cov-fail-under=80
markers = 
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

## Essential Fixtures
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base

# Test database
engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(test_user):
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
```

## Unit Test Patterns
```python
# tests/unit/test_models.py
class TestUserModel:
    def test_user_creation(self, db_session):
        user = User(email="test@example.com", name="Test User", hashed_password="hash")
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_active is True

# tests/unit/test_services.py
class TestAuthService:
    def test_password_hashing(self):
        auth_service = AuthService(None)
        password = "TestPassword123"
        
        hashed = auth_service.get_password_hash(password)
        assert auth_service.verify_password(password, hashed)
    
    def test_create_access_token(self):
        auth_service = AuthService(None)
        token = auth_service.create_access_token({"sub": "123"})
        assert isinstance(token, str)
        assert len(token) > 0

# tests/unit/test_repositories.py
class TestUserRepository:
    def test_create_user(self, db_session):
        repo = UserRepository(db_session)
        user_data = {"email": "test@example.com", "name": "Test User"}
        
        user = repo.create(user_data)
        assert user.email == "test@example.com"
        assert user.id is not None
    
    def test_soft_delete(self, db_session, test_user):
        repo = UserRepository(db_session)
        success = repo.soft_delete(test_user.id)
        assert success is True
        
        # Should not be returned by normal queries
        active_user = repo.get_by_id(test_user.id)
        assert active_user is None
```

## Integration Test Patterns
```python
# tests/integration/test_api_endpoints.py
class TestAuthEndpoints:
    def test_register_user(self, client):
        user_data = {"email": "new@example.com", "name": "New User", "password": "Password123"}
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == user_data["email"]
        assert "access_token" in data
    
    def test_login_valid_credentials(self, client, test_user):
        login_data = {"username": test_user.email, "password": "password123"}
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

class TestUserEndpoints:
    def test_get_users_authenticated(self, client, auth_headers):
        response = client.get("/api/v1/users/", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "users" in data
        assert "total" in data
    
    def test_get_users_unauthenticated(self, client):
        response = client.get("/api/v1/users/")
        assert response.status_code == 401
```

## E2E Test Patterns
```python
# tests/e2e/test_user_journey.py
class TestUserJourney:
    def test_complete_registration_flow(self, client):
        # Step 1: Register
        user_data = {"email": "journey@example.com", "name": "Journey User", "password": "Password123"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 200
        
        # Step 2: Use token
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Access protected endpoint
        profile_response = client.get("/api/v1/auth/me", headers=headers)
        assert profile_response.status_code == 200
        
        # Step 4: Create document
        doc_data = {"title": "Test Doc", "content": "Test content"}
        doc_response = client.post("/api/v1/documents/", json=doc_data, headers=headers)
        assert doc_response.status_code == 201
```

## Performance Test Patterns
```python
# tests/performance/test_load.py
class TestLoadPerformance:
    @pytest.mark.slow
    async def test_concurrent_requests(self):
        async def make_request(client, i):
            user_data = {"email": f"user{i}@example.com", "name": f"User {i}", "password": "Password123"}
            response = await client.post("/api/v1/auth/register", json=user_data)
            return response.status_code
        
        async with AsyncClient(app=app) as client:
            start_time = time.time()
            tasks = [make_request(client, i) for i in range(50)]
            results = await asyncio.gather(*tasks)
            duration = time.time() - start_time
            
            assert all(status == 200 for status in results)
            assert duration < 10.0  # Should complete within 10 seconds
    
    @pytest.mark.slow
    def test_database_performance(self, db_session):
        # Create test data
        users = [User(email=f"user{i}@example.com", name=f"User {i}") for i in range(100)]
        db_session.add_all(users)
        db_session.commit()
        
        # Test query performance
        start_time = time.time()
        all_users = db_session.query(User).all()
        query_time = time.time() - start_time
        
        assert len(all_users) >= 100
        assert query_time < 0.5  # Should complete within 500ms
```

## Test Data Fixtures
```python
# tests/fixtures/users.py
def create_test_user(db_session, email="test@example.com", role=UserRole.USER):
    hashed_password = get_password_hash("password123")
    user = User(email=email, name="Test User", hashed_password=hashed_password, role=role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

# tests/fixtures/documents.py
def create_test_document(db_session, user_id, title="Test Document"):
    document = Document(title=title, content="Test content", user_id=user_id)
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    return document
```

## Running Tests
```bash
# Run all tests
pytest

# Run by category
pytest -m unit
pytest -m integration
pytest -m e2e

# With coverage
pytest --cov=app --cov-report=html

# Performance tests
pytest -m slow

# Specific file
pytest tests/unit/test_models.py

# Parallel execution
pytest -n auto

# Stop on first failure
pytest -x
```

## Best Practices
- **Test Organization**: Separate unit/integration/e2e tests
- **Naming**: Use descriptive test names explaining what's tested
- **Fixtures**: Use fixtures for common test data and setup
- **Mocking**: Mock external dependencies in unit tests
- **Coverage**: Aim for 80%+ coverage, focus on critical paths
- **Performance**: Mark slow tests, set reasonable thresholds
- **CI/CD**: Run tests on every commit, fail builds on test failures
- **Data Management**: Use factories, clean up after tests, separate test DB
# API Design Conventions

## Environment
```bash
# .env
PROJECT_NAME=my-app
API_VERSION=v1
API_BASE_URL=https://api.example.com
RATE_LIMIT_REQUESTS=1000
CORS_ORIGINS=["https://app.example.com"]
```

## REST API Standards

### URL Structure
```
# Base pattern
https://api.{domain}.com/{version}/

# Resources (plural nouns)
GET    /api/v1/users
POST   /api/v1/users
GET    /api/v1/users/{id}
PUT    /api/v1/users/{id}
DELETE /api/v1/users/{id}

# Nested resources
GET    /api/v1/users/{id}/documents
POST   /api/v1/users/{id}/documents

# Actions (when REST verbs insufficient)
POST   /api/v1/users/{id}/activate
POST   /api/v1/documents/{id}/share

# Query params
GET /api/v1/users?page=1&limit=20&sort=created_at&order=desc
GET /api/v1/users?filter[status]=active&search=john
```

### HTTP Status Codes
```python
# Success
200 # OK (GET, PUT, PATCH)
201 # Created (POST)
204 # No Content (DELETE)

# Client Errors
400 # Bad Request
401 # Unauthorized
403 # Forbidden
404 # Not Found
409 # Conflict
422 # Validation Error
429 # Rate Limited

# Server Errors
500 # Internal Server Error
503 # Service Unavailable
```

## Request/Response Format

### Standard Response
```python
# Success Response
{
    "success": True,
    "data": {...},
    "message": "Optional message",
    "timestamp": "2024-01-01T12:00:00Z"
}

# Error Response
{
    "success": False,
    "message": "Error message",
    "error_code": "VALIDATION_ERROR",
    "errors": [
        {
            "field": "email",
            "message": "Invalid email format",
            "code": "INVALID_EMAIL"
        }
    ],
    "timestamp": "2024-01-01T12:00:00Z"
}

# Paginated Response
{
    "success": True,
    "data": [...],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total": 50,
        "pages": 3,
        "has_next": True
    }
}
```

### Request Validation
```python
# Pydantic schemas
class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: Optional[str] = "user"
    
    @validator('password')
    def validate_password(cls, v):
        # Check uppercase, lowercase, digit
        return v

class UserListRequest(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    sort: Optional[str] = "created_at"
    order: Optional[str] = Field("desc", regex="^(asc|desc)$")
    search: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
```

## API Versioning

### URL Path Versioning
```python
# Version routing
v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")
latest_router = APIRouter(prefix="/api/latest")  # Alias to stable
```

### Header Versioning
```python
# Middleware for Accept-Version header
class APIVersionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        version = request.headers.get("API-Version", "v1")
        if version not in supported_versions:
            return error_response(400, "Unsupported version")
        request.state.api_version = version
        return await call_next(request)
```

## Rate Limiting

### Implementation Pattern
```python
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, requests_per_minute=60, requests_per_hour=1000):
        self.rpm = requests_per_minute
        self.rph = requests_per_hour
        self.request_times = defaultdict(deque)
    
    async def dispatch(self, request: Request, call_next):
        client_id = self.get_client_id(request)
        
        if not self.check_rate_limit(client_id):
            return JSONResponse(
                status_code=429,
                content={"success": False, "message": "Rate limit exceeded"},
                headers={"Retry-After": "60"}
            )
        
        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(self.get_remaining(client_id))
        return response
```

## Error Handling

### Exception Classes
```python
class APIException(HTTPException):
    def __init__(self, status_code: int, message: str, error_code: str = None):
        super().__init__(status_code=status_code, detail=message)
        self.error_code = error_code

class ValidationException(APIException):
    def __init__(self, message="Validation failed", errors=None):
        super().__init__(422, message, "VALIDATION_ERROR")
        self.errors = errors or []

class ResourceNotFoundException(APIException):
    def __init__(self, resource_type: str, resource_id: Any):
        super().__init__(404, f"{resource_type} not found", "RESOURCE_NOT_FOUND")
```

### Global Handler
```python
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

## OpenAPI Documentation

### Route Documentation
```python
@router.get(
    "/",
    response_model=UserListResponse,
    summary="List users",
    description="Retrieve paginated list of users",
    responses={
        200: {"description": "Success"},
        401: {"description": "Unauthorized"},
        429: {"description": "Rate limited"}
    }
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search query")
):
    """List users with pagination and search."""
    pass
```

### Schema Configuration
```python
def custom_openapi(app: FastAPI):
    openapi_schema = get_openapi(
        title=f"{settings.PROJECT_NAME} API",
        version="1.0.0",
        description="API Documentation",
        routes=app.routes
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    return openapi_schema
```

## GraphQL Schema

### Types & Inputs
```python
@strawberry.type
class User:
    id: int
    name: str
    email: str
    role: str
    created_at: datetime

@strawberry.input
class CreateUserInput:
    name: str
    email: str
    password: str
    role: Optional[str] = "user"

@strawberry.type
class UserConnection:
    users: List[User]
    total_count: int
    page_info: PageInfo
```

### Resolvers
```python
@strawberry.type
class Query:
    @strawberry.field
    def users(self, pagination: Optional[PaginationInput] = None) -> UserConnection:
        # Implementation
        pass
    
    @strawberry.field
    def user(self, id: int) -> Optional[User]:
        # Implementation
        pass

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, input: CreateUserInput) -> User:
        # Implementation
        pass
```

## Security

### Middleware
```python
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000"
        })
        return response
```

### Input Validation
```python
def sanitize_string(value: str, max_length: int = 1000) -> str:
    # Remove null bytes, limit length, escape HTML
    value = value.replace('\x00', '')[:max_length]
    return escape(value).strip()

def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    errors = []
    if len(password) < 8:
        errors.append("Password too short")
    if not re.search(r'[A-Z]', password):
        errors.append("Missing uppercase letter")
    # Additional checks...
    return len(errors) == 0, errors
```

## Testing

### Test Structure
```python
class TestUserAPI:
    def test_create_user_success(self, admin_headers):
        response = client.post("/api/v1/users/", json=user_data, headers=admin_headers)
        assert response.status_code == 201
        assert response.json()["success"] is True
    
    def test_validation_error(self, admin_headers):
        response = client.post("/api/v1/users/", json=invalid_data, headers=admin_headers)
        assert response.status_code == 422
        assert response.json()["error_code"] == "VALIDATION_ERROR"
    
    def test_unauthorized_access(self):
        response = client.get("/api/v1/users/")
        assert response.status_code == 401
```

## Performance

### Caching
```python
class CachingMiddleware(BaseHTTPMiddleware):
    def __init__(self, cache_service, cacheable_paths=["/api/v1/users"]):
        self.cache_service = cache_service
        self.cacheable_paths = cacheable_paths
    
    async def dispatch(self, request: Request, call_next):
        if not self.is_cacheable(request):
            return await call_next(request)
        
        cache_key = self.generate_cache_key(request)
        cached = await self.cache_service.get(cache_key)
        if cached:
            return cached
        
        response = await call_next(request)
        await self.cache_service.set(cache_key, response, ttl=300)
        return response
```

### Monitoring
```python
class MonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        logger.info(f"Request {request_id}: {request.method} {request.url} - {response.status_code} ({duration:.3f}s)")
        return response
```

## Best Practices

### Design Principles
- Use RESTful design with proper HTTP methods
- Implement consistent error handling
- Support pagination for list endpoints
- Use proper HTTP status codes
- Version APIs for breaking changes

### Security
- Require authentication for protected endpoints
- Validate and sanitize all inputs
- Implement rate limiting
- Use HTTPS in production
- Add security headers

### Performance
- Cache frequently accessed data
- Use async/await for I/O operations
- Implement connection pooling
- Monitor API performance
- Use compression for responses

### Documentation
- Generate OpenAPI documentation
- Include request/response examples
- Document error codes
- Maintain API changelog
- Provide clear descriptions
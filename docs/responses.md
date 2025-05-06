# Custom API Response

🚀 **Clean, Consistent API Responses with Standardized Structure**

Our FastAPI application implements a custom response system that wraps all API responses in a standardized format. This approach provides several benefits:

- **Consistency**: All endpoints return responses with the same structure
- **Error handling**: Simplified error handling with consistent status reporting
- **Internationalization**: Built-in support for translated messages
- **Metadata**: Every response includes status information alongside the actual content

## Response Structure

Each API response follows this JSON structure:

```json
{
  "header": {
    "status": "success|failure",
    "message": "Human-readable message about the operation",
    "code": 200
  },
  "content": {
    // The actual data returned by the endpoint (if any)
  }
}
```

## Implementation Details

### Core Components

#### 1. ResponseStatus Enum

```python
class ResponseStatus(StrEnum):
    SUCCESS = auto()
    FAILURE = auto()
```

This enum defines the possible status values for API responses, automatically converted to lowercase strings in the JSON output (`"success"` or `"failure"`).

#### 2. APIResponseHeader Model

```python
class APIResponseHeader(BaseModel):
    """Header type for API responses."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS)
    message: str = Field(default=_("Operation completed successfully."))
    code: int = Field(default=HTTPStatus.OK)
```

The header model encapsulates:

- `status`: The operation result (`success` or `failure`)
- `message`: A human-readable message (with i18n support via the `_()` translation function)
- `code`: The HTTP status code for the response

#### 3. APIResponseType Generic Model

```python
class APIResponseType(BaseModel, Generic[T]):
    """Type definition for API responses."""
    header: APIResponseHeader
    content: Optional[T] = None
```

This generic model defines the structure of all API responses with:

- `header`: Metadata about the response (status, message, code)
- `content`: The actual data payload, which can be of any type `T` or `None`

#### 4. APIResponse Implementation

```python
class APIResponse(APIResponseType[T], Generic[T]):
    """
    Generic API response wrapper with automatic exception handling.
    """
    def __init__(self, data: T):
        super().__init__(
            header=APIResponseHeader(
                status=ResponseStatus.SUCCESS,
                message=_("Operation completed successfully."),
                code=HTTPStatus.OK,
            ),
            content=data,
        )
```

This is the concrete implementation that wraps any data in the standardized response format, with default values for successful operations.

## Using the Custom Response System

### Example Endpoint

```python
@user_router.get("/{user_id}", dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
@Cache.cached(prefix=prefix, ttl=60)
async def get_user(
    user_id: UUID4,
    user_controller: UserController = Depends(Factory().get_user_controller),
    assert_access: Callable = Depends(Permissions(UserPermission.READ)),
) -> APIResponseType[UserResponse]:
    """
    Get details of a specific user by ID.
    - **path parameter**: `user_id` (UUID)
    - **permissions required**: Authenticated + `user:read`
    - **response**: User object
    """
    user = await user_controller.get_user(uuid=user_id)
    assert_access(resource=user)
    return APIResponse(user)
```

In this example:

1. The endpoint declares its return type as `APIResponseType[UserResponse]`
2. The business logic retrieves the user data
3. The raw user object is wrapped in `APIResponse(user)` before being returned
4. FastAPI automatically serializes this to the standardized JSON format

### Example Response

```json
{
  "header": {
    "status": "success",
    "message": "Operation completed successfully.",
    "code": 200
  },
  "content": {
    "uuid": "a3b8f042-1e16-4f0a-a8f0-421e16df0a2f",
    "email": "johndoe@example.com",
    "first_name": "john",
    "last_name": "doe",
    "role": "USER",
    "activated": true
  }
}
```

## Benefits of This Approach

### 🔄 Consistency

All API endpoints return data in the same format, making integration simpler for frontend developers and API consumers.

### 🌐 Internationalization

Response messages are run through the translation system, allowing for localized error and success messages.

### 🛡️ Type Safety

Thanks to Python's typing system and Pydantic, we get full type checking for our response data.

### 📦 Separation of Concerns

The response header (metadata) is clearly separated from the actual content, making it easy to process status information independently from the data.

### 🔧 Extensibility

The system can be easily extended to include additional metadata in the header or to handle different response scenarios.

## Best Practices

1. **Always use the APIResponse wrapper**: Never return raw data directly from endpoint functions
2. **Define specific return types**: Always specify the content type like `APIResponseType[UserResponse]`
3. **Custom error responses**: For error cases, you can create a similar error response class
4. **Keep the pattern consistent**: All endpoints should follow this pattern to maintain API consistency

## Advanced Usage

For handling error scenarios, you might create a companion error response class:

```python
class APIErrorResponse(APIResponseType[None]):
    def __init__(self, message: str, code: int = HTTPStatus.BAD_REQUEST):
        super().__init__(
            header=APIResponseHeader(
                status=ResponseStatus.FAILURE,
                message=message,
                code=code,
            ),
            content=None,
        )
```

This could be used in exception handlers or directly in endpoints for known error conditions.

---

✨ By implementing this standardized response system, our API becomes more maintainable, consistent, and developer-friendly while enabling robust client-side error handling.
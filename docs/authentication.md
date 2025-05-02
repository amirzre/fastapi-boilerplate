### 📝 Overview

This document provides a detailed explanation of the authentication system implemented in the project. The system utilizes JWT-based authentication with added security through CSRF tokens, session middleware, and cookies to handle access and refresh tokens. It includes mechanisms for login, token refresh, and logout functionalities.

### 🧩 Components

#### **🔑 JWTHandler**

The `JWTHandler` class is responsible for encoding and decoding JSON Web Tokens (JWTs). It supports both access and refresh tokens.

##### **Methods**
- **`encode(payload: dict) -> str`**: Encodes a payload into an access token with an expiration time.
- **`encode_refresh_token(payload: dict) -> str`**: Encodes a payload into a refresh token with a longer expiration time.
- **`decode(token: str) -> dict`**: Decodes a JWT, verifying its validity and expiration.
- **`decode_expired(token: str) -> dict`**: Decodes a JWT without verifying expiration (used for expired tokens).
- **`token_expiration(token: str) -> datetime | None`**: Retrieves the expiration time of a JWT.

##### **Errors**
- **`JWTDecodeError`**: Raised if the token is invalid.
- **`JWTExpiredError`**: Raised if the token is expired.


#### **🛡️ Authentication Handler**

The `AuthenticationHandler` class handles user authentication by validating tokens and extracting user identifiers.

##### **Methods**
- **`_get_token(token_type: str) -> str`**: Retrieves a token from cookies based on its type (Access/Refresh).
- **`_decode_token(token: str, key: str) -> str`**: Decodes the token and validates the presence of a specific key.
- **`_validate_token(token: str, credentials, token_type: str) -> None`**: Validates the provided credentials against the token.
- **`authenticate_user(token_type: str, key: str, credentials=None) -> str`**: Combines the above methods to authenticate a user and return their identifier.


#### **🍪 Session Middleware**

The `SessionMiddleware` generates a unique session ID for each user request and stores it in a cookie. It ensures session continuity.


#### **⚙️ AuthController**

The `AuthController` manages the business logic for authentication-related operations, such as login, token refresh, and logout.

##### **Methods**
- **`login(login_user_request, cache) -> Token`**: Authenticates a user, generates tokens, and stores the refresh token in a Redis cache.
- **`refresh_token(old_refresh_token, session_id, cache) -> Token`**: Generates new access and refresh tokens after validating the old refresh token.
- **`logout(refresh_token, cache) -> None`**: Deletes the refresh token from the Redis cache.


#### **🌐 Endpoints**

The authentication system exposes several API endpoints for client interaction.

##### **Routes**
- **`POST /login`**: Logs in the user, generates tokens, and sets cookies.
- **`POST /refresh`**: Issues new tokens using the refresh token.
- **`GET /me`**: Retrieves the current user's information.
- **`DELETE /logout`**: Logs out the user by clearing tokens and cookies.


### 🔄 Token Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Backend
    participant Redis

    User->>Backend: POST /login (email, password)
    Backend->>Redis: Store refresh token
    Backend-->>User: Set cookies (Access-Token, Refresh-Token, X-CSRF-TOKEN)

    User->>Backend: POST /refresh (with Refresh-Token)
    Backend->>Redis: Validate old Refresh-Token
    Backend->>Redis: Store new Refresh-Token
    Backend-->>User: Set new cookies (Access-Token, Refresh-Token, X-CSRF-TOKEN)

    User->>Backend: DELETE /logout (with Refresh-Token)
    Backend->>Redis: Delete Refresh-Token
    Backend-->>User: Clear cookies
```


### 🪪 Identity Verification

To verify a user's identity, the `authenticate_user` method in the `AuthenticationHandler` class is used:

-    Extract the Access/Refresh token from cookies.
-    Decode the token and validate its contents.
-    Return the user's unique identifier (UUID).

This process ensures secure and reliable authentication while maintaining user data integrity.


### 🔒 Security Measures

1. **HTTPOnly Cookies**: Access and refresh tokens are stored in cookies with `HttpOnly` and `Secure` flags.

2. **CSRF Protection**: CSRF tokens are included in the response headers to protect against cross-site request forgery attacks.

3. **Redis Integration**: Refresh tokens are stored in Redis with expiration times, ensuring they can be invalidated on logout or misuse.

4. **Session IDs**: Unique session IDs are generated and stored in cookies to enhance user session security.

5. **Token Expiration**: Both access and refresh tokens have configurable expiration times.


### ⚙️ Configuration

Update the following settings in the configuration file to customize token expiration, algorithm, and other parameters:

```env title="env file"
SECRET_KEY = "your_secret_key"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 60
SESSION_EXPIRE_MINUTES = 15
```
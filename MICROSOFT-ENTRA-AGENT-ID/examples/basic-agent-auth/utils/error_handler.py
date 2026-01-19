"""
Authentication Error Handler for Microsoft Entra Agent ID
Date: January 19, 2026

Provides centralized error handling for authentication scenarios.
"""

import logging
from enum import Enum
from typing import Optional, Callable
from azure.core.exceptions import (
    ClientAuthenticationError,
    ServiceRequestError,
    HttpResponseError
)

logger = logging.getLogger(__name__)


class AuthErrorType(Enum):
    """Types of authentication errors."""
    INVALID_CREDENTIALS = "invalid_credentials"
    UNAUTHORIZED_CLIENT = "unauthorized_client"
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"
    EXPIRED_TOKEN = "expired_token"
    NETWORK_ERROR = "network_error"
    SERVICE_ERROR = "service_error"
    UNKNOWN = "unknown"


class AuthenticationException(Exception):
    """Custom exception for authentication errors."""
    
    def __init__(
        self,
        message: str,
        error_type: AuthErrorType,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.error_type = error_type
        self.original_error = original_error


def handle_auth_error(
    error: Exception,
    context: str = "",
    retry_callback: Optional[Callable] = None
) -> AuthenticationException:
    """
    Handle authentication errors and provide actionable information.
    
    Args:
        error: The original exception
        context: Additional context about where the error occurred
        retry_callback: Optional function to call for retryable errors
        
    Returns:
        AuthenticationException with error details
    """
    error_msg = str(error)
    error_type = AuthErrorType.UNKNOWN
    
    # Analyze the error
    if isinstance(error, ClientAuthenticationError):
        if "AADSTS7000215" in error_msg or "invalid_client" in error_msg.lower():
            error_type = AuthErrorType.INVALID_CREDENTIALS
            message = (
                "Agent credentials are invalid or expired. "
                "Please verify:\n"
                "  1. Client ID is correct\n"
                "  2. Client secret is valid and not expired\n"
                "  3. Service principal exists in the tenant"
            )
            
        elif "AADSTS700016" in error_msg or "application not found" in error_msg.lower():
            error_type = AuthErrorType.INVALID_CREDENTIALS
            message = (
                "Agent application not found. "
                "Please verify:\n"
                "  1. App registration exists\n"
                "  2. Service principal is created\n"
                "  3. Client ID is correct"
            )
            
        elif "unauthorized_client" in error_msg.lower():
            error_type = AuthErrorType.UNAUTHORIZED_CLIENT
            message = (
                "Agent is not authorized for the requested scope. "
                "Please verify:\n"
                "  1. API permissions are granted\n"
                "  2. Admin consent is provided (if required)\n"
                "  3. Scope/resource is correct"
            )
            
        elif "AADSTS65001" in error_msg or "consent" in error_msg.lower():
            error_type = AuthErrorType.UNAUTHORIZED_CLIENT
            message = (
                "Admin consent required. "
                "Please grant admin consent for the requested permissions."
            )
            
        else:
            error_type = AuthErrorType.INVALID_CREDENTIALS
            message = f"Authentication failed: {error_msg}"
    
    elif isinstance(error, HttpResponseError):
        status_code = getattr(error, 'status_code', None)
        
        if status_code == 401:
            error_type = AuthErrorType.EXPIRED_TOKEN
            message = (
                "Authentication token is invalid or expired. "
                "The agent needs to acquire a new token."
            )
            
        elif status_code == 403:
            error_type = AuthErrorType.INSUFFICIENT_PERMISSIONS
            message = (
                "Agent does not have sufficient permissions. "
                "Please verify:\n"
                "  1. RBAC role assignments\n"
                "  2. Required permissions for the operation\n"
                "  3. Resource access policies"
            )
            
        else:
            error_type = AuthErrorType.SERVICE_ERROR
            message = f"Service error (HTTP {status_code}): {error_msg}"
    
    elif isinstance(error, ServiceRequestError):
        error_type = AuthErrorType.NETWORK_ERROR
        message = (
            f"Network error during authentication: {error_msg}\n"
            "Please check network connectivity and firewall settings."
        )
        
        # Network errors are often retryable
        if retry_callback:
            logger.info("Network error is retryable, invoking retry callback")
            try:
                retry_callback()
            except Exception as retry_error:
                logger.error(f"Retry failed: {retry_error}")
    
    else:
        error_type = AuthErrorType.UNKNOWN
        message = f"Unexpected error: {error_msg}"
    
    # Log the error
    log_message = f"[{error_type.value}] {message}"
    if context:
        log_message = f"{context}: {log_message}"
    
    logger.error(log_message)
    
    # Return wrapped exception
    return AuthenticationException(message, error_type, error)


def get_error_guidance(error_type: AuthErrorType) -> str:
    """
    Get detailed guidance for resolving an error.
    
    Args:
        error_type: The type of authentication error
        
    Returns:
        Guidance string with resolution steps
    """
    guidance = {
        AuthErrorType.INVALID_CREDENTIALS: """
To resolve invalid credentials:

1. Verify environment variables:
   - TENANT_ID
   - AGENT_CLIENT_ID
   - AGENT_CLIENT_SECRET

2. Check app registration:
   az ad app show --id <AGENT_CLIENT_ID>

3. Verify service principal:
   az ad sp show --id <AGENT_CLIENT_ID>

4. Generate new client secret if expired:
   az ad app credential reset --id <AGENT_CLIENT_ID>
""",
        
        AuthErrorType.UNAUTHORIZED_CLIENT: """
To resolve authorization issues:

1. Grant required API permissions:
   az ad app permission add --id <AGENT_CLIENT_ID> \\
     --api 00000003-0000-0000-c000-000000000000 \\
     --api-permissions <permission-id>=Scope

2. Grant admin consent:
   az ad app permission admin-consent --id <AGENT_CLIENT_ID>

3. Verify permissions:
   az ad app permission list --id <AGENT_CLIENT_ID>
""",
        
        AuthErrorType.INSUFFICIENT_PERMISSIONS: """
To resolve permission issues:

1. Check RBAC assignments:
   az role assignment list --assignee <AGENT_CLIENT_ID>

2. Grant required role:
   az role assignment create \\
     --assignee <AGENT_CLIENT_ID> \\
     --role "Reader" \\
     --scope "/subscriptions/<subscription-id>"

3. Verify resource policies and conditions
""",
        
        AuthErrorType.EXPIRED_TOKEN: """
To resolve expired token:

1. The agent should acquire a new token automatically
2. Ensure token refresh logic is implemented
3. Check token cache configuration
4. Verify credential is still valid
""",
        
        AuthErrorType.NETWORK_ERROR: """
To resolve network issues:

1. Check network connectivity
2. Verify firewall rules allow HTTPS to:
   - login.microsoftonline.com
   - management.azure.com
3. Check proxy configuration
4. Verify DNS resolution
""",
    }
    
    return guidance.get(error_type, "No specific guidance available.")


# Context manager for error handling
class AuthErrorContext:
    """Context manager for authentication operations with error handling."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
    
    def __enter__(self):
        logger.info(f"Starting authentication operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Handle the error
            auth_error = handle_auth_error(exc_val, self.operation_name)
            logger.error(f"Operation failed: {self.operation_name}")
            
            # Get guidance
            guidance = get_error_guidance(auth_error.error_type)
            logger.info(f"Error guidance:\n{guidance}")
            
            # Re-raise as AuthenticationException
            raise auth_error from exc_val
        else:
            logger.info(f"Operation completed successfully: {self.operation_name}")
        
        return False  # Don't suppress exceptions

"""
Token Management Example
Date: January 19, 2026

Demonstrates:
- Token lifecycle management
- Token validation and inspection
- Token caching strategies
- Refresh token handling
- Secure token storage
"""

import os
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.core.credentials import AccessToken

from utils.token_validator import TokenValidator
from utils.error_handler import AuthErrorContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TokenCache:
    """
    Simple file-based token cache.
    In production, use Azure Key Vault or encrypted storage.
    """
    
    def __init__(self, cache_file: str = ".token_cache.json"):
        """
        Initialize token cache.
        
        Args:
            cache_file: Path to cache file
        """
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()
    
    def _load_cache(self) -> dict:
        """Load cache from file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            # In production, encrypt this file!
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(self.cache_file, 0o600)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def get_token(self, key: str) -> Optional[dict]:
        """
        Get token from cache.
        
        Args:
            key: Cache key (e.g., "scope:client_id")
            
        Returns:
            Token dict if found and valid, None otherwise
        """
        token_data = self.cache.get(key)
        
        if not token_data:
            logger.debug(f"Cache miss for: {key}")
            return None
        
        # Check expiration
        expires_on = token_data.get('expires_on')
        if expires_on:
            exp_time = datetime.fromtimestamp(expires_on, tz=timezone.utc)
            # Refresh if within 5 minutes of expiry
            if datetime.now(timezone.utc) >= (exp_time - timedelta(minutes=5)):
                logger.info(f"Cached token expired or expiring soon: {key}")
                return None
        
        logger.info(f"Cache hit for: {key}")
        return token_data
    
    def set_token(self, key: str, token: str, expires_on: int):
        """
        Store token in cache.
        
        Args:
            key: Cache key
            token: Token string
            expires_on: Expiration timestamp
        """
        self.cache[key] = {
            'token': token,
            'expires_on': expires_on,
            'cached_at': datetime.now(timezone.utc).isoformat()
        }
        self._save_cache()
        logger.info(f"Token cached: {key}")
    
    def clear(self):
        """Clear all cached tokens."""
        self.cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info("Token cache cleared")


class TokenManager:
    """
    Comprehensive token management with caching and validation.
    """
    
    def __init__(
        self,
        credential: ClientSecretCredential,
        tenant_id: str,
        cache_enabled: bool = True
    ):
        """
        Initialize token manager.
        
        Args:
            credential: Azure credential
            tenant_id: Azure AD tenant ID
            cache_enabled: Enable token caching
        """
        self.credential = credential
        self.tenant_id = tenant_id
        self.validator = TokenValidator(tenant_id)
        self.cache = TokenCache() if cache_enabled else None
    
    def get_token(self, scope: str, force_refresh: bool = False) -> AccessToken:
        """
        Get token with caching and automatic refresh.
        
        Args:
            scope: OAuth scope
            force_refresh: Force token refresh even if cached
            
        Returns:
            AccessToken object
        """
        cache_key = f"{scope}"
        
        # Try cache first
        if self.cache and not force_refresh:
            cached = self.cache.get_token(cache_key)
            if cached:
                logger.info("Using cached token")
                return AccessToken(
                    token=cached['token'],
                    expires_on=cached['expires_on']
                )
        
        # Acquire new token
        logger.info(f"Acquiring new token for scope: {scope}")
        with AuthErrorContext("Token Acquisition"):
            token_result = self.credential.get_token(scope)
        
        # Cache the token
        if self.cache:
            self.cache.set_token(
                cache_key,
                token_result.token,
                token_result.expires_on
            )
        
        return token_result
    
    def validate_token(self, token: str) -> dict:
        """
        Validate a token.
        
        Args:
            token: JWT token string
            
        Returns:
            Token claims if valid
        """
        return self.validator.validate_token(token)
    
    def inspect_token(self, token: str):
        """
        Inspect token and display information.
        
        Args:
            token: JWT token string
        """
        logger.info("\n=== Token Inspection ===")
        
        claims = self.validator.get_token_claims(token)
        
        # Basic info
        logger.info(f"Issuer: {claims.get('iss')}")
        logger.info(f"Audience: {claims.get('aud')}")
        logger.info(f"Subject: {claims.get('sub')}")
        
        # Identity info
        if 'appid' in claims:
            logger.info(f"Application ID: {claims.get('appid')}")
            logger.info(f"Identity Type: Agent/Service Principal")
        elif 'upn' in claims:
            logger.info(f"User Principal: {claims.get('upn')}")
            logger.info(f"Identity Type: User")
        
        # Timestamps
        iat = claims.get('iat')
        exp = claims.get('exp')
        if iat:
            logger.info(f"Issued At: {datetime.fromtimestamp(iat, tz=timezone.utc)}")
        if exp:
            exp_time = datetime.fromtimestamp(exp, tz=timezone.utc)
            logger.info(f"Expires At: {exp_time}")
            time_left = exp_time - datetime.now(timezone.utc)
            logger.info(f"Time Remaining: {time_left}")
        
        # Permissions
        if 'roles' in claims:
            logger.info(f"Roles: {claims.get('roles')}")
        if 'scp' in claims:
            logger.info(f"Scopes: {claims.get('scp')}")
        
        # Validate
        is_valid = not self.validator.is_token_expired(token)
        logger.info(f"Valid: {'✓' if is_valid else '✗'}")
        
        is_agent = self.validator.validate_agent_identity(token)
        logger.info(f"Agent Identity: {'✓' if is_agent else '✗'}")
    
    def demonstrate_lifecycle(self, scope: str):
        """
        Demonstrate complete token lifecycle.
        
        Args:
            scope: OAuth scope to use
        """
        logger.info("\n=== Token Lifecycle Demo ===")
        
        # 1. Initial acquisition
        logger.info("\n1. Acquiring initial token...")
        token1 = self.get_token(scope)
        logger.info(f"   ✓ Token acquired, expires at: {datetime.fromtimestamp(token1.expires_on)}")
        
        # 2. Inspect token
        logger.info("\n2. Inspecting token...")
        self.inspect_token(token1.token)
        
        # 3. Cache hit
        logger.info("\n3. Requesting same token (should hit cache)...")
        token2 = self.get_token(scope)
        if token1.token == token2.token:
            logger.info("   ✓ Token retrieved from cache")
        else:
            logger.info("   ✗ New token acquired (cache miss)")
        
        # 4. Force refresh
        logger.info("\n4. Forcing token refresh...")
        token3 = self.get_token(scope, force_refresh=True)
        if token1.token != token3.token:
            logger.info("   ✓ New token acquired")
        else:
            logger.info("   ⚠ Same token returned (may be from SDK cache)")
        
        # 5. Validate token
        logger.info("\n5. Validating token...")
        try:
            claims = self.validate_token(token3.token)
            logger.info(f"   ✓ Token is valid")
            logger.info(f"   Issued for: {claims.get('appid')}")
        except Exception as e:
            logger.error(f"   ✗ Token validation failed: {e}")


def demonstrate_security_best_practices():
    """Demonstrate token security best practices."""
    logger.info("\n=== Token Security Best Practices ===")
    
    logger.info("\n✓ DO:")
    logger.info("  1. Store tokens in memory only")
    logger.info("  2. Use secure caches (Azure Key Vault)")
    logger.info("  3. Encrypt token cache files")
    logger.info("  4. Set restrictive file permissions (0600)")
    logger.info("  5. Clear tokens on logout")
    logger.info("  6. Validate tokens before use")
    logger.info("  7. Handle expiration gracefully")
    logger.info("  8. Log token events (not token values!)")
    logger.info("  9. Use shortest-lived tokens possible")
    logger.info("  10. Implement token refresh logic")
    
    logger.info("\n✗ DON'T:")
    logger.info("  1. Log token values")
    logger.info("  2. Store tokens in plain text files")
    logger.info("  3. Store tokens in databases unencrypted")
    logger.info("  4. Send tokens in URL parameters")
    logger.info("  5. Store tokens in cookies (for APIs)")
    logger.info("  6. Share tokens between agents")
    logger.info("  7. Ignore token expiration")
    logger.info("  8. Commit token caches to git")
    
    logger.info("\n=== Token Storage Comparison ===")
    logger.info("\nIn-Memory (Best for short-lived processes):")
    logger.info("  ✓ Most secure")
    logger.info("  ✓ No persistence")
    logger.info("  ❌ Lost on restart")
    
    logger.info("\nEncrypted File Cache:")
    logger.info("  ✓ Survives restarts")
    logger.info("  ⚠ Must encrypt properly")
    logger.info("  ⚠ File permissions critical")
    
    logger.info("\nAzure Key Vault (Best for production):")
    logger.info("  ✓ Hardware-backed security")
    logger.info("  ✓ Audit logs")
    logger.info("  ✓ Access policies")
    logger.info("  ⚠ Requires network call")


def main():
    """Main execution function."""
    
    load_dotenv()
    
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("AGENT_CLIENT_ID")
    client_secret = os.getenv("AGENT_CLIENT_SECRET")
    
    if not all([tenant_id, client_id, client_secret]):
        logger.error("Missing required environment variables!")
        return 1
    
    try:
        logger.info("=== Token Management Demo ===\n")
        
        # Create credential
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Create token manager
        token_manager = TokenManager(credential, tenant_id, cache_enabled=True)
        
        # Demo 1: Token lifecycle
        logger.info("\n--- Demo 1: Token Lifecycle ---")
        token_manager.demonstrate_lifecycle("https://management.azure.com/.default")
        
        # Demo 2: Security best practices
        logger.info("\n--- Demo 2: Security Best Practices ---")
        demonstrate_security_best_practices()
        
        # Cleanup
        logger.info("\n--- Cleanup ---")
        if token_manager.cache:
            token_manager.cache.clear()
            logger.info("✓ Token cache cleared")
        
        logger.info("\n=== All demos completed successfully ===")
        return 0
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

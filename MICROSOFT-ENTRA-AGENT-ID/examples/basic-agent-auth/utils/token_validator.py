"""
Token Validator for Microsoft Entra Agent ID
Date: January 19, 2026

Validates JWT tokens issued by Microsoft Entra ID for agent identities.
"""

import jwt
import requests
import logging
from typing import Dict, Optional
from datetime import datetime, timezone
from functools import lru_cache

logger = logging.getLogger(__name__)


class TokenValidator:
    """Validates Microsoft Entra ID tokens for agents."""
    
    def __init__(self, tenant_id: str, expected_audience: Optional[str] = None):
        """
        Initialize token validator.
        
        Args:
            tenant_id: Azure AD tenant ID
            expected_audience: Expected token audience (e.g., your API's client ID)
        """
        self.tenant_id = tenant_id
        self.expected_audience = expected_audience
        self.issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
        self.jwks_uri = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
    
    @lru_cache(maxsize=10)
    def _get_signing_keys(self) -> Dict:
        """
        Fetch public signing keys from Microsoft Entra ID.
        Cached to avoid repeated calls.
        """
        try:
            response = requests.get(self.jwks_uri, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch signing keys: {e}")
            raise ValueError("Unable to retrieve token signing keys")
    
    def _get_public_key(self, token: str) -> str:
        """Extract the public key for token verification."""
        # Get unverified header to find key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')
        
        if not kid:
            raise ValueError("Token missing 'kid' in header")
        
        # Find matching key in JWKS
        jwks = self._get_signing_keys()
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                # Convert JWK to PEM format
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
        
        raise ValueError(f"Unable to find signing key with kid: {kid}")
    
    def validate_token(self, token: str) -> Dict:
        """
        Validate a JWT token from Microsoft Entra ID.
        
        Args:
            token: The JWT token string
            
        Returns:
            Decoded token payload if valid
            
        Raises:
            jwt.InvalidTokenError: If token is invalid
            ValueError: If token structure is invalid
        """
        try:
            # Get public key for verification
            public_key = self._get_public_key(token)
            
            # Decode and verify token
            decoded = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                issuer=self.issuer,
                audience=self.expected_audience,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_aud": True if self.expected_audience else False,
                    "verify_iss": True
                }
            )
            
            logger.info(f"Token validated successfully for subject: {decoded.get('sub')}")
            return decoded
            
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            raise
        except jwt.InvalidAudienceError:
            logger.error(f"Invalid audience. Expected: {self.expected_audience}")
            raise
        except jwt.InvalidIssuerError:
            logger.error(f"Invalid issuer. Expected: {self.issuer}")
            raise
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            raise
    
    def is_token_expired(self, token: str) -> bool:
        """
        Check if a token is expired without full validation.
        
        Args:
            token: The JWT token string
            
        Returns:
            True if expired, False otherwise
        """
        try:
            # Decode without verification to check expiration
            decoded = jwt.decode(token, options={"verify_signature": False})
            exp_timestamp = decoded.get('exp')
            
            if not exp_timestamp:
                return True
            
            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            return datetime.now(timezone.utc) >= exp_datetime
            
        except Exception as e:
            logger.warning(f"Error checking token expiration: {e}")
            return True
    
    def get_token_claims(self, token: str) -> Dict:
        """
        Extract claims from token without validation.
        Useful for debugging or when signature verification isn't needed.
        
        Args:
            token: The JWT token string
            
        Returns:
            Token claims dictionary
        """
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            return decoded
        except Exception as e:
            logger.error(f"Failed to decode token: {e}")
            raise ValueError("Invalid token format")
    
    def validate_agent_identity(self, token: str) -> bool:
        """
        Validate that the token represents an agent identity (not a user).
        
        Args:
            token: The JWT token string
            
        Returns:
            True if token is for an agent identity
        """
        claims = self.get_token_claims(token)
        
        # Check for service principal indicators
        # Agent identities typically have:
        # - oid (object ID) but no 'unique_name' or 'upn'
        # - appid (application ID)
        # - idtyp = 'app' (for v2.0 tokens)
        
        has_oid = 'oid' in claims
        has_appid = 'appid' in claims or 'azp' in claims
        no_user_claims = 'unique_name' not in claims and 'upn' not in claims
        is_app_token = claims.get('idtyp') == 'app' or claims.get('ver') == '1.0'
        
        is_agent = has_oid and has_appid and no_user_claims and is_app_token
        
        if is_agent:
            logger.info(f"Validated agent identity: {claims.get('appid')}")
        else:
            logger.warning("Token does not represent an agent identity")
        
        return is_agent


# Convenience function
def validate_agent_token(token: str, tenant_id: str, audience: Optional[str] = None) -> Dict:
    """
    Quick validation of an agent token.
    
    Args:
        token: JWT token string
        tenant_id: Azure AD tenant ID
        audience: Expected audience
        
    Returns:
        Decoded token claims
    """
    validator = TokenValidator(tenant_id, audience)
    return validator.validate_token(token)

# Copyright (c) Microsoft. All rights reserved.
"""
Schema Cache Module

Provides caching functionality for database schema information to improve
performance by avoiding repeated schema queries.

Features:
- In-memory caching with TTL (time-to-live)
- File-based persistent cache
- Automatic cache invalidation
- Thread-safe operations
"""
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SchemaCache:
    """Caches database schema information to improve performance."""
    
    def __init__(
        self,
        cache_dir: str = ".cache",
        ttl_seconds: int = 3600,  # 1 hour default
        enable_file_cache: bool = True,
    ):
        """Initialize schema cache.
        
        Args:
            cache_dir: Directory for persistent cache files
            ttl_seconds: Time-to-live for cache entries in seconds (default: 1 hour)
            enable_file_cache: Whether to use file-based persistent cache
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_seconds
        self.enable_file_cache = enable_file_cache
        
        # In-memory cache: {cache_key: (schema_data, timestamp)}
        self._memory_cache: dict[str, tuple[dict, float]] = {}
        
        # Create cache directory if using file cache
        if self.enable_file_cache:
            self.cache_dir.mkdir(exist_ok=True, parents=True)
            logger.info(f"Schema cache initialized: {self.cache_dir.absolute()}")
    
    def _get_cache_key(self, server: str, database: str) -> str:
        """Generate cache key from server and database name."""
        # Sanitize for filename
        safe_server = server.replace(".", "_").replace(":", "_")
        safe_db = database.replace(".", "_").replace(":", "_")
        return f"{safe_server}_{safe_db}"
    
    def _get_cache_file(self, cache_key: str) -> Path:
        """Get path to cache file for given key."""
        return self.cache_dir / f"schema_{cache_key}.json"
    
    def _is_expired(self, timestamp: float) -> bool:
        """Check if cache entry is expired based on TTL."""
        return (time.time() - timestamp) > self.ttl_seconds
    
    def get(self, server: str, database: str) -> Optional[dict]:
        """Get cached schema if available and not expired.
        
        Args:
            server: Database server name
            database: Database name
            
        Returns:
            Cached schema dict or None if not found/expired
        """
        cache_key = self._get_cache_key(server, database)
        
        # Check in-memory cache first
        if cache_key in self._memory_cache:
            schema_data, timestamp = self._memory_cache[cache_key]
            
            if not self._is_expired(timestamp):
                logger.info(f"✅ Schema cache HIT (memory): {server}/{database}")
                return schema_data
            else:
                logger.info(f"⚠️  Schema cache EXPIRED (memory): {server}/{database}")
                # Remove expired entry
                del self._memory_cache[cache_key]
        
        # Check file cache if enabled
        if self.enable_file_cache:
            cache_file = self._get_cache_file(cache_key)
            
            if cache_file.exists():
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cache_entry = json.load(f)
                    
                    timestamp = cache_entry.get("timestamp", 0)
                    schema_data = cache_entry.get("schema")
                    
                    if not self._is_expired(timestamp) and schema_data:
                        logger.info(f"✅ Schema cache HIT (file): {server}/{database}")
                        # Populate memory cache
                        self._memory_cache[cache_key] = (schema_data, timestamp)
                        return schema_data
                    else:
                        logger.info(f"⚠️  Schema cache EXPIRED (file): {server}/{database}")
                        cache_file.unlink()  # Remove expired file
                        
                except Exception as e:
                    logger.warning(f"Failed to read cache file: {e}")
        
        logger.info(f"❌ Schema cache MISS: {server}/{database}")
        return None
    
    def set(self, server: str, database: str, schema_data: dict) -> None:
        """Store schema in cache.
        
        Args:
            server: Database server name
            database: Database name
            schema_data: Schema information to cache
        """
        cache_key = self._get_cache_key(server, database)
        timestamp = time.time()
        
        # Store in memory cache
        self._memory_cache[cache_key] = (schema_data, timestamp)
        logger.info(f"💾 Schema cached (memory): {server}/{database}")
        
        # Store in file cache if enabled
        if self.enable_file_cache:
            cache_file = self._get_cache_file(cache_key)
            
            try:
                cache_entry = {
                    "server": server,
                    "database": database,
                    "timestamp": timestamp,
                    "schema": schema_data,
                }
                
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache_entry, f, indent=2)
                
                logger.info(f"💾 Schema cached (file): {cache_file}")
                
            except Exception as e:
                logger.warning(f"Failed to write cache file: {e}")
    
    def invalidate(self, server: str, database: str) -> None:
        """Manually invalidate cache for a specific database.
        
        Args:
            server: Database server name
            database: Database name
        """
        cache_key = self._get_cache_key(server, database)
        
        # Remove from memory cache
        if cache_key in self._memory_cache:
            del self._memory_cache[cache_key]
            logger.info(f"🗑️  Invalidated memory cache: {server}/{database}")
        
        # Remove file cache
        if self.enable_file_cache:
            cache_file = self._get_cache_file(cache_key)
            if cache_file.exists():
                cache_file.unlink()
                logger.info(f"🗑️  Invalidated file cache: {cache_file}")
    
    def clear_all(self) -> None:
        """Clear all cache entries (memory and file)."""
        # Clear memory cache
        self._memory_cache.clear()
        logger.info("🗑️  Cleared all memory cache")
        
        # Clear file cache
        if self.enable_file_cache:
            for cache_file in self.cache_dir.glob("schema_*.json"):
                try:
                    cache_file.unlink()
                    logger.info(f"🗑️  Deleted cache file: {cache_file}")
                except Exception as e:
                    logger.warning(f"Failed to delete cache file {cache_file}: {e}")
    
    def get_cache_info(self) -> dict:
        """Get information about current cache state.
        
        Returns:
            Dict with cache statistics
        """
        info = {
            "memory_entries": len(self._memory_cache),
            "ttl_seconds": self.ttl_seconds,
            "file_cache_enabled": self.enable_file_cache,
        }
        
        if self.enable_file_cache:
            cache_files = list(self.cache_dir.glob("schema_*.json"))
            info["file_entries"] = len(cache_files)
            info["cache_dir"] = str(self.cache_dir.absolute())
        
        return info


# Global cache instance
_global_cache: Optional[SchemaCache] = None


def get_global_cache() -> SchemaCache:
    """Get or create the global schema cache instance.
    
    Configuration from environment variables:
    - SCHEMA_CACHE_TTL: Cache TTL in seconds (default: 3600 = 1 hour)
    - SCHEMA_CACHE_ENABLED: Enable/disable caching (default: true)
    - SCHEMA_CACHE_DIR: Cache directory (default: .cache)
    
    Returns:
        Global SchemaCache instance
    """
    global _global_cache
    
    if _global_cache is None:
        ttl = int(os.environ.get("SCHEMA_CACHE_TTL", "3600"))
        enabled = os.environ.get("SCHEMA_CACHE_ENABLED", "true").lower() == "true"
        cache_dir = os.environ.get("SCHEMA_CACHE_DIR", ".cache")
        
        _global_cache = SchemaCache(
            cache_dir=cache_dir,
            ttl_seconds=ttl,
            enable_file_cache=enabled,
        )
    
    return _global_cache


def clear_global_cache() -> None:
    """Clear and reset the global cache instance."""
    global _global_cache
    
    if _global_cache is not None:
        _global_cache.clear_all()
        _global_cache = None

# Schema Cache Guide

## 🚀 Overview

The NL2SQL pipeline includes intelligent schema caching to dramatically improve performance by avoiding repeated database schema queries.

### Performance Impact

**Without Cache:**
- Schema retrieval: ~500-1000ms per query
- Every question requires a fresh schema fetch

**With Cache:**
- First query: ~500-1000ms (cache miss)
- Subsequent queries: ~1-5ms (cache hit)
- **Performance improvement: 100-500x faster**

## 🔧 How It Works

### Two-Tier Caching

1. **Memory Cache** (in-process)
   - Ultra-fast access (<1ms)
   - Active for the duration of the workflow process
   - Cleared when workflow restarts

2. **File Cache** (persistent)
   - Survives workflow restarts
   - Stored in `.cache/` directory as JSON files
   - Shared across multiple workflow instances

### Cache Flow

```
Question received
    ↓
Check memory cache → HIT? → Use cached schema ✅
    ↓ MISS
Check file cache → HIT? → Load to memory + Use ✅
    ↓ MISS
Fetch from database → Store in memory + file → Use ✅
```

## ⚙️ Configuration

### Environment Variables

Add to `.env`:

```bash
# Enable/disable schema caching (default: true)
SCHEMA_CACHE_ENABLED=true

# Cache time-to-live in seconds (default: 3600 = 1 hour)
SCHEMA_CACHE_TTL=3600

# Cache directory (default: .cache)
SCHEMA_CACHE_DIR=.cache
```

### Cache TTL Settings

Choose based on how often your schema changes:

```bash
# Development (schema changes frequently)
SCHEMA_CACHE_TTL=300        # 5 minutes

# Production (stable schema)
SCHEMA_CACHE_TTL=86400      # 24 hours

# Very stable schema
SCHEMA_CACHE_TTL=604800     # 1 week
```

## 📊 Cache Information

### View Cache Status

The cache logs useful information:

```
✅ Schema cache HIT (memory): aqsqlserver001.database.windows.net/TERADATA-FI
✅ Schema cache HIT (file): aqsqlserver001.database.windows.net/TERADATA-FI
❌ Schema cache MISS: aqsqlserver001.database.windows.net/TERADATA-FI
💾 Schema cached (memory): aqsqlserver001.database.windows.net/TERADATA-FI
💾 Schema cached (file): .cache/schema_aqsqlserver001_database_windows_net_TERADATA-FI.json
```

### Cache Files

Schema is stored in `.cache/` directory:

```bash
.cache/
└── schema_aqsqlserver001_database_windows_net_TERADATA-FI.json
```

Each file contains:
- Server and database name
- Timestamp of cache creation
- Complete schema information (tables, columns, types)

## 🔄 Cache Management

### Manual Cache Invalidation

If your schema changes, you may want to clear the cache:

**Option 1: Delete cache files**
```bash
rm -rf nl2sql-pipeline/.cache/*.json
```

**Option 2: Programmatic invalidation**
```python
from schema_cache import get_global_cache

cache = get_global_cache()

# Clear specific database
cache.invalidate("aqsqlserver001.database.windows.net", "TERADATA-FI")

# Or clear all caches
cache.clear_all()
```

**Option 3: Wait for TTL expiration**
- Cache automatically expires after the configured TTL
- Next query will fetch fresh schema

### Automatic Invalidation

Cache is automatically invalidated when:
- TTL expires (based on `SCHEMA_CACHE_TTL`)
- Workflow detects schema changes (future enhancement)
- Cache files are deleted manually

## 🐛 Troubleshooting

### Issue: Getting stale schema information

**Symptoms:**
- Query fails with "column not found"
- New tables not appearing
- Schema shows old structure

**Solution:**
```bash
# Clear cache to force refresh
rm -rf nl2sql-pipeline/.cache/*.json

# Or reduce TTL for development
SCHEMA_CACHE_TTL=60  # 1 minute
```

### Issue: Cache not working

**Check:**
1. Cache enabled: `SCHEMA_CACHE_ENABLED=true`
2. Cache directory exists: `ls -la .cache/`
3. Check logs for cache HIT/MISS messages

**Verify:**
```bash
# First query - should see "cache MISS"
python nl2sql_workflow.py
# Ask a question, check logs

# Second query - should see "cache HIT"
# Ask the same question, check logs
```

### Issue: Cache taking too much disk space

**Check cache size:**
```bash
du -sh .cache/
```

**Cleanup old caches:**
```bash
# Remove caches older than 7 days
find .cache/ -name "schema_*.json" -mtime +7 -delete
```

## 📈 Performance Metrics

### Typical Performance

| Scenario | Without Cache | With Cache | Improvement |
|----------|---------------|------------|-------------|
| First query | 1000ms | 1000ms | - |
| Second query | 1000ms | 2ms | 500x |
| 10 queries | 10000ms | 1018ms | 9.8x |
| 100 queries | 100000ms | 1098ms | 91x |

### When Cache Helps Most

✅ **High benefit:**
- Multiple questions in same session
- Exploratory data analysis
- Testing/development
- Demo scenarios

⚠️ **Limited benefit:**
- Single one-off questions
- Schemas that change frequently
- Different databases each query

## 🔒 Security Considerations

### What's Cached

- Table names
- Column names
- Data types
- Column constraints (nullable, primary key, etc.)

### What's NOT Cached

- Actual data
- Row counts
- Index information
- Permissions
- Connection credentials

### Cache Location

Cache files are stored locally:
- Default: `.cache/` in the workflow directory
- Contains schema metadata only
- Can be safely deleted without affecting database

### Best Practices

1. **Add `.cache/` to `.gitignore`**
   ```bash
   echo ".cache/" >> .gitignore
   ```

2. **Don't share cache files** - They may contain database/table names
3. **Regular cleanup** - Remove old cache files periodically
4. **Secure the cache directory** - Ensure proper file permissions

## 🚀 Advanced Usage

### Custom Cache Implementation

```python
from schema_cache import SchemaCache

# Create custom cache with specific settings
cache = SchemaCache(
    cache_dir="my_cache",
    ttl_seconds=7200,  # 2 hours
    enable_file_cache=True
)

# Get schema
schema = cache.get("server", "database")

# Store schema
cache.set("server", "database", schema_data)

# Get cache statistics
info = cache.get_cache_info()
print(f"Memory entries: {info['memory_entries']}")
print(f"File entries: {info['file_entries']}")
```

### Pre-warming the Cache

```python
# Useful for deployment or startup
from schema_cache import get_global_cache
from db_utils import create_connection_from_env

# Fetch and cache schema immediately
with create_connection_from_env() as db:
    schema_info = db.get_schema_info()
    cache = get_global_cache()
    cache.set(db.server, db.database, schema_info)

print("✅ Cache pre-warmed!")
```

## 📚 Related Documentation

- [Database Setup Guide](DATABASE_SETUP.md)
- [Export Guide](EXPORT_GUIDE.md)
- [Main README](README.md)

---

**Questions or Issues?** Check the logs for cache HIT/MISS patterns or review the implementation in `schema_cache.py`.

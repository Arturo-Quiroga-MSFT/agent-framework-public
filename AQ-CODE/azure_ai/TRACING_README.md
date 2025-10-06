# 📚 Azure AI Agent Tracing Documentation Index

Welcome! This directory contains comprehensive documentation for adding tracing to your Azure AI agents.

## 🎯 Quick Navigation

### I Want To...

**See traces immediately in my terminal**
→ [`TRACING_QUICKSTART.md`](./TRACING_QUICKSTART.md) - Option 1

**See traces in a web interface**
→ [`DEVUI_TRACING_QUICKSTART.md`](./DEVUI_TRACING_QUICKSTART.md) - 2 minute setup

**Understand all tracing options**
→ [`TRACING_SUMMARY.md`](./TRACING_SUMMARY.md) - Complete comparison

**Learn DevUI tracing in detail**
→ [`DEVUI_TRACING_GUIDE.md`](./DEVUI_TRACING_GUIDE.md) - Full guide

**Deep dive into all tracing features**
→ [`TRACING_GUIDE.md`](./TRACING_GUIDE.md) - Comprehensive documentation

**Just use DevUI (no tracing focus)**
→ [`DEVUI_GUIDE.md`](./DEVUI_GUIDE.md) - DevUI basics

---

## 📖 Document Descriptions

### Quick Start Guides

| Document | Time | Best For |
|----------|------|----------|
| [`DEVUI_TRACING_QUICKSTART.md`](./DEVUI_TRACING_QUICKSTART.md) | 2 min | **Visual traces in DevUI** |
| [`TRACING_QUICKSTART.md`](./TRACING_QUICKSTART.md) | 2 min | All tracing options overview |

### Comprehensive Guides

| Document | Pages | Coverage |
|----------|-------|----------|
| [`TRACING_GUIDE.md`](./TRACING_GUIDE.md) | ~40 | **Everything about tracing** |
| [`DEVUI_TRACING_GUIDE.md`](./DEVUI_TRACING_GUIDE.md) | ~30 | DevUI-specific tracing |
| [`DEVUI_GUIDE.md`](./DEVUI_GUIDE.md) | ~15 | General DevUI usage |

### Reference Documents

| Document | Purpose |
|----------|---------|
| [`TRACING_SUMMARY.md`](./TRACING_SUMMARY.md) | **All tracing options comparison** |
| This file | Navigation and overview |

---

## 🚀 Fastest Path to Tracing

### 30 Second Setup (Console)
```bash
echo "ENABLE_CONSOLE_TRACING=true" >> .env
python azure_ai_basic_devui.py --test
```
📖 See: [`TRACING_QUICKSTART.md`](./TRACING_QUICKSTART.md)

### 2 Minute Setup (DevUI - Visual)
```bash
echo "ENABLE_DEVUI_TRACING=true" >> .env
echo "ENABLE_OTEL=true" >> .env
echo "ENABLE_SENSITIVE_DATA=true" >> .env
python azure_ai_basic_devui.py
```
📖 See: [`DEVUI_TRACING_QUICKSTART.md`](./DEVUI_TRACING_QUICKSTART.md)

---

## 🎨 Tracing Options at a Glance

| Method | Visualization | Setup | Persistence | Production |
|--------|---------------|-------|-------------|------------|
| **DevUI** | ⭐⭐⭐⭐⭐ Web | 2 min | No | No |
| **Console** | ⭐⭐ Terminal | 30 sec | No | No |
| **Jaeger** | ⭐⭐⭐⭐⭐ Web | 3 min | Yes | Maybe |
| **Azure AI** | ⭐⭐⭐⭐ Portal | 2 min | Yes | Yes |

📖 Full comparison: [`TRACING_SUMMARY.md`](./TRACING_SUMMARY.md)

---

## 📚 Learning Path

### Beginner Path
1. Start: [`DEVUI_TRACING_QUICKSTART.md`](./DEVUI_TRACING_QUICKSTART.md) - Get tracing working fast
2. Explore: Try different queries in DevUI
3. Learn: [`DEVUI_TRACING_GUIDE.md`](./DEVUI_TRACING_GUIDE.md) - Understand what you're seeing

### Intermediate Path
1. Review: [`TRACING_SUMMARY.md`](./TRACING_SUMMARY.md) - See all options
2. Try: Set up Jaeger or Azure AI tracing
3. Deep dive: [`TRACING_GUIDE.md`](./TRACING_GUIDE.md) - Master all features

### Advanced Path
1. Implement: Multiple tracing backends simultaneously
2. Customize: Add custom spans to your code
3. Optimize: Use traces for performance tuning
4. Monitor: Set up production monitoring with Azure

---

## 🎯 Use Case Index

### Development Scenarios

| Scenario | Best Option | Document |
|----------|-------------|----------|
| Quick debugging | Console | [`TRACING_QUICKSTART.md`](./TRACING_QUICKSTART.md) |
| Visual debugging | DevUI | [`DEVUI_TRACING_QUICKSTART.md`](./DEVUI_TRACING_QUICKSTART.md) |
| Understanding flow | DevUI or Jaeger | [`DEVUI_TRACING_GUIDE.md`](./DEVUI_TRACING_GUIDE.md) |
| Performance analysis | DevUI or Jaeger | [`TRACING_GUIDE.md`](./TRACING_GUIDE.md) |
| Learning agents | DevUI | [`DEVUI_TRACING_GUIDE.md`](./DEVUI_TRACING_GUIDE.md) |

### Production Scenarios

| Scenario | Best Option | Document |
|----------|-------------|----------|
| Monitoring | Azure AI | [`TRACING_GUIDE.md`](./TRACING_GUIDE.md) |
| Alerting | Azure AI | [`TRACING_GUIDE.md`](./TRACING_GUIDE.md) |
| Cost tracking | Azure AI | [`TRACING_GUIDE.md`](./TRACING_GUIDE.md) |
| Compliance | Azure AI | [`TRACING_GUIDE.md`](./TRACING_GUIDE.md) |

---

## 🔍 Quick Reference

### Enable DevUI Tracing
```bash
# In .env file
ENABLE_DEVUI_TRACING=true
ENABLE_OTEL=true
ENABLE_SENSITIVE_DATA=true
```

### Enable Console Tracing
```bash
# In .env file
ENABLE_CONSOLE_TRACING=true
```

### Enable Azure AI Tracing
```bash
# In .env file
ENABLE_AZURE_AI_TRACING=true
```

### Enable Jaeger Tracing
```bash
# In .env file
OTLP_ENDPOINT=http://localhost:4317

# Start Jaeger first:
docker run -d -p 4317:4317 -p 16686:16686 jaegertracing/all-in-one
```

---

## 📊 What Gets Traced

All tracing options capture:
- ✅ Agent invocations with timing
- ✅ LLM requests with token usage
- ✅ Tool executions with parameters
- ✅ Success/failure status
- ✅ Parent-child relationships
- ✅ Performance metrics

With `ENABLE_SENSITIVE_DATA=true`:
- ✅ Full prompts and responses
- ✅ Complete tool parameters and results

---

## 🛠️ Files in This Directory

### Code Files
- `azure_ai_basic_devui.py` - Main script with tracing support
- `devui_agents/weather_agent/agent.py` - Directory-based agent

### Configuration
- `.env` - Environment variables for all tracing options

### Documentation
- `TRACING_README.md` - **This file** (navigation)
- `DEVUI_TRACING_QUICKSTART.md` - DevUI tracing in 2 minutes
- `TRACING_QUICKSTART.md` - All tracing options quick start
- `DEVUI_TRACING_GUIDE.md` - Complete DevUI tracing guide
- `TRACING_GUIDE.md` - Complete tracing documentation
- `TRACING_SUMMARY.md` - Comparison of all options
- `DEVUI_GUIDE.md` - General DevUI usage

---

## 🎓 Additional Resources

### External Links
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Azure Monitor OpenTelemetry](https://learn.microsoft.com/azure/azure-monitor/app/opentelemetry-overview)
- [Jaeger Tracing](https://www.jaegertracing.io/)
- [Agent Framework Repository](https://github.com/microsoft/agent-framework)

### Sample Code
- [Agent Framework Observability Samples](../../../observability/)
- [Azure AI Examples](../../../agents/azure_ai/)

---

## 🚦 Getting Started Steps

1. **Choose your tracing method** from the comparison table above
2. **Open the relevant quick start guide**:
   - DevUI: [`DEVUI_TRACING_QUICKSTART.md`](./DEVUI_TRACING_QUICKSTART.md)
   - Other: [`TRACING_QUICKSTART.md`](./TRACING_QUICKSTART.md)
3. **Follow the setup steps** (takes 2-3 minutes)
4. **Run your agent** and see traces!
5. **Read the comprehensive guide** to understand more:
   - [`DEVUI_TRACING_GUIDE.md`](./DEVUI_TRACING_GUIDE.md)
   - [`TRACING_GUIDE.md`](./TRACING_GUIDE.md)

---

## 💡 Pro Tips

1. **Start with DevUI tracing** - Best learning experience
2. **Enable sensitive data** in development for full details
3. **Try multiple backends** to see what works best
4. **Use console tracing** for quick checks
5. **Set up Azure AI tracing** for production deployments

---

## 🎉 You're All Set!

You now have access to complete tracing documentation. **Pick your path** and start exploring! 🚀

**Recommended first stop:** [`DEVUI_TRACING_QUICKSTART.md`](./DEVUI_TRACING_QUICKSTART.md) for the best visual experience!

# Changelog - Agent Framework Streamlit Demo

All notable changes to the Streamlit demo application are documented in this file.

## [1.2.0] - 2025-10-26

### 🎉 Major New Features

#### Conversation Memory (Thread Persistence)
- **Added conversation memory to 4 scenarios**: Thread Management, Azure AI Search, Bing Grounding, and File Search
- **Session-based thread persistence**: Conversations maintain context across multiple messages
- **User-controlled memory**: "Clear Conversation Memory" buttons allow users to reset context
- **Seamless follow-up questions**: "Tell me more about that" and similar queries reference previous responses
- **Technical implementation**: Thread IDs stored in `st.session_state`, reused via `agent.get_new_thread(service_thread_id=...)`

**Scenarios with Memory:**
- ✅ Thread Management (built-in framework feature)
- ✅ Azure AI Search (hotel searches with context)
- ✅ Bing Grounding (web searches with follow-ups)
- ✅ File Search (document Q&A with context)

**Remaining scenarios (planned for future releases):**
- ⏳ Basic Chat
- ⏳ Weather Agent
- ⏳ Code Interpreter
- ⏳ Firecrawl MCP
- ⏳ Microsoft Learn MCP

#### Plot Download Button
- **Instant plot downloads**: One-click PNG download for Code Interpreter visualizations
- **No external storage needed**: Direct browser downloads via `st.download_button()`
- **Works in all environments**: Local development and Azure Container Apps
- **Automatic detection**: Finds latest generated plot in `/app/generated_plots/`
- **User-friendly**: Download button appears immediately after plot generation

#### Automated Azure Deployment
- **One-command deployment**: New `deploy-to-azure.sh` script automates entire deployment
- **Timestamp-based versioning**: Images tagged with `YYYYMMDD-HHMMSS` format (e.g., `20251026-211128`)
- **Azure Container Registry builds**: No local Docker installation needed
- **Zero-downtime updates**: Rolling updates via Azure Container Apps
- **~2-minute deployment**: From code change to live production

**Deployment script features:**
- Automatic resource creation if needed
- Build in ACR with cloud-based Docker
- Push to registry with timestamp tags
- Update or create Container App
- Configure Managed Identity and RBAC
- Health checks and URL retrieval
- Comprehensive error handling

#### Managed Identity Authentication
- **No API keys in code**: Migrated from environment variables to Azure Managed Identity
- **DefaultAzureCredential**: Automatic authentication with Azure services
- **Role-based access control**: "Cognitive Services User" role assigned to MI
- **Enterprise security compliance**: No secrets in environment, automatic credential rotation
- **Multi-service support**: Works with Azure AI Foundry, Azure OpenAI, Azure AI Search, etc.

**Security improvements:**
- Eliminated API keys from `.env` files (for Azure services)
- Automatic credential rotation via Azure AD
- Audit trail via Azure Activity Log
- Least-privilege access model
- SOC 2 / ISO 27001 compliant architecture

### 🔧 Technical Improvements

#### Code Changes
- **File**: `streamlit_azure_ai_demo.py` (1273 lines)
  - Added 4 new session state variables for thread persistence
  - Updated 4 async functions with thread management logic
  - Added 4 UI sections with memory documentation and clear buttons
  - Implemented download button for Code Interpreter plots
  - Migrated to DefaultAzureCredential for Azure authentication

#### Infrastructure Changes
- **File**: `deploy-to-azure.sh` (217 lines, new)
  - Automated deployment script with timestamp tagging
  - ACR build orchestration
  - Container App lifecycle management
  - Managed Identity configuration
  - Role assignment automation

- **File**: `Dockerfile` (updated)
  - Verified non-root user permissions for plot directory
  - Ensured `/app/generated_plots` ownership set to `appuser:appuser`
  - Multi-stage build optimized for ~1.5GB runtime image

#### Documentation Updates
- **File**: `README.md`
  - Added live demo link
  - Documented 3 deployment options (local, Docker, ACA)
  - Added conversation memory details to 4 scenario descriptions
  - Created comprehensive "Latest Enhancements" section
  - Updated configuration section with Managed Identity info
  - Enhanced demo files listing

- **File**: `DOCKER_README.md`
  - Added quick start section with automated script
  - Documented Managed Identity setup
  - Added new features technical documentation
  - Created changelog section
  - Enhanced security best practices

- **File**: `CHANGELOG.md` (new)
  - This file!

### 📊 Usage Improvements

#### User Experience
- **Memory persistence**: Users can ask follow-up questions naturally
- **Clear controls**: Explicit buttons to reset conversation memory
- **Instant downloads**: No waiting for blob storage uploads
- **Faster deployments**: 2-minute code-to-production cycle

#### Developer Experience
- **Simplified deployment**: One command instead of 10+ manual steps
- **Better security**: No secrets management for Azure services
- **Faster iteration**: Timestamp tags allow easy rollback
- **Better debugging**: Structured logs with deployment timestamps

### 🌐 Production Deployment

**Live Demo**: https://agent-framework-demo.livelyforest-d40d7875.eastus.azurecontainerapps.io

**Infrastructure:**
- Resource Group: `agent-framework-rg`
- Location: `East US`
- Container Registry: `aqr2d2agentframeworkacr007.azurecr.io`
- Container App: `agent-framework-demo`
- Environment: `agent-framework-env`

**Specifications:**
- CPU: 1.0 cores
- Memory: 2.0 GiB
- Replicas: 1-3 (auto-scaling)
- Ingress: External (HTTPS)
- Authentication: Managed Identity
- RBAC: Cognitive Services User

---

## [1.1.0] - 2025-10-25

### Added
- Docker containerization with multi-stage build
- Non-root user configuration (`appuser:appuser`)
- Azure Container Registry integration
- Manual deployment documentation
- Environment variable configuration via Container Apps secrets

### Technical Details
- **Dockerfile**: Multi-stage build with Python 3.11
- **Base images**: `python:3.11-slim` for runtime
- **Security**: Non-root user with UID 1000
- **Directory structure**: `/app` as working directory
- **Generated plots**: `/app/generated_plots` with proper permissions

---

## [1.0.0] - 2025-10-24

### Initial Release
- **9 Agent Scenarios**:
  1. Basic Chat Agent
  2. Function Tools (Weather API)
  3. Thread Management
  4. Code Interpreter
  5. Bing Web Search (Grounding)
  6. File Search (RAG)
  7. Azure AI Search
  8. Hosted MCP - Microsoft Learn
  9. Firecrawl MCP - Web Scraping

### Features
- Token usage tracking
- Execution timing
- Chat history per scenario
- Markdown rendering
- Session state management
- Responsive design
- Error handling

### Sample Documents
- `employees.pdf` - Employee directory
- `product_catalog.txt` - Product specifications
- `ai_research.pdf` - SigLIP research paper (2.1MB)

### Configuration
- Environment variable-based configuration
- Support for multiple API providers
- Azure AI Foundry integration
- OpenWeatherMap API integration
- Bing Search API integration
- Firecrawl API integration

---

## Future Roadmap

### Planned Features (v1.3.0)
- [ ] Add conversation memory to remaining 5 scenarios
  - [ ] Basic Chat
  - [ ] Weather Agent
  - [ ] Code Interpreter
  - [ ] Firecrawl MCP
  - [ ] Microsoft Learn MCP
- [ ] Memory statistics display (thread age, message count)
- [ ] Export conversation history feature
- [ ] Custom instructions per scenario
- [ ] Response streaming with real-time updates

### Planned Improvements (v1.4.0)
- [ ] Persistent plot storage with Azure Blob Storage (optional)
- [ ] User authentication with Azure AD
- [ ] Multi-user support with isolated sessions
- [ ] Cost tracking and budget alerts
- [ ] Performance monitoring dashboard
- [ ] A/B testing framework for different models

### Under Consideration
- WebSocket support for real-time agent communication
- Voice input/output integration
- Multi-modal agent demonstrations
- Agent-to-agent collaboration examples
- Custom agent marketplace
- Plugin architecture for extensibility

---

## Migration Notes

### From v1.1.0 to v1.2.0

**Breaking Changes:**
- None! All changes are backward compatible.

**New Requirements:**
- Azure Managed Identity must be configured for production deployments
- "Cognitive Services User" role must be assigned to MI principal

**Migration Steps:**
1. Update to latest code: `git pull`
2. Redeploy using new script: `cd AQ-CODE && bash deploy-to-azure.sh`
3. Verify Managed Identity is enabled and has correct role
4. Test memory features in Azure AI Search, Bing, and File Search scenarios
5. Test plot download button in Code Interpreter

**Rollback:**
If needed, redeploy previous version:
```bash
az containerapp update \
  --name agent-framework-demo \
  --resource-group agent-framework-rg \
  --image aqr2d2agentframeworkacr007.azurecr.io/agent-framework-demo:20251025-HHMMSS
```

---

## Technical Details

### File Changes Summary

**Modified Files:**
- `streamlit_azure_ai_demo.py`: +157 lines (memory + download + MI auth)
- `DOCKER_README.md`: +200 lines (new features documentation)
- `README.md`: +150 lines (enhanced demo descriptions)

**New Files:**
- `deploy-to-azure.sh`: 217 lines (automated deployment)
- `CHANGELOG.md`: This file (version history)

**Total Lines Changed**: ~724 lines added/modified

### Performance Metrics

**Deployment Speed:**
- v1.1.0: ~15-20 minutes (manual steps)
- v1.2.0: ~2 minutes (automated)
- Improvement: **87.5% faster**

**Security Posture:**
- v1.1.0: API keys in environment (medium risk)
- v1.2.0: Managed Identity (low risk, enterprise-grade)
- Improvement: **Eliminated secret sprawl**

**User Experience:**
- v1.1.0: Single-turn questions only
- v1.2.0: Multi-turn conversations with context
- Improvement: **4 scenarios with conversation memory**

---

## Contributors

- **Arturo Quiroga** - Sr. Partner Solutions Architect, Microsoft
  - Initial Streamlit demo implementation
  - Docker containerization
  - Azure Container Apps deployment
  - Managed Identity migration
  - Conversation memory feature
  - Plot download button
  - Automated deployment script
  - Comprehensive documentation

---

## Acknowledgments

- Microsoft Agent Framework team for the core framework
- Azure AI Foundry team for the AI capabilities
- Streamlit team for the excellent UI framework
- Azure Container Apps team for the deployment platform

---

## License

This project follows the same license as the parent Microsoft Agent Framework repository.

See [LICENSE](../LICENSE) in the repository root.

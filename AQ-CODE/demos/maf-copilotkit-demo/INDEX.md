# MAF + CopilotKit Demo - Documentation Index

Welcome! This is a complete demo showcasing **Microsoft Agent Framework** with **CopilotKit** for production-ready agent UIs.

---

## 📖 Documentation Guide

### 🚀 Getting Started

Start here based on your goal:

| If you want to... | Read this |
|-------------------|-----------|
| **Set up and run the demo (5 min)** | [QUICK_START.md](./QUICK_START.md) |
| **Understand the full project** | [README.md](./README.md) |
| **Prepare for Teradata presentation** | [DEMO_GUIDE.md](./DEMO_GUIDE.md) |
| **Compare to Streamlit demo** | [STREAMLIT_VS_COPILOTKIT.md](./STREAMLIT_VS_COPILOTKIT.md) |
| **See what was created** | [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) |

---

## 📚 Document Descriptions

### [README.md](./README.md) - Main Documentation
**Purpose:** Complete project documentation  
**Length:** ~15 minutes to read  
**Contains:**
- Architecture overview
- All 6 agents described
- Setup instructions (detailed)
- Usage guide with examples
- Troubleshooting
- Comparison to Streamlit

**When to use:** First-time setup, comprehensive understanding

---

### [QUICK_START.md](./QUICK_START.md) - Fast Setup
**Purpose:** Get running ASAP  
**Length:** 5 minutes to read, 5 minutes to execute  
**Contains:**
- Minimal setup steps
- Quick demo scripts (30 sec each)
- Common issues & fixes
- Essential commands
- Key concepts summary

**When to use:** You just want it working now

---

### [DEMO_GUIDE.md](./DEMO_GUIDE.md) - Presentation Script
**Purpose:** Nail your Teradata presentation  
**Length:** 15-20 minutes to present  
**Contains:**
- Part-by-part demo flow
- What to say (talk tracks)
- What to show (screen steps)
- Code deep dive
- Q&A preparation
- Troubleshooting during demo

**When to use:** Preparing for live presentation

---

### [STREAMLIT_VS_COPILOTKIT.md](./STREAMLIT_VS_COPILOTKIT.md) - Comparison
**Purpose:** Understand the migration rationale  
**Length:** ~10 minutes to read  
**Contains:**
- Feature-by-feature comparison
- Architecture differences
- Use case recommendations
- Migration strategy
- ROI analysis
- When to use each

**When to use:** Justifying the technology choice

---

### [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) - What's Included
**Purpose:** Overview of deliverables  
**Length:** ~5 minutes to read  
**Contains:**
- What was created
- File structure
- Features implemented
- What's missing
- Next steps
- Success criteria

**When to use:** Understanding scope and completeness

---

## 🎯 Quick Navigation

### By Role

**🧑‍💻 Developer** (first time with project)
1. [QUICK_START.md](./QUICK_START.md) - Get it running
2. [README.md](./README.md) - Understand architecture
3. [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) - See what's included

**👔 Presenter** (preparing for Teradata)
1. [DEMO_GUIDE.md](./DEMO_GUIDE.md) - Presentation script
2. [STREAMLIT_VS_COPILOTKIT.md](./STREAMLIT_VS_COPILOTKIT.md) - Comparison points
3. [QUICK_START.md](./QUICK_START.md) - Quick test before demo

**🤔 Decision Maker** (evaluating technologies)
1. [STREAMLIT_VS_COPILOTKIT.md](./STREAMLIT_VS_COPILOTKIT.md) - Why CopilotKit?
2. [README.md](./README.md) - What can it do?
3. [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) - What's the scope?

---

## ⏱️ Time-Based Guide

### I have 5 minutes
→ [QUICK_START.md](./QUICK_START.md)
- Run `./setup.sh`
- Start servers
- See it working

### I have 15 minutes
→ [DEMO_GUIDE.md](./DEMO_GUIDE.md)
- Prepare presentation
- Practice demo flow
- Memorize key points

### I have 30 minutes
→ [README.md](./README.md)
- Full setup
- Test all agents
- Customize for Teradata

### I have 1 hour
1. [README.md](./README.md) - Architecture
2. [DEMO_GUIDE.md](./DEMO_GUIDE.md) - Presentation
3. [STREAMLIT_VS_COPILOTKIT.md](./STREAMLIT_VS_COPILOTKIT.md) - Comparison
4. Practice live demo

---

## 🔍 Search by Topic

### Setup & Installation
- [QUICK_START.md](./QUICK_START.md) - Fast setup
- [README.md](./README.md) § Quick Start - Detailed setup
- `setup.sh` - Automated script

### Architecture
- [README.md](./README.md) § Architecture
- [STREAMLIT_VS_COPILOTKIT.md](./STREAMLIT_VS_COPILOTKIT.md) § Architecture
- [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) § Project Structure

### Agent Capabilities
- [README.md](./README.md) § Features
- [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) § Key Features
- Backend code: `backend/src/agents/`

### Demo Scripts
- [DEMO_GUIDE.md](./DEMO_GUIDE.md) § Demo Flow
- [QUICK_START.md](./QUICK_START.md) § Quick Demo Script
- [README.md](./README.md) § Usage Guide

### Troubleshooting
- [QUICK_START.md](./QUICK_START.md) § Common Issues
- [README.md](./README.md) § Troubleshooting
- [DEMO_GUIDE.md](./DEMO_GUIDE.md) § Troubleshooting During Demo

### Comparison to Streamlit
- [STREAMLIT_VS_COPILOTKIT.md](./STREAMLIT_VS_COPILOTKIT.md) - Full comparison
- [README.md](./README.md) § Comparison table
- [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) § Comparison summary

---

## 🎯 Recommended Reading Order

### First Time Here?
1. **Start:** [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) (5 min)
2. **Quick test:** [QUICK_START.md](./QUICK_START.md) (10 min)
3. **Deep dive:** [README.md](./README.md) (20 min)

### Preparing for Demo?
1. **Test it:** [QUICK_START.md](./QUICK_START.md) (10 min)
2. **Plan it:** [DEMO_GUIDE.md](./DEMO_GUIDE.md) (20 min)
3. **Defend it:** [STREAMLIT_VS_COPILOTKIT.md](./STREAMLIT_VS_COPILOTKIT.md) (10 min)

### Building on It?
1. **Understand:** [README.md](./README.md) (20 min)
2. **See scope:** [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) (5 min)
3. **Check code:** `backend/src/` directory

---

## 📞 Quick Reference

### Essential Commands
```bash
# Setup
./setup.sh

# Backend
cd backend/src && python main.py

# Frontend
cd frontend && npm run dev

# Test
curl http://localhost:8000/
```

### Essential Files
- **Environment:** `backend/.env`
- **Backend entry:** `backend/src/main.py`
- **Agents:** `backend/src/agents/`
- **Frontend:** `frontend/` (from teradata-pres)

### Essential URLs
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🎓 Learning Path

### Beginner
You're new to MAF and CopilotKit:
1. [README.md](./README.md) - What is this?
2. [QUICK_START.md](./QUICK_START.md) - See it work
3. [DEMO_GUIDE.md](./DEMO_GUIDE.md) - Understand features

### Intermediate
You know MAF or Streamlit:
1. [STREAMLIT_VS_COPILOTKIT.md](./STREAMLIT_VS_COPILOTKIT.md) - What's different?
2. [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) - What's included?
3. [DEMO_GUIDE.md](./DEMO_GUIDE.md) - How to present?

### Advanced
You're ready to extend:
1. [README.md](./README.md) § Customization
2. Backend code: `backend/src/agents/`
3. AG-UI docs: https://docs.ag-ui.com
4. CopilotKit docs: https://docs.copilotkit.ai

---

## 📊 Cheat Sheet

| Need to... | Command | File |
|------------|---------|------|
| **Start backend** | `cd backend/src && python main.py` | `main.py` |
| **Start frontend** | `cd frontend && npm run dev` | - |
| **Edit config** | - | `backend/.env` |
| **Add agent** | - | `backend/src/agents/` |
| **Test API** | `curl http://localhost:8000/` | - |
| **View docs** | Open http://localhost:8000/docs | - |

---

## 🎉 Success Checklist

Before your demo:
- [ ] Read [DEMO_GUIDE.md](./DEMO_GUIDE.md)
- [ ] Test all 6 agents work
- [ ] Practice transitions
- [ ] Prepare for Q&A
- [ ] Have backup plan

Before development:
- [ ] Read [README.md](./README.md)
- [ ] Run [QUICK_START.md](./QUICK_START.md)
- [ ] Understand architecture
- [ ] Review agent code

---

**Pick a document above and start exploring! 🚀**

All docs are in this directory. No external links required.

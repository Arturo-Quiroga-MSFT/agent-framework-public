# NL2SQL Implementation Protection

This directory contains three protected, production-ready NL2SQL implementations.

## 🔒 Protected Versions

### 1. nl2sql-pipeline/ (Original - DevUI)
- ✅ Status: **PROTECTED - DO NOT MODIFY**
- Purpose: Web interface with REST API
- Port: 8097
- Features: DevUI, REST API, full workflow

### 2. nl2sql-cli/ (Command Line)
- ✅ Status: **PROTECTED - DO NOT MODIFY**
- Purpose: CLI execution without web server
- Features: Direct command execution, automation-ready

### 3. nl2sql-gradio/ (Chat UI)
- ✅ Status: **PROTECTED - STABLE**
- Purpose: Interactive chat interface
- Port: 7860
- Features: Chat UI, inline charts, suggested questions

## 📚 Documentation

See [NL2SQL_DEPLOYMENT_GUIDE.md](./NL2SQL_DEPLOYMENT_GUIDE.md) for:
- Quick start commands
- Configuration guide
- Troubleshooting
- Deployment options

## ⚠️ Important Rules

1. **DO NOT modify protected versions** - Create new copies for experiments
2. **Test changes in copies first** before considering backports
3. **Keep .env files private** - Never commit credentials
4. **Backup before updates** - Use provided backup commands

## 🚀 Quick Start

```bash
# DevUI
cd nl2sql-pipeline && python nl2sql_workflow.py

# CLI
cd nl2sql-cli && python nl2sql_workflow.py "Your question here"

# Gradio (Recommended)
cd nl2sql-gradio && python app.py
```

## 🔄 Creating New Versions

To experiment without breaking protected versions:

```bash
# Create experimental copy
cp -r nl2sql-gradio nl2sql-experimental

# Work in experimental version
cd nl2sql-experimental
# Make your changes...
```

## 📦 Backups

Protected versions are backed up:
- Git branch: `protected/nl2sql-stable`
- Local archives: `nl2sql-*-backup-YYYYMMDD.tar.gz`

## Last Verified

- Date: November 28, 2025
- All versions tested and working
- Database: TERADATA-FI on aqsqlserver001.database.windows.net
- Model: gpt-5-mini (Azure OpenAI)

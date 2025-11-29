#!/bin/bash
# Quick launcher for NL2SQL Gradio Chat

cd "$(dirname "$0")"
source ../.venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null
python app.py

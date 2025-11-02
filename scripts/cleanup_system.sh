#!/bin/bash
###############################################################################
# Unity Cyber Security Office — System Cleanup Script
#
# MacBook Optimization Specialist's automated cleanup routine
#
# This script safely removes:
# 1. Python bytecode caches (__pycache__, *.pyc)
# 2. User caches (~/.cache)
# 3. npm cache
# 4. Unused Ollama models (interactive)
#
# Philosophy:
# "Every GB matters. Waste is the enemy. This machine deserves peak performance."
#
# Author: MacBook Optimization Specialist
# Date: October 17, 2025
###############################################################################

set -e

echo "======================================================================="
echo "UNITY CYBER SECURITY OFFICE — SYSTEM CLEANUP"
echo "======================================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TOTAL_FREED=0

###############################################################################
# 1. CLEAN PYTHON CACHES
###############################################################################

echo "🧹 Step 1: Cleaning Python bytecode caches..."
echo ""

BEFORE=$(du -sm ~ 2>/dev/null | cut -f1)

echo "   Finding __pycache__ directories..."
PYCACHE_COUNT=$(find ~ -name "__pycache__" -type d 2>/dev/null | wc -l | tr -d ' ')
echo "   Found: $PYCACHE_COUNT directories"

if [ "$PYCACHE_COUNT" -gt 0 ]; then
    echo "   Deleting..."
    find ~ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    echo -e "   ${GREEN}✅ Python caches cleaned${NC}"
else
    echo "   ℹ️  No Python caches found"
fi

echo ""

###############################################################################
# 2. CLEAN USER CACHE
###############################################################################

echo "🧹 Step 2: Cleaning user cache directory..."
echo ""

if [ -d ~/.cache ]; then
    CACHE_SIZE=$(du -sm ~/.cache 2>/dev/null | cut -f1)
    echo "   ~/.cache size: ${CACHE_SIZE}MB"

    if [ "$CACHE_SIZE" -gt 100 ]; then
        echo "   Cleaning ~/.cache..."
        rm -rf ~/.cache/*
        echo -e "   ${GREEN}✅ User cache cleaned (freed ${CACHE_SIZE}MB)${NC}"
        TOTAL_FREED=$((TOTAL_FREED + CACHE_SIZE))
    else
        echo "   ℹ️  Cache is small, skipping"
    fi
else
    echo "   ℹ️  No ~/.cache directory found"
fi

echo ""

###############################################################################
# 3. CLEAN NPM CACHE
###############################################################################

echo "🧹 Step 3: Cleaning npm cache..."
echo ""

if command -v npm &> /dev/null; then
    if [ -d ~/.npm ]; then
        NPM_SIZE=$(du -sm ~/.npm 2>/dev/null | cut -f1)
        echo "   ~/.npm size: ${NPM_SIZE}MB"

        if [ "$NPM_SIZE" -gt 100 ]; then
            echo "   Running npm cache clean..."
            npm cache clean --force 2>/dev/null || true
            echo -e "   ${GREEN}✅ npm cache cleaned (freed ~${NPM_SIZE}MB)${NC}"
            TOTAL_FREED=$((TOTAL_FREED + NPM_SIZE))
        else
            echo "   ℹ️  npm cache is small, skipping"
        fi
    else
        echo "   ℹ️  No npm cache found"
    fi
else
    echo "   ℹ️  npm not installed"
fi

echo ""

###############################################################################
# 4. OLLAMA MODEL CLEANUP (INTERACTIVE)
###############################################################################

echo "🤖 Step 4: Ollama model cleanup..."
echo ""

if command -v ollama &> /dev/null; then
    echo "   Installed models:"
    ollama list
    echo ""

    echo "   Unity uses these models:"
    echo "   - deepseek-r1:14b (reasoning)"
    echo "   - qwen2.5-coder:7b (coding)"
    echo ""

    echo "   Recommended deletions to free space:"
    echo "   1. deepseek-r1:32b (19GB) — Larger version, use 14b instead"
    echo "   2. qwen3:8b (5.2GB) — Not used by Unity"
    echo "   3. mistral:7b (4.4GB) — Not used by Unity"
    echo "   4. llama3:latest (4.7GB) — Not used by Unity"
    echo "   5. wizardcoder:latest (3.8GB) — Not used by Unity"
    echo "   6. llama3.2:latest (2.0GB) — Not used by Unity"
    echo ""

    echo -e "${YELLOW}⚠️  Would you like to remove unused models? (y/n)${NC}"
    read -p "   > " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "   Removing unused models..."

        # Remove models
        ollama rm deepseek-r1:32b 2>/dev/null && echo "   ✅ Removed deepseek-r1:32b (19GB)" || echo "   ℹ️  deepseek-r1:32b not found"
        ollama rm qwen3:8b 2>/dev/null && echo "   ✅ Removed qwen3:8b (5.2GB)" || echo "   ℹ️  qwen3:8b not found"
        ollama rm mistral:7b 2>/dev/null && echo "   ✅ Removed mistral:7b (4.4GB)" || echo "   ℹ️  mistral:7b not found"
        ollama rm llama3:latest 2>/dev/null && echo "   ✅ Removed llama3:latest (4.7GB)" || echo "   ℹ️  llama3:latest not found"
        ollama rm wizardcoder:latest 2>/dev/null && echo "   ✅ Removed wizardcoder:latest (3.8GB)" || echo "   ℹ️  wizardcoder:latest not found"
        ollama rm llama3.2:latest 2>/dev/null && echo "   ✅ Removed llama3.2:latest (2.0GB)" || echo "   ℹ️  llama3.2:latest not found"
        ollama rm nomic-embed-text:latest 2>/dev/null && echo "   ✅ Removed nomic-embed-text:latest (274MB)" || echo "   ℹ️  nomic-embed-text:latest not found"

        echo ""
        echo "   Remaining models:"
        ollama list

        echo -e "   ${GREEN}✅ Ollama cleanup complete${NC}"
    else
        echo "   ℹ️  Skipping Ollama cleanup"
    fi
else
    echo "   ℹ️  Ollama not installed"
fi

echo ""

###############################################################################
# SUMMARY
###############################################################################

echo "======================================================================="
echo "CLEANUP SUMMARY"
echo "======================================================================="
echo ""

AFTER=$(du -sm ~ 2>/dev/null | cut -f1)
FREED=$((BEFORE - AFTER))

if [ "$FREED" -gt 0 ]; then
    echo -e "${GREEN}✅ Freed approximately ${FREED}MB${NC}"
else
    echo "ℹ️  Space freed (some may not be reflected immediately)"
fi

echo ""
echo "Next steps:"
echo "1. Review ~/Downloads for old files (7.0GB available)"
echo "2. Review ~/Library/Caches if needed (10.7GB)"
echo "3. Run this script weekly for maintenance"
echo ""
echo "To check disk usage:"
echo "   df -h"
echo ""
echo "To run MacBook Optimizer report:"
echo "   python ~/evoagentx_project/sprint_1hour/agents/cybersecurity/macos_optimizer.py"
echo ""
echo -e "${GREEN}✅ System cleanup complete${NC}"
echo ""

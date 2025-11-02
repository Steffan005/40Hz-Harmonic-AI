#!/usr/bin/env python3
"""
Unity Backend API - SIMPLE VERSION
Minimal Flask app without complex initialization to prevent hangs
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simple health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "OK",
        "timestamp": time.time(),
        "simple_backend": True,
        "message": "Unity Backend - Simple Mode"
    })

# Basic evaluate endpoint
@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.json
        goal = data.get('goal', '')
        output = data.get('output', '')
        
        # Simple evaluation logic
        quality_score = 75.0 if output else 50.0
        
        return jsonify({
            "quality_score": quality_score,
            "delta_score": quality_score - 50.0,
            "robust_pct": 85.0,
            "cache_hit": False,
            "time_ms": 50.0,
            "routing_path": "simple_evaluator",
            "violations": []
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Basic memory snapshot
@app.route('/memory/snapshot', methods=['POST'])
def memory_snapshot():
    try:
        data = request.json
        title = data.get('title', 'Snapshot')
        content = data.get('content', '')
        
        # Simple memory storage
        memory_id = f"mem_{int(time.time())}"
        
        return jsonify({
            "id": memory_id,
            "title": title,
            "note": content[:100] if content else "No content",
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Simple system status
@app.route('/system/status', methods=['GET'])
def system_status():
    return jsonify({
        "success": True,
        "status": {
            "timestamp": time.time(),
            "engines": {
                "simple_backend": True,
                "complex_engines": False
            },
            "offices": {
                "total": 1,
                "online": 1,
                "categories": ["Simple"]
            },
            "evolution": {
                "continuous_loop": False,
                "generations_completed": 0,
                "best_score": 0.0,
                "improvements_pending": 0
            },
            "infrastructure": {
                "simple_api": "running"
            },
            "performance": {
                "backend_mode": "simple"
            }
        }
    })

if __name__ == '__main__':
    print("="*50)
    print("UNITY BACKEND - SIMPLE MODE")
    print("="*50)
    print("Starting on http://127.0.0.1:8000")
    print("Simple endpoints only - no complex initialization")
    print("="*50)
    
    app.run(host='127.0.0.1', port=8000, debug=False)
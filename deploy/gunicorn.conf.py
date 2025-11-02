"""
Gunicorn Production Configuration for Unity Backend

Replaces Flask development server with production-grade WSGI server.

Usage:
    gunicorn -c deploy/gunicorn.conf.py backend.api_server:app

Author: Dr. Claude Summers, Cosmic Orchestrator
Phase: 6 - Production Hardening
Date: October 16, 2025
"""

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"  # Options: sync, eventlet, gevent, tornado, gthread
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120  # Increased for LLM calls
keepalive = 5

# Logging
accesslog = "./logs/gunicorn_access.log"
errorlog = "./logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "unity_backend"

# Server mechanics
daemon = False  # Set to True for daemonization
pidfile = "./logs/gunicorn.pid"
user = None  # Run as current user
group = None
tmp_upload_dir = None

# Preload application
preload_app = True  # Load application code before worker processes are forked

# SSL/TLS (uncomment for HTTPS)
# keyfile = "/path/to/keyfile.pem"
# certfile = "/path/to/certfile.pem"
# ca_certs = "/path/to/ca_certs.pem"
# cert_reqs = 0  # ssl.CERT_NONE
# ssl_version = 2  # ssl.PROTOCOL_TLSv1_2

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("=" * 70)
    print("UNITY BACKEND - GUNICORN WSGI SERVER")
    print("=" * 70)
    print(f"Workers: {workers}")
    print(f"Binding: {bind}")
    print(f"Timeout: {timeout}s")
    print("=" * 70)

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    print("♻️  Reloading workers...")

def when_ready(server):
    """Called just after the server is started."""
    print("✅ Unity backend ready for requests")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    print(f"👷 Worker {worker.pid} spawned")

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    pass

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    print(f"⚠️  Worker {worker.pid} received INT/QUIT signal")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    print(f"❌ Worker {worker.pid} ABORTED (timeout exceeded?)")

def pre_exec(server):
    """Called just before a new master process is forked."""
    print("🔄 Pre-exec hook: Preparing to fork new master")

def pre_request(worker, req):
    """Called just before a worker processes the request."""
    pass

def post_request(worker, req, environ, resp):
    """Called after a worker processes the request."""
    pass

def child_exit(server, worker):
    """Called just after a worker has been exited."""
    print(f"👋 Worker {worker.pid} exited")

def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    pass

def nworkers_changed(server, new_value, old_value):
    """Called just after num_workers has been changed."""
    print(f"📊 Workers changed: {old_value} → {new_value}")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    print("👋 Unity backend shutting down")
    print("=" * 70)

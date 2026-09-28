#!/usr/bin/env python3
"""Run backend uvicorn server with proper paths and environment settings."""
import os
import sys
import subprocess

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(root_dir)

cmd = [
    sys.executable,
    "-m",
    "uvicorn",
    "app.main:app",
    "--app-dir",
    "backend",
    "--host",
    "0.0.0.0",
    "--port",
    "8000",
    "--reload",
]

print(f"Starting CycloneGuard backend from {root_dir}...")
print(f"Command: {' '.join(cmd)}")
sys.exit(subprocess.call(cmd))

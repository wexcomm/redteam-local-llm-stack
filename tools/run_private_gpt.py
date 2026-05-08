#!/usr/bin/env python3
"""Wrapper to apply qdrant-client compatibility patch before starting PrivateGPT."""
import sys
import os

# Apply qdrant-client compatibility patch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qdrant_compat  # noqa: F401

# Run PrivateGPT as module
from private_gpt.__main__ import main

if __name__ == "__main__":
    main()

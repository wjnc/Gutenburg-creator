#!/usr/bin/env python3
"""
Wrapper script to run the pipeline with API key from Claude Code session.
This script gets the API key from command line arg and passes it to the pipeline
without ever writing it to disk.
"""

import sys
import os

# Accept API key as command line argument
if len(sys.argv) > 1:
    api_key = sys.argv[1]
    os.environ['ANTHROPIC_API_KEY'] = api_key
    print("✓ API key configured from argument")
else:
    # Try to use existing environment
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠ Warning: No API key provided and none found in environment")
        print("Usage: python run_with_session_key.py <api_key>")
        print("Or set ANTHROPIC_API_KEY environment variable")

# Now import and run the main pipeline
from main import main

if __name__ == "__main__":
    main()

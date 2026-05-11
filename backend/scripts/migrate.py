#!/usr/bin/env python
"""
Manual migration CLI script.
Use these commands during development when you add new models:

  python scripts/migrate.py auto    # Auto-generate migration from model changes
  python scripts/migrate.py upgrade # Apply all pending migrations
  python scripts/migrate.py both    # Auto-generate AND upgrade (default)
"""

import sys
import os

# Add the parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.migration_helper import auto_generate_migrations, apply_migrations

def main():
    if len(sys.argv) < 2:
        command = "both"
    else:
        command = sys.argv[1].lower()
    
    if command == "auto":
        print("Auto-generating migrations from model changes...")
        auto_generate_migrations()
    elif command == "upgrade":
        print("Applying all pending migrations...")
        apply_migrations()
    elif command == "both":
        print("Auto-generating and applying migrations...")
        auto_generate_migrations()
        apply_migrations()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: auto, upgrade, both")
        sys.exit(1)

if __name__ == "__main__":
    main()

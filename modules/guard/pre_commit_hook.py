"""
pre_commit_hook.py
------------------
Git pre-commit hook template for DevShield AI Developer Guard.
Scans staged files for secrets before allowing a commit.
"""

import os
import sys
import subprocess

# Path to the CLI scanner (relative to the .git/hooks directory)
CLI_SCANNER_PATH = os.path.join(os.path.dirname(__file__), 'cli_scanner.py')



def main():
    """
    Main function to run the CLI scanner on staged files before commit.
    If secrets are found, the commit is blocked unless override is used.
    """
    import argparse
    parser = argparse.ArgumentParser(description="DevShield Guard Pre-commit Hook")
    parser.add_argument('--allow-secret', action='store_true', help='Override and allow commit with secrets (requires justification)')
    parser.add_argument('--justification', type=str, default='', help='Justification for allowing secret commit')
    args, unknown = parser.parse_known_args()

    # Run the CLI scanner
    result = subprocess.run([sys.executable, CLI_SCANNER_PATH], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        # Check for override flag or environment variable
        allow_env = os.environ.get('DEVSHIELD_ALLOW_SECRET', '').lower() == 'true'
        if args.allow_secret or allow_env:
            justification = args.justification or os.environ.get('DEVSHIELD_JUSTIFICATION', '')
            print("\n[DevShield Guard] WARNING: Commit override used. Secret(s) detected but commit allowed.")
            if justification:
                print(f"Justification: {justification}")
                # Optionally, log justification to a file
                with open('.devshield_override.log', 'a', encoding='utf-8') as logf:
                    from datetime import datetime
                    logf.write(f"[{datetime.utcnow().isoformat()}] OVERRIDE: {justification}\n")
            else:
                print("No justification provided.")
            sys.exit(0)
        else:
            print("\n[DevShield Guard] Commit aborted due to detected secrets. Use --allow-secret with --justification to override.")
            sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

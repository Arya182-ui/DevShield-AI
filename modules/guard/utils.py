"""
utils.py
--------
Utility functions for Developer Guard.
"""

import re


def redact_secret(secret):
    """
    Redact a secret for safe display in logs (show only first/last 2 chars).
    """
    if len(secret) <= 4:
        return '*' * len(secret)
    return f"{secret[:2]}{'*' * (len(secret) - 4)}{secret[-2:]}"


def print_warning(msg):
    """
    Print a warning message in yellow.
    """
    print(f"\033[93m[WARNING] {msg}\033[0m")


def print_success(msg):
    """
    Print a success message in green.
    """
    print(f"\033[92m{msg}\033[0m")

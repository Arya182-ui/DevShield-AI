"""
cli_scanner.py
--------------
CLI tool to scan staged files for secrets using regex and entropy-based detection.
"""


import re
import sys
import subprocess
import os
import json
from datetime import datetime
from utils import redact_secret, print_warning, print_success

# Enhanced regex patterns for secrets (API keys, DB, JWT, cloud, etc.)
SECRET_PATTERNS = [
    # Generic API keys
    (r'(?i)api[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9\-_=]{16,})["\']', 'API Key'),
    (r'(?i)secret[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9\-_=]{16,})["\']', 'Secret Key'),
    (r'(?i)token["\']?\s*[:=]\s*["\']([A-Za-z0-9\-_=]{16,})["\']', 'Token'),
    (r'(?i)password["\']?\s*[:=]\s*["\'](.{8,})["\']', 'Password'),
    # AWS Access Key ID
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
    # AWS Secret Access Key
    (r'(?i)aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9/+=]{40})["\']', 'AWS Secret Access Key'),
    # Google API Key
    (r'AIza[0-9A-Za-z\-_]{35}', 'Google API Key'),
    # Azure Storage Key
    (r'(?i)azure[_-]?storage[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9+/=]{88})["\']', 'Azure Storage Key'),
    # JWT (JSON Web Token)
    (r'eyJ[A-Za-z0-9\-_]+?\.[A-Za-z0-9\-_]+?\.[A-Za-z0-9\-_]+', 'JWT'),
    # OAuth Client Secret
    (r'(?i)client[_-]?secret["\']?\s*[:=]\s*["\']([A-Za-z0-9\-_=]{16,})["\']', 'OAuth Client Secret'),
    # Database password
    (r'(?i)(db|database|sql|mysql|postgres)[_-]?password["\']?\s*[:=]\s*["\'](.{8,})["\']', 'Database Password'),
    # Slack Token
    (r'xox[baprs]-([0-9a-zA-Z]{10,48})', 'Slack Token'),
    # Generic cloud provider secret
    (r'(?i)(cloud|provider)[_-]?secret["\']?\s*[:=]\s*["\']([A-Za-z0-9\-_=]{16,})["\']', 'Cloud Provider Secret'),
]

# Entropy threshold for random string detection
ENTROPY_THRESHOLD = 4.0


def get_staged_files():
    """Get a list of staged files for commit."""
    result = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True)
    files = result.stdout.strip().split('\n')
    return [f for f in files if f and os.path.isfile(f)]


def calculate_shannon_entropy(data):
    """Calculate the Shannon entropy of a string."""
    import math
    if not data:
        return 0
    entropy = 0
    for x in set(data):
        p_x = float(data.count(x)) / len(data)
        entropy -= p_x * math.log2(p_x)
    return entropy



def scan_file_for_secrets(filepath):
    """Scan a file for secrets using regex and entropy-based detection."""
    findings = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        for i, line in enumerate(lines, 1):
            # Regex-based detection
            for pattern, label in SECRET_PATTERNS:
                for match in re.finditer(pattern, line):
                    secret = match.group(1) if match.groups() else match.group(0)
                    entropy = calculate_shannon_entropy(secret)
                    findings.append({
                        'timestamp': datetime.utcnow().isoformat(),
                        'file': filepath,
                        'line': i,
                        'secret_type': label,
                        'redacted': redact_secret(secret),
                        'entropy': entropy,
                        'risk_score': int(min(entropy * 20, 100))
                    })
            # Entropy-based detection (for long strings)
            for word in re.findall(r'[A-Za-z0-9\-_=]{16,}', line):
                entropy = calculate_shannon_entropy(word)
                if entropy > ENTROPY_THRESHOLD:
                    findings.append({
                        'timestamp': datetime.utcnow().isoformat(),
                        'file': filepath,
                        'line': i,
                        'secret_type': 'High-entropy string',
                        'redacted': redact_secret(word),
                        'entropy': entropy,
                        'risk_score': int(min(entropy * 20, 100))
                    })
    except Exception as e:
        print_warning(f"Could not scan {filepath}: {e}")
    return findings



def main():
    """Main entry point for CLI scanner."""
    import argparse
    parser = argparse.ArgumentParser(description="DevShield CLI Scanner")
    parser.add_argument('--report', type=str, help='Output scan report to file (JSON or HTML)')
    parser.add_argument('--format', type=str, choices=['json', 'html'], default='json', help='Report format (json/html)')
    args = parser.parse_args()

    staged_files = get_staged_files()
    if not staged_files:
        print_success("No staged files to scan.")
        sys.exit(0)
    all_findings = []
    for file in staged_files:
        findings = scan_file_for_secrets(file)
        all_findings.extend(findings)

    # Output report if requested
    if args.report:
        if args.format == 'json':
            with open(args.report, 'w', encoding='utf-8') as f:
                json.dump(all_findings, f, indent=2)
            print_success(f"Scan report written to {args.report} (JSON)")
        elif args.format == 'html':
            with open(args.report, 'w', encoding='utf-8') as f:
                f.write('<html><head><title>DevShield Scan Report</title></head><body>')
                f.write('<h2>DevShield Scan Report</h2><table border="1"><tr><th>Timestamp</th><th>File</th><th>Line</th><th>Type</th><th>Redacted</th><th>Entropy</th><th>Risk Score</th></tr>')
                for finding in all_findings:
                    f.write(f"<tr><td>{finding['timestamp']}</td><td>{finding['file']}</td><td>{finding['line']}</td><td>{finding['secret_type']}</td><td>{finding['redacted']}</td><td>{finding['entropy']:.2f}</td><td>{finding['risk_score']}</td></tr>")
                f.write('</table></body></html>')
            print_success(f"Scan report written to {args.report} (HTML)")

    if all_findings:
        print_warning("\nPotential secrets detected:")
        # Log findings to file
        with open('devshield_scan.log', 'a', encoding='utf-8') as logf:
            for finding in all_findings:
                log_line = (
                    f"[{finding['timestamp']}] {finding['file']}:{finding['line']} "
                    f"[{finding['secret_type']}] {finding['redacted']} "
                    f"(Entropy: {finding['entropy']:.2f}, Risk: {finding['risk_score']})\n"
                )
                logf.write(log_line)
                print_warning(log_line.strip())
        print_warning("\nPlease remove secrets before committing.")
        sys.exit(1)
    else:
        print_success("No secrets detected in staged files. Safe to commit.")
        sys.exit(0)


if __name__ == "__main__":
    main()

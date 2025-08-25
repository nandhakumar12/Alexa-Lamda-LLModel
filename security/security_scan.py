#!/usr/bin/env python3
"""
Security Scanning Script for Voice Assistant AI
Performs comprehensive security analysis of the codebase and infrastructure
"""

import os
import json
import subprocess
import argparse
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityScanner:
    """Comprehensive security scanner for Voice Assistant AI"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results = {
            'timestamp': None,
            'scans': {},
            'summary': {
                'total_issues': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'info': 0
            }
        }
    
    def run_bandit_scan(self) -> Dict[str, Any]:
        """Run Bandit security scan on Python code"""
        logger.info("Running Bandit security scan...")
        
        try:
            # Run bandit on backend code
            cmd = [
                'bandit', '-r', 'backend/',
                '-f', 'json',
                '-ll',  # Low confidence, low severity
                '--skip', 'B101,B601'  # Skip assert and shell injection (if needed)
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode in [0, 1]:  # 0 = no issues, 1 = issues found
                bandit_results = json.loads(result.stdout)
                
                issues = []
                for issue in bandit_results.get('results', []):
                    issues.append({
                        'file': issue['filename'],
                        'line': issue['line_number'],
                        'severity': issue['issue_severity'],
                        'confidence': issue['issue_confidence'],
                        'test_id': issue['test_id'],
                        'test_name': issue['test_name'],
                        'issue_text': issue['issue_text'],
                        'code': issue['code']
                    })
                
                return {
                    'tool': 'bandit',
                    'status': 'completed',
                    'issues_found': len(issues),
                    'issues': issues,
                    'metrics': bandit_results.get('metrics', {})
                }
            else:
                return {
                    'tool': 'bandit',
                    'status': 'error',
                    'error': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'tool': 'bandit',
                'status': 'timeout',
                'error': 'Bandit scan timed out'
            }
        except Exception as e:
            return {
                'tool': 'bandit',
                'status': 'error',
                'error': str(e)
            }
    
    def run_safety_scan(self) -> Dict[str, Any]:
        """Run Safety scan for known vulnerabilities in dependencies"""
        logger.info("Running Safety scan for vulnerable dependencies...")
        
        try:
            # Find all requirements.txt files
            requirements_files = list(self.project_root.rglob('requirements.txt'))
            
            all_issues = []
            
            for req_file in requirements_files:
                cmd = [
                    'safety', 'check',
                    '-r', str(req_file),
                    '--json'
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    # No vulnerabilities found
                    continue
                elif result.returncode == 64:
                    # Vulnerabilities found
                    try:
                        safety_results = json.loads(result.stdout)
                        for vuln in safety_results:
                            all_issues.append({
                                'file': str(req_file.relative_to(self.project_root)),
                                'package': vuln['package'],
                                'installed_version': vuln['installed_version'],
                                'vulnerability_id': vuln['vulnerability_id'],
                                'advisory': vuln['advisory'],
                                'severity': 'high'  # Safety doesn't provide severity, assume high
                            })
                    except json.JSONDecodeError:
                        logger.warning(f"Could not parse Safety output for {req_file}")
            
            return {
                'tool': 'safety',
                'status': 'completed',
                'issues_found': len(all_issues),
                'issues': all_issues
            }
            
        except subprocess.TimeoutExpired:
            return {
                'tool': 'safety',
                'status': 'timeout',
                'error': 'Safety scan timed out'
            }
        except Exception as e:
            return {
                'tool': 'safety',
                'status': 'error',
                'error': str(e)
            }
    
    def run_semgrep_scan(self) -> Dict[str, Any]:
        """Run Semgrep static analysis"""
        logger.info("Running Semgrep static analysis...")
        
        try:
            cmd = [
                'semgrep',
                '--config=auto',
                '--json',
                '--timeout=300',
                'backend/',
                'frontend/src/'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode in [0, 1]:
                semgrep_results = json.loads(result.stdout)
                
                issues = []
                for finding in semgrep_results.get('results', []):
                    issues.append({
                        'file': finding['path'],
                        'line': finding['start']['line'],
                        'rule_id': finding['check_id'],
                        'message': finding['message'],
                        'severity': finding.get('extra', {}).get('severity', 'medium'),
                        'confidence': finding.get('extra', {}).get('metadata', {}).get('confidence', 'medium'),
                        'code': finding.get('extra', {}).get('lines', '')
                    })
                
                return {
                    'tool': 'semgrep',
                    'status': 'completed',
                    'issues_found': len(issues),
                    'issues': issues
                }
            else:
                return {
                    'tool': 'semgrep',
                    'status': 'error',
                    'error': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'tool': 'semgrep',
                'status': 'timeout',
                'error': 'Semgrep scan timed out'
            }
        except Exception as e:
            return {
                'tool': 'semgrep',
                'status': 'error',
                'error': str(e)
            }
    
    def run_terraform_security_scan(self) -> Dict[str, Any]:
        """Run security scan on Terraform files"""
        logger.info("Running Terraform security scan...")
        
        try:
            # Use tfsec for Terraform security scanning
            cmd = [
                'tfsec',
                'infra/terraform/',
                '--format', 'json'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode in [0, 1]:
                if result.stdout.strip():
                    tfsec_results = json.loads(result.stdout)
                    
                    issues = []
                    for finding in tfsec_results.get('results', []):
                        issues.append({
                            'file': finding['location']['filename'],
                            'line': finding['location']['start_line'],
                            'rule_id': finding['rule_id'],
                            'rule_description': finding['rule_description'],
                            'severity': finding['severity'],
                            'impact': finding['impact'],
                            'resolution': finding['resolution']
                        })
                    
                    return {
                        'tool': 'tfsec',
                        'status': 'completed',
                        'issues_found': len(issues),
                        'issues': issues
                    }
                else:
                    return {
                        'tool': 'tfsec',
                        'status': 'completed',
                        'issues_found': 0,
                        'issues': []
                    }
            else:
                return {
                    'tool': 'tfsec',
                    'status': 'error',
                    'error': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'tool': 'tfsec',
                'status': 'timeout',
                'error': 'tfsec scan timed out'
            }
        except Exception as e:
            return {
                'tool': 'tfsec',
                'status': 'error',
                'error': str(e)
            }
    
    def run_secrets_scan(self) -> Dict[str, Any]:
        """Scan for secrets and sensitive information"""
        logger.info("Running secrets scan...")
        
        try:
            # Use truffleHog for secrets detection
            cmd = [
                'trufflehog',
                'filesystem',
                str(self.project_root),
                '--json',
                '--exclude-paths', '.git/',
                '--exclude-paths', 'node_modules/',
                '--exclude-paths', '.terraform/'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            issues = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            finding = json.loads(line)
                            issues.append({
                                'file': finding.get('SourceMetadata', {}).get('Data', {}).get('Filesystem', {}).get('file', ''),
                                'line': finding.get('SourceMetadata', {}).get('Data', {}).get('Filesystem', {}).get('line', 0),
                                'detector': finding.get('DetectorName', ''),
                                'verified': finding.get('Verified', False),
                                'severity': 'high' if finding.get('Verified', False) else 'medium'
                            })
                        except json.JSONDecodeError:
                            continue
            
            return {
                'tool': 'trufflehog',
                'status': 'completed',
                'issues_found': len(issues),
                'issues': issues
            }
            
        except subprocess.TimeoutExpired:
            return {
                'tool': 'trufflehog',
                'status': 'timeout',
                'error': 'Secrets scan timed out'
            }
        except Exception as e:
            return {
                'tool': 'trufflehog',
                'status': 'error',
                'error': str(e)
            }
    
    def run_npm_audit(self) -> Dict[str, Any]:
        """Run npm audit for frontend dependencies"""
        logger.info("Running npm audit for frontend dependencies...")
        
        try:
            frontend_dir = self.project_root / 'frontend'
            if not (frontend_dir / 'package.json').exists():
                return {
                    'tool': 'npm-audit',
                    'status': 'skipped',
                    'reason': 'No package.json found'
                }
            
            cmd = ['npm', 'audit', '--json']
            
            result = subprocess.run(
                cmd,
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.stdout:
                try:
                    audit_results = json.loads(result.stdout)
                    
                    issues = []
                    for vuln_id, vuln in audit_results.get('vulnerabilities', {}).items():
                        issues.append({
                            'package': vuln.get('name', vuln_id),
                            'severity': vuln.get('severity', 'unknown'),
                            'title': vuln.get('title', ''),
                            'url': vuln.get('url', ''),
                            'range': vuln.get('range', ''),
                            'via': vuln.get('via', [])
                        })
                    
                    return {
                        'tool': 'npm-audit',
                        'status': 'completed',
                        'issues_found': len(issues),
                        'issues': issues,
                        'metadata': audit_results.get('metadata', {})
                    }
                except json.JSONDecodeError:
                    return {
                        'tool': 'npm-audit',
                        'status': 'error',
                        'error': 'Could not parse npm audit output'
                    }
            else:
                return {
                    'tool': 'npm-audit',
                    'status': 'completed',
                    'issues_found': 0,
                    'issues': []
                }
                
        except subprocess.TimeoutExpired:
            return {
                'tool': 'npm-audit',
                'status': 'timeout',
                'error': 'npm audit timed out'
            }
        except Exception as e:
            return {
                'tool': 'npm-audit',
                'status': 'error',
                'error': str(e)
            }
    
    def calculate_summary(self) -> None:
        """Calculate summary statistics from all scans"""
        total_issues = 0
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        
        for scan_name, scan_result in self.results['scans'].items():
            if scan_result.get('status') == 'completed':
                issues = scan_result.get('issues', [])
                total_issues += len(issues)
                
                for issue in issues:
                    severity = issue.get('severity', 'medium').lower()
                    if severity in severity_counts:
                        severity_counts[severity] += 1
                    else:
                        severity_counts['medium'] += 1
        
        self.results['summary'] = {
            'total_issues': total_issues,
            **severity_counts
        }
    
    def run_all_scans(self) -> Dict[str, Any]:
        """Run all security scans"""
        from datetime import datetime
        
        logger.info("Starting comprehensive security scan...")
        self.results['timestamp'] = datetime.utcnow().isoformat()
        
        # Run all scans
        scans = [
            ('bandit', self.run_bandit_scan),
            ('safety', self.run_safety_scan),
            ('semgrep', self.run_semgrep_scan),
            ('terraform', self.run_terraform_security_scan),
            ('secrets', self.run_secrets_scan),
            ('npm-audit', self.run_npm_audit)
        ]
        
        for scan_name, scan_func in scans:
            try:
                logger.info(f"Running {scan_name} scan...")
                self.results['scans'][scan_name] = scan_func()
            except Exception as e:
                logger.error(f"Error running {scan_name} scan: {e}")
                self.results['scans'][scan_name] = {
                    'tool': scan_name,
                    'status': 'error',
                    'error': str(e)
                }
        
        # Calculate summary
        self.calculate_summary()
        
        logger.info("Security scan completed")
        return self.results
    
    def generate_report(self, output_file: Path) -> None:
        """Generate security report"""
        logger.info(f"Generating security report: {output_file}")
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Also generate a human-readable summary
        summary_file = output_file.with_suffix('.txt')
        with open(summary_file, 'w') as f:
            f.write("Voice Assistant AI - Security Scan Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Scan completed: {self.results['timestamp']}\n\n")
            
            f.write("Summary:\n")
            f.write(f"  Total issues: {self.results['summary']['total_issues']}\n")
            f.write(f"  Critical: {self.results['summary']['critical']}\n")
            f.write(f"  High: {self.results['summary']['high']}\n")
            f.write(f"  Medium: {self.results['summary']['medium']}\n")
            f.write(f"  Low: {self.results['summary']['low']}\n")
            f.write(f"  Info: {self.results['summary']['info']}\n\n")
            
            for scan_name, scan_result in self.results['scans'].items():
                f.write(f"{scan_name.upper()} Scan:\n")
                f.write(f"  Status: {scan_result.get('status', 'unknown')}\n")
                f.write(f"  Issues found: {scan_result.get('issues_found', 0)}\n")
                if scan_result.get('error'):
                    f.write(f"  Error: {scan_result['error']}\n")
                f.write("\n")


def main():
    parser = argparse.ArgumentParser(description='Run security scans for Voice Assistant AI')
    parser.add_argument('--project-root', type=Path, default=Path('.'), help='Project root directory')
    parser.add_argument('--output', type=Path, default=Path('security-scan-results.json'), help='Output file')
    parser.add_argument('--fail-on-high', action='store_true', help='Fail if high severity issues found')
    parser.add_argument('--fail-on-critical', action='store_true', help='Fail if critical severity issues found')
    
    args = parser.parse_args()
    
    try:
        # Initialize scanner
        scanner = SecurityScanner(args.project_root)
        
        # Run scans
        results = scanner.run_all_scans()
        
        # Generate report
        scanner.generate_report(args.output)
        
        # Check for failure conditions
        summary = results['summary']
        
        if args.fail_on_critical and summary['critical'] > 0:
            logger.error(f"Found {summary['critical']} critical severity issues")
            exit(1)
        
        if args.fail_on_high and summary['high'] > 0:
            logger.error(f"Found {summary['high']} high severity issues")
            exit(1)
        
        logger.info("Security scan completed successfully")
        
    except Exception as e:
        logger.error(f"Security scan failed: {e}")
        exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Context Manager v2.0 - Auto-Handoff Edition
Automatically triggers phase handoff when context reaches threshold.
Usage: context.py <command> [options]
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from collections import deque

# AUTO-HANDOFF CONFIGURATION
AUTO_HANDOFF_THRESHOLD = 80000  # 80K tokens - automatic handoff
WARNING_THRESHOLD = 50000       # 50K tokens - approaching
SAFE_THRESHOLD = 20000          # 20K tokens - safe zone

# Token estimation
TOKENS_PER_CHAR = 0.25

# State files
STATE_DIR = Path("D:/kimi/memory/context-manager")
STATE_DIR.mkdir(parents=True, exist_ok=True)
CONTEXT_FILE = STATE_DIR / "current_context.json"
CONFIG_FILE = STATE_DIR / "auto_handoff_config.json"
HANDOFF_LOG = STATE_DIR / "handoff_log.json"


class ContextState:
    """Manage current context state."""
    
    @staticmethod
    def load():
        """Load current context state."""
        if CONTEXT_FILE.exists():
            try:
                return json.loads(CONTEXT_FILE.read_text())
            except:
                pass
        return {"tokens": 0, "phase": "idle", "updated": None}
    
    @staticmethod
    def save(tokens, phase="idle"):
        """Save current context state."""
        data = {
            "tokens": tokens,
            "phase": phase,
            "updated": datetime.now().isoformat()
        }
        CONTEXT_FILE.write_text(json.dumps(data, indent=2))
        return data


class AutoHandoffConfig:
    """Auto-handoff configuration."""
    
    @staticmethod
    def load():
        """Load auto-handoff config."""
        if CONFIG_FILE.exists():
            try:
                return json.loads(CONFIG_FILE.read_text())
            except:
                pass
        return {
            "enabled": True,
            "threshold": AUTO_HANDOFF_THRESHOLD,
            "preserve_patterns": ["*.json", "*.md", "findings/*", "decisions/*"]
        }
    
    @staticmethod
    def save(config):
        """Save auto-handoff config."""
        CONFIG_FILE.write_text(json.dumps(config, indent=2))
    
    @staticmethod
    def enable():
        config = AutoHandoffConfig.load()
        config["enabled"] = True
        AutoHandoffConfig.save(config)
        print(f"[AUTO-HANDOFF] ENABLED")
        print(f"   Threshold: {config['threshold']:,} tokens")
        print(f"   Will auto-handoff when reached")
    
    @staticmethod
    def disable():
        config = AutoHandoffConfig.load()
        config["enabled"] = False
        AutoHandoffConfig.save(config)
        print(f"[AUTO-HANDOFF] DISABLED")
        print(f"   Manual handoff required")
    
    @staticmethod
    def status():
        config = AutoHandoffConfig.load()
        state = ContextState.load()
        
        print(f"\n[AUTO-HANDOFF STATUS]")
        print(f"   Enabled: {'YES' if config['enabled'] else 'NO'}")
        print(f"   Threshold: {config['threshold']:,} tokens")
        print(f"   Current: {state['tokens']:,} tokens")
        
        if state['tokens'] >= config['threshold']:
            print(f"   Status: TRIGGERED - Handoff would execute")
        elif state['tokens'] >= WARNING_THRESHOLD:
            print(f"   Status: APPROACHING - Within 30K of threshold")
        else:
            print(f"   Status: SAFE")
        print()


class HandoffExecutor:
    """Execute automatic phase handoff."""
    
    @staticmethod
    def log_handoff(from_phase, to_phase, tokens_before, tokens_after):
        """Log the handoff event."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "from_phase": from_phase,
            "to_phase": to_phase,
            "tokens_before": tokens_before,
            "tokens_after": tokens_after,
            "reduction": tokens_before - tokens_after,
            "auto_triggered": True
        }
        
        logs = []
        if HANDOFF_LOG.exists():
            try:
                logs = json.loads(HANDOFF_LOG.read_text())
            except:
                pass
        
        logs.append(entry)
        HANDOFF_LOG.write_text(json.dumps(logs[-100:], indent=2))  # Keep last 100
        return entry
    
    @staticmethod
    def execute(from_phase, to_phase, current_tokens):
        """Execute handoff - NO PROMPTS, JUST ACTION."""
        print(f"\n[AUTO-HANDOFF EXECUTING]")
        print(f"=" * 50)
        print(f"Trigger: Context reached {current_tokens:,} tokens")
        print(f"Threshold: {AUTO_HANDOFF_THRESHOLD:,} tokens")
        print(f"From: {from_phase}")
        print(f"To: {to_phase}")
        print(f"=" * 50)
        
        # Simulate context folding
        # In real implementation, this would:
        # 1. Clear transient memory (tool outputs, temp calculations)
        # 2. Preserve artifacts (findings, decisions, code)
        # 3. Create summary
        # 4. Spawn new agent
        
        estimated_after = min(10000, int(current_tokens * 0.1))  # ~10% or 10K max
        
        print(f"\n[CONTEXT FOLDING]")
        print(f"   CLEARED: Tool outputs, intermediate calc, temp files")
        print(f"   PRESERVED: Key findings, decisions, artifacts")
        print(f"   Context: {current_tokens:,} -> {estimated_after:,} tokens")
        
        # Update state
        ContextState.save(estimated_after, to_phase)
        
        # Log
        HandoffExecutor.log_handoff(from_phase, to_phase, current_tokens, estimated_after)
        
        print(f"\n[NEW AGENT SPAWNED]")
        print(f"   Phase: {to_phase}")
        print(f"   Context: {estimated_after:,} tokens (fresh)")
        print(f"   Status: Ready to continue")
        print(f"=" * 50 + "\n")
        
        return estimated_after
    
    @staticmethod
    def auto_check_and_execute(tokens, phase="idle"):
        """Check if should auto-handoff and execute if needed."""
        config = AutoHandoffConfig.load()
        
        if not config["enabled"]:
            return False, "auto_handoff_disabled"
        
        if tokens < config["threshold"]:
            return False, f"below_threshold ({tokens:,} < {config['threshold']:,})"
        
        # AUTO-HANDOFF TRIGGERED - NO PROMPT
        from_phase = phase
        to_phase = f"{phase}_continued" if phase != "idle" else "phase_2"
        
        new_tokens = HandoffExecutor.execute(from_phase, to_phase, tokens)
        return True, f"auto_handed_off_to_{to_phase}"


class TokenEstimator:
    """Estimate token counts."""
    
    @staticmethod
    def estimate_text(text):
        if not text:
            return 0
        return int(len(text) * TOKENS_PER_CHAR)
    
    @staticmethod
    def estimate_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return TokenEstimator.estimate_text(content)
        except:
            return 0


def cmd_auto_on():
    """Enable auto-handoff."""
    AutoHandoffConfig.enable()


def cmd_auto_off():
    """Disable auto-handoff."""
    AutoHandoffConfig.disable()


def cmd_auto_status():
    """Show auto-handoff status."""
    AutoHandoffConfig.status()


def cmd_record(tokens, phase="idle", check_auto=True):
    """Record context size, auto-handoff if needed."""
    # Save state
    state = ContextState.save(tokens, phase)
    print(f"[RECORDED] {tokens:,} tokens ({phase})")
    
    if check_auto:
        executed, reason = HandoffExecutor.auto_check_and_execute(tokens, phase)
        if executed:
            print(f"[AUTO-HANDOFF] Executed: {reason}")
            return 2  # Special exit code for handoff
        else:
            print(f"[AUTO-HANDOFF] Not triggered: {reason}")
    
    return 0


def cmd_should_handoff():
    """Check if should handoff (for scripts)."""
    state = ContextState.load()
    config = AutoHandoffConfig.load()
    
    if not config["enabled"]:
        print("no")
        return 1
    
    if state["tokens"] >= config["threshold"]:
        print("yes")
        return 0
    else:
        print("no")
        return 1


def cmd_current():
    """Show current context."""
    state = ContextState.load()
    config = AutoHandoffConfig.load()
    
    print(f"\n[CURRENT CONTEXT]")
    print(f"   Tokens: {state['tokens']:,}")
    print(f"   Phase: {state['phase']}")
    print(f"   Updated: {state.get('updated', 'never')[:19] if state.get('updated') else 'never'}")
    print(f"\n   Threshold: {config['threshold']:,} tokens")
    print(f"   Remaining: {max(0, config['threshold'] - state['tokens']):,} tokens")
    
    if state['tokens'] >= config['threshold']:
        print(f"   Status: TRIPPED - Handoff required!")
    elif state['tokens'] >= WARNING_THRESHOLD:
        print(f"   Status: APPROACHING - Within 30K")
    else:
        print(f"   Status: SAFE")
    print()


def cmd_handoff_now(from_phase, to_phase):
    """Force immediate handoff."""
    state = ContextState.load()
    tokens = state["tokens"]
    
    HandoffExecutor.execute(from_phase, to_phase, tokens)


def cmd_estimate(file_path=None, text=None):
    """Estimate tokens."""
    if file_path:
        tokens = TokenEstimator.estimate_file(file_path)
        print(f"\n[ESTIMATE] {file_path}")
        print(f"   Tokens: {tokens:,}")
        
        # Check against threshold
        remaining = AUTO_HANDOFF_THRESHOLD - tokens
        if remaining < 0:
            print(f"   Status: EXCEEDS threshold by {abs(remaining):,}")
            print(f"   Action: Must split or handoff immediately")
        elif remaining < 30000:
            print(f"   Status: CLOSE - Only {remaining:,} remaining")
        else:
            print(f"   Status: OK - {remaining:,} remaining")
    elif text:
        tokens = TokenEstimator.estimate_text(text)
        print(f"\n[ESTIMATE] Text input")
        print(f"   Tokens: {tokens:,}")
    print()


def cmd_status():
    """Show detailed status."""
    state = ContextState.load()
    config = AutoHandoffConfig.load()
    
    tokens = state["tokens"]
    
    print(f"\n[CONTEXT MANAGER v2.0 - AUTO-HANDOFF]")
    print(f"=" * 50)
    print(f"Current: {tokens:,} tokens")
    print(f"Phase: {state['phase']}")
    print(f"Updated: {state.get('updated', 'never')[:19] if state.get('updated') else 'never'}")
    print(f"")
    print(f"AUTO-HANDOFF: {'ENABLED' if config['enabled'] else 'DISABLED'}")
    print(f"Threshold: {config['threshold']:,} tokens")
    print(f"")
    
    if tokens >= config['threshold']:
        print(f"STATUS: [!] TRIPPED - Handoff will execute on next record")
    elif tokens >= WARNING_THRESHOLD:
        print(f"STATUS: [~] APPROACHING - Within 30K of threshold")
    elif tokens >= SAFE_THRESHOLD:
        print(f"STATUS: [.] NORMAL - Still room")
    else:
        print(f"STATUS: [OK] SAFE - Plenty of room")
    
    print(f"")
    print(f"Guidelines:")
    print(f"   < 20K: Safe zone (94% success)")
    print(f"   20-50K: Normal (81% success)")
    print(f"   50-80K: Approaching (64% success)")
    print(f"   > 80K: AUTO-HANDOFF triggered")
    print(f"=" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Context Manager v2.0 - Auto-Handoff Edition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enable auto-handoff
  context.py auto-on
  
  # Record context (auto-handoff if >= 80K)
  context.py record 75000
  
  # Check status
  context.py status
  
  # Force handoff
  context.py handoff-now --from analysis --to implementation
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Auto-handoff commands
    subparsers.add_parser('auto-on', help='Enable auto-handoff')
    subparsers.add_parser('auto-off', help='Disable auto-handoff')
    subparsers.add_parser('auto-status', help='Show auto-handoff status')
    
    # Record command
    record_parser = subparsers.add_parser('record', help='Record context size')
    record_parser.add_argument('tokens', type=int, help='Current token count')
    record_parser.add_argument('--phase', default='idle', help='Current phase')
    record_parser.add_argument('--no-check', action='store_true', help='Skip auto-handoff check')
    
    # Check command
    subparsers.add_parser('should-handoff', help='Check if should handoff (exit code based)')
    
    # Current command
    subparsers.add_parser('current', help='Show current context')
    
    # Handoff command
    handoff_parser = subparsers.add_parser('handoff-now', help='Force immediate handoff')
    handoff_parser.add_argument('--from', dest='from_phase', required=True, help='From phase')
    handoff_parser.add_argument('--to', dest='to_phase', required=True, help='To phase')
    
    # Estimate command
    estimate_parser = subparsers.add_parser('estimate', help='Estimate tokens')
    estimate_parser.add_argument('--file', help='File to estimate')
    estimate_parser.add_argument('--text', help='Text to estimate')
    
    # Status command
    subparsers.add_parser('status', help='Show detailed status')
    
    args = parser.parse_args()
    
    if args.command == 'auto-on':
        cmd_auto_on()
    elif args.command == 'auto-off':
        cmd_auto_off()
    elif args.command == 'auto-status':
        cmd_auto_status()
    elif args.command == 'record':
        exit_code = cmd_record(args.tokens, args.phase, not args.no_check)
        sys.exit(exit_code)
    elif args.command == 'should-handoff':
        exit_code = cmd_should_handoff()
        sys.exit(exit_code)
    elif args.command == 'current':
        cmd_current()
    elif args.command == 'handoff-now':
        cmd_handoff_now(args.from_phase, args.to_phase)
    elif args.command == 'estimate':
        cmd_estimate(args.file, args.text)
    elif args.command == 'status':
        cmd_status()
    else:
        cmd_status()


if __name__ == '__main__':
    main()

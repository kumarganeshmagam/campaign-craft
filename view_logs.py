#!/usr/bin/env python3
"""
Log Viewer for CampaignCraft
View and monitor log files in real-time
"""

import sys
from pathlib import Path
from datetime import datetime
import time

PROJECT_ROOT = Path(__file__).parent
LOG_DIR = PROJECT_ROOT / "logs"

def print_colored(text, color="white"):
    """Print colored text"""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "end": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['end']}")

def view_log_file(filename):
    """View a log file"""
    filepath = LOG_DIR / filename
    
    if not filepath.exists():
        print_colored(f"✗ Log file not found: {filepath}", "red")
        return False
    
    print_colored(f"\n{'='*70}", "cyan")
    print_colored(f"Log File: {filename}", "cyan")
    print_colored(f"{'='*70}\n", "cyan")
    
    try:
        with open(filepath, "r") as f:
            content = f.read()
            
            if not content:
                print_colored("(Empty log file)", "yellow")
            else:
                print(content)
        
        return True
    except Exception as e:
        print_colored(f"✗ Error reading log: {e}", "red")
        return False

def tail_log_file(filename, lines=20):
    """Show last N lines of a log file"""
    filepath = LOG_DIR / filename
    
    if not filepath.exists():
        print_colored(f"✗ Log file not found: {filepath}", "red")
        return False
    
    print_colored(f"\n{'='*70}", "cyan")
    print_colored(f"Last {lines} lines of: {filename}", "cyan")
    print_colored(f"{'='*70}\n", "cyan")
    
    try:
        with open(filepath, "r") as f:
            content = f.readlines()
            
        if not content:
            print_colored("(Empty log file)", "yellow")
        else:
            for line in content[-lines:]:
                print(line, end="")
        
        return True
    except Exception as e:
        print_colored(f"✗ Error reading log: {e}", "red")
        return False

def list_logs():
    """List all available log files"""
    if not LOG_DIR.exists():
        print_colored(f"✗ Log directory not found: {LOG_DIR}", "red")
        return
    
    logs = list(LOG_DIR.glob("*.log"))
    
    if not logs:
        print_colored("No log files found", "yellow")
        return
    
    print_colored(f"\n{'='*70}", "cyan")
    print_colored("Available Log Files:", "cyan")
    print_colored(f"{'='*70}\n", "cyan")
    
    for i, log in enumerate(sorted(logs), 1):
        size = log.stat().st_size
        size_mb = size / (1024*1024)
        mod_time = datetime.fromtimestamp(log.stat().st_mtime)
        
        print(f"{i}. {log.name}")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

def menu():
    """Interactive menu"""
    while True:
        print_colored("\n" + "="*70, "cyan")
        print_colored("CampaignCraft Log Viewer", "cyan")
        print_colored("="*70, "cyan")
        
        print("\nOptions:")
        print("1. View Startup Log")
        print("2. View Backend Log")
        print("3. View Frontend Log")
        print("4. View Test Results Log")
        print("5. View Errors Log")
        print("6. Tail Startup Log (last 20 lines)")
        print("7. Tail Backend Log (last 20 lines)")
        print("8. Tail Test Results (last 20 lines)")
        print("9. List All Logs")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-9): ").strip()
        
        if choice == "0":
            print_colored("\nGoodbye!", "green")
            break
        elif choice == "1":
            view_log_file("startup.log")
        elif choice == "2":
            view_log_file("backend_startup.log")
        elif choice == "3":
            view_log_file("frontend_startup.log")
        elif choice == "4":
            view_log_file("test_results.log")
        elif choice == "5":
            view_log_file("errors.log")
        elif choice == "6":
            tail_log_file("startup.log", 20)
        elif choice == "7":
            tail_log_file("backend_startup.log", 20)
        elif choice == "8":
            tail_log_file("test_results.log", 20)
        elif choice == "9":
            list_logs()
        else:
            print_colored("Invalid choice", "red")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1].lower()
        
        if command == "list":
            list_logs()
        elif command == "backend":
            view_log_file("backend_startup.log")
        elif command == "frontend":
            view_log_file("frontend_startup.log")
        elif command == "tests":
            view_log_file("test_results.log")
        elif command == "startup":
            view_log_file("startup.log")
        elif command == "errors":
            view_log_file("errors.log")
        else:
            print_colored(f"Unknown command: {command}", "red")
            print("Usage: python view_logs.py [backend|frontend|tests|startup|errors|list]")
    else:
        # Interactive mode
        menu()

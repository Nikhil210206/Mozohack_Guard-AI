import psutil
import os
import time
import subprocess
from datetime import datetime

log_file_path = "website_usage_logs.txt"

def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def is_safari_open():
    for proc in psutil.process_iter(['pid', 'name']):
        if 'Safari' in proc.info['name']:
            return True
    return False

def get_safari_tabs():
    script = '''
    tell application "Safari"
        set windowList to windows
        set tabList to {}
        repeat with aWindow in windowList
            set tabList to tabList & (get name of tabs of aWindow)
        end repeat
        return tabList
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split(", ")
        else:
            return []
    except Exception as e:
        print(f"Error running AppleScript: {e}")
        log_event(f"Error running AppleScript: {e}")
        return []

def run_website_monitor():
    print("Monitoring website usage... Press Ctrl+C to stop.")
    log_event("🚨 Guard AI Monitoring Started!")

    try:
        while True:
            if is_safari_open():
                print("Safari is open.")
                log_event("Safari is open.")
                open_tabs = get_safari_tabs()
                print(f"Open tabs in Safari: {open_tabs}")
                log_event(f"Open tabs in Safari: {open_tabs}")
            else:
                print("Safari is not open.")
                log_event("Safari is not open.")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Monitoring stopped.")
        log_event("Monitoring stopped.")

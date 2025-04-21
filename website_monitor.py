import psutil
import os
import time
import subprocess

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
        return []
def monitor_website_usage():
    print("Monitoring website usage... Press Ctrl+C to stop.")
    while True:
        if is_safari_open():
            print("Safari is open.")
            open_tabs = get_safari_tabs()
            print(f"Open tabs in Safari: {open_tabs}")
        else:
            print("Safari is not open.")
        time.sleep(10) 
if __name__ == "__main__":
    monitor_website_usage()
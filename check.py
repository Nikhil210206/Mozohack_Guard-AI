import psutil
import time
from datetime import datetime
import subprocess

# Logs file
log_file_path = "guardai_monitor_logs.txt"

# Apps to monitor (Notes app removed)
apps_to_check = ["Safari", "Google Chrome", "WhatsApp", "Photos", "Microsoft PowerPoint"]

# Sound file for alert (macOS built-in sound)
alert_sound = "/System/Library/Sounds/Glass.aiff"

# Interval
monitor_interval = 7  # seconds

# ------------------ Logging ------------------

def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def play_alert_sound():
    try:
        subprocess.run(["afplay", alert_sound])
    except Exception as e:
        print(f"Error playing sound: {e}")

# ------------------ Check if app has visible window ------------------

def is_app_window_open(app_name):
    try:
        script = f'''
        tell application "System Events"
            set isRunning to exists (process "{app_name}")
            if isRunning then
                set visibleWindows to visible of windows of process "{app_name}"
                if visibleWindows contains true then
                    return "open"
                else
                    return "background"
                end if
            else
                return "not running"
            end if
        end tell
        '''
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if result.returncode == 0:
            status = result.stdout.strip()
            return status == "open"
        else:
            return False
    except Exception as e:
        print(f"Error checking window for {app_name}: {e}")
        return False

# ------------------ Safari Tabs Monitoring ------------------

def is_safari_open():
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'Safari' in proc.info['name']:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
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
        error_message = f"Error running AppleScript: {e}"
        print(error_message)
        log_event(error_message)
        return []

def monitor_safari_tabs():
    if is_safari_open():
        safari_open_message = "Safari is open."
        print(safari_open_message)
        log_event(safari_open_message)

        open_tabs = get_safari_tabs()
        tab_message = f"Open tabs in Safari: {open_tabs}"
        print(tab_message)
        log_event(tab_message)
    else:
        safari_closed_message = "Safari is not open."
        print(safari_closed_message)
        log_event(safari_closed_message)

# ------------------ Main Monitoring ------------------

if __name__ == "__main__":
    print("🚨 GuardAI Monitoring Started... 🚨")
    log_event("GuardAI Monitoring Started.")

    try:
        while True:
            # Check Apps
            for app in apps_to_check:
                if is_app_window_open(app):
                    warning_message = f"[WARNING] {app} is actively open!"
                    print(warning_message)
                    log_event(warning_message)
                    play_alert_sound()

            # Check Safari websites
            monitor_safari_tabs()

            time.sleep(monitor_interval)
    except KeyboardInterrupt:
        print("\n🛑 GuardAI Monitoring Stopped by User.")
        log_event("GuardAI Monitoring Stopped by User.")

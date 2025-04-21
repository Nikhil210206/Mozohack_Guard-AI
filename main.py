import threading
import queue
import cv2
import mediapipe as mp
import numpy as np
import sounddevice as sd
import psutil
import os
import time
import subprocess
from datetime import datetime
import logging

# Logging setup
logging.basicConfig(filename="logs/guard_ai_logs.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# Lip Detection Constants
UPPER_LIP = [13, 14]
LOWER_LIP = [17, 18]
LIP_MOVEMENT_THRESHOLD = 2.5
SPEAKING_AUDIO_THRESHOLD = 0.01
BACKGROUND_NOISE_THRESHOLD = 0.08
AUDIO_DURATION = 0.3
FS = 44100

# Gaze Tracking Constants
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]
AWAY_THRESHOLD = 2
LOOK_AWAY_DURATION = 5

# Website Monitor Constants
log_file_path = "website_usage_logs.txt"

# Global Variables
audio_detected = False
background_noise_detected = False
frame_queue = queue.Queue()  # Queue to share frames between threads

# Helper Functions
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

# Lip Detection
def get_lip_distance(landmarks, upper_lip_idx, lower_lip_idx, frame_w, frame_h):
    upper_lip_points = np.array([(landmarks[i].x * frame_w, landmarks[i].y * frame_h) for i in upper_lip_idx])
    lower_lip_points = np.array([(landmarks[i].x * frame_w, landmarks[i].y * frame_h) for i in lower_lip_idx])
    return np.linalg.norm(np.mean(upper_lip_points, axis=0) - np.mean(lower_lip_points, axis=0))

def audio_listener():
    global audio_detected, background_noise_detected
    while True:
        try:
            audio_data = sd.rec(int(AUDIO_DURATION * FS), samplerate=FS, channels=1, dtype='float64')
            sd.wait()
            volume_norm = np.linalg.norm(audio_data) * 10
            audio_detected = volume_norm > SPEAKING_AUDIO_THRESHOLD
            background_noise_detected = volume_norm > BACKGROUND_NOISE_THRESHOLD
        except Exception as e:
            print("Audio Error:", e)
            continue

# Gaze Tracking
def get_iris_position(landmarks, eye_landmarks, iris_landmarks, frame):
    h, w, _ = frame.shape
    eye_points = np.array([(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in eye_landmarks])
    iris_points = np.array([(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in iris_landmarks])
    x_min, y_min = np.min(eye_points, axis=0)
    x_max, y_max = np.max(eye_points, axis=0)

    eye_region = frame[y_min:y_max, x_min:x_max]
    gray_eye = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
    _, threshold_eye = cv2.threshold(gray_eye, 50, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(threshold_eye, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        contour = max(contours, key=cv2.contourArea)
        (x, y, w_eye, h_eye) = cv2.boundingRect(contour)
        cx = x + w_eye // 2
        cy = y + h_eye // 2
        if cx < eye_region.shape[1] // 3:
            return "Looking Left"
        elif cx > 2 * eye_region.shape[1] // 3:
            return "Looking Right"
        elif cy < eye_region.shape[0] // 3:
            return "Looking Up"
        elif cy > 2 * eye_region.shape[0] // 3:
            return "Looking Down"
        else:
            return "Looking Center"
    return "Looking Center"

# Combined Lip Detection and Gaze Tracking
def run_combined_detection():
    print("[Combined Detection] Started")
    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
    threading.Thread(target=audio_listener, daemon=True).start()
    cap = cv2.VideoCapture(0)
    previous_distance = 0
    look_away_start = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb_frame)

        status = "Not Speaking"
        direction = "No face detected"
        warning = ""

        if result.multi_face_landmarks:
            for landmarks in result.multi_face_landmarks:
                # Lip Detection
                distance = get_lip_distance(landmarks.landmark, UPPER_LIP, LOWER_LIP, w, h)
                lip_moving = abs(distance - previous_distance) > LIP_MOVEMENT_THRESHOLD
                previous_distance = distance
                if lip_moving and audio_detected:
                    status = "Speaking"
                elif background_noise_detected and not lip_moving:
                    status = "Background Noise Detected"
                else:
                    status = "Not Speaking"

                # Gaze Tracking
                left_eye_direction = get_iris_position(landmarks.landmark, LEFT_EYE, LEFT_IRIS, frame)
                right_eye_direction = get_iris_position(landmarks.landmark, RIGHT_EYE, RIGHT_IRIS, frame)
                direction = left_eye_direction if left_eye_direction == right_eye_direction else "Looking Away"

        # Handle "Looking Away" warning
        if direction != "Looking Center":
            if look_away_start is None:
                look_away_start = time.time()
                logging.info("User started looking away.")
            elif time.time() - look_away_start > LOOK_AWAY_DURATION:
                warning = "⚠ Please focus on screen!"
                logging.warning("User has been looking away for more than 5 seconds.")
        else:
            if look_away_start is not None:
                logging.info(f"User refocused after {time.time() - look_away_start:.2f} seconds of looking away.")
            look_away_start = None

        # Add text to the frame
        cv2.putText(frame, f"Lip Status: {status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Gaze Direction: {direction}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        if warning:
            cv2.putText(frame, warning, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Add the frame to the queue
        if not frame_queue.full():
            frame_queue.put(frame)

    cap.release()

# Website Monitor
def run_website_monitor():
    print("[Website Monitor] Started")
    log_event("🚨 Guard AI Monitoring Started!")

    while True:
        if is_safari_open():
            log_event("Safari is open.")
            open_tabs = get_safari_tabs()
            log_event(f"Open tabs in Safari: {open_tabs}")
            print(f"Safari is open. Open tabs: {open_tabs}")
        else:
            log_event("Safari is not open.")
            print("Safari is not open.")
        time.sleep(5)

# Main Function
if __name__ == "__main__":
    combined_thread = threading.Thread(target=run_combined_detection, daemon=True)
    website_thread = threading.Thread(target=run_website_monitor, daemon=True)

    combined_thread.start()
    website_thread.start()

    print("All features are running. Press Ctrl+C to stop.")
    try:
        while True:
            if not frame_queue.empty():
                frame = frame_queue.get()
                cv2.imshow("Combined Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Exiting Guard-AI.")
    finally:
        cv2.destroyAllWindows()
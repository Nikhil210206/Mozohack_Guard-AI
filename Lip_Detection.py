import cv2
import mediapipe as mp
import numpy as np
import sounddevice as sd
import threading
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
UPPER_LIP = [13, 14]
LOWER_LIP = [17, 18]
LIP_MOVEMENT_THRESHOLD = 2.5  
SPEAKING_AUDIO_THRESHOLD = 0.01  
BACKGROUND_NOISE_THRESHOLD = 0.08  
AUDIO_DURATION = 0.3  
FS = 44100  

audio_detected = False
background_noise_detected = False

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

audio_thread = threading.Thread(target=audio_listener, daemon=True)
audio_thread.start()

cap = cv2.VideoCapture(0)
previous_distance = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb_frame)

    status = "Not Speaking"

    if result.multi_face_landmarks:
        for landmarks in result.multi_face_landmarks:
            distance = get_lip_distance(landmarks.landmark, UPPER_LIP, LOWER_LIP, w, h)
            lip_moving = abs(distance - previous_distance) > LIP_MOVEMENT_THRESHOLD
            previous_distance = distance
            if lip_moving and audio_detected:
                status = "Speaking"
            elif background_noise_detected and not lip_moving:
                status = "Background Noise Detected"
            else:
                status = "Not Speaking"
            for idx in UPPER_LIP + LOWER_LIP:
                x = int(landmarks.landmark[idx].x * w)
                y = int(landmarks.landmark[idx].y * h)
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

    color = (0, 255, 0) if status == "Speaking" else (0, 0, 255) if status == "Not Speaking" else (255, 0, 0)
    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.imshow("Lip + Audio Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

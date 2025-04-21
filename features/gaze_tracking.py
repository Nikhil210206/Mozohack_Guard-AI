import cv2
import mediapipe as mp
import numpy as np
import time
import logging

logging.basicConfig(filename="logs/gaze_tracking_logs.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

mp_face_mesh = mp.solutions.face_mesh
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

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

def run_gaze_tracking():
    print("[Gaze Tracking] Started")
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
    cap = cv2.VideoCapture(0)
    look_away_start = None
    AWAY_THRESHOLD = 2
    LOOK_AWAY_DURATION = 5

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        direction = "No face detected"
        warning = ""

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                left_eye_direction = get_iris_position(face_landmarks.landmark, LEFT_EYE, LEFT_IRIS, frame)
                right_eye_direction = get_iris_position(face_landmarks.landmark, RIGHT_EYE, RIGHT_IRIS, frame)
                direction = left_eye_direction if left_eye_direction == right_eye_direction else "Looking away !!"
                for idx in LEFT_EYE + RIGHT_EYE + LEFT_IRIS + RIGHT_IRIS:
                    x = int(face_landmarks.landmark[idx].x * w)
                    y = int(face_landmarks.landmark[idx].y * h)
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

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

        cv2.putText(frame, f"{direction}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        if warning:
            cv2.putText(frame, warning, (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        cv2.imshow("Gaze Tracker - Eye Movement", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

import cv2
import mediapipe as mp
import numpy as np
from transparent import *

# Load transparent assets
jungle = cv2.imread("assets/jungle_bg.png", cv2.IMREAD_UNCHANGED)
chad = cv2.imread("assets/chad.png", cv2.IMREAD_UNCHANGED)

# Mediapipe Pose setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)

# Game state
frame_counter = 0
score = 0
chad_y_ratio = 0.7  # relative Y position (0.0 = top, 1.0 = bottom)


# Check if both arms are overhead
def is_overhead_arms(landmarks):
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
    return left_wrist.y < nose.y and right_wrist.y < nose.y

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_h, frame_w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb)

    # Resize assets dynamically
    chad_size = int(min(frame_w, frame_h) * 0.12)
    chad_resized = cv2.resize(chad, (chad_size, chad_size))

    jungle_overlay_resized = cv2.resize(jungle, (frame_w,int(frame_h*0.05) ))

    # Update Chad's position on arm raise
    if result.pose_landmarks:
        landmarks = result.pose_landmarks.landmark
        if is_overhead_arms(landmarks):
            frame_counter += 1
            if frame_counter % 10 == 0:
                chad_y_ratio = max(0.05, chad_y_ratio - 0.02)  # move up
                score += 1
        else:
            frame_counter = 0

    # Convert ratio to pixels
    chad_x = int((frame_w - chad_size) / 2)
    chad_y = int(frame_h * chad_y_ratio)

    # Step 1: Webcam base
    display = frame.copy()

    # Step 2: Add Chad
    display = overlay_transparent(display, chad_resized, chad_x, chad_y)

    # Step 3: Jungle vines overlay
    display = overlay_transparent(display, jungle_overlay_resized,)

    # Step 4: Score + text
    font_scale = frame_w / 1000
    thickness = 2

    cv2.putText(display, f"Climb Score: {score}", (int(0.05 * frame_w), int(0.08 * frame_h)),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness + 1)
    cv2.putText(display, "Raise Arms Overhead to Help Chad Climb!",
                (int(0.05 * frame_w), int(0.95 * frame_h)),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)

    # Display game frame
    cv2.imshow("Chad's Jungle Climb", display)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

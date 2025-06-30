import cv2
import mediapipe as mp
import numpy as np
import random
import time
from transparent import overlay_transparent

# Load assets
coconut_img = cv2.imread("assets/coconut.png", cv2.IMREAD_UNCHANGED)
chad_img = cv2.imread("assets/chad.png", cv2.IMREAD_UNCHANGED)

# Mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Game variables
coconut = {"x": random.randint(100, 500), "y": 0, "speed": 10}
score = 0
prev_wrist = {"Left": None, "Right": None}

# Camera
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame_h, frame_w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    display = frame.copy()

    # Move and draw single coconut
    coconut_resized = cv2.resize(coconut_img, (100, 100))
    coconut["y"] += coconut["speed"]
    if 0 <= coconut["x"] <= frame_w - 100 and 0 <= coconut["y"] <= frame_h - 100:
        display = overlay_transparent(display, coconut_resized, coconut["x"], coconut["y"])
    if coconut["y"] > frame_h - 100:
        coconut["y"] = 0
        coconut["x"] = random.randint(100, frame_w - 100)
        coconut["speed"] = random.randint(8, 12)

    # Hand tracking + draw landmarks
    if results.multi_hand_landmarks and results.multi_handedness:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            handedness = results.multi_handedness[idx].classification[0].label  # 'Left' or 'Right'
            wrist_lm = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            wrist_vis = wrist_lm.visibility if hasattr(wrist_lm, 'visibility') else 1.0

            if wrist_vis < 0.5:
                continue  # skip low visibility

            wrist_x = int(wrist_lm.x * frame_w)
            wrist_y = int(wrist_lm.y * frame_h)

            # Draw landmarks on original frame
            mp_drawing.draw_landmarks(
                display,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )

            # Punch detection
            if prev_wrist[handedness] is not None:
                dx = wrist_x - prev_wrist[handedness][0]
                dy = wrist_y - prev_wrist[handedness][1]
                speed = np.sqrt(dx**2 + dy**2)

                if speed > 20:
                    cx_center = coconut["x"] + 50
                    cy_center = coconut["y"] + 50
                    if abs(wrist_x - cx_center) < 60 and abs(wrist_y - cy_center) < 60:
                        score += 1
                        coconut["y"] = 0
                        coconut["x"] = random.randint(100, frame_w - 100)
                        coconut["speed"] = random.randint(8, 12)

            prev_wrist[handedness] = (wrist_x, wrist_y)

    # Draw Chad bottom-right
    chad = cv2.resize(chad_img, (int(frame_w * 0.2), int(frame_h * 0.4)))
    display = overlay_transparent(display, chad, frame_w - chad.shape[1], frame_h - chad.shape[0])

    # Display score
    cv2.putText(display, f"Score: {score}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 255, 255), 3)

    # Flip the final frame for webcam-mirrored feel
    display = cv2.flip(display, 1)

    # Show window
    cv2.imshow("Jungle Punch: Chad's Coconut Smash", display)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

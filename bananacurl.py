import cv2
import mediapipe as mp
import numpy as np
import math

# Load banana dumbbell PNG (must have alpha channel)
banana = cv2.imread("assets/banana.png", cv2.IMREAD_UNCHANGED)

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)

def calculate_angle(a, b, c):
    a = np.array(a)  # Shoulder
    b = np.array(b)  # Elbow
    c = np.array(c)  # Wrist
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return angle if angle <= 180 else 360 - angle

def overlay_transparent(background, overlay, x, y, overlay_size=None):
    if overlay_size:
        overlay = cv2.resize(overlay, overlay_size)
    h, w, _ = overlay.shape
    rows, cols, _ = background.shape
    if x >= cols or y >= rows: return background
    if x + w > cols: w = cols - x; overlay = overlay[:, :w]
    if y + h > rows: h = rows - y; overlay = overlay[:h]
    if overlay.shape[2] < 4: return background
    overlay_img = overlay[:, :, :3]
    mask = overlay[:, :, 3:] / 255.0
    background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_img
    return background

counter = 0
stage = None
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # Get arm coordinates
        shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

        # Convert wrist to pixel coords
        wrist_px = tuple(np.multiply(wrist, [image.shape[1], image.shape[0]]).astype(int))

        # Overlay banana PNG on wrist
        banana_size = (80, 80)  # Resize as needed
        image = overlay_transparent(image, banana, wrist_px[0]-40, wrist_px[1]-40, banana_size)

        # Angle + counter logic
        angle = calculate_angle(shoulder, elbow, wrist)

        cv2.putText(image, str(int(angle)),
                    tuple(np.multiply(elbow, [image.shape[1], image.shape[0]]).astype(int)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        if angle > 160: stage = "down"
        if angle < 45 and stage == "down":
            stage = "up"
            counter += 1

    # Display counter
    cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)
    cv2.putText(image, 'REPS', (15,12), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
    cv2.putText(image, str(counter), 
                (10,60), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)

    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.imshow('🍌 Banana Curl Brawl - Chad', image)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

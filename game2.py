import time
import cv2
import mediapipe as mp
from transparent import overlay_transparent

# --- MediaPipe setup ---
mp_drawing = mp.solutions.drawing_utils
mp_hands   = mp.solutions.hands
hands      = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# --- Load and prepare overlays ---
ducky = cv2.imread("assets/ducky.png", cv2.IMREAD_UNCHANGED)
path  = cv2.imread("assets/path.png", cv2.IMREAD_UNCHANGED)
basket= cv2.imread("assets/basket.png", cv2.IMREAD_UNCHANGED)

ducky   = cv2.flip(cv2.resize(ducky,   (400, 400)), 1)
path    = cv2.resize(path,  (2400, 500))
basket  = cv2.resize(basket,(200, 200))

ducky_h, ducky_w = ducky.shape[:2]

# --- Game state ---
ducky_x         = 0
score           = 0
last_score_time = 0
score_delay     = 1.0  # seconds between scoring

# --- Fist detection helper ---
def is_fist(landmarks):
    # landmarks indices for fingertips: thumb=4, index=8, middle=12, ring=16, pinky=20
    tips = [4, 8, 12, 16, 20]
    folded = sum(1 for i in tips[1:]
                 if landmarks[i].y > landmarks[i-2].y)
    return folded >= 4

# --- Start webcam ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Mirror & process
    frame = cv2.flip(frame, 1)
    frame_h, frame_w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Draw path & basket
    frame = overlay_transparent(frame, path, 0, frame_h - path.shape[0])
    bx = frame_w - basket.shape[1]
    by = frame_h - basket.shape[0] - 100
    frame = overlay_transparent(frame, basket, bx, by)

    # Draw ducky at current x
    y_ducky = frame_h - ducky_h - 110
    frame = overlay_transparent(frame, ducky, ducky_x, y_ducky)

    # Process hand & scoring
    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        if is_fist(hand.landmark):
            now = time.time()
            if now - last_score_time > score_delay:
                # move ducky
                if ducky_x + ducky_w + 10 < frame_w:
                    ducky_x += 75
                score += 10
                last_score_time = now

    # Display score
    cv2.putText(frame, f"Score: {score}",
                (20, 50), cv2.FONT_HERSHEY_SIMPLEX,
                1.2, (255, 255, 255), 2)

    # Check for victory (duck in basket)
    if ducky_x + ducky_w >= bx:
        cv2.putText(frame, "You Passed :)",
                    (int(frame_w/2 - 200), int(frame_h/2)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    # Show frame
    cv2.imshow("Fist Game", frame)
    if cv2.waitKey(25) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()


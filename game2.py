import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

def isfist(landmarks):
    id = [4, 8, 12, 16, 20]
    fold = 0
    for i in id[1:]:  # skipping thumb
        if landmarks[i].y > landmarks[i - 2].y:
            fold += 1
    return fold >= 4

cap = cv2.VideoCapture(0)

success, frame = cap.read()
if not success:
    print("Error in webcam")
    cap.release()
    exit()

while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for i in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, i, mp_hands.HAND_CONNECTIONS)

            if isfist(i.landmark):
                cv2.putText(frame, "YO (FIST DETECTED)", (50, 100), cv2.FONT_HERSHEY_SIMPLEX,
                            1.5, (0, 0, 255), 3)

    cv2.imshow("Fist game", frame)
    if cv2.waitKey(25) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

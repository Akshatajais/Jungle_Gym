import cv2
from egg_fall import EggManager
from transparent import *
from button import *

# Load overlay images with alpha channel
ducky = cv2.imread("assets/ducky.png", cv2.IMREAD_UNCHANGED)
path = cv2.imread("assets/path.png", cv2.IMREAD_UNCHANGED)
egg = cv2.imread("assets/egg.png", cv2.IMREAD_UNCHANGED)

# Resize overlays
ducky = cv2.resize(ducky, (400, 400))  
path = cv2.resize(path, (2400, 500))    
egg = cv2.resize(egg, (150, 150))


# Start webcam
cap = cv2.VideoCapture(0)

# Read first frame to get size
success, frame = cap.read()
if not success:
    print("Error: Could not read from camera.")
    cap.release()
    exit()

frame_h, frame_w = frame.shape[:2]

# Initialize EggManager AFTER getting frame size
egg_manager = EggManager(egg, frame_w, frame_h, num_eggs=3)

while True:
    success, frame = cap.read()
    if not success:
        break
    frame = cv2.flip(frame, 1)  # 1 means horizontal flip

    cv2.putText(frame, "Pinch your thumb and index finger to drag the egg", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 120, 255), 2)
    


    # Overlay ducky at bottom-right
    ducky_h, ducky_w = ducky.shape[:2]
    x_ducky = frame_w - ducky_w
    y_ducky = frame_h - ducky_h - 110
    frame = overlay_transparent(frame, ducky, x_ducky, y_ducky)

    # Update and draw eggs using your class
    egg_manager.update_eggs()
    frame = egg_manager.draw_eggs(frame, overlay_transparent)

    # Overlay path at bottom
    frame = overlay_transparent(frame, path, 0, frame_h - path.shape[0])
    cv2.imshow("Ducky", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

#https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker#models
#download in local folder
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import serial
import time


ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)

model_file = "hand_landmarker.task"

base_options = python.BaseOptions
hand_landmarker = vision.HandLandmarker
hand_options = vision.HandLandmarkerOptions
running_mode = vision.RunningMode

options = hand_options(
    base_options=base_options(model_asset_path=model_file),
    running_mode=running_mode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

detector = hand_landmarker.create_from_options(options)
def get_gesture(landmarks_list):
    if not landmarks_list:
        return None
    #numbers shown in mediapipe link
    lm = landmarks_list[0]   # first hand
    # thumbs up
    if (lm[4].y < lm[3].y < lm[2].y and  lm[8].y  > lm[6].y  and lm[12].y > lm[10].y and lm[16].y > lm[14].y and lm[20].y > lm[18].y):
        return "thumbs_up"

    # thumbs down
    if (lm[4].y > lm[3].y > lm[2].y and lm[8].y  > lm[6].y  and lm[12].y > lm[10].y and lm[16].y > lm[14].y and lm[20].y > lm[18].y):
        return "thumbs_down"

    # open palm
    if (lm[4].y < lm[3].y and lm[8].y  < lm[7].y  < lm[6].y  and lm[12].y < lm[11].y < lm[10].y and
        lm[16].y < lm[15].y < lm[14].y and
        lm[20].y < lm[19].y < lm[18].y):
        return "open_palm"

    return None
camera = cv2.VideoCapture(0)
last_gesture = None
last_send = time.time()
while camera.isOpened():
    ok, frame = camera.read()
    if not ok:
        break
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    now_ms = int(time.time() * 1000)
    result = detector.detect_for_video(mp_img, now_ms)
    text = "no gesture"
    if result.hand_landmarks:
        for hand_lm in result.hand_landmarks:
            for point in hand_lm:
                x = int(point.x * frame.shape[1])
                y = int(point.y * frame.shape[0])
                cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)
        gesture = get_gesture(result.hand_landmarks)
        if gesture:
            text = gesture.upper()
            now = time.time()
            if gesture != last_gesture and (now - last_send > 1.0):
                if gesture == "thumbs_up":
                    ser.write(b'1')
                elif gesture == "thumbs_down":
                    ser.write(b'2')
                elif gesture == "open_palm":
                    ser.write(b'3')
                print(f"sent: {gesture} → LED {1 if gesture=='thumbs_up' else 2 if gesture=='thumbs_down' else 3}")
                last_gesture = gesture
                last_send = now
    cv2.putText(frame, text, (30, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    cv2.imshow("q = quit", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
detector.close()
ser.close()

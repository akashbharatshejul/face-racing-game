import cv2
import mediapipe as mp
import time
import math

# -------------------------------
# CONFIG
# -------------------------------
EMOTION_DURATION = 2
SMILE_THRESHOLD = 1.4
MOUTH_OPEN_THRESHOLD = 1.8
EYEBROW_RAISE_THRESHOLD = 1.3

# -------------------------------
# INIT
# -------------------------------
mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(max_num_faces=1)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

baseline_width = None
baseline_mouth = None
baseline_eyebrow = None

emotion = "NORMAL"
emotion_timer = 0

def dist(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

print("Look neutral for 3 seconds to calibrate...")

calib_start = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        face = results.multi_face_landmarks[0]

        # ---------- LANDMARKS ----------
        left_corner = face.landmark[61]
        right_corner = face.landmark[291]

        upper_lip = face.landmark[13]
        lower_lip = face.landmark[14]

        eyebrow = face.landmark[159]
        eye_top = face.landmark[145]

        # ---------- MEASUREMENTS ----------
        mouth_width = dist(left_corner, right_corner)
        mouth_open = dist(upper_lip, lower_lip)
        eyebrow_height = dist(eyebrow, eye_top)

        # ---------- CALIBRATION ----------
        if baseline_width is None:
            if time.time() - calib_start > 3:
                baseline_width = mouth_width
                baseline_mouth = mouth_open
                baseline_eyebrow = eyebrow_height
                print("Calibration Done.")
        else:
            smile_ratio = mouth_width / baseline_width
            mouth_ratio = mouth_open / baseline_mouth
            eyebrow_ratio = eyebrow_height / baseline_eyebrow

            # ---------- SURPRISE ----------
            if mouth_ratio > MOUTH_OPEN_THRESHOLD and eyebrow_ratio > EYEBROW_RAISE_THRESHOLD:
                emotion = "SURPRISE"
                emotion_timer = time.time()

            # ---------- SMILE ----------
            elif smile_ratio > SMILE_THRESHOLD:
                emotion = "SMILE"
                emotion_timer = time.time()

    # ---------- TIMER ----------
    if emotion != "NORMAL":
        if time.time() - emotion_timer > EMOTION_DURATION:
            emotion = "NORMAL"

    # ---------- DISPLAY ----------
    color = (255,255,255)

    if emotion == "SMILE":
        color = (0,255,0)
    elif emotion == "SURPRISE":
        color = (0,200,255)

    cv2.putText(frame, f"Emotion: {emotion}",
                (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

    if baseline_width is None:
        cv2.putText(frame, "Calibrating...",
                    (20,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)

    cv2.imshow("Emotion Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
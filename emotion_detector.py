import time
import math

class EmotionDetector:

    def __init__(self):

        self.baseline_width = None
        self.baseline_mouth = None
        self.baseline_eyebrow = None

        self.width_hist = []
        self.mouth_hist = []
        self.brow_hist = []

        self.calib_start = time.time()
        self.calibrated = False

        self.emotion = "NORMAL"
        self.timer = 0

        self.detect_count = 0

        self.SMILE_THRESHOLD = 1.35
        self.MOUTH_THRESHOLD = 1.8
        self.EYEBROW_THRESHOLD = 1.2

        self.EMOTION_DURATION = 30

    def dist(self, p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def reset(self):

        self.baseline_width = None
        self.baseline_mouth = None
        self.baseline_eyebrow = None

        self.width_hist.clear()
        self.mouth_hist.clear()
        self.brow_hist.clear()

        self.calib_start = time.time()
        self.calibrated = False

        self.emotion = "NORMAL"
        self.timer = 0
        self.detect_count = 0

    def update(self, results):

        if not results or not results.multi_face_landmarks:
            return self.emotion

        face = results.multi_face_landmarks[0]

        left_corner = face.landmark[61]
        right_corner = face.landmark[291]
        upper_lip = face.landmark[13]
        lower_lip = face.landmark[14]
        eyebrow = face.landmark[159]
        eye_top = face.landmark[145]

        width = self.dist(left_corner, right_corner)
        mouth = self.dist(upper_lip, lower_lip)
        brow = self.dist(eyebrow, eye_top)

        # ---------- CALIBRATION ----------
        if not self.calibrated:

            self.width_hist.append(width)
            self.mouth_hist.append(mouth)
            self.brow_hist.append(brow)

            if time.time() - self.calib_start > 3:

                self.baseline_width = sum(self.width_hist) / len(self.width_hist)
                self.baseline_mouth = sum(self.mouth_hist) / len(self.mouth_hist)
                self.baseline_eyebrow = sum(self.brow_hist) / len(self.brow_hist)

                self.calibrated = True

            return "NORMAL"

        smile_ratio = width / self.baseline_width
        mouth_ratio = mouth / self.baseline_mouth
        brow_ratio = brow / self.baseline_eyebrow

        new_emotion = "NORMAL"

        if mouth_ratio > self.MOUTH_THRESHOLD and brow_ratio > self.EYEBROW_THRESHOLD:
            new_emotion = "SURPRISE"

        elif smile_ratio > self.SMILE_THRESHOLD:
            new_emotion = "SMILE"

        # ---------- STABLE DETECTION ----------
        if new_emotion != "NORMAL":
            self.detect_count += 1
        else:
            self.detect_count = 0

        if self.detect_count > 3:
            self.emotion = new_emotion
            self.timer = time.time()

        # ---------- TIMER ----------
        if self.emotion != "NORMAL":
            if time.time() - self.timer > self.EMOTION_DURATION:
                self.emotion = "NORMAL"

        return self.emotion
import mediapipe as mp
import statistics

class HeadTracker:

    def __init__(self):
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(max_num_faces=1)

        self.center_x = None
        self.calib = []
        self.nose_history = []
        self.last_results = None

    def process(self, rgb):
        self.last_results = self.face_mesh.process(rgb)

    def face_present(self):
        return self.last_results and self.last_results.multi_face_landmarks

    def update(self, width):

        direction = "CENTER"

        if not self.last_results or not self.last_results.multi_face_landmarks:
            return direction

        face = self.last_results.multi_face_landmarks[0]
        nose = int(face.landmark[1].x * width)

        # ---------- SMOOTHING ----------
        self.nose_history.append(nose)
        if len(self.nose_history) > 5:
            self.nose_history.pop(0)

        nose = int(statistics.mean(self.nose_history))

        # ---------- CALIBRATION ----------
        if self.center_x is None:
            self.calib.append(nose)

            if len(self.calib) > 20:
                self.center_x = int(statistics.median(self.calib))

        else:
            threshold = width * 0.06

            if nose < self.center_x - threshold:
                direction = "LEFT"

            elif nose > self.center_x + threshold:
                direction = "RIGHT"

        return direction
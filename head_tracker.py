import mediapipe as mp
import statistics

class HeadTracker:

    def __init__(self):
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(max_num_faces=1)

        self.center_x = None
        self.calib = []
        self.last_results = None   # ⭐ store results

    # ---------- PROCESS ONCE ----------
    def process(self, rgb):
        self.last_results = self.face_mesh.process(rgb)

    # ---------- FACE PRESENT ----------
    def face_present(self):
        return self.last_results and self.last_results.multi_face_landmarks

    # ---------- HEAD DIRECTION ----------
    def update(self, width):

        direction = "CENTER"

        if not self.last_results or not self.last_results.multi_face_landmarks:
            return direction

        face = self.last_results.multi_face_landmarks[0]
        nose = int(face.landmark[1].x * width)

        if self.center_x is None:
            self.calib.append(nose)
            if len(self.calib) > 20:
                self.center_x = int(statistics.median(self.calib))
        else:
            if nose < self.center_x - 40:
                direction = "LEFT"
            elif nose > self.center_x + 40:
                direction = "RIGHT"

        return direction
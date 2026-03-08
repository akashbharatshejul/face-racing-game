import mediapipe as mp

class MouthDetector:

    def __init__(self):
        self.hist = []
        self.baseline = None

    # 🔹 now receives FaceMesh results
    def update(self, results):

        if not results or not results.multi_face_landmarks:
            return False

        face = results.multi_face_landmarks[0]

        m_top = face.landmark[13]
        m_bottom = face.landmark[14]

        dist = abs(m_top.y - m_bottom.y)

        # ---------- BUILD BASELINE ----------
        self.hist.append(dist)

        if len(self.hist) > 30:
            self.hist.pop(0)

        self.baseline = sum(self.hist) / len(self.hist)

        # ---------- MOUTH OPEN ----------
        if self.baseline is None:
            return False

        return dist > self.baseline * 2.1
import mediapipe as mp
import math

mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(max_num_faces=1)

def dist(p1,p2):
    return math.hypot(p1.x-p2.x,p1.y-p2.y)

class BlinkDetector:

    def __init__(self):
        self.prev_x=None
        self.prev_y=None
        self.ear_hist=[]
        self.base_hist=[]
        self.frames_closed=0
        self.EAR_DROP=0.04

    def update(self, rgb):

        results=face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return False

        face=results.multi_face_landmarks[0]

        # HEAD MOVEMENT
        nose=face.landmark[1]
        head_moving=False

        if self.prev_x is not None:
            if abs(nose.x-self.prev_x)>0.01 or abs(nose.y-self.prev_y)>0.01:
                head_moving=True

        self.prev_x=nose.x
        self.prev_y=nose.y

        # BOTH EYES EAR
        l_top=face.landmark[159]
        l_bottom=face.landmark[145]
        l_left=face.landmark[33]
        l_right=face.landmark[133]

        r_top=face.landmark[386]
        r_bottom=face.landmark[374]
        r_left=face.landmark[362]
        r_right=face.landmark[263]

        left_ear=dist(l_top,l_bottom)/dist(l_left,l_right)
        right_ear=dist(r_top,r_bottom)/dist(r_left,r_right)

        ear=(left_ear+right_ear)/2

        self.ear_hist.append(ear)
        if len(self.ear_hist)>5:
            self.ear_hist.pop(0)

        ear_smooth=sum(self.ear_hist)/len(self.ear_hist)

        self.base_hist.append(ear_smooth)
        if len(self.base_hist)>30:
            self.base_hist.pop(0)

        baseline=sum(self.base_hist)/len(self.base_hist)

        blink=False

        if not head_moving:
            if ear_smooth < baseline-self.EAR_DROP:
                self.frames_closed+=1
            else:
                if self.frames_closed>=3:
                    blink=True
                self.frames_closed=0
        else:
            self.frames_closed=0

        return blink
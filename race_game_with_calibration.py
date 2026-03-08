import pygame
import sys
import random
import cv2
import mediapipe as mp
import time

# ---------- MediaPipe ----------
mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(max_num_faces=1)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# ---------- Pygame ----------
pygame.init()
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Face Controlled Racing")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 50)

# ---------- GAME VARIABLES ----------
player_w, player_h = 80, 120
speed = 7

center_x = None
calibration_data = []
calibration_time = 3
start_time = time.time()

road_speed = 6
road_y = 0
last_speed_increase = pygame.time.get_ticks()

LANES = [100, 250, 400]
enemies = []

# ---------- LIVES ----------
lives = 3

# ---------- SPAWN ENEMIES ----------
def spawn_enemies():
    enemies.clear()
    lanes = random.sample(LANES, 2)
    enemies.append([lanes[0], -300])
    enemies.append([lanes[1], -700])

# ---------- RESET ----------
def reset_game():
    global player_x, player_y, score, game_over
    global center_x, calibration_data, start_time
    global road_speed, last_speed_increase, lives

    player_x = WIDTH // 2 - 40
    player_y = HEIGHT - 140

    spawn_enemies()

    score = 0
    game_over = False
    lives = 3

    center_x = None
    calibration_data.clear()
    start_time = time.time()

    road_speed = 6
    last_speed_increase = pygame.time.get_ticks()

# ---------- INITIAL ----------
player_x = WIDTH // 2 - 40
player_y = HEIGHT - 140
spawn_enemies()

score = 0
game_over = False

# ---------- MAIN LOOP ----------
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            cap.release()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()

    direction = "CENTER"

    if not game_over:

        # ---------- CAMERA ----------
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:

                    nose = face_landmarks.landmark[1]
                    nose_x = int(nose.x * w)

                    # Calibration
                    if center_x is None:
                        calibration_data.append(nose_x)
                        elapsed = time.time() - start_time

                        cv2.putText(frame, "Calibrating...",
                                    (30,50), cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (0,0,255), 2)

                        if elapsed >= calibration_time:
                            center_x = int(sum(calibration_data) / len(calibration_data))

                    else:
                        cv2.line(frame, (center_x, 0), (center_x, h), (255,0,0), 2)

                        if nose_x < center_x - 40:
                            direction = "LEFT"
                        elif nose_x > center_x + 40:
                            direction = "RIGHT"

                    cv2.circle(frame, (nose_x, int(nose.y * h)), 6, (0,255,0), -1)

            cv2.imshow("Camera", frame)
            cv2.waitKey(1)

        # ---------- DIFFICULTY ----------
        current_time = pygame.time.get_ticks()
        if current_time - last_speed_increase > 3000:
            road_speed += 0.5
            last_speed_increase = current_time

        # ---------- PLAYER MOVE ----------
        if direction == "LEFT":
            player_x -= speed
        elif direction == "RIGHT":
            player_x += speed

        player_x = max(50, min(WIDTH - player_w - 50, player_x))

        # ---------- ROAD ----------
        road_y += road_speed
        if road_y > HEIGHT:
            road_y = 0

        # ---------- ENEMIES ----------
        for enemy in enemies:
            enemy[1] += road_speed

            if enemy[1] > HEIGHT:
                enemy[1] = random.randint(-600, -150)
                enemy[0] = random.choice(LANES)
                score += 1

        # ---------- COLLISION ----------
        player_rect = pygame.Rect(player_x, player_y, player_w, player_h)

        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], 80, 120)

            if player_rect.colliderect(enemy_rect):
                lives -= 1
                enemy[1] = random.randint(-600, -150)

                if lives <= 0:
                    game_over = True

    # ---------- DRAW ----------
    screen.fill((30, 30, 30))

    for i in range(10):
        pygame.draw.rect(screen, (255,255,255),
                         (WIDTH//2 - 5, road_y + i*80, 10, 40))

    pygame.draw.rect(screen, (0, 255, 0),
                     (player_x, player_y, player_w, player_h))

    for enemy in enemies:
        pygame.draw.rect(screen, (255, 0, 0),
                         (enemy[0], enemy[1], 80, 120))

    # Score
    screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (10,10))

    # Speed
    screen.blit(font.render(f"Speed: {int(road_speed)}", True, (255,255,0)), (10,60))

    # ---------- LIVES DISPLAY ----------
    for i in range(lives):
        pygame.draw.circle(screen, (255,0,0), (500 + i*30, 40), 12)

    # Game Over
    if game_over:
        screen.blit(font.render("GAME OVER", True, (255,0,0)), (150,350))
        screen.blit(font.render("Press R to Restart", True, (255,255,255)), (110,420))

    pygame.display.update()
    clock.tick(60)

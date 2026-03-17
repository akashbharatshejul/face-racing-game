import mediapipe as mp
import pygame, sys, random, cv2, time
import os
import math
def resource_path(relative_path):
    """Get absolute path for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


HIGHSCORE_FILE = "highscore.txt"

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read())
    return 0

def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))

from car_graphics import *
from blink_detector import BlinkDetector
from mouth_detector import MouthDetector
from head_tracker import HeadTracker
from emotion_detector import EmotionDetector

pygame.init()
pygame.mixer.init()   
# ---------- LOAD SOUNDS ----------
coin_sound = pygame.mixer.Sound(resource_path("sounds/coin.mp3"))
explosion_sound = pygame.mixer.Sound(resource_path("sounds/explosion.mp3"))
shield_sound = pygame.mixer.Sound(resource_path("sounds/shield.mp3"))
gameover_sound = pygame.mixer.Sound(resource_path("sounds/gameover1.wav"))
engine_sound = pygame.mixer.Sound(resource_path("sounds/engine.mp3"))
engine_sound.set_volume(0.3)
 
# Background music
pygame.mixer.music.load(resource_path("sounds/bgm.mp3"))
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1)   # loop forever

start_sound = pygame.mixer.Sound(resource_path("sounds/car_start.mp3"))
start_sound.set_volume(1.0)

WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# ---------- INITIAL LOADING SCREEN ----------
screen.fill((20,20,20))

loading_font = pygame.font.SysFont(None, 50)
small_font = pygame.font.SysFont(None, 40)

scan_text = loading_font.render("SCANNING FACE...", True, (0,255,200))
look_text = small_font.render("LOOK AT CAMERA", True, (255,255,255))
move_text = small_font.render("DO NOT MOVE", True, (255,80,80))

screen.blit(scan_text, (WIDTH//2 - scan_text.get_width()//2, 300))
screen.blit(look_text, (WIDTH//2 - look_text.get_width()//2, 380))
screen.blit(move_text, (WIDTH//2 - move_text.get_width()//2, 430))

pygame.display.update()

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 45)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# ---------- AI MODULES ----------
blink_detector = BlinkDetector()
mouth_detector = MouthDetector()
head_tracker = HeadTracker()
emotion_detector = EmotionDetector()

# ---------- GAME VARIABLES ----------
player_x = WIDTH//2 - CAR_W//2
player_y = HEIGHT - 140

LANES = [70, 160,250,350, 450]
enemies = []
coins = []

shield_energy = 0   
SHIELD_PER_COIN = 3
COIN_COUNTER = 0

road_speed = 6
road_y = 0
last_speed_increase = pygame.time.get_ticks()

score = 0
high_score = load_highscore()
new_record = False
record_time = 0
new_record_popup = False
record_popup_time = 0
record_triggered = False
lives = 3
game_over = False

shield_active = False
shield_time = 0
mouth_timer = 0

face_missing_frames = 0
FACE_LIMIT = 60
game_paused = False
engine_started = False

calibration_done = False
calibration_start_time = time.time()
game_started = False
CALIBRATION_TIME = 2
calibration_started = False
start_played = False
frame_counter = 0

current_weather = "NORMAL"
weather_timer = 0
emotion = "NORMAL"
current_ambience = None
current_music = "BGM"

game_state = "MENU"   # MENU, PLAYING, GAME_OVER
menu_cooldown = 0

# ---------- SPAWN ----------
def spawn_enemies():
    enemies.clear()

    enemy_types = ["car", "suv", "truck", "bus"]

    lanes = random.sample(LANES, 2)   # 👈 only 2 lanes

    for lane in lanes:
        etype = random.choice(enemy_types)

        enemies.append([
            lane,
            random.randint(-800, -100),
            etype
        ])

def spawn_coin():
    global COIN_COUNTER

    coins.clear()

    lane = random.choice(LANES)
    y = random.randint(-600, -100)

    COIN_COUNTER += 1
    is_shield = (COIN_COUNTER % 5 == 0)

    coins.append([lane + 30, y, is_shield])

spawn_coin()
spawn_enemies()



# ---------- RESET ----------
def reset_game():
    global player_x, score, lives, road_speed, game_over
    global shield_active, shield_energy
    global calibration_done, start_played, engine_started
    global calibration_start_time, calibration_started ,game_started
    global current_weather
    global current_music
    global game_state
    global new_record_popup
    global record_triggered
    record_triggered = False
    new_record_popup = False
    global new_record
    new_record = False
    game_state = "PLAYING"
    current_music = "BGM"
    switch_music("NORMAL")
    current_weather = "NORMAL"
    

    # Reset calibration state
    calibration_start_time = time.time()
    game_started = False
    calibration_started = False
    calibration_done = False
    emotion_detector.reset()

    # Reset player/game
    player_x = WIDTH//2 - CAR_W//2
    score = 0
    lives = 3
    road_speed = 6
    game_over = False
    shield_active = False
    shield_energy = 0

    spawn_enemies()
    spawn_coin()

    # Reset head tracker calibration
    head_tracker.center_x = None
    head_tracker.calib.clear()

    # Reset sound state
    engine_started = False
    start_played = False

    engine_sound.stop()
    start_sound.stop()

def switch_music(weather):
    global current_music

    if weather == "SNOW" and current_music != "SNOW":
        pygame.mixer.music.stop()
        pygame.mixer.music.load(resource_path("sounds/wind.mp3"))
        pygame.mixer.music.play(-1)
        current_music = "SNOW"

    elif weather == "SUNNY" and current_music != "SUNNY":
        pygame.mixer.music.stop()
        pygame.mixer.music.load(resource_path("sounds/sunny.mp3"))
        pygame.mixer.music.play(-1)
        current_music = "SUNNY"

    elif weather == "NORMAL" and current_music != "BGM":
        pygame.mixer.music.stop()
        pygame.mixer.music.load(resource_path("sounds/bgm.mp3"))
        pygame.mixer.music.play(-1)
        current_music = "BGM"  

def handle_menu_controls(results):
    global game_state, menu_cooldown

    if not results:
        return

    if time.time() - menu_cooldown < 1.5:
        return  # prevent double triggers

    blink = blink_detector.update(results)
    emotion = emotion_detector.update(results)

    # ---------- MAIN MENU ----------
    if game_state == "MENU":

        if blink:
            game_state = "PLAYING"
            menu_cooldown = time.time()
            reset_game()

        elif emotion == "SMILE":
            pygame.quit()
            sys.exit()

    # ---------- GAME OVER MENU ----------
    elif game_state == "GAME_OVER":

        if blink:
            game_state = "PLAYING"
            menu_cooldown = time.time()
            reset_game()
    
# ---------- MAIN LOOP ----------
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                reset_game()

    direction = "CENTER"

    ret, frame = cap.read()

    if ret:
       frame = cv2.flip(frame, 1)
       rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

       frame_counter += 1

       if frame_counter % 2 == 0:
           head_tracker.process(rgb)

       results = head_tracker.last_results
       handle_menu_controls(results)
       
    else:
     results = None

  

   # ---------- FACE PRESENCE ----------
    face_present = head_tracker.face_present()

    if face_present:
        face_missing_frames = 0

        # Resume game
        if game_paused:
            game_paused = False

            # Resume sounds
            pygame.mixer.music.unpause()

            if not pygame.mixer.get_busy():
                engine_sound.play(-1)

    else:
        face_missing_frames += 1

        if face_missing_frames > FACE_LIMIT:
            game_paused = True

            # Pause sounds
            pygame.mixer.music.pause()
            engine_sound.stop()

    
    # ---------- AI CONTROLS ----------
    if game_state == "PLAYING" and not game_paused and results:
        direction = head_tracker.update(WIDTH)

        if head_tracker.center_x is None:
            calibration_done = False
            calibration_started = False

        else:
            if not calibration_started:
                calibration_start_time = time.time()
                calibration_started = True

            if not calibration_done:
                if time.time() - calibration_start_time > CALIBRATION_TIME:
                    calibration_done = True
                    start_sound.play()

            elif not engine_started:
                if not start_sound.get_num_channels():
                    engine_sound.play(-1)
                    engine_started = True
                    game_started = True # ⭐ Unlock gameplay
                    game_state = "PLAYING"
        
        
       # ⭐ FREEZE GAME UNTIL ENGINE STARTS
        if not game_started:
            direction = "CENTER"

        else:

            blink = blink_detector.update(results)
            mouth = mouth_detector.update(results)
            emotion = emotion_detector.update(results)
           
            if emotion == "SMILE":
                current_weather = "SNOW"

            elif emotion == "SURPRISE":
                current_weather = "SUNNY"

            else:
                current_weather = "NORMAL"
            switch_music(current_weather)    
              

    # ⭐ SHIELD FROM BLINK
            if blink and shield_energy > 0:
                shield_active = True
                shield_time = time.time()
                shield_energy -= 1
                shield_sound.play()

            if shield_active and time.time() - shield_time > 1:
                shield_active = False

            if mouth:
                mouth_timer = time.time()

            slow_active = (time.time() - mouth_timer) < 1

            # ---------- PLAYER MOVE ----------
            if direction == "LEFT":
                player_x -= 7
            elif direction == "RIGHT":
                player_x += 7

            player_x = max(50, min(WIDTH - 110, player_x))

            # ---------- DIFFICULTY ----------
            if pygame.time.get_ticks() - last_speed_increase > 2000:
                road_speed += 0.5
                last_speed_increase = pygame.time.get_ticks()

            # ---------- ENGINE SPEED CONTROL ----------
            engine_sound.set_volume(min(1.0, 0.3 + road_speed / 40))    

            enemy_speed = road_speed * (0.5 if slow_active else 1)

            # ---------- ENEMIES ----------
            for enemy in enemies:
                enemy[1] += enemy_speed

                if enemy[1] > HEIGHT:

                    enemy_types = ["car", "suv", "truck", "bus"]

                    # choose a lane NOT used by other enemy
                    other_lanes = [e[0] for e in enemies if e != enemy]
                    available_lanes = [l for l in LANES if l not in other_lanes]

                    if available_lanes:
                        enemy[0] = random.choice(available_lanes)
                    else:
                        enemy[0] = random.choice(LANES)

                    enemy[1] = random.randint(-800, -150)
                    enemy[2] = random.choice(enemy_types)
                    score += 1

                    if score > high_score:
                        high_score = score

                        if not record_triggered:
                            new_record_popup = True
                            record_popup_time = time.time()
                            record_triggered = True

            # ---------- COINS ----------
            for coin in coins[:]:
                coin[1] += road_speed

                if coin[1] > HEIGHT:
                    coins.remove(coin)
                    spawn_coin()

            player_rect = pygame.Rect(player_x, player_y, CAR_W, CAR_H)

            # ---------- COLLISION ----------
            for enemy in enemies:
                rect = pygame.Rect(enemy[0], enemy[1], CAR_W, CAR_H)
                if player_rect.colliderect(rect):
                    if not shield_active:
                        add_explosion(enemy[0]+30, enemy[1]+50)
                        explosion_sound.play()
                        lives -= 1
                        enemy[1] = -400
                        if lives <= 0:
                            game_over = True
                            game_state = "GAME_OVER"
                            gameover_sound.play()
                            engine_sound.stop()
                            save_highscore(high_score)
                            current_weather = "NORMAL"
                            switch_music("NORMAL")
                            emotion_detector.reset()

            # ---------- COIN COLLISION ----------
            for coin in coins[:]:
                rect = pygame.Rect(coin[0]-20, coin[1]-20, 40, 40)

                if player_rect.colliderect(rect):

                    if coin[2]:
                        shield_energy += SHIELD_PER_COIN
                    else:
                        score += 5

                    coin_sound.play()
                    add_coin_effect(coin[0], coin[1])
                    coins.remove(coin)
                    spawn_coin()
    # ---------- DRAW ----------
    if game_state == "MENU":

      screen.fill((10,10,20))

      screen.blit(font.render("FACE RACING GAME", True, (0,255,200)), (120,200))
      screen.blit(font.render("Blink 🙂 = Start", True, (255,255,255)), (160,350))
      screen.blit(font.render("Smile 😄 = Quit", True, (255,255,255)), (160,420))

      pygame.display.update()
      continue

    screen.fill((20,20,20))
    draw_road(screen, road_y, WIDTH, HEIGHT)
    road_y = (road_y + road_speed) % HEIGHT

    # ---------- LOADING SCREEN ----------
    if not game_started:

      overlay = pygame.Surface((WIDTH, HEIGHT))
      overlay.set_alpha(180)
      overlay.fill((0,0,0))
      screen.blit(overlay, (0,0))

      dots = "." * int((time.time()*3) % 4)

      scan_text = font.render("SCANNING FACE" + dots, True, (0,255,200))
      look_text = font.render("LOOK AT CAMERA", True, (255,255,255))
      move_text = font.render("DO NOT MOVE", True, (255,80,80))

      screen.blit(scan_text, (WIDTH//2 - scan_text.get_width()//2, 260))
      screen.blit(look_text, (WIDTH//2 - look_text.get_width()//2, 320))
      screen.blit(move_text, (WIDTH//2 - move_text.get_width()//2, 380))

      # progress bar
      if calibration_started:
          progress = min(1, (time.time() - calibration_start_time) / CALIBRATION_TIME)
      else:
          progress = 0

      pygame.draw.rect(screen, (80,80,80), (150,450,300,30), border_radius=10)
      pygame.draw.rect(screen, (0,255,200),
                       (150,450,int(300*progress),30), border_radius=10)

    update_speed_lines(WIDTH, HEIGHT)
    draw_speed_lines(screen)
    # ---------- WEATHER DRAW ----------
    if current_weather == "SNOW":
        update_snow(WIDTH, HEIGHT)
        draw_snow(screen)

    elif current_weather == "SUNNY":
        draw_sunny_overlay(screen)

    draw_car(screen, player_x, player_y, (0,255,0))
    

    for enemy in enemies:
        draw_enemy(screen, enemy[0], enemy[1], enemy[2])

    for coin in coins:
        if coin[2]:
            draw_coin(screen, coin[0], coin[1], shield=True)
        else:
            draw_coin(screen, coin[0], coin[1])

    draw_coin_effects(screen)
    draw_explosions(screen)
    

    if shield_active:
        pygame.draw.circle(screen, (0,200,255),
                           (player_x+30, player_y+50), 60, 3)

    draw_modern_hud(screen, score, shield_energy, emotion, lives, font)
    # ---------- NEW RECORD POPUP ----------
    if new_record_popup:
        if time.time() - record_popup_time < 1:

            big_font = pygame.font.SysFont(None, 70)
            text = big_font.render("🏆 NEW RECORD!", True, (255,215,0))

            screen.blit(
                text,
                (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 150)
            )
        else:
             new_record_popup = False 
    screen.blit(font.render(f"HIGH SCORE: {high_score}", True, (255,255,0)), (20,50))

    if game_paused:

      overlay = pygame.Surface((WIDTH, HEIGHT))
      overlay.set_alpha(180)
      overlay.fill((0,0,0))
      screen.blit(overlay, (0,0))

      text1 = font.render("LOOK AT CAMERA", True, (255,255,0))
      text2 = font.render("DO NOT MOVE", True, (255,80,80))

      screen.blit(text1, (WIDTH//2 - text1.get_width()//2, 350))
      screen.blit(text2, (WIDTH//2 - text2.get_width()//2, 420))

    if game_state == "GAME_OVER":
      overlay = pygame.Surface((WIDTH, HEIGHT))
      overlay.set_alpha(200)
      overlay.fill((0,0,0))
      screen.blit(overlay, (0,0))

      screen.blit(font.render("GAME OVER", True, (255,0,0)), (160,300))
      screen.blit(font.render("Blink 🙂 to Restart", True, (255,255,255)), (120,380))

    pygame.display.update()

    if ret:
      del frame

    clock.tick(60)
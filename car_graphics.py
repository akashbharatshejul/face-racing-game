import pygame
import random
import math

CAR_W = 60
CAR_H = 100

wheel_angle = 0


# ---------- 3D ROAD ----------
def draw_road(screen, road_y, width, height):
    screen.fill((20,20,20))

    # Perspective lane borders
    pygame.draw.polygon(screen, (60,60,60),
        [(80,0),(width-80,0),(width-40,height),(40,height)])

    # Center lines perspective
    for i in range(15):
        y = (road_y + i*80) % height
        scale = 1 + y/height
        pygame.draw.rect(screen, (240,240,240),
            (width//2 - 5*scale, y, 10*scale, 40*scale))


# ---------- 3D CAR ----------
def draw_car(screen, x, y, color):
    global wheel_angle

    # Shadow
    pygame.draw.ellipse(screen, (0,0,0), (x+5,y+90,50,15))

    # Main body
    pygame.draw.rect(screen, color, (x,y,60,100), border_radius=8)

    # Top highlight (3D effect)
    pygame.draw.polygon(screen, (255,255,255,50),
        [(x+5,y+10),(x+55,y+10),(x+45,y+40),(x+15,y+40)])

    # Side panel darker
    dark = (max(0,color[0]-60),0,0)
    pygame.draw.rect(screen, dark, (x,y+40,60,60))

    # Windows
    pygame.draw.rect(screen, (180,220,255), (x+10,y+15,40,25), border_radius=5)

    # Headlights
    pygame.draw.circle(screen, (255,255,120),(x+12,y+5),4)
    pygame.draw.circle(screen, (255,255,120),(x+48,y+5),4)

    # Wheels rotating
    wheel_angle += 0.3
    for wx, wy in [(x+10,y+20),(x+50,y+20),(x+10,y+80),(x+50,y+80)]:
        pygame.draw.circle(screen, (20,20,20), (wx,wy), 8)
        lx = wx + math.cos(wheel_angle)*6
        ly = wy + math.sin(wheel_angle)*6
        pygame.draw.line(screen,(200,200,200),(wx,wy),(lx,ly),2)


# ---------- 3D COIN ----------
coin_angle = 0

def draw_coin(screen, x, y, color=(255,215,0), shield=False):
    global coin_angle

    coin_angle += 0.15

    if shield:

        # glowing pulse
        glow = 18 + abs(math.sin(coin_angle)) * 4
        pygame.draw.circle(screen, (0,150,255), (x,y), int(glow))

        # shield body
        pygame.draw.circle(screen, (0,255,255), (x,y), 14)

        # rotating highlight
        rot_x = x + math.cos(coin_angle) * 6
        rot_y = y + math.sin(coin_angle) * 6
        pygame.draw.circle(screen, (255,255,255), (int(rot_x), int(rot_y)), 3)

        # shield icon
        pygame.draw.polygon(
            screen,
            (255,255,255),
            [
                (x, y-8),
                (x+6, y-2),
                (x+4, y+6),
                (x, y+10),
                (x-4, y+6),
                (x-6, y-2)
            ]
        )

    else:

        # rotating coin illusion
        width = abs(math.cos(coin_angle)) * 20 + 6
        height = 30

        pygame.draw.ellipse(
            screen,
            color,
            (x - width/2, y - height/2, width, height)
        )

        pygame.draw.circle(screen, (255,255,255), (int(x-5), int(y-5)), 3)

# ---------- HEART ----------
def draw_heart(screen, x, y, size=12):
    pygame.draw.circle(screen,(255,50,80),(x-size//2,y),size//2)
    pygame.draw.circle(screen,(255,50,80),(x+size//2,y),size//2)
    pygame.draw.polygon(screen,(255,50,80),
        [(x-size,y),(x+size,y),(x,y+size+5)])


# ---------- COIN GLOW ----------
coin_effects = []

def add_coin_effect(x,y):
    coin_effects.append([x,y,10])

def draw_coin_effects(screen):
    for e in coin_effects[:]:
        pygame.draw.circle(screen,(255,255,150),(e[0],e[1]),e[2],3)
        e[2]+=2
        if e[2]>40:
            coin_effects.remove(e)

# ---------- EXPLOSION PARTICLES ----------
explosions = []

def add_explosion(x, y):
    for i in range(15):
        explosions.append([x, y,
                           random.uniform(-4,4),
                           random.uniform(-4,4),
                           random.randint(3,6)])

def draw_explosions(screen):
    for e in explosions[:]:
        e[0] += e[2]
        e[1] += e[3]
        e[4] -= 0.2

        pygame.draw.circle(screen, (255,200,50), (int(e[0]), int(e[1])), int(e[4]))

        if e[4] <= 0:
            explosions.remove(e)


# ---------- NEON HUD PANEL ----------
def draw_hud_panel(screen):
    pygame.draw.rect(screen, (20,20,40), (0,0,600,80))
    pygame.draw.line(screen, (0,255,255), (0,80), (600,80), 3)


# ---------- SPEED LINES ----------
speed_lines = []

def update_speed_lines(width, height):
    import random
    if random.random() < 0.3:
        speed_lines.append([random.randint(0,width), 0])

    for line in speed_lines[:]:
        line[1] += 15
        if line[1] > height:
            speed_lines.remove(line)

def draw_speed_lines(screen):
    for line in speed_lines:
        pygame.draw.line(screen, (200,200,200),
                         (line[0], line[1]),
                         (line[0], line[1]+20), 2)
        
# ---------- MODERN HUD ----------
def draw_modern_hud(screen, score, shield, emotion, lives, font):

    WIDTH = screen.get_width()

    # Panel
    panel = pygame.Surface((WIDTH, 50))
    panel.set_alpha(170)
    panel.fill((10, 10, 30))
    screen.blit(panel, (0, 0))

    # -------- SCORE --------
    score_text = font.render(f"SCORE: {score}", True, (255,255,255))
    screen.blit(score_text, (25, 10))

    # -------- SHIELD --------
    shield_text = font.render(f"SHIELD: {shield}", True, (0,255,255))
    screen.blit(shield_text, (240, 10))

    # -------- LIVES (HEARTS INSIDE PANEL) --------
    for i in range(lives):
        x = 465 + i*40
        y = 20
        pygame.draw.circle(screen,(255,50,80),(x-8,y),8)
        pygame.draw.circle(screen,(255,50,80),(x+8,y),8)
        pygame.draw.polygon(screen,(255,50,80),
            [(x-16,y),(x+16,y),(x,y+18)])

    # -------- EMOTION BADGE --------
    color = (200,200,200)

    if emotion == "SMILE":
        color = (0,255,120)
    elif emotion == "SURPRISE":
        color = (255,200,0)

    badge_rect = pygame.Rect(WIDTH - 140, 50, 130, 40)
    pygame.draw.rect(screen, color, badge_rect, 3, border_radius=12)

    emo_text = font.render(emotion, True, color)
    text_rect = emo_text.get_rect(center=badge_rect.center)
    screen.blit(emo_text, text_rect)

    # ---------- WEATHER SYSTEM ----------

snow_particles = []

def update_snow(width, height):
    # spawn new snow
    if random.random() < 0.5:
        snow_particles.append([random.randint(0,width), 0, random.randint(2,5)])

    for s in snow_particles[:]:
        s[1] += s[2]
        if s[1] > height:
            snow_particles.remove(s)

def draw_snow(screen):
    for s in snow_particles:
        pygame.draw.circle(screen, (255,255,255), (int(s[0]), int(s[1])), 2)


def draw_sunny_overlay(screen):
    overlay = pygame.Surface((600,800))
    overlay.set_alpha(40)
    overlay.fill((255, 230, 150))
    screen.blit(overlay, (0,0))
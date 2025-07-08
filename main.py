import cv2
import pygame
import random
from hand_module import HandDetector


WIDTH, HEIGHT = 720, 700
pygame.init()
pygame.mixer.init()
collect_sound = pygame.mixer.Sound("coin.mp3")
over_sound = pygame.mixer.Sound("over.mp3")
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("S-400 Dual Missile Catcher ")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 64)
game_over_font = pygame.font.SysFont(None, 100)

# Missile images
missile_images = []
for i in range(1, 9):
    img = pygame.image.load(f"PK Missile {i}.png").convert_alpha()
    img = pygame.transform.scale(img, (40, 80))
    img = pygame.transform.rotate(img,180)
    missile_images.append(img)

# Load launcher image
s400_img = pygame.image.load("S400.png").convert_alpha()
launcher_width, launcher_height = 150, 60
s400_img = pygame.transform.scale(s400_img, (launcher_width, launcher_height))
launcher_y = HEIGHT - launcher_height - 20

# Game state
missiles = []
missile_speed = 8
spawn_timer = 0
spawn_delay = 40
score = 0
lives = 1
game_over = False

# WebCAm
cap = cv2.VideoCapture(0)
cap.set(3, WIDTH)
cap.set(4, HEIGHT)
detector = HandDetector(detectionCon=0.8, maxHands=2)

def reset_game():
    global missiles, spawn_timer, score, lives, game_over
    missiles.clear()
    spawn_timer = 0
    score = 0
    lives = 1
    game_over = False

# Game 
running = True
while running:
    pygame.event.pump()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            reset_game()

    # Frame
    success, img = cap.read()
    if not success:
        continue
    img = cv2.flip(img, 1)
    img = detector.findHands(img)

    
    left_x = None
    right_x = None
    hands = detector.results.multi_hand_landmarks if detector.results else []

    if hands:
        for i, hand in enumerate(hands):
            lmList = detector.findPosition(img, handNo=i)
            if lmList:
                x = lmList[8][1]  # Index finger X
                handedness = detector.results.multi_handedness[i].classification[0].label
                if handedness == "Left":
                    left_x = x
                elif handedness == "Right":
                    right_x = x

    # Convert camera frame to background
    try:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        frame = pygame.surfarray.make_surface(img_rgb)
        frame = pygame.transform.rotate(frame, -90)
        frame = pygame.transform.flip(frame, True, False)
        frame = pygame.transform.scale(frame, (WIDTH, HEIGHT))
    except:
        continue

    win.blit(frame, (0, 0))  # Background

    # Draw launchers
    launcher_left = None
    launcher_right = None

    if left_x:
        x = max(0, min(WIDTH - launcher_width, left_x - launcher_width // 2))
        win.blit(s400_img, (x, launcher_y))
        launcher_left = pygame.Rect(x, launcher_y, launcher_width, launcher_height)

    if right_x:
        x = max(0, min(WIDTH - launcher_width, right_x - launcher_width // 2))
        win.blit(s400_img, (x, launcher_y))
        launcher_right = pygame.Rect(x, launcher_y, launcher_width, launcher_height)

    if not game_over:
        # Spawn missiles
        spawn_timer += 1
        if spawn_timer >= spawn_delay:
            spawn_x = random.randint(40, WIDTH - 40)
            missile_img = random.choice(missile_images)
            missiles.append([spawn_x, -80, missile_img])
            spawn_timer = 0

        # Move and draw missiles
        for missile in missiles[:]:
            missile[1] += missile_speed
            win.blit(missile[2], (missile[0] - 20, missile[1]))

            caught = False
            if launcher_left and launcher_left.collidepoint(missile[0], missile[1] + 40):
                caught = True
            if launcher_right and launcher_right.collidepoint(missile[0], missile[1] + 40):
                caught = True

            if caught:
                missiles.remove(missile)
                score += 1
                collect_sound.play() 
                
            elif missile[1] > HEIGHT:
                missiles.remove(missile)
                lives -= 1
                if lives <= 0:
                    over_sound.play()
                    game_over = True

        # Display score
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        win.blit(score_text, (20, 20))
    else:
        
        # Game Over screen
        over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        final_score = font.render(f"Your Score: {score}", True, (0, 0, 0))
        restart_text = font.render("Press R to Restart", True, (0, 0, 0))
        win.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 120))
        win.blit(final_score, (WIDTH//2 - final_score.get_width()//2, HEIGHT//2 - 30))
        win.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))

    pygame.display.update()
    clock.tick(60)

# Cleanup
cap.release()
cv2.destroyAllWindows()
pygame.quit()

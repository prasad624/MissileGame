import cv2
import pygame
import random
from hand_module import HandDetector

# Game setup
WIDTH, HEIGHT = 720, 700
pygame.init()
pygame.mixer.init()

# Load sounds
collect_sound = pygame.mixer.Sound("coin.mp3")
over_sound = pygame.mixer.Sound("over.mp3")

# Set up window and fonts
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("S-400 Dual Missile Catcher")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 64)
game_over_font = pygame.font.SysFont(None, 100)

# Load logo
logo_img = pygame.image.load("logo.png").convert_alpha()
logo_img = pygame.transform.scale(logo_img, (300, 300))

# Load launcher
s400_img = pygame.image.load("S400.png").convert_alpha()
launcher_width, launcher_height = 150, 60
s400_img = pygame.transform.scale(s400_img, (launcher_width, launcher_height))
launcher_y = HEIGHT - launcher_height - 20

# Load explosion image for bomb
explosion_img = pygame.image.load("explosion.png").convert_alpha()
explosion_img = pygame.transform.scale(explosion_img, (180, 80))

# Load missiles
missile_images = []
for i in range(1, 9):
    img = pygame.image.load(f"PK Missile {i}.png").convert_alpha()
    img = pygame.transform.scale(img, (40, 80))
    img = pygame.transform.rotate(img, 180)
    missile_images.append(img)

# Load bomb image
bomb_img = pygame.image.load("bomb.png").convert_alpha()
bomb_img = pygame.transform.scale(bomb_img, (50, 80))
bomb_img = pygame.transform.flip(bomb_img, False, True)

# Game variables
missiles = []
missile_speed = 8
spawn_timer = 0
spawn_delay = 40
score = 0
lives = 1
game_over = False
player_name = ""

# Webcam and hand tracking
cap = cv2.VideoCapture(0)
cap.set(3, WIDTH)
cap.set(4, HEIGHT)
detector = HandDetector(detectionCon=0.8, maxHands=2)

def get_player_name():
    global player_name
    input_active = True
    name_font = pygame.font.SysFont(None, 50)
    input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    user_text = ""
    active = False

    while input_active:
        win.fill((255, 255, 255))
        title = game_over_font.render("Enter Your Name", True, (0, 0, 0))
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        player_name = user_text.strip() or "Player"
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        if len(user_text) < 15:
                            user_text += event.unicode

        txt_surface = name_font.render(user_text, True, (0, 0, 0))
        width = max(300, txt_surface.get_width() + 10)
        input_box.w = width
        win.blit(txt_surface, (input_box.x + 5, input_box.y + 10))
        pygame.draw.rect(win, color, input_box, 2)
        pygame.display.flip()
        clock.tick(30)

def show_intro_screen():
    waiting = True
    instruction_font_size = 32 if WIDTH < 800 else 36
    instruction_font = pygame.font.SysFont(None, instruction_font_size)
    instructions = [
        "Use your LEFT and RIGHT hand to control two launchers",
        "Catch the falling missiles (PK Missiles)",
        "Avoid catching the bombs with fire (they end the game)",
        "Score increases by 1 for each missile caught",
    ]

    while waiting:
        win.fill((255, 255, 255))
        title = game_over_font.render("S-400 Missile Catcher", True, (0, 0, 0))
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        win.blit(logo_img, (WIDTH // 2 - logo_img.get_width() // 2, 120))

        base_y = 450
        line_height = instruction_font_size + 10
        for i, line in enumerate(instructions):
            rendered = instruction_font.render(line, True, (0, 0, 0))
            win.blit(rendered, (WIDTH // 2 - rendered.get_width() // 2, base_y + i * line_height))

        prompt = font.render("Press SPACE to Start", True, (50, 50, 50))
        win.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 50))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

def reset_game():
    global missiles, spawn_timer, score, lives, game_over
    missiles.clear()
    spawn_timer = 0
    score = 0
    lives = 1
    game_over = False

get_player_name()
show_intro_screen()

# Game loop
running = True
while running:
    pygame.event.pump()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            reset_game()

    success, img = cap.read()
    if not success:
        continue
    img = cv2.flip(img, 1)
    img = detector.findHands(img)

    left_x, right_x = None, None
    hands = detector.results.multi_hand_landmarks if detector.results else []
    if hands:
        for i, hand in enumerate(hands):
            lmList = detector.findPosition(img, handNo=i)
            if lmList:
                x = lmList[8][1]
                handedness = detector.results.multi_handedness[i].classification[0].label
                if handedness == "Left":
                    left_x = x
                elif handedness == "Right":
                    right_x = x

    try:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        frame = pygame.surfarray.make_surface(img_rgb)
        frame = pygame.transform.rotate(frame, -90)
        frame = pygame.transform.flip(frame, True, False)
        frame = pygame.transform.scale(frame, (WIDTH, HEIGHT))
    except:
        continue

    win.blit(frame, (0, 0))

    launcher_left = launcher_right = None
    if left_x:
        x = max(0, min(WIDTH - launcher_width, left_x - launcher_width // 2))
        win.blit(s400_img, (x, launcher_y))
        launcher_left = pygame.Rect(x, launcher_y, launcher_width, launcher_height)
    if right_x:
        x = max(0, min(WIDTH - launcher_width, right_x - launcher_width // 2))
        win.blit(s400_img, (x, launcher_y))
        launcher_right = pygame.Rect(x, launcher_y, launcher_width, launcher_height)

    if not game_over:
        spawn_timer += 1
        if spawn_timer >= spawn_delay:
            spawn_x = random.randint(40, WIDTH - 40)
            missile_type = random.choice(["normal"] * 4 + ["bomb"])
            if missile_type == "bomb":
                missiles.append([spawn_x, -80, bomb_img, "bomb"])
            else:
                missile_img = random.choice(missile_images)
                missiles.append([spawn_x, -80, missile_img, "normal"])
            spawn_timer = 0

        for missile in missiles[:]:
            missile[1] += missile_speed
            win.blit(missile[2], (missile[0] - 20, missile[1]))
            caught = False
            if launcher_left and launcher_left.collidepoint(missile[0], missile[1] + 40):
                caught = True
                caught_launcher = launcher_left
            elif launcher_right and launcher_right.collidepoint(missile[0], missile[1] + 40):
                caught = True
                caught_launcher = launcher_right

            if caught:
                if missile[3] == "bomb":
                    over_sound.play()
                    win.blit(explosion_img, (caught_launcher.x - 15, caught_launcher.y - 10))
                    pygame.display.update()
                    pygame.time.delay(500)
                    game_over = True
                    missiles.remove(missile)
                    break
                else:
                    collect_sound.play()
                    score += 1
                    missiles.remove(missile)
            elif missile[1] > HEIGHT:
                if missile[3] == "normal":
                    lives -= 1
                    if lives <= 0:
                        over_sound.play()
                        game_over = True
                missiles.remove(missile)

        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        win.blit(score_text, (20, 20))
    else:
        over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        final_score = font.render(f"{player_name}'s Score: {score}", True, (0, 0, 0))
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

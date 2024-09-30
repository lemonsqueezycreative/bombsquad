import pygame
import sys
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 500, 600  # Screen dimensions
GRID_SIZE = 5  # Number of rows and columns in the grid
CELL_SIZE = 100  # Size of each cell in pixels
SQUARE_SIZE = 75  # Size of the movable square
BOMB_SIZE = 100  # Size of the enemy square (bomb)
MOVEMENT_DELAY = 100  # Delay in milliseconds
BOMB_DELAY = 2000  # Delay in milliseconds for bomb spawn

# Initialize game variables
current_score = 0
high_score = 0
level = 1

# Sound effects
main_menu_theme = pygame.mixer.Sound('theme.mp3')
bg_music_file = 'bd_bg.mp3'
sound = pygame.mixer.Sound(bg_music_file)
bomb_diffused_sound = pygame.mixer.Sound('bomb_success.mp3')
bomb_fail_sound = pygame.mixer.Sound('bomb_fail.mp3')
game_over_sound = pygame.mixer.Sound('game_over.mp3')
timer_sound = pygame.mixer.Sound('timer_short.mp3')
timer_long_sound = pygame.mixer.Sound('timer_long.mp3')

# Colors
GRID_COLOR = (110, 110, 110)
NIGHT_GRID_COLOR = (20, 20, 20)
SMOKE_GRID_COLOR = (150, 150, 150)

SQUARE_COLOR = (137, 154, 104)

ENEMY_SQUARE_COLOR = (30, 0, 0)
NIGHT_ENEMY_SQUARE_COLOR = (14, 14, 14)
SMOKE_ENEMY_SQUARE_COLOR = (154, 154, 154)

BACKGROUND_COLOR = (100, 100, 100)
NIGHT_BACKGROUND_COLOR = (10, 10, 10)
SMOKE_BACKGROUND_COLOR = (160, 160, 160)

TEXT_COLOR = (255, 255, 255)
TEXT_COLOR_RED = (255, 0, 0)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('LSC Bomb Squad')

# Initialize the font
font = pygame.font.Font(None, 24)
label_font = pygame.font.Font(None, 36)  # Larger font for the label

# Menu state
menu_state = 'main_menu'  # 'main_menu', 'instructions', or 'game'

# Square settings
square_row, square_col = 0, 0  # Start position (top-left corner)

# Enemy square settings
def get_random_position():
    return random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)

enemy_square_row, enemy_square_col = get_random_position()
bomb_diffused = False  # Flag to indicate whether the bomb has been diffused

# Timing variables
game_time = 4  # Starting time in seconds
last_time_update = pygame.time.get_ticks()
last_movement_time = pygame.time.get_ticks()  # Initialize last_movement_time
clock = pygame.time.Clock()

# Target position for level completion
target_row = random.randint(0, GRID_SIZE - 1)
target_col = random.randint(0, GRID_SIZE - 1)

# Blinking variables
blink_start_time = None
blink_interval = 250  # Time in milliseconds for each blink interval

# some more initialization stuff
background_color = BACKGROUND_COLOR
current_enemy_square_color = ENEMY_SQUARE_COLOR
GRID_COLOR = GRID_COLOR
game_over = False
main_menu_theme.play()

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def main_menu():
    global menu_state
    screen.fill(NIGHT_BACKGROUND_COLOR)
    draw_text('BOMB SQUAD', label_font, TEXT_COLOR_RED, screen, WIDTH // 2, HEIGHT // 2 - 100)
    draw_text('Press ENTER to Start', font, TEXT_COLOR, screen, WIDTH // 2, HEIGHT // 2)
    draw_text('Press I for Instructions', font, TEXT_COLOR, screen, WIDTH // 2, HEIGHT // 2 + 50)
    draw_text('Press ESC to Quit', font, TEXT_COLOR, screen, WIDTH // 2, HEIGHT // 2 + 100)

def instructions_menu():
    global menu_state
    screen.fill(NIGHT_BACKGROUND_COLOR)
    draw_text('Instructions', label_font, TEXT_COLOR_RED, screen, WIDTH // 2, HEIGHT // 2 - 100)
    draw_text('Use arrow keys or wasd to move the', font, TEXT_COLOR, screen, WIDTH // 2, HEIGHT // 2 - 50)
    draw_text('green square [BOMB SQUAD]', font, TEXT_COLOR, screen, WIDTH // 2, HEIGHT // 2 - 25)
    draw_text('Diffuse the bomb by moving to the', font, TEXT_COLOR, screen, WIDTH // 2, HEIGHT // 2 + 25)
    draw_text('other square [BOMB] and pressing ENTER', font, TEXT_COLOR, screen, WIDTH // 2, HEIGHT // 2 + 50)
    draw_text('Once the bomb is diffused, reach the yellow', font, TEXT_COLOR, screen, WIDTH // 2, HEIGHT // 2 + 100)
    draw_text('square [EXIT] before time runs out', font, TEXT_COLOR, screen, WIDTH // 2, HEIGHT // 2 + 125)
    draw_text('Press ESC to return to the main menu', font, TEXT_COLOR_RED, screen, WIDTH // 2, HEIGHT // 2 + 175)

def diffuse_bomb(square_rect, enemy_square_rect):
    global current_score, game_label_text, bomb_diffused
    if square_rect.colliderect(enemy_square_rect):
        bomb_chance = random.randint(1, 6)
        if bomb_chance == 5:
            bomb_diffused_sound.play()
            game_label_text = f"Bomb diffused! Get to the exit!"
            bomb_diffused = True  # Set the flag to indicate the bomb has been diffused
            # Move the enemy square off-screen
            enemy_square_rect.topleft = (-BOMB_SIZE, -BOMB_SIZE)  # Set both x and y
        else:
            bomb_fail_sound.play()

def reset_game():
    global square_row, square_col, enemy_square_row, enemy_square_col
    global bomb_diffused, game_time, level, current_score, game_over, game_label_text
    square_row, square_col = 0, 0
    enemy_square_row, enemy_square_col = get_random_position()
    bomb_diffused = False
    game_time = 4
    level = 1
    current_score = 0
    game_over = False
    game_label_text = "Diffuse the bomb! Go go go!"
    sound.play(loops=-1)  # Restart background music

def next_stage():
    global background_color, current_enemy_square_color, GRID_COLOR
    stage_choice_num = random.randint(1, 10)
    if stage_choice_num == 9:
        GRID_COLOR = NIGHT_GRID_COLOR
        background_color = NIGHT_BACKGROUND_COLOR
        current_enemy_square_color = NIGHT_ENEMY_SQUARE_COLOR
    elif stage_choice_num == 10:
        GRID_COLOR = SMOKE_GRID_COLOR
        background_color = SMOKE_BACKGROUND_COLOR
        current_enemy_square_color = SMOKE_ENEMY_SQUARE_COLOR
    else:
        GRID_COLOR = GRID_COLOR
        background_color = BACKGROUND_COLOR
        current_enemy_square_color = ENEMY_SQUARE_COLOR

def game_loop():
    global square_row, square_col, enemy_square_row, enemy_square_col, target_row, target_col
    global bomb_diffused, game_time, level, current_score, high_score, game_over, game_label_text
    global blink_start_time, last_movement_time, current_time, last_time_update
    
    while True:
        current_time = pygame.time.get_ticks()  # Get the current time in milliseconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and not game_over:
                    diffuse_bomb(square_rect, enemy_square_rect)
                elif event.key == pygame.K_ESCAPE and game_over:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r and game_over:
                    reset_game()
                elif event.key == pygame.K_i:
                    menu_state = 'instructions'

        if not game_over:
            # Key handling with delay
            keys = pygame.key.get_pressed()
            if current_time - last_movement_time >= MOVEMENT_DELAY:
                if keys[pygame.K_LEFT]:
                    if square_col > 0:
                        square_col -= 1
                        last_movement_time = current_time
                if keys[pygame.K_a]:
                    if square_col > 0:
                        square_col -= 1
                        last_movement_time = current_time
                if keys[pygame.K_RIGHT]:
                    if square_col < GRID_SIZE - 1:
                        square_col += 1
                        last_movement_time = current_time
                if keys[pygame.K_d]:
                    if square_col < GRID_SIZE - 1:
                        square_col += 1
                        last_movement_time = current_time
                if keys[pygame.K_UP]:
                    if square_row > 0:
                        square_row -= 1
                        last_movement_time = current_time
                if keys[pygame.K_w]:
                    if square_row > 0:
                        square_row -= 1
                        last_movement_time = current_time
                if keys[pygame.K_DOWN]:
                    if square_row < GRID_SIZE - 1:
                        square_row += 1
                        last_movement_time = current_time
                if keys[pygame.K_s]:
                    if square_row < GRID_SIZE - 1:
                        square_row += 1
                        last_movement_time = current_time

            # Check if the player has reached the target position
            if bomb_diffused and square_row == target_row and square_col == target_col:
                # Reset player position and spawn new bomb
                square_row, square_col = 0, 0
                enemy_square_row, enemy_square_col = get_random_position()
                next_stage()
                bomb_diffused = False
                game_time = 4
                level += 1
                current_score += 1
                if current_score > high_score:
                    high_score = current_score
                
                # Generate new target position
                target_row, target_col = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                
                game_label_text = f"Level {level}: Find and diffuse the bomb!"

            # Timer logic
            if current_time - last_time_update >= 1000:  # 1000 milliseconds = 1 second
                game_time -= 1
                last_time_update = current_time
                if game_time == 2:
                    timer_sound.play()
                elif game_time == 1:
                    timer_sound.play()
                if game_time <= 0:
                    sound.stop()
                    timer_long_sound.play()
                    game_over_sound.play()
                    game_over = True
                    game_label_text = "Game Over! ESC to quit, R to restart"

            # Calculate the top-left corner of the squares
            top_left_x = square_col * CELL_SIZE + (CELL_SIZE - SQUARE_SIZE) // 2
            top_left_y = square_row * CELL_SIZE + (CELL_SIZE - SQUARE_SIZE) // 2
            top_left_x_enemy = enemy_square_col * CELL_SIZE + (CELL_SIZE - BOMB_SIZE) // 2
            top_left_y_enemy = enemy_square_row * CELL_SIZE + (CELL_SIZE - BOMB_SIZE) // 2

            # Draw gradient background
            screen.fill(background_color)

            # Draw the 5x5 grid with updated color
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    top_left_x_grid = col * CELL_SIZE
                    top_left_y_grid = row * CELL_SIZE
                    cell_rect = pygame.Rect(top_left_x_grid, top_left_y_grid, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, GRID_COLOR, cell_rect, 1)  # Draw the grid lines

            # Draw the enemy square (bomb) if it hasn't been diffused
            if not bomb_diffused:
                enemy_square_rect = pygame.Rect(top_left_x_enemy, top_left_y_enemy, BOMB_SIZE, BOMB_SIZE)
                pygame.draw.rect(screen, current_enemy_square_color, enemy_square_rect)

            # Draw the movable square
            square_rect = pygame.Rect(top_left_x, top_left_y, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, SQUARE_COLOR, square_rect)

            # Draw the target blinking square if applicable
            if bomb_diffused:
                if blink_start_time is None:
                    blink_start_time = current_time

                if (current_time - blink_start_time) % (2 * blink_interval) < blink_interval:
                    top_left_x_target = target_col * CELL_SIZE + (CELL_SIZE - SQUARE_SIZE) // 2
                    top_left_y_target = target_row * CELL_SIZE + (CELL_SIZE - SQUARE_SIZE) // 2
                    target_square_rect = pygame.Rect(top_left_x_target, top_left_y_target, SQUARE_SIZE, SQUARE_SIZE)
                    pygame.draw.rect(screen, (255, 255, 0), target_square_rect)  # Yellow color for the blinking square

        # Create the label text
        game_label_text = "Diffuse the bomb! Go go go!" if not bomb_diffused and not game_over else game_label_text
        game_label_surface = label_font.render(game_label_text, True, TEXT_COLOR)
        text_width, text_height = game_label_surface.get_size()
        text_x = (WIDTH - text_width) // 2
        text_y = (HEIGHT - text_height) // 2 + 240
        screen.blit(game_label_surface, (text_x, text_y))

        time_label_text = f"Time: {game_time}"
        time_label_surface = label_font.render(time_label_text, True, TEXT_COLOR)
        screen.blit(time_label_surface, (25, 570))

        score_label_text = f"Score: {current_score}"
        score_label_surface = label_font.render(score_label_text, True, TEXT_COLOR)
        screen.blit(score_label_surface, (150, 570))

        high_score_label_text = f"High Score: {high_score}"
        high_score_label_surface = label_font.render(high_score_label_text, True, TEXT_COLOR)
        screen.blit(high_score_label_surface, (300, 570))

        # Update the display
        pygame.display.flip()
        clock.tick(30)  # Limit frame rate to 30 FPS

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and menu_state == 'main_menu':
                menu_state = 'game'
                reset_game()
            elif event.key == pygame.K_i and menu_state == 'main_menu':
                menu_state = 'instructions'
            elif event.key == pygame.K_ESCAPE:
                if menu_state == 'instructions':
                    menu_state = 'main_menu'
                elif menu_state == 'game' and game_over:
                    pygame.quit()
                    sys.exit()  # Quit the game when ESC is pressed at game over screen

    if menu_state == 'main_menu':
        main_menu()
    elif menu_state == 'instructions':
        instructions_menu()
    elif menu_state == 'game':
        game_loop()

    pygame.display.flip()
    clock.tick(30)  # Limit frame rate to 30 FPS

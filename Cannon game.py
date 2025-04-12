# Import modules
import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Define colors
BLACK = 0, 0, 0
WHITE = 255, 255, 255
BLUE = 0, 0, 255
RED = 255, 0, 0
YELLOW = 255, 255, 0
WIND_COLOR = (0, 255, 0)  # Green color for the wind arrow

# Define a frame rate
frames_per_second = 60

# Initialize real world parameters
g = 9.8  # Gravitational acceleration (m/s**2)
mass = 1  # Mass of projectile (kg)
D = 0.1  # Coefficient of friction (drag coefficient)
max_velocity = 230  # Maximum launch velocity

# Set parameters for time
speedup = 8  # Speed up the simulation
t = 0.0  # time in seconds
dt = (1 / frames_per_second) * speedup  # time increment in seconds

width = 2000.0  # Field width
height = 1000.0  # Field height
x_grid = 100  # X-axis grid interval
y_grid = 100  # Y-axis grid interval

scale_real_to_screen = 0.5  # scale from the real-world to screen-coordinate system

# Define total rounds
total_rounds = 5

def convert(real_world_x, real_world_y, scale=scale_real_to_screen, real_world_height=height):
    ''' conversion from real-world coordinates to pixel-coordinates '''
    return int(real_world_x * scale), int((real_world_height - real_world_y) * scale - 1)


def convert_to_real(mouse_x, mouse_y, scale=scale_real_to_screen, real_world_height=height):
    ''' conversion from pixel coordinates to real-world coordinates '''
    return mouse_x / scale, real_world_height - (mouse_y / scale)


# Initialize real world cannon(s):
cannon_width, cannon_height = 30, 30
cannon1 = {
    "x": 200,
    "y": 0 + cannon_height,
    "vx": 10,  # Initial x velocity
    "vy": 10,  # Initial y velocity
    "width": cannon_width,
    "height": cannon_height,
    "color": BLUE,
    "ball_radius": 10
}

cannon2 = {
    "x": 1800,
    "y": 0 + cannon_height,
    "vx": 10,
    "vy": 10,
    "width": cannon_width,
    "height": cannon_height,
    "color": YELLOW,
    "ball_radius": 10
}

# List of players
players = [cannon1, cannon2]
scores = [0, 0]  # Track scores for cannon 1 and cannon 2

# Initialize random wind for each turn
def generate_random_wind():
    ''' Generate random wind velocity in x direction between -15 and 15 meters per second '''
    return random.uniform(-15, 15), 0  # Wind only affects x direction

wind_x, wind_y = generate_random_wind()  # Initial wind


def calc_init_ball_pos(cannon):
    ''' Finds the center of the cannon '''
    return cannon['x'] + cannon['width'] / 2, cannon['y'] - cannon['height'] / 2


def draw_cannon(surface, cannon, angle):
    ''' Draw the cannon with a barrel following the mouse '''
    base_x, base_y = convert(cannon["x"], cannon["y"])

    barrel_length = 80
    barrel_width = 12

    end_x = base_x + int(barrel_length * math.cos(angle))
    end_y = base_y + int(barrel_length * math.sin(angle))

    offset_x = int(barrel_width / 2 * math.sin(angle))
    offset_y = int(barrel_width / 2 * math.cos(angle))

    pygame.draw.circle(surface, cannon["color"], (base_x, base_y), 15)
    pygame.draw.polygon(surface, cannon["color"], [
        (base_x - offset_x, base_y + offset_y),
        (base_x + offset_x, base_y - offset_y),
        (end_x + offset_x, end_y - offset_y),
        (end_x - offset_x, end_y + offset_y)
    ])


def is_inside_field(real_world_x, real_world_y, field_width=width):
    ''' Return true if input is within world '''
    return 0 < real_world_x < field_width and real_world_y > 0


def draw_wind(surface, wind_x, wind_y, color):
    ''' Draws an arrow representing wind on the screen '''
    arrow_start = (50, 50)
    arrow_end = (50 + int(wind_x * 2), 50)
    pygame.draw.line(surface, color, arrow_start, arrow_end, 4)
    pygame.draw.polygon(surface, color, [(arrow_end[0], arrow_end[1]),
                                         (arrow_end[0] - 10, arrow_end[1] - 5),
                                         (arrow_end[0] - 10, arrow_end[1] + 5)])


def check_hit(x, y, target_cannon):
    ''' Check if the projectile hit the other cannon '''
    cannon_x, cannon_y = target_cannon["x"], target_cannon["y"]
    distance = math.sqrt((x - cannon_x) ** 2 + (y - cannon_y) ** 2)
    return distance <= target_cannon["width"]  # Adjust hit radius based on cannon size


# Create PyGame screen:
screen_width, screen_height = int(width * scale_real_to_screen), int(height * scale_real_to_screen)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Projectile Simulation with Cannon Targeting")

clock = pygame.time.Clock()

def draw_grid(surface, color, real_x_grid, real_y_grid, real_width=width, real_height=height):
    ''' Draw real-world grid on screen '''
    for i in range(int(real_width / real_x_grid)):
        pygame.draw.line(surface, color, convert(i * real_x_grid, 0), convert(i * real_x_grid, real_height))
    for i in range(int(real_height / y_grid)):
        pygame.draw.line(surface, color, convert(0, i * real_y_grid), convert(real_width, i * real_y_grid))


def change_player():
    ''' Initialize the global variables of the projectile to be those of the players cannon '''
    global players, turn, x, y, vx, vy, ball_color, ball_radius, round_counter, wind_x, wind_y
    turn = (turn + 1) % len(players)
    if turn == 0:
        round_counter += 1
        if round_counter > total_rounds:  # End game after specified rounds
            print(f"Game over! {total_rounds} rounds completed.")
            if scores[0] > scores[1]:
                print("Cannon 1 wins!")
            elif scores[1] > scores[0]:
                print("Cannon 2 wins!")
            else:
                print("It's a tie!")
            pygame.quit()
            sys.exit()

    wind_x, wind_y = generate_random_wind()
    x, y = calc_init_ball_pos(players[turn])
    vx, vy = players[turn]['vx'], players[turn]['vy']
    ball_color = players[turn]['color']
    ball_radius = players[turn]['ball_radius']


# Game loop:
running = True
shooting = False
show_grid = True
turn = 0
round_counter = 1  # Start from round 1
x, y = calc_init_ball_pos(players[turn])
vx = players[turn]['vx']
vy = players[turn]['vy']
ball_color = players[turn]['color']
ball_radius = players[turn]['ball_radius']

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
            show_grid = not show_grid
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            shooting = True

    if not shooting:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        real_mouse_x, real_mouse_y = convert_to_real(mouse_x, mouse_y)

        dx = real_mouse_x - players[turn]["x"]
        dy = real_mouse_y - players[turn]["y"]
        angle = math.atan2(-dy, dx)

        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            scale_factor = min(distance / 100, 1.0)
            vx = (dx / distance) * max_velocity * scale_factor
            vy = (dy / distance) * max_velocity * scale_factor

    if shooting:
        # Calculate forces and update projectile motion
        Fx_gravity = 0
        Fy_gravity = -mass * g

        # Relative velocity (with respect to wind)
        # Relative velocity (with respect to wind)
        relative_vx = vx - wind_x
        relative_vy = vy - wind_y
        Fx_drag = -D * relative_vx
        Fy_drag = -D * relative_vy

        # Total force and acceleration
        Fx = Fx_gravity + Fx_drag
        Fy = Fy_gravity + Fy_drag
        ax = Fx / mass
        ay = Fy / mass

        # Update velocity and position
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt

        # Check if projectile hits the other cannon
        target_cannon = players[(turn + 1) % len(players)]  # Target is the other cannon
        if check_hit(x, y, target_cannon):
            scores[turn] += 1  # Increase score for the current player
            print(f"Player {turn + 1} hit the other cannon! Score: {scores[turn]}")
            change_player()  # Switch to the next player
            shooting = False  # Stop shooting when target is hit

        # If the projectile goes out of bounds, change player
        elif not is_inside_field(x, y):
            change_player()
            shooting = False

        # Clear the screen
    screen.fill(BLACK)

    # Draw grid if enabled
    if show_grid:
        draw_grid(screen, RED, x_grid, y_grid, width, height)

    # Draw each cannon
    for cannon in players:
        draw_cannon(screen, cannon, angle if players[turn] == cannon else 0)

    # Convert and draw projectile
    x_pix, y_pix = convert(x, y)
    ball_radius_pix = round(scale_real_to_screen * ball_radius)
    pygame.draw.circle(screen, ball_color, (x_pix, y_pix), ball_radius_pix)

    # Draw wind arrow
    draw_wind(screen, wind_x, wind_y, WIND_COLOR)

    # Draw centered score text
    score_text = f"Scores - Cannon 1: {scores[0]} | Cannon 2: {scores[1]}"
    font = pygame.font.SysFont(None, 36)
    text = font.render(score_text, True, WHITE)
    text_rect = text.get_rect(center=(screen_width // 2, 30))  # Center horizontally at y=30
    screen.blit(text, text_rect)

    # Draw round counter
    round_text = f"Round: {round_counter} / {total_rounds}"
    round_text_surface = font.render(round_text, True, WHITE)
    round_text_rect = round_text_surface.get_rect(center=(screen_width // 2, 70))  # Below score display
    screen.blit(round_text_surface, round_text_rect)

    # Refresh display
    pygame.display.flip()
    clock.tick(frames_per_second)

# Quit pygame
pygame.quit()
sys.exit()


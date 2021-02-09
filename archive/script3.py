# Import the pygame library and initialise the game engine
import pygame
import time
import sys

# pygame.init()
pygame.display.init()
pygame.font.init()
myfont = pygame.font.SysFont('MS Comic Sans', 62)
# pygame.mixer.init() # Disable Sound

# Define some colors
BLACK = ( 0, 0, 0)
WHITE = ( 255, 255, 255)
GREEN = ( 0, 255, 0)
RED = ( 255, 0, 0)
BLUE = ( 0, 0, 255)

# Line 1 config
x = 50
y = 50
width = 40
height = 60
vel = 5

# Open a new window
(width, height) = (640, 480)
screen = pygame.display.set_mode((width, height))
pygame.mouse.set_visible(False)

# background
background_image = pygame.image.load("edge_dash.png").convert()
screen.blit(background_image, [0, 0])
pygame.display.flip()

FPSCLOCK = pygame.time.Clock()
startpoint = pygame.math.Vector2(120, 240) # Center Point of arc
startpoint_2 = pygame.math.Vector2(500, 240) # Center Point of arc
endpoint = pygame.math.Vector2(80, 0) # Length of the arm

# 0 = Point to the right
# 90 = point down, the rest you can work out

angle = 135 # Start Angle 90+45
done = False
run_count = 0

while not done:
    # The current endpoint is the startpoint vector + the
    # rotated original endpoint vector.
    current_endpoint = startpoint + endpoint.rotate(angle)
    current_endpoint_2 = startpoint_2 + endpoint.rotate(angle)
    pygame.draw.line(screen, BLACK, startpoint, current_endpoint, 3)
    pygame.draw.line(screen, BLACK, startpoint_2, current_endpoint_2, 3)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    if run_count <= 54:
      # % 360 to keep the angle between 0 and 360.
      angle = (angle+5) % 360 # 360 - 90 = MAX = 270
    if run_count > 54:
      # % 360 to keep the angle between 0 and 360.
      angle = (angle-5) % 360 # 360 - 90 = MAX = 270
    if run_count == 108:
      done = True

#    screen.fill((0, 0, 0))
# Logo
    background_image = pygame.image.load("edge_dash.png").convert()
    screen.blit(background_image, [0, 0])

# SPEED gauge
#    pygame.draw.circle(screen, RED, [120, 240], 120, 3)
    pygame.draw.line(screen, BLUE, startpoint, current_endpoint, 3)
    textsurface_SPEED = myfont.render(str(run_count), True, RED, BLACK)
    textRect_SPEED = textsurface_SPEED.get_rect()
    textRect_SPEED.center = (120, 320)
    screen.blit(textsurface_SPEED,textRect_SPEED)
# RPM gauge
#    pygame.draw.circle(screen, BLUE, [500, 240], 120, 3)
    pygame.draw.line(screen, RED, startpoint_2, current_endpoint_2, 3)
    textsurface_RPM = myfont.render(str(run_count*100), True, RED, BLACK)
    textRect_RPM = textsurface_RPM.get_rect()
    textRect_RPM.center = (500, 320)
    screen.blit(textsurface_RPM,textRect_RPM)

    pygame.display.flip()
    FPSCLOCK.tick(120)

    run_count = run_count + 1

pygame.quit()
sys.exit()

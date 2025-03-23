import pygame
import noise
import random
import sys

MAP_WIDTH = 50
MAP_HEIGHT = 50
TILE_SIZE = 10
NOISE_SCALE = 0.05
OCTAVES = 6
PERSISTENCE = 0.5
LACUNARITY = 2.0
THRESHOLD = 0.25
FLOOR_TEXTURE_SCALE = 0.3
FLOOR_OCTAVES = 4
FLOOR_PERSISTENCE = 0.5
FLOOR_LACUNARITY = 2.0
WALL_COLOR = (0, 0, 0)
FLOOR_BASE_COLOR = (100, 100, 100)
FLOOR_COLOR_VARIATION = 120

pygame.init()
screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE), pygame.RESIZABLE)
clock = pygame.time.Clock()

def generate_map(s):
    m = [[0]*MAP_WIDTH for _ in range(MAP_HEIGHT)]
    f = [[0]*MAP_WIDTH for _ in range(MAP_HEIGHT)]
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if x == 0 or x == MAP_WIDTH - 1 or y == 0 or y == MAP_HEIGHT - 1:
                m[y][x] = 1
            else:
                v = noise.pnoise2(
                    (x + s*10) * NOISE_SCALE,
                    (y + s*10) * NOISE_SCALE,
                    octaves=OCTAVES,
                    persistence=PERSISTENCE,
                    lacunarity=LACUNARITY,
                    repeatx=999999,
                    repeaty=999999,
                    base=0
                )
                m[y][x] = 1 if v > THRESHOLD else 0
            fv = noise.pnoise2(
                (x + s*10) * FLOOR_TEXTURE_SCALE,
                (y + s*10) * FLOOR_TEXTURE_SCALE,
                octaves=FLOOR_OCTAVES,
                persistence=FLOOR_PERSISTENCE,
                lacunarity=FLOOR_LACUNARITY,
                repeatx=999999,
                repeaty=999999,
                base=1
            )
            f[y][x] = fv
    return m, f

sd = random.randint(0, 999999)
level_map, floor_map = generate_map(sd)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                sd = random.randint(0, 999999)
                level_map, floor_map = generate_map(sd)
            elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False
    screen.fill(FLOOR_BASE_COLOR)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if level_map[y][x] == 1:
                pygame.draw.rect(screen, WALL_COLOR, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
            else:
                n = (floor_map[y][x] + 1) / 2
                var = int((n * 2 - 1) * FLOOR_COLOR_VARIATION)
                base_val = FLOOR_BASE_COLOR[0]
                c = max(0, min(255, base_val + var))
                pygame.draw.rect(screen, (c, c, c), (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
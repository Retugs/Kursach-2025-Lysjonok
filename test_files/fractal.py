import pygame
import noise
import random
import sys

# Настройки окна и сетки
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20  # размер ячейки сетки в пикселях
COLS = WIDTH // GRID_SIZE
ROWS = HEIGHT // GRID_SIZE

# Параметры фрактального шума (Perlin Noise)
SCALE = 20.0  # масштаб шума, влияет на размер паттернов
OCTAVES = 4  # количество октав для создания деталей
PERSISTENCE = 0.5  # амплитудное уменьшение каждой октавы
LACUNARITY = 2.0  # частотное увеличение каждой октавы
THRESHOLD = 0.1  # пороговое значение: выше – ячейка считается стеной, ниже – пол


def generate_room(seed):
    """
    Генерирует 2D-карту комнаты с использованием Perlin Noise.
    Возвращает двумерный список (grid), где 1 означает стену, а 0 – проходимое пространство.
    """
    grid = []
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            # Вычисляем значение шума для координаты (x, y)
            n = noise.pnoise2(x / SCALE,
                              y / SCALE,
                              octaves=OCTAVES,
                              persistence=PERSISTENCE,
                              lacunarity=LACUNARITY,
                              repeatx=COLS,
                              repeaty=ROWS,
                              base=seed)
            # Если значение шума больше порога, ячейка считается стеной (1)
            cell = 1 if n > THRESHOLD else 0
            row.append(cell)
        grid.append(row)
    return grid


def draw_room(screen, grid):
    """
    Отрисовывает карту комнаты на экране.
    Стены рисуются в сером цвете, пол — в тёмном.
    """
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            if cell:
                pygame.draw.rect(screen, (100, 100, 100), rect)
            else:
                pygame.draw.rect(screen, (30, 30, 30), rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Procedurally Generated Room Prototype")

    # Изначальный seed для генерации уровня
    seed = random.randint(0, 1000)
    grid = generate_room(seed)

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # При нажатии клавиши R происходит генерация нового уровня
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    seed = random.randint(0, 1000)
                    grid = generate_room(seed)

        screen.fill((0, 0, 0))
        draw_room(screen, grid)

        # Отображаем инструкцию для игрока
        text = font.render("Press 'R' to regenerate the room", True, (200, 200, 200))
        screen.blit(text, (20, 20))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
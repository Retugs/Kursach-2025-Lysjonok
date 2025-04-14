import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from shapely.geometry import Polygon as ShPolygon, LineString
from shapely.ops import nearest_points

# Параметры
a = 5
num_main = 20      # количество основных комнат
num_side = 52     # количество побочных комнат
num_bonus = 3    # количество бонусных (конусных) комнат

def generate_polygon(center, a, n_vertices=None):
    """
    Генерирует случайный выпуклый многоугольник с центром center.
    Количество вершин случайно от 4 до 6 (если не задано).
    Радиус выбирается так, чтобы длина стороны была от a до 3a.
    """
    if n_vertices is None:
        n_vertices = random.randint(4, 8)
    center = np.array(center)
    base_angles = np.linspace(0, 2*np.pi, n_vertices, endpoint=False)
    angles = [angle + random.uniform(-np.pi/(4*n_vertices), np.pi/(4*n_vertices)) for angle in base_angles]
    angles = np.sort(angles)
    R_min = a / (2 * np.sin(np.pi / n_vertices))
    R_max = 3*a / (2 * np.sin(np.pi / n_vertices))
    vertices = []
    for angle in angles:
        rad = random.uniform(R_min, R_max)
        x = center[0] + rad * np.cos(angle)
        y = center[1] + rad * np.sin(angle)
        vertices.append((x, y))
    return vertices

def room_polygon(center, a, n_vertices=None):
    """
    Возвращает список вершин и shapely-полигон для комнаты.
    """
    verts = generate_polygon(center, a, n_vertices)
    poly = ShPolygon(verts)
    return verts, poly

def check_room_intersection(candidate_poly, rooms):
    """
    Проверяет, пересекается или касается candidate_poly (shapely Polygon)
    с полигонами в rooms (список словарей с ключом 'poly').
    """
    for room in rooms:
        if candidate_poly.intersects(room['poly']) or candidate_poly.touches(room['poly']):
            return True
    return False

def generate_main_rooms(num_main, a):
    main_rooms = []
    iterations_limit = 100
    current_center = (0, 0)
    # Первая комната
    verts, poly = room_polygon(current_center, a)
    main_rooms.append({'center': current_center, 'verts': verts, 'poly': poly, 'type': 'main'})
    for i in range(1, num_main):
        success = False
        iter_count = 0
        while not success and iter_count < iterations_limit:
            iter_count += 1
            # Новая комната в правой полуплоскости; расстояние теперь от 4a до 7a
            dx = random.uniform(4*a, 6*a)
            dy = random.uniform(-a, a)
            new_center = (current_center[0] + dx, current_center[1] + dy)
            verts, poly = room_polygon(new_center, a)
            if not check_room_intersection(poly, main_rooms):
                main_rooms.append({'center': new_center, 'verts': verts, 'poly': poly, 'type': 'main'})
                current_center = new_center
                success = True
        if not success:
            print(f"Не удалось сгенерировать основную комнату {i} после {iter_count} итераций")
    return main_rooms

def generate_side_rooms(main_rooms, num_side, a):
    side_rooms = []
    iterations_limit = 100
    # Родительские комнаты: не первая и не последняя
    possible_indices = list(range(1, len(main_rooms)-1))
    for i in range(num_side):
        success = False
        iter_count = 0
        while not success and iter_count < iterations_limit:
            iter_count += 1
            parent_idx = random.choice(possible_indices)
            parent_center = main_rooms[parent_idx]['center']
            # Генерируем комнату в верхней или нижней полуплоскости относительно родителя
            angle = random.choice([np.pi/2, -np.pi/2]) + random.uniform(-np.pi/8, np.pi/8)
            distance = random.uniform(4*a, 7*a)  # увеличенный диапазон
            new_center = (parent_center[0] + distance * np.cos(angle),
                          parent_center[1] + distance * np.sin(angle))
            verts, poly = room_polygon(new_center, a)
            if not check_room_intersection(poly, main_rooms + side_rooms):
                side_rooms.append({'center': new_center, 'verts': verts, 'poly': poly, 'type': 'side', 'parent': parent_idx})
                success = True
        if not success:
            print(f"Не удалось сгенерировать побочную комнату после {iter_count} итераций")
    return side_rooms

def generate_bonus_rooms(main_rooms, side_rooms, num_bonus, a):
    bonus_rooms = []
    iterations_limit = 100
    # Теперь бонусные комнаты генерируются ТОЛЬКО относительно побочных комнат
    if not side_rooms:
        return bonus_rooms
    for i in range(num_bonus):
        success = False
        iter_count = 0
        while not success and iter_count < iterations_limit:
            iter_count += 1
            parent = random.choice(side_rooms)
            parent_center = parent['center']
            angle = random.uniform(0, 2*np.pi)
            distance = random.uniform(4*a, 7*a)  # увеличенный диапазон
            new_center = (parent_center[0] + distance * np.cos(angle),
                          parent_center[1] + distance * np.sin(angle))
            verts, poly = room_polygon(new_center, a)
            if not check_room_intersection(poly, main_rooms + side_rooms + bonus_rooms):
                bonus_rooms.append({'center': new_center, 'verts': verts, 'poly': poly, 'type': 'bonus', 'parent': parent})
                success = True
        if not success:
            print(f"Не удалось сгенерировать бонусную комнату после {iter_count} итераций")
    return bonus_rooms

def generate_corridor(room_a, room_b):
    """
    Генерирует прямую линию (LineString) между ближайшими точками на границах room_a и room_b.
    Использует shapely.ops.nearest_points.
    """
    pts = nearest_points(room_a['poly'].boundary, room_b['poly'].boundary)
    return LineString([pts[0], pts[1]])

def check_corridor_intersection(corridor, room_a, room_b, all_rooms):
    """
    Проверяет, пересекает ли corridor (LineString) любую комнату из all_rooms, кроме room_a и room_b.
    """
    for room in all_rooms:
        if room == room_a or room == room_b:
            continue
        if corridor.intersects(room['poly']) or corridor.touches(room['poly']):
            return True
    return False

# Генерация комнат
main_rooms = generate_main_rooms(num_main, a)
side_rooms = generate_side_rooms(main_rooms, num_side, a)
bonus_rooms = generate_bonus_rooms(main_rooms, side_rooms, num_bonus, a)
all_rooms = main_rooms + side_rooms + bonus_rooms

# Генерация коридоров
corridors = []
iterations_limit = 100

# Коридоры между основными комнатами (последовательные)
for i in range(1, len(main_rooms)):
    success = False
    iter_count = 0
    while not success and iter_count < iterations_limit:
        iter_count += 1
        corridor = generate_corridor(main_rooms[i-1], main_rooms[i])
        if not check_corridor_intersection(corridor, main_rooms[i-1], main_rooms[i], all_rooms):
            corridors.append(corridor)
            success = True
        else:
            # Если коридор конфликтует, перегенерируем основную комнату main_rooms[i]
            dx = random.uniform(4*a, 7*a)
            dy = random.uniform(-a, a)
            new_center = (main_rooms[i-1]['center'][0] + dx, main_rooms[i-1]['center'][1] + dy)
            verts, poly = room_polygon(new_center, a)
            if not check_room_intersection(poly, main_rooms[:i]):
                main_rooms[i] = {'center': new_center, 'verts': verts, 'poly': poly, 'type': 'main'}
    if not success:
        print(f"Не удалось сгенерировать корректный коридор между основными комнатами {i-1} и {i} после {iter_count} итераций")

# Коридоры для побочных комнат
for room in side_rooms:
    parent_idx = room['parent']
    success = False
    iter_count = 0
    while not success and iter_count < iterations_limit:
        iter_count += 1
        corridor = generate_corridor(main_rooms[parent_idx], room)
        if not check_corridor_intersection(corridor, main_rooms[parent_idx], room, all_rooms):
            corridors.append(corridor)
            success = True
        else:
            # Перегенерируем побочную комнату
            parent_center = main_rooms[parent_idx]['center']
            angle = random.choice([np.pi/2, -np.pi/2]) + random.uniform(-np.pi/8, np.pi/8)
            distance = random.uniform(4*a, 7*a)
            new_center = (parent_center[0] + distance * np.cos(angle),
                          parent_center[1] + distance * np.sin(angle))
            verts, poly = room_polygon(new_center, a)
            if not check_room_intersection(poly, all_rooms):
                room['center'] = new_center
                room['verts'] = verts
                room['poly'] = poly
    if not success:
        print(f"Не удалось сгенерировать корректный коридор для побочной комнаты после {iter_count} итераций")

# Коридоры для бонусных комнат (только от побочных)
for room in bonus_rooms:
    parent = room['parent']
    success = False
    iter_count = 0
    while not success and iter_count < iterations_limit:
        iter_count += 1
        corridor = generate_corridor(parent, room)
        if not check_corridor_intersection(corridor, parent, room, all_rooms):
            corridors.append(corridor)
            success = True
        else:
            # Перегенерируем бонусную комнату
            parent_center = parent['center']
            angle = random.uniform(0, 2*np.pi)
            distance = random.uniform(4*a, 7*a)
            new_center = (parent_center[0] + distance * np.cos(angle),
                          parent_center[1] + distance * np.sin(angle))
            verts, poly = room_polygon(new_center, a)
            if not check_room_intersection(poly, all_rooms):
                room['center'] = new_center
                room['verts'] = verts
                room['poly'] = poly
    if not success:
        print(f"Не удалось сгенерировать корректный коридор для бонусной комнаты после {iter_count} итераций")

# Визуализация
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_aspect('equal')
ax.set_title('Процедурная генерация этажа с прямыми коридорами (расстояние 4a-7a)')

def plot_polygon(verts, color):
    poly_patch = patches.Polygon(verts, closed=True, edgecolor='black', facecolor=color, alpha=0.7, lw=2)
    ax.add_patch(poly_patch)

# Отрисовка всех комнат
for room in all_rooms:
    if room['type'] == 'main':
        color = 'orange'
    elif room['type'] == 'side':
        color = 'red'
    elif room['type'] == 'bonus':
        color = 'green'
    else:
        color = 'gray'
    plot_polygon(room['verts'], color)

# Отрисовка коридоров (прямые линии)
for corridor in corridors:
    x, y = corridor.xy
    ax.plot(x, y, color='blue', linewidth=2)

plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)
plt.show()

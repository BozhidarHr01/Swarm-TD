from settings import *
import pytmx
import os
from os.path import join
import random

class Room:
    def __init__(self, path, doors=None):
        # path: path to tmx file
        # doors: dict {'top': False, 'bottom': False, 'left': True, 'right': False}

        self.path = path
        self.tmx = pytmx.load_pygame(path)
        self.doors = doors or {'top': False, 'bottom': False, 'left': False, 'right': False}
        self.width = self.tmx.width
        self.height = self.tmx.height
        
        # enemy spawning for each room
        self.enemies_spawned = False
        self.spawn_points = []
        self.enemies = []
        self.loot_spawned = False
        self.is_start = False

        # minimap state
        self.visited = False
        self.cleared = False

def import_rooms():
    # import normal rooms and the start room
    rooms = []
    start_room = None

    for filename in os.listdir(ROOMS_DIR):
        if not filename.endswith('.tmx'):
            continue

        path = join(ROOMS_DIR, filename)
        tmx = pytmx.load_pygame(path) 

        # detect doors from a 'doors' object layer
        doors = {'top': False, 'bottom': False, 'left': False, 'right': False}
        for obj in tmx.get_layer_by_name('doors'):
            if hasattr(obj, 'name') and obj.name.lower() in doors:
                doors[obj.name.lower()] = True

        room = Room(path, doors)

        # detect start room
        if 'start' in filename.lower():
            start_room = room
        else:
            rooms.append(room)

    return start_room, rooms

def generate_map_with_positions(start_room, rooms, max_rooms):
    placed = {(0, 0): start_room}
    positions = {(0, 0): (0, 0)}
    start_room.pos = (0, 0)

    # get open doors of the start room
    available_doors = [((0, 0), direction) for direction, open in start_room.doors.items() if open]

    # expand rooms while there are available open doors
    while available_doors and len(placed) < max_rooms:
        # pick a random door to expand, then remove it so it doesnt get used twice
        (gx, gy), direction = random.choice(available_doors)
        available_doors.remove(((gx, gy), direction))

        # pick a candidate room that has a door matching the opposite
        candidates = [r for r in rooms if r.doors.get(opposite_direction(direction), False)]
        if not candidates:
            candidates = rooms  # fallback

        template_room = random.choice(candidates)
        room = Room(template_room.path, template_room.doors.copy())
        new_grid = get_new_grid((gx, gy), direction)
        if new_grid in placed:
            continue

        room.pos = new_grid
        placed[new_grid] = room
        positions[new_grid] = (new_grid[0] * room.width * TILE_SIZE,
                               new_grid[1] * room.height * TILE_SIZE)

        # add new doors
        for d, open in room.doors.items():
            if open and d != opposite_direction(direction):
                new_pos = get_new_grid(new_grid, d)
                if new_pos not in placed:
                    available_doors.append((new_grid, d))

    # after all rooms are placed add closed doors for each room
    for (gx, gy), room in placed.items():
        room.closed_doors = []
        for direction, has_door in room.doors.items():
            adjacent_pos = get_new_grid((gx, gy), direction)
            if has_door and adjacent_pos not in placed:
                room.closed_doors.append(direction)

    return placed, positions

def opposite_direction(direction):
    return {'top':'bottom', 'bottom':'top', 'left':'right', 'right':'left'}[direction]

def get_new_grid(grid, direction):
    # calculates new grid coordinates
    # if current is (0,0) and direction is right returns (1,0)
    gx, gy = grid
    if direction == 'top': return (gx, gy-1)
    if direction == 'bottom': return (gx, gy+1)
    if direction == 'left': return (gx-1, gy)
    if direction == 'right': return (gx+1, gy)

def add_room_colliders_with_doors(placed, positions, all_sprites, collision_sprites, tile_size=2 * TILE_SIZE, door_size=DOOR_SIZE):
    # adds colliders to all walls with no adjacent rooms

    # load textures once outsite the collider
    WALL_TOP    = pygame.image.load(join('maps','tsx','tboi','door','up.png')).convert_alpha()
    WALL_BOTTOM = pygame.image.load(join('maps','tsx','tboi','door','down.png')).convert_alpha()
    WALL_LEFT   = pygame.image.load(join('maps','tsx','tboi','door','left.png')).convert_alpha()
    WALL_RIGHT  = pygame.image.load(join('maps','tsx','tboi','door','right.png')).convert_alpha()

    TEXTURES = {
        'top': WALL_TOP,
        'bottom': WALL_BOTTOM,
        'left': WALL_LEFT,
        'right': WALL_RIGHT
    }

    class Collider(pygame.sprite.Sprite):
        def __init__(self, rect, direction, groups):
            super().__init__(groups)
            self.rect = rect
            self.old_rect = self.rect

            img = TEXTURES[direction]
            self.image = pygame.transform.scale(img, (rect.width, rect.height))
    
    for (gx, gy), room in placed.items():
        px, py = positions[(gx, gy)]
        w, h = room.width * tile_size , room.height * tile_size

        # get neighbor room helper
        def neighbor(pos, direction):
            dx, dy = {'top':(0,-1),'bottom':(0,1),'left':(-1,0),'right':(1,0)}[direction]
            return placed.get((pos[0]+dx,pos[1]+dy))

        for direction in ['top','bottom','left','right']:
            if not (room.doors.get(direction) and neighbor((gx,gy), direction)):
                if direction == 'top':
                    Collider(pygame.Rect(px, py, w, 2 * tile_size), direction, (all_sprites, collision_sprites))
                elif direction == 'bottom':
                    Collider(pygame.Rect(px, py+h-2 * tile_size, w, 2 * tile_size), direction, (all_sprites, collision_sprites))
                elif direction == 'left':
                    Collider(pygame.Rect(px, py, 2 *tile_size, h), direction, (all_sprites, collision_sprites))
                elif direction == 'right':
                    Collider(pygame.Rect(px+w-2 * tile_size, py, 2 *tile_size, h), direction, (all_sprites, collision_sprites))

    return placed, positions

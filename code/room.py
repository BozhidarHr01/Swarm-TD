from settings import *
from sprites import *
import pytmx
from collections import deque
import random

class Room:
    def __init__(self, tmx_path, wall_config):
        """
        wall_config example:
        {
            "top": True, 
            "bottom": False,
            "left": False,
            "right": True
        }
        """
        self.tmx_path = tmx_path
        self.tmx = pytmx.load_pygame(tmx_path)
        self.walls = wall_config

        self.width = self.tmx.width
        self.height = self.tmx.height

    def compatible(self, b, direction: str):
        if direction == "right":
            return (not self.walls["right"]) and (not b.walls["left"])
        if direction == "left":
            return (not self.walls["left"]) and (not b.walls["right"])
        if direction == "top":
            return (not self.walls["top"]) and (not b.walls["bottom"])
        if direction == "bottom":
            return (not self.walls["bottom"]) and (not b.walls["top"])
        return False
    
def generate_map_with_positions(start_room, room_list, max_rooms=7):
    """
    Generate a map using rooms, repeating rooms if needed.
    Returns:
        placed: {(grid_x, grid_y): Room}
        positions: {(grid_x, grid_y): (pixel_x, pixel_y)}
    """
    placed = {}
    positions = {}
    queue = deque()

    # Start with the first room at (0,0)
    placed[(0, 0)] = start_room
    positions[(0, 0)] = (0, 0)
    queue.append((0, 0, start_room))

    dirs = {
        "left": (-1, 0),
        "right": (1, 0),
        "top": (0, -1),
        "bottom": (0, 1)
    }

    rooms_placed = 1

    while queue and rooms_placed < max_rooms:
        x, y, room = queue.popleft()
        px, py = positions[(x, y)]

        for direction, (dx, dy) in dirs.items():
            nx, ny = x + dx, y + dy
            if (nx, ny) in placed:
                continue

            random.shuffle(room_list)
            for candidate in room_list:
                if Room.compatible(room, candidate, direction):
                    placed[(nx, ny)] = candidate

                    # Calculate pixel positions based on room dimensions
                    if direction == "left":
                        positions[(nx, ny)] = (px - candidate.width * TILE_SIZE, py)
                    elif direction == "right":
                        positions[(nx, ny)] = (px + room.width * TILE_SIZE, py)
                    elif direction == "top":
                        positions[(nx, ny)] = (px, py - candidate.height * TILE_SIZE)
                    elif direction == "bottom":
                        positions[(nx, ny)] = (px, py + room.height * TILE_SIZE)

                    queue.append((nx, ny, candidate))
                    rooms_placed += 1
                    break

            if rooms_placed >= max_rooms:
                break

    return placed, positions

def random_wall_config():
    """
    Choose one of four sides and set its wall_config to have a wall
    """
    sides = ["top", "bottom", "left", "right"]
    chosen = random.choice(sides)
    
    config = {side: False for side in sides}
    config[chosen] = True
    return config

def import_rooms():
    start_room = Room(join("maps", "tsx", "start.tmx"), {"top": False, "bottom": False, "left": False, "right": False})

    rooms = [
        Room(join("maps", "tsx", "4.tmx"), random_wall_config()),
        Room(join("maps", "tsx", "1.tmx"), random_wall_config()),
        Room(join("maps", "tsx", "2.tmx"), random_wall_config()),
        Room(join("maps", "tsx", "3.tmx"), random_wall_config()),
        Room(join("maps", "tsx", "5.tmx"), random_wall_config()),
        Room(join("maps", "tsx", "4.tmx"), random_wall_config()),

        # add more rooms...
    ]

    return start_room, rooms

def add_walls(placed, positions, wall_horizontal_up, wall_horizontal_down, wall_vertical_left, wall_vertical_right):
    """
    Adds wall rooms on the edges of each room that have no neighbor.
    placed: dict of grid coords → Room
    positions: dict of grid coords → pixel coords
    Returns updated dict with wall rooms.
    """
    new_placed = dict(placed)
    
    for (gx, gy), room in placed.items():
        px, py = positions[(gx, gy)]
        room_width_px = room.width * TILE_SIZE
        room_height_px = room.height * TILE_SIZE

        # neighbors in grid
        neighbors = {
            "top": (gx, gy - 1),
            "bottom": (gx, gy + 1),
            "left": (gx - 1, gy),
            "right": (gx + 1, gy)
        }

        for direction, (nx, ny) in neighbors.items():
            if (nx, ny) not in placed:
                # Create a wall room for this direction
                if direction == "top":
                    wall = Room(wall_horizontal_up.tmx_path, wall_horizontal_up.walls)
                    positions[(nx, ny)] = (px, py - wall.height * TILE_SIZE)
                elif direction == "bottom":
                    wall = Room(wall_horizontal_down.tmx_path, wall_horizontal_down.walls)
                    positions[(nx, ny)] = (px, py + room_height_px)
                elif direction == "left":
                    wall = Room(wall_vertical_left.tmx_path, wall_vertical_left.walls)
                    positions[(nx, ny)] = (px - wall.width * TILE_SIZE, py)
                elif direction == "right":
                    wall = Room(wall_vertical_right.tmx_path, wall_vertical_right.walls)
                    positions[(nx, ny)] = (px + room_width_px, py)

                new_placed[(nx, ny)] = wall

    return new_placed, positions

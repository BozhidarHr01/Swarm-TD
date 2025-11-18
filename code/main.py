from settings import * 
from player import Player
from sprites import *

from groups import AllSprites
from room import Room, generate_map_with_positions, import_rooms, add_walls

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Swarm TD")
        self.clock = pygame.time.Clock()
        self.running = True

        # camera zoom
        self.camera_zoom = CAMERA_ZOOM
        self.camera_width = int(CAMERA_WIDTH / self.camera_zoom)
        self.camera_height = int(CAMERA_HEIGHT / self.camera_zoom)
        self.camera_surface = pygame.Surface((self.camera_width, self.camera_height))
        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

        self.setup()

    def setup(self):
        start_room, rooms = import_rooms()
        placed, positions = generate_map_with_positions(start_room, rooms, max_rooms=ROOM_COUNT)

        # wall templates
        wall_horizontal_up = Room(join("maps", "tsx", "walls_everywhere.tmx"), {"top": True, "bottom": True, "left": True, "right": True})
        wall_horizontal_down = Room(join("maps", "tsx", "walls_everywhere.tmx"), {"top": True, "bottom": True, "left": True, "right": True})
        wall_vertical_left = Room(join("maps", "tsx", "walls_everywhere.tmx"), {"top": True, "bottom": True, "left": True, "right": True})
        wall_vertical_right = Room(join("maps", "tsx", "walls_everywhere.tmx"), {"top": True, "bottom": True, "left": True, "right": True})

        # Add walls
        placed, positions = add_walls(placed, positions, wall_horizontal_up, wall_horizontal_down, wall_vertical_left, wall_vertical_right)

        # Render all rooms
        for (gx, gy), room in placed.items():
            px, py = positions[(gx, gy)]
            
            # Floors
            for x, y, image in room.tmx.get_layer_by_name('floor').tiles():
                Sprite((px + x*TILE_SIZE, py + y*TILE_SIZE), image, self.all_sprites, True)
            
            # Collisions
            for obj in room.tmx.get_layer_by_name('collisions'):
                Sprite((px + obj.x, py + obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
            
            # Walls & objects
            for layer in ['walls','objects']:
                for x, y, image in room.tmx.get_layer_by_name(layer).tiles():
                    Sprite((px + x*TILE_SIZE, py + y*TILE_SIZE), image, self.all_sprites)

            # Player
            for obj in room.tmx.get_layer_by_name('entities'):
                if obj.name == 'Player':
                    self.player = Player((px + obj.x, py + obj.y), self.all_sprites, self.collision_sprites)

    def run(self):
        while self.running:
            # dt
            dt = self.clock.tick() / 1000
            
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # zoom camera with scroll
                if event.type == pygame.MOUSEWHEEL:
                    self.camera_zoom += event.y * 0.1
                    self.camera_zoom = max(0.1, min(self.camera_zoom, 4))
                    self.camera_width = int(CAMERA_WIDTH / self.camera_zoom)
                    self.camera_height = int(CAMERA_HEIGHT / self.camera_zoom)
                    self.camera_surface = pygame.Surface((self.camera_width, self.camera_height))

            # update
            self.all_sprites.update(dt)

            # draw
            self.camera_surface.fill('#1d1c2b')
            self.all_sprites.draw(self.player.rect.center, self.camera_surface)

            zoomed_view = pygame.transform.scale(self.camera_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.display_surface.blit(zoomed_view, (0, 0))
            pygame.display.flip()
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()

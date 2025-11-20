from settings import * 
from player import Player
from sprites import *

from groups import AllSprites
from room import Room, generate_map_with_positions, import_rooms, add_walls
from random import randint, choice

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
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # attack timer
        self.can_shoot = True
        self.shoot_time = 0
        self.attack_cooldown = 200 # 200ms

        # enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_positions = []

        self.load_images()
        self.setup()

    def load_images(self):
        self.bullet_surf = pygame.image.load(join('images', 'fireball', 'fireball.png')).convert_alpha()
        self.bullet_surf = pygame.transform.scale(self.bullet_surf, (16, 16))

        folders = list(walk(join('images', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in file_names:
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            pos = self.player.rect.center + self.player.direction * 10
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            direction_x = mouse_x - WINDOW_WIDTH / 2
            direction_y = mouse_y - WINDOW_HEIGHT / 2
            direction = pygame.Vector2(direction_x, direction_y).normalize()

            Bullet(self.bullet_surf, pos, direction, (self.all_sprites, self.bullet_sprites), self.collision_sprites)

            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def attack_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.attack_cooldown:
                self.can_shoot = True

    def setup(self):
        start_room, rooms = import_rooms()
        placed, positions = generate_map_with_positions(start_room, rooms, max_rooms=ROOM_COUNT)

        # wall templates
        wall_horizontal_up = Room(join("maps", "tsx", "walls_everywhere.tmx"), 
                                  {"top": True, "bottom": True, "left": True, "right": True})
        wall_horizontal_down = Room(join("maps", "tsx", "walls_everywhere.tmx"), 
                                    {"top": True, "bottom": True, "left": True, "right": True})
        wall_vertical_left = Room(join("maps", "tsx", "walls_everywhere.tmx"), 
                                  {"top": True, "bottom": True, "left": True, "right": True})
        wall_vertical_right = Room(join("maps", "tsx", "walls_everywhere.tmx"), 
                                   {"top": True, "bottom": True, "left": True, "right": True})
        placed, positions = add_walls(placed, positions, 
                                      wall_horizontal_up, wall_horizontal_down, 
                                      wall_vertical_left, wall_vertical_right)
        
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
                elif obj.name == 'Enemy':
                    self.spawn_positions.append((px + obj.x, py + obj.y))

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    for sprite in collision_sprites:
                        sprite.destroy()
                    bullet.kill()

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.running = False

    def run(self):
        while self.running:
            # dt
            dt = self.clock.tick() / 1000
            
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)

            # zoom camera with scroll
                if event.type == pygame.MOUSEWHEEL:
                    self.camera_zoom += event.y * 0.1
                    self.camera_zoom = max(0.1, min(self.camera_zoom, 4))
                    self.camera_width = int(CAMERA_WIDTH / self.camera_zoom)
                    self.camera_height = int(CAMERA_HEIGHT / self.camera_zoom)
                    self.camera_surface = pygame.Surface((self.camera_width, self.camera_height))

            # update
            self.attack_timer()
            self.input()
            self.all_sprites.update(dt)
            self.bullet_collision()
            # self.player_collision() 

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

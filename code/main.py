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
        self.turret_sprites = pygame.sprite.Group()

        # attack timer
        self.can_shoot = True
        self.shoot_time = 0
        self.attack_cooldown = 200 # 200ms

        # enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_positions = []

        # build mode
        self.build_mode = False
        self.money = STARTING_MONEY

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
        # shooting
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            pos = self.player.rect.center + self.player.direction * 10
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            direction_x = mouse_x - WINDOW_WIDTH / 2
            direction_y = mouse_y - WINDOW_HEIGHT / 2
            direction = pygame.Vector2(direction_x, direction_y).normalize()

            Bullet(self.bullet_surf, pos, direction, (self.all_sprites, self.bullet_sprites), self.collision_sprites, self.enemy_sprites, game=self)

            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def get_mouse_pos(self):
        mx, my = pygame.mouse.get_pos()

        mx /= WINDOW_WIDTH / self.camera_width
        my /= WINDOW_HEIGHT / self.camera_height

        world_x = mx + self.player.rect.centerx - self.camera_width // 2
        world_y = my + self.player.rect.centery - self.camera_height // 2

        return pygame.Vector2(world_x, world_y)
    
    def place_turret(self, pos):
        # print('#', len(self.turret_sprites))
        if len(self.turret_sprites) >= MAX_TURRET_COUNT:
            return
        if self.money < TURRET_COST:
            return
        
        pos.x = round(pos.x / TILE_SIZE) * TILE_SIZE
        pos.y = round(pos.y / TILE_SIZE) * TILE_SIZE

        Turret(pos, pygame.Surface((32,32)), (self.all_sprites, self.turret_sprites), self.bullet_surf,
               (self.all_sprites, self.bullet_sprites), self.all_sprites, self.collision_sprites, self.enemy_sprites, game)
        self.money -= TURRET_COST
        self.build_mode = False
        print('#', len(self.turret_sprites))
        print("$", self.money)

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

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.player.take_damage(ENEMY_DAMAGE)
            if self.player.health <= 0:
                self.running = False


    def run(self):
        while self.running:
            # dt
            dt = self.clock.tick() / 1000
            
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                # spawning enemies on their spawnpoints
                if event.type == self.enemy_event:
                    if len(self.enemy_sprites) < MAX_ENEMY_COUNT:
                        Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites, game=self)
                # turning build mode on and off
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.build_mode = not self.build_mode
                # turret placing
                if self.build_mode and event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        mouse_world_pos = self.get_mouse_pos()
                        self.place_turret(mouse_world_pos)

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


            self.player_collision() 

            # draw
            self.camera_surface.fill('#1d1c2b')
            # self.all_sprites.draw(self.player.rect.center, self.camera_surface)
            
            cam_offset_x = self.player.rect.centerx - self.camera_width // 2
            cam_offset_y = self.player.rect.centery - self.camera_height // 2

            for sprite in self.all_sprites:
                if sprite != self.player:
                    sprite_rect = sprite.rect.copy()
                    sprite_rect.topleft = (sprite.rect.x - cam_offset_x, sprite.rect.y - cam_offset_y)
                    self.camera_surface.blit(sprite.image, sprite_rect)
                
            player_rect = self.player.rect.copy()
            player_rect.topleft = (self.player.rect.x - cam_offset_x, self.player.rect.y - cam_offset_y)
            self.player.draw(self.camera_surface, player_rect)
            
            # Building ghost preview
            if self.build_mode:
                ghost_pos = self.get_mouse_pos()


                ghost_cam_x = ghost_pos.x - cam_offset_x
                ghost_cam_y = ghost_pos.y - cam_offset_y

                ghost_rect = pygame.Rect(ghost_cam_x - 16, ghost_cam_y - 16, 32, 32)
                pygame.draw.rect(self.camera_surface, (0,200,0, 30), ghost_rect)

            zoomed_view = pygame.transform.scale(self.camera_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.display_surface.blit(zoomed_view, (0, 0))


            self.all_sprites.update(dt)
            pygame.display.flip()
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()

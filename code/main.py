from settings import * 
from player import Player
from sprites import *
from turret import Turret
from enemy import *
from bullet import Bullet
from room import *

from groups import AllSprites
from random import randint, choice, choices
from hud import HUD

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Swarm TD')
        self.clock = pygame.time.Clock()
        self.running = True

        # camera zoom
        self.camera_zoom = CAMERA_ZOOM
        self.camera_width = int(CAMERA_WIDTH / self.camera_zoom)
        self.camera_height = int(CAMERA_HEIGHT / self.camera_zoom)
        self.camera_surface = pygame.Surface((self.camera_width, self.camera_height))

        # smooth camera zoom 
        self.target_zoom = CAMERA_ZOOM
        self.zoom_speed = 0.05

        self.camera_pos = pygame.Vector2(0, 0)
        self.camera_target = pygame.Vector2(0, 0)
        self.camera_speed = 0.2

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.turret_sprites = pygame.sprite.Group()
        self.upgrade_sprites = pygame.sprite.Group()
        self.player_sprites = pygame.sprite.Group()
        self.trap_sprites = pygame.sprite.Group()

        # attack timer
        self.can_shoot = True
        self.shoot_time = 0
        self.attack_cooldown = PLAYER_FIRE_RATE # 200ms # fire rate
        self.bullet_lifetime = BULLET_LIFETIME

        # enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_positions = []

        # build mode
        self.build_mode = False
        self.state = 'build'
        self.money = STARTING_MONEY

        # angle for walls
        self.wall_rotation_angle = 0
        self.trap_rotation_angle = 0

        self.portal_spawned = False
        self.kills = 0

        self.enemy_classes = {'goblin' : Enemy, 'vampire' : FlyingEnemy, 'skeleton' : Skeleton}
        self.enemy_types = ['goblin', 'vampire', 'skeleton']

        self.load_images()

        self.setup()
        self.current_room = self.get_player_room()
        self.hud = HUD(self)

    def load_images(self):
        # fireball bullet
        self.bullet_surf = pygame.image.load(join('images', 'bullets', 'fireball.png')).convert_alpha()
        self.bullet_surf = pygame.transform.scale2x(self.bullet_surf)
        self.bullet_surf = pygame.transform.smoothscale(self.bullet_surf, (16,16))
        # bone bullet
        self.bone_bullet = pygame.image.load(join('images', 'bullets', 'bone.png')).convert_alpha()
        self.bone_bullet = pygame.transform.scale2x(self.bone_bullet)
        self.bone_bullet = pygame.transform.smoothscale(self.bone_bullet, (16,16))
        # create a round bullet surface
        bullet_radius = 6
        self.round_bullet_surf = pygame.Surface((bullet_radius*2, bullet_radius*2), pygame.SRCALPHA)

        # draw outer yellow circle
        pygame.draw.circle(self.round_bullet_surf, (20, 120, 120), (bullet_radius, bullet_radius), bullet_radius)

        # draw inner circle
        inner_radius = 4  # smaller radius
        pygame.draw.circle(self.round_bullet_surf, (255, 165, 0), (bullet_radius, bullet_radius), inner_radius)

        # turret
        self.turret_base = pygame.image.load(join('images', 'turret', 'base.png')).convert_alpha()
        self.turret_base = pygame.transform.scale2x(self.turret_base)
        self.turret_base = pygame.transform.smoothscale(self.turret_base, (24,24))
        self.turret_gun = pygame.image.load(join('images', 'turret', 'gun.png')).convert_alpha()
        self.turret_gun = pygame.transform.scale(self.turret_gun, (24,9))
        
        # bomb
        self.bomb_surf = pygame.image.load(join('images', 'bullets','bomb.png')).convert_alpha()
        self.bomb_surf = pygame.transform.scale(self.bomb_surf, (16,16))
        # traps
        # spikes static surf
        self.trap_surf = pygame.image.load(join('images', 'traps', '1.png')).convert_alpha()
        self.trap_surf = pygame.transform.scale(self.trap_surf, (720 // TILE_SIZE, 1280 // TILE_SIZE))
        
        # barbed wire
        self.barbed_wire_surf = pygame.image.load(join('images', 'barbedwire', 'wire.png')).convert_alpha()
        self.barbed_wire_surf= pygame.transform.scale(self.barbed_wire_surf, (100, 67))

        # boss smash cone radius
        self.smash_cone_surf = pygame.image.load(join('images', 'boss','boss_cone_effect.png')).convert_alpha()

        # trap animation frames
        self.trap_frames = []
        trap_folder = join('images', 'traps')
        for i in range(1, 10):
            full_path = join(trap_folder, f'{i if i <= 5 else 1}.png')
            surf = pygame.image.load(full_path).convert_alpha()
            self.trap_frames.append(surf)
        
        self.trap_surf = self.trap_frames[0]

        folders = list(walk(join('images', 'enemies')))[0][1] 
        self.enemy_frames = {}
        for folder in folders:
            folder_path = join('images', 'enemies', folder)
            self.enemy_frames[folder] = {}
            for direction in ['up', 'down', 'left', 'right']:
                direction_path = join(folder_path, direction)
                self.enemy_frames[folder][direction] = []
                for _, _, file_names in walk(direction_path):
                    for file_name in file_names:
                        full_path = join(direction_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        if folder.lower() == 'goblin':
                            surf_big = pygame.transform.scale2x(surf)
                            surf = pygame.transform.smoothscale(surf_big, (int(surf_big.width * 0.075), int(surf_big.height * 0.075)))

                        elif folder.lower() == 'skeleton':
                            surf_big = pygame.transform.scale2x(surf)
                            surf = pygame.transform.scale(surf_big, (int(surf_big.width * 0.35), int(surf_big.height * 0.35)))
                        self.enemy_frames[folder][direction].append(surf)
                        
            # handle boss separately
            if folder.lower() == 'boss':
                self.enemy_frames['boss'] = { 'idle': {}, 'throw': {}, 'smash': {} }

                for state in ['idle','throw', 'smash']:
                    for direction in ['up','down','left','right']:
                        path = join(folder_path, state, direction)
                        frames = []

                        for _, _, files in walk(path):
                            for file_name in files:
                                surf = pygame.image.load(join(path, file_name)).convert_alpha()
                                frames.append(surf)

                        self.enemy_frames['boss'][state][direction] = frames
                continue

    def input(self):
        # shooting
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            if self.build_mode:
                return
            pos = self.player.rect.center + self.player.direction * 10
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            direction_x = mouse_x - WINDOW_WIDTH / 2
            direction_y = mouse_y - WINDOW_HEIGHT / 2
            direction = pygame.Vector2(direction_x, direction_y).normalize()

            mouse_world_pos = self.get_mouse_pos()
            pos = pygame.Vector2(self.player.rect.center)
            direction = (mouse_world_pos - pos).normalize()

            Bullet(self.bullet_surf, pos, direction, self.bullet_lifetime, self.player, (self.all_sprites, self.bullet_sprites), self.collision_sprites, self.enemy_sprites, game=self)

            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def get_mouse_pos(self):
        mx, my = pygame.mouse.get_pos()

        mx /= WINDOW_WIDTH / self.camera_width
        my /= WINDOW_HEIGHT / self.camera_height

        world_x = mx + self.camera_pos.x
        world_y = my + self.camera_pos.y

        return pygame.Vector2(world_x, world_y)
    
    def can_place_at(self, pos, size=TILE_SIZE):
        x = round(pos.x / TILE_SIZE) * TILE_SIZE
        y = round(pos.y / TILE_SIZE) * TILE_SIZE
        test_rect = pygame.Rect(x,y,size,size)

        for sprite in self.collision_sprites:
            if test_rect.colliderect(sprite.rect):
                return False
            
        for sprite in self.turret_sprites:
            if test_rect.colliderect(sprite.rect):
                return False

        return True

    def place_turret(self, pos):
        if len(self.turret_sprites) >= MAX_TURRET_COUNT:
            return
        if self.money < TURRET_COST:
            return
        if not self.can_place_at(pos):
            return
        
        pos.x = round(pos.x / TILE_SIZE) * TILE_SIZE
        pos.y = round(pos.y / TILE_SIZE) * TILE_SIZE

        Turret(pos, self.turret_base, self.turret_gun, (self.all_sprites, self.turret_sprites), self.round_bullet_surf,
               (self.all_sprites, self.bullet_sprites), self.all_sprites, self.collision_sprites, self.enemy_sprites, game)
        self.money -= TURRET_COST

    def place_trap(self, pos, angle = 0):
        if self.money < TRAP_COST:
            return
        if not self.can_place_at(pos):
            return
        
        pos.x = round(pos.x / TILE_SIZE) * TILE_SIZE
        pos.y = round(pos.y / TILE_SIZE) * TILE_SIZE

        Trap(pos, self.trap_surf, (self.all_sprites, self.trap_sprites), animation_frames=self.trap_frames, game=self)

        self.money -= TRAP_COST

    def place_barbed_wire(self, pos, rotation):
        if self.money < BARBED_WIRE_COST:
            return
        if not self.can_place_at(pos):
            return
        
        pos.x = round(pos.x / TILE_SIZE) * TILE_SIZE
        pos.y = round(pos.y / TILE_SIZE) * TILE_SIZE

        BarbedWire(pos, self.barbed_wire_surf, (self.all_sprites, self.trap_sprites), game=self, rotation=rotation)
        self.money -= BARBED_WIRE_COST

    def attack_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.attack_cooldown:
                self.can_shoot = True

    def render_room_to_surface(self, room, tile_size=TILE_SIZE):
        # convert a room tiles into a single surface to imporve performance
        width = room.width * tile_size
        height = room.height * tile_size
        surf = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw layers: floor, walls, objects
        for layer_name in ['floor', 'walls', 'objects']:
            try:
                layer = room.tmx.get_layer_by_name(layer_name)
            except ValueError:
                continue
            for x, y, image in layer.tiles():
                surf.blit(image, (x * tile_size, y * tile_size))

        room.rendered_surface = surf

    def setup(self):
        start_room, rooms = import_rooms()
        start_room.is_start = True
        self.start_room = start_room
        # Place rooms
        placed, positions = generate_map_with_positions(start_room, rooms, max_rooms=ROOM_COUNT)
        print('Rooms placed:', list(placed.keys()))

        self.player = None  # reset
        self.room_positions = positions
        self.rooms = placed

        for (gx, gy), room in placed.items():
            px, py = positions[(gx, gy)]

            self.render_room_to_surface(room)
            
            # Collisions
            for obj in room.tmx.get_layer_by_name('collisions'):
                Sprite((px + obj.x, py + obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

            # Entities
            for obj in room.tmx.get_layer_by_name('entities'):
                if obj.name == 'Player':
                    self.player = Player((px + obj.x, py + obj.y),
                                        self.all_sprites,
                                        self.player_sprites,
                                        self.collision_sprites)
                    self.player_start_pos = (px + obj.x, py + obj.y)
                elif obj.name == 'Enemy':
                    room.spawn_points.append((px + obj.x, py + obj.y))

        self.rooms, self.room_positions = add_room_colliders_with_doors(self.rooms, self.room_positions, self.all_sprites, self.collision_sprites, tile_size=TILE_SIZE, door_size=60)
        
        if self.player is None:
            # fallback: spawn at center of start room
            px, py = positions[(0,0)]
            self.player = Player((px + start_room.width*TILE_SIZE//2,
                                py + start_room.height*TILE_SIZE//2),
                                self.all_sprites,
                                self.player_sprites,
                                self.collision_sprites)
            self.player_start_pos = self.player.rect.center

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.player.take_hit(self, ENEMY_DAMAGE)
            if self.player.health <= 0:
                self.running = False

    # GAME LOOPS
    def run(self, loop_function):
        self.running = True

        while self.running:
            dt = self.clock.tick() / 1000

            loop_function(dt)
            pygame.display.flip()

    def get_player_room(self):
        px, py = self.player.rect.center

        for (gx, gy), (room_x, room_y) in self.room_positions.items():
            room = self.rooms[(gx, gy)]

            room_w = room.width * TILE_SIZE
            room_h = room.height * TILE_SIZE

            if room_x <= px < room_x + room_w and room_y <= py < room_y + room_h:
                return (gx, gy)

        return None

    def spawn_enemies_for_room(self, room):
        if room.enemies_spawned or not room.spawn_points:
            return
        
        num_enemies = randint(MIN_ENEMY_COUNT, MAX_ENEMY_COUNT)
        spawn_points = getattr(room, 'spawn_points', [])
        room.enemies = []
        for _ in range(num_enemies):
            if not spawn_points:
                break

            spawn_pos = choice(spawn_points)
            enemy_type = choice(self.enemy_types)
            frames = self.enemy_frames[enemy_type]
            EnemyClass = self.enemy_classes.get(enemy_type.lower(), Enemy)

            enemy = EnemyClass(spawn_pos, frames, (self.all_sprites, self.enemy_sprites),
                    self.player, self.collision_sprites, game=self)
            
            room.enemies.append(enemy)

        room.enemies_spawned = True

    def check_room_cleared(self, room):
        if getattr(room, 'is_start', False):
            room.cleared=True
            return

        room.enemies = [e for e in room.enemies if e.alive()]
        print(room.loot_spawned)

        if not room.enemies:
            if not getattr(room, 'loot_spawned', False):
                if random.random() < LOOT_DROP_CHANCE:
                    print('loot drop')            
                    
                    if room.spawn_points:
                        spawn_pos = choice(room.spawn_points)
                    
                    min_distance = 50
                    if pygame.Vector2(spawn_pos).distance_to(self.player.rect.center) <= min_distance or spawn_pos in room.spawn_points:
                        spawn_pos = choice(room.spawn_points)

                    names  = [u['name'] for u in UPGRADES]
                    weights = [u['weight'] for u in UPGRADES]
                    upgrade_type = choices(names, weights=weights, k=1)[0]

                    Upgrade(spawn_pos, upgrade_type, (self.all_sprites, self.upgrade_sprites))

                room.loot_spawned = True
            room.cleared = True

    def all_rooms_cleared(self):
        for room in self.rooms.values():
            if not room.cleared and not room.is_start:
                return False
            
        return True
    
    def spawn_portal(self):
        start_x, start_y = self.player_start_pos
        Portal((start_x, start_y), self)

    def enter_boss_room(self):
        self.load_boss_room()
        self.target_zoom = 0.6
        self.camera_zoom += (self.target_zoom - self.camera_zoom) * self.zoom_speed
        self.camera_width = int(CAMERA_WIDTH / self.camera_zoom)
        self.camera_height = int(CAMERA_HEIGHT / self.camera_zoom)
        self.camera_surface = pygame.Surface((self.camera_width, self.camera_height))
        self.rooms = {(0,0): self.boss_room}
        self.room_positions = {(0,0): (0,0)}
        self.current_room = (0,0)
        self.state = 'boss'

    def load_boss_room(self):
        # clear current stage
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.enemy_sprites.empty()
        self.turret_sprites.empty()
        self.bullet_sprites.empty()
        self.trap_sprites.empty()
        self.player_sprites.empty()
        self.upgrade_sprites.empty()
        self.camera_zoom = 0.6
        for sprite in self.all_sprites:
            sprite.kill()
        
        path = join('maps','tsx','tboi','boss_room', 'boss_room.tmx')
        room = Room(path)
        self.boss_room = room

        px, py = 0, 0
        self.render_room_to_surface(room)

        for obj in room.tmx.get_layer_by_name('collisions'):
            Sprite((px + obj.x, py + obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
        
        boss_pos = None
        player_pos = None

        for obj in room.tmx.get_layer_by_name('entities'):
            if obj.name == 'Player':
                player_pos = (px + obj.x, py + obj.y)
            if obj.name == 'Boss':
                boss_pos = (px + obj.x, py + obj.y)

        self.player = Player(player_pos, self.all_sprites, self.player_sprites, self.collision_sprites)

        frames = self.enemy_frames['boss']
        idle_frames = frames['idle']
        throw_frames = frames['throw']
        smash_frames = frames['smash']
        boss = Boss(boss_pos, idle_frames, throw_frames, smash_frames, (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites, self)
        self.boss = boss

    def boss_defeated(self):
        self.state = 'victory'
        self.run(self.victory_screen_loop)

    def victory_screen_loop(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.__init__()
                self.running = False
                self.run(self.start_screen_loop)
                return
        
        self.display_surface.fill((0,0,0))
        title_font = pygame.font.Font(FONT_PATH, 70)
        small_font = pygame.font.Font(FONT_PATH, 36)

        title = title_font.render('Victory!', True, (0,180,0))
        prompt = small_font.render('Press R to play again', True, (255,255,255))

        self.display_surface.blit(title, title.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 40)))
        self.display_surface.blit(prompt, prompt.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 20)))

    def gameplay_loop(self, dt):
        current_room_key = self.get_player_room()
        if current_room_key:
            current_room = self.rooms[current_room_key]
            current_room.visited = True
            self.current_room = current_room_key
            rx, ry = self.room_positions[current_room_key]
            self.camera_target.update(rx, ry)

            # Spawn enemies when entering a room
            self.check_upgrade_pickup()
            self.spawn_enemies_for_room(current_room)
            if not self.portal_spawned:
                self.check_room_cleared(current_room)
        
        if self.all_rooms_cleared() and not self.portal_spawned:
            self.spawn_portal()
            self.portal_spawned = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # pause
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
                self.run(self.pause_screen_loop)
                return
            
            self.handle_event(event)
        
        self.attack_timer()
        self.input()
        self.player_collision()
        self.camera_pos.x += (self.camera_target.x - self.camera_pos.x) * self.camera_speed
        self.camera_pos.y += (self.camera_target.y - self.camera_pos.y) * self.camera_speed

        cam_offset_x = self.camera_pos.x
        cam_offset_y = self.camera_pos.y

        self.all_sprites.offset = pygame.Vector2(-cam_offset_x, -cam_offset_y)

        current_room = self.get_player_room()
        self.current_room = current_room
        if current_room:
            rx, ry = self.room_positions[current_room]
            self.camera_target.update(rx, ry)
        
        camera_rect = pygame.Rect(cam_offset_x, cam_offset_y, self.camera_width, self.camera_height)

        for sprite in self.all_sprites:
            if camera_rect.colliderect(sprite.rect):
                if isinstance(sprite, Trap) or isinstance(sprite, BarbedWire):
                    sprite.update(dt, self.enemy_sprites)
                else:
                    sprite.update(dt)

        if self.player.health <= 0:
            self.running = False
            self.run(self.end_screen_loop)
            return
        self.draw_world(dt)
        self.hud.draw(self.display_surface)

    def can_spawn_enemy(self, spawn_pos, min_distance=200):
        # checks if the spawn_pos is valid (the player is not near the position so the enemies do not spawn over the player)
        player_pos = pygame.Vector2(self.player.rect.center)
        spawn_pos = pygame.Vector2(spawn_pos)

        distance = player_pos.distance_to(spawn_pos)
        return distance >= min_distance

    def check_upgrade_pickup(self):
        # checks if player walks over upgrade
        hits = pygame.sprite.spritecollide(self.player, self.upgrade_sprites, True)

        if not hits:
            return
        
        for upgrade in hits:
            print(upgrade.upgrade_type)
            if upgrade.upgrade_type == 'Damage':
                self.player.damage += DAMAGE_UPGRADE
            elif upgrade.upgrade_type == 'Money':
                self.money += MONEY_UPGRADE
            elif upgrade.upgrade_type == 'FireRate':
                self.attack_cooldown = max(50, self.attack_cooldown - 50)
            elif upgrade.upgrade_type == 'Speed':
                self.player.speed += SPEED_UPGRADE
            elif upgrade.upgrade_type == 'Range':
                self.bullet_lifetime += RANGE_UPGRADE
            elif upgrade.upgrade_type == 'HealthUp':
                self.player.max_health += 1
                self.player.health += 1
            elif upgrade.upgrade_type == 'Heal':
                self.player.health += 1

    def destroy_structure(self, pos):
        # convert world pos to tile corner
        tile_x = int(pos.x // TILE_SIZE) * TILE_SIZE
        tile_y = int(pos.y // TILE_SIZE) * TILE_SIZE
        target = pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE)

        destroyables = []

        for sprite in self.collision_sprites:
            if getattr(sprite, 'is_buildable', False):
                destroyables.append(sprite)

        destroyables += list(self.turret_sprites)
        destroyables += list(self.trap_sprites)

        for sprite in destroyables:
            if target.colliderect(sprite.rect):
                sprite.kill()
                
                if isinstance(sprite, Turret):
                    self.money += TURRET_COST // 2
                elif isinstance(sprite, (Trap, BarbedWire)):
                    self.money += TRAP_COST // 2
                break

    def handle_event(self, event):
        # turret placing
        if self.build_mode and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_world_pos = self.get_mouse_pos()
                if self.hud.selected_slot == -1:  # destroy mode
                    self.destroy_structure(mouse_world_pos)
                if self.hud.selected_slot == 0:         # turret
                    self.place_turret(mouse_world_pos)  
                elif self.hud.selected_slot == 1:       # barbed wire
                    self.place_barbed_wire(mouse_world_pos, self.wall_rotation_angle)
                elif self.hud.selected_slot == 2:       # trap
                    self.place_trap(mouse_world_pos, self.trap_rotation_angle)
                elif self.hud.selected_slot == 3:       # bomb
                    valid = True
                    for sprite in self.collision_sprites:
                        if pygame.Rect(sprite.rect).collidepoint(mouse_world_pos):
                            valid = False
                            break
                    if valid:
                        if not self.money < BOMB_COST:
                            Bomb(self.bomb_surf, self.player.rect.center, mouse_world_pos, self, self.all_sprites, self.enemy_sprites)
                            self.build_mode = False
                            self.money -= BOMB_COST
                        
 
        # hud
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                slot = event.key - pygame.K_1 # converts key to slot 0-4
                if self.build_mode:
                    if self.hud.selected_slot == slot:
                        self.build_mode = False
                    else:
                        self.hud.select_slot(slot)
                else:
                    self.hud.select_slot(slot)
                    self.build_mode = True
                
            if event.key == pygame.K_e: #exit build mode
                self.build_mode = False

            if event.key == pygame.K_q:  # example key for destroy mode
                self.build_mode = True
                self.hud.selected_slot = -1  # -1 = destroy mode

            # wall placing
            if self.hud.selected_slot == 1 and event.key == pygame.K_r:
                self.wall_rotation_angle = (self.wall_rotation_angle + 90) % 180
            if self.hud.selected_slot == 4 and event.key == pygame.K_r:
                self.wall_rotation_angle = (self.wall_rotation_angle + 90) % 180

        # zoom camera with scroll
        if event.type == pygame.MOUSEWHEEL:
            self.camera_zoom += event.y * 0.1
            self.camera_zoom += (self.target_zoom - self.camera_zoom) * self.zoom_speed
            self.camera_zoom = max(0.1, min(self.camera_zoom, 4))
            self.camera_width = int(CAMERA_WIDTH / self.camera_zoom)
            self.camera_height = int(CAMERA_HEIGHT / self.camera_zoom)
            self.camera_surface = pygame.Surface((self.camera_width, self.camera_height))

    def draw_world(self, dt):
        self.camera_surface.fill('#1d1c2b')

        # update camera offset to match current room
        current_room = self.get_player_room()
        if current_room:
            rx, ry = self.room_positions[current_room]
            self.camera_target.update(rx, ry)

        # smooth camera movement
        self.camera_pos.x += (self.camera_target.x - self.camera_pos.x) * self.camera_speed
        self.camera_pos.y += (self.camera_target.y - self.camera_pos.y) * self.camera_speed

        cam_offset_x = self.camera_pos.x
        cam_offset_y = self.camera_pos.y
        self.all_sprites.offset = pygame.Vector2(-cam_offset_x, -cam_offset_y)

        # draw rooms
        for (gx, gy), room in self.rooms.items():
            room_x, room_y = self.room_positions[(gx, gy)]
            self.camera_surface.blit(
                room.rendered_surface,
                (room_x - cam_offset_x, room_y - cam_offset_y)
            )

        # separating sprites in group for sorting
        ground_sprites = [s for s in self.all_sprites if getattr(s, 'ground', False) and s not in self.trap_sprites]
        object_sprites = [s for s in self.all_sprites if not getattr(s, 'ground', False) and not isinstance(s, FlyingEnemy) and s not in self.trap_sprites]
        flying_sprites = [s for s in self.all_sprites if isinstance(s, FlyingEnemy)]
        trap_sprites = list(self.trap_sprites)

        # y sorting
        ground_sprites.sort(key=lambda s: s.rect.centery)
        object_sprites.sort(key=lambda s: s.rect.centery)

        # ground and object sprites
        for sprite in ground_sprites + trap_sprites + object_sprites:
            draw_pos = pygame.Vector2(sprite.rect.topleft) + self.all_sprites.offset

            if isinstance(sprite, Turret):
                # turret base
                base_rect = sprite.rect.copy()
                base_rect.topleft = (sprite.rect.x - cam_offset_x, sprite.rect.y - cam_offset_y)
                self.camera_surface.blit(sprite.image, base_rect)

                # turret gun
                gun_rect = sprite.gun_rect.copy()
                gun_rect.topleft = (sprite.gun_rect.x - cam_offset_x, sprite.gun_rect.y - cam_offset_y)
                self.camera_surface.blit(sprite.gun_image, gun_rect)

                # turret healthbar
                bar_width = base_rect.width
                bar_height = 5
                elapsed = pygame.time.get_ticks() - sprite.spawn_time
                remaining_ratio = max(0, (sprite.lifetime - elapsed) / sprite.lifetime)
                bar_bg_rect = pygame.Rect(base_rect.x, base_rect.y - 10, bar_width, bar_height)
                bar_fg_rect = pygame.Rect(base_rect.x, base_rect.y - 10, bar_width * remaining_ratio, bar_height)
                pygame.draw.rect(self.camera_surface, (80, 80, 80), bar_bg_rect)
                pygame.draw.rect(self.camera_surface, (0, 255, 50), bar_fg_rect)

            elif isinstance(sprite, Bomb):
                sprite.draw_countdown(self.camera_surface, self.all_sprites.offset)
            elif isinstance(sprite, Player):
                sprite.draw(self.camera_surface, pygame.Rect(draw_pos, sprite.rect.size))
            else:
                self.camera_surface.blit(sprite.image, draw_pos)

        # draw flying enemies separately
        for sprite in flying_sprites:
            draw_pos = pygame.Vector2(sprite.rect.topleft) + self.all_sprites.offset
            self.camera_surface.blit(sprite.image, draw_pos)

        # draw
        for sprite in self.upgrade_sprites:
            draw_pos = pygame.Vector2(sprite.rect.topleft) + self.all_sprites.offset
            sprite.draw(self.camera_surface, self.all_sprites.offset)

        if self.state == 'boss' and hasattr(self, 'boss') and self.boss.show_cone:
            self.draw_boss_cone(self.camera_surface)

        # ghost build preview
        if self.build_mode:
            ghost_pos = self.get_mouse_pos()
            ghost_cam_x = ghost_pos.x - cam_offset_x
            ghost_cam_y = ghost_pos.y - cam_offset_y
            ghost_image = None

            if self.hud.selected_slot == -1:
                ghost_pos = self.get_mouse_pos()
                ghost_rect = pygame.Rect(0,0,TILE_SIZE,TILE_SIZE)
                ghost_rect.center = ghost_pos
                pygame.draw.rect(self.camera_surface, (255,0,0,120), ghost_rect, 3)  # outline

            if self.hud.selected_slot == 0:
                ghost_image = pygame.transform.scale(self.turret_base, (24, 24))
            elif self.hud.selected_slot == 1:
                ghost_image = pygame.transform.rotate(self.barbed_wire_surf, self.wall_rotation_angle)
            elif self.hud.selected_slot == 2:
                ghost_image = pygame.transform.rotate(self.trap_surf, self.trap_rotation_angle)
            elif self.hud.selected_slot == 3:
                ghost_image = pygame.transform.scale(self.bomb_surf, (16, 16))
            # ghost image transparent
            if ghost_image:
                if self.can_place_at(ghost_pos):
                    ghost_image.set_alpha(120)
                else:
                    ghost_image.fill((255, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)

            grid_x = round(ghost_cam_x / TILE_SIZE) * TILE_SIZE
            grid_y = round(ghost_cam_y / TILE_SIZE) * TILE_SIZE
            if ghost_image:
                ghost_rect = ghost_image.get_frect(center=(grid_x, grid_y))
                self.camera_surface.blit(ghost_image, ghost_rect)

        # draw camera surface to main display surface
        zoomed_view = pygame.transform.scale(self.camera_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.display_surface.blit(zoomed_view, (0, 0))
    
    def draw_boss_cone(self, surface):
        boss = self.boss
        if not boss.show_cone:
            return

        start = pygame.Vector2(boss.rect.center)
        direction = boss.direction.normalize()

        angle = direction.angle_to(pygame.Vector2(0, -1))  # point cone upwards
        cone = pygame.transform.rotate(self.smash_cone_surf, angle)

        scale = boss.smash_cone_range / 256 # 256 is cone resolution so we adjust for scaling correctly
        w, h = cone.get_size()
        cone = pygame.transform.smoothscale(cone, (int(w * scale), int(h * scale)))

        offset = direction * (boss.smash_cone_range * 0.5)
        pos = start + offset + self.all_sprites.offset

        rect = cone.get_rect(center=(pos.x, pos.y))
        surface.blit(cone, rect)

    def start_screen_loop(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.running = False
                self.run(self.gameplay_loop)
                return
        
        self.display_surface.fill((20,20,40))
        title_font = pygame.font.Font(FONT_PATH, 70)
        small_font = pygame.font.Font(FONT_PATH, 36)

        title = title_font.render('SWARM TD', True, (255,255,255))
        prompt = small_font.render('Press SPACE to start', True, (200,200,200))

        self.display_surface.blit(title, title.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 50)))
        self.display_surface.blit(prompt, prompt.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 20)))

    def pause_screen_loop(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
                self.run(self.gameplay_loop)
                return
        
        overlay = pygame.Surface((WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2), pygame.SRCALPHA)

        overlay.fill((0, 0, 0, 20))

        pause_window_width = 400
        pause_window_height = 250
        border_radius = 25
        border_thickness = 4

        pause_window_x = (WINDOW_WIDTH - pause_window_width) // 2
        pause_window_y = (WINDOW_HEIGHT - pause_window_height) // 2

        pause_window = pygame.Surface((pause_window_width, pause_window_height), pygame.SRCALPHA)

        background = pygame.Rect(border_thickness, border_thickness, pause_window_width - 2*border_thickness, pause_window_height - 2*border_thickness)
        
        pygame.draw.rect(pause_window, (30,30,40,100), background, border_radius=border_radius) # pause window backgroound
        pygame.draw.rect(pause_window, (200, 200, 220), background, width=border_thickness * 2, border_radius = border_radius) # pause window border

        title_font = pygame.font.Font(FONT_PATH, 60)
        small_font = pygame.font.Font(FONT_PATH, 20)
        title = title_font.render('Paused', True, (255,255,255))
        info = small_font.render('Press ESC to Resume', True, (220,220,220))

        pause_window.blit(title, title.get_frect(center=(pause_window_width // 2, 80)))
        pause_window.blit(info, info.get_frect(center=(pause_window_width // 2, 150)))

        self.display_surface.blit(pause_window, (pause_window_x, pause_window_y))

    def end_screen_loop(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.__init__()
                self.running = False
                self.run(self.start_screen_loop)
                return
        
        self.display_surface.fill((0,0,0))
        title_font = pygame.font.Font(FONT_PATH, 70)
        small_font = pygame.font.Font(FONT_PATH, 36)

        title = title_font.render('GAME OVER', True, (255,0,0))
        prompt = small_font.render('Press R to Restart', True, (255,255,255))
        self.boss = None
        self.display_surface.blit(title, title.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 40)))
        self.display_surface.blit(prompt, prompt.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 20)))

if __name__ == '__main__':
    game = Game()
    game.run(game.start_screen_loop)

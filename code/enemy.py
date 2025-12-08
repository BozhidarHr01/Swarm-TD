from settings import *
from bullet import Bullet, RockProjectile

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites, game):
        super().__init__(groups)
        self.player = player
        self.health = ENEMY_HEALTH
        self.game = game

        # destroy enemy after 20 seconds
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = ENEMY_DESPAWN_TIME

        self.frames = frames
        self.direction_state = 'down'

        self.frame_index = 0
        self.image = self.frames[self.direction_state][self.frame_index]

        self.animation_speed = 6

        # rect
        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-15, -25)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = ENEMY_SPEED
        self.old_rect = self.rect.copy()

        # timer
        self.death_time = 0
        self.death_duration = 1

        # flash when taking damage
        self.flash_duration = 100 # ms
        self.flash_start_time = 0
        
        self.is_flashing = False
        self.mask = pygame.mask.from_surface(self.image)
        self.original_image = self.image.copy()

        # pathfinding
        self.move_dir = pygame.Vector2(0,1)
        self.last_pos = pygame.Vector2(self.rect.center)
        self.stuck_timer = 0
        self.stuck_threshold = 200

    def animate(self, dt):
        frames = self.frames[self.direction_state]

        self.frame_index += self.animation_speed * dt
        self.frame_index %= len(frames)
        self.image = frames[int(self.frame_index)]

        self.original_image = self.image.copy()
        self.mask = pygame.mask.from_surface(self.image)

    def update_direction_state(self):
        dx, dy = self.direction.x, self.direction.y

        if abs(dx) > abs(dy):
            if dx > 0:
                self.direction_state = 'right'
            else:
                self.direction_state = 'left'
        else:
            if dy > 0:
                self.direction_state = 'down'
            else:
                self.direction_state = 'up'

    def has_line_of_sight(self):
        # returns true if there is no wall between the player and the enemy
        start = pygame.Vector2(self.rect.center)
        end = pygame.Vector2(self.player.rect.center)
        direction = end - start
        dist = direction.length()

        if dist == 0:
            return True

        direction = direction.normalize()
        step = 3  # pixels per step
        steps = int(dist // step)

        probe = start.copy()
        for _ in range(steps):
            probe += direction * step
            for sprite in self.collision_sprites:
                if sprite.rect.collidepoint(probe):
                    return False
        return True

    def move(self, dt):
        # convert dt to ms because stuck_timer uses ms
        dt_ms = dt * 1000

        # get direction to player
        to_player = pygame.Vector2(self.player.rect.center) - pygame.Vector2(self.rect.center)
        if to_player.length() > 0:
            to_player = to_player.normalize()
        else:
            to_player = pygame.Vector2(0, 1)

        # if no object between player and enemy, move to player
        if self.has_line_of_sight():
            self.move_dir = to_player
            self.stuck_timer = 0  # reset stuck timer when we see the player

        # try moving to current direction
        self.direction = self.move_dir
        # store position before trying to move to measure movement
        before = pygame.Vector2(self.rect.center)

        # actual movement
        self.hitbox_rect.centerx += self.direction.x * self.speed * dt
        self.collisions('horizontal')
        self.hitbox_rect.centery += self.direction.y * self.speed * dt
        self.collisions('vertical')
        self.rect.center = self.hitbox_rect.center

        # detect if enemy is stuck by checking how much it moved
        moved_dist = (pygame.Vector2(self.rect.center) - before).length()
        if moved_dist < 0.5:      # not moving (blocked)
            self.stuck_timer += dt_ms
        else:
            self.stuck_timer = 0  # moving again

        # if enemy is stuck and has not line of sight to player, rotate direction by 90 degrees and try moving again
        if self.stuck_timer >= self.stuck_threshold and not self.has_line_of_sight():
            # rotate movement direction by 90 degrees
            if self.move_dir.length() == 0:
                self.move_dir = to_player  # fallback
            self.move_dir = self.move_dir.rotate(90)
            self.stuck_timer = 0  # reset timer after changing direction

    def collisions(self, direction):
        nearby_sprites = [s for s in self.collision_sprites if s.rect.colliderect(self.hitbox_rect.inflate(32,32))]
        for sprite in nearby_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top
    
    def take_hit(self, game, damage):
        self.health -= damage

        self.is_flashing = True
        self.flash_start_time = pygame.time.get_ticks()

        if self.health <= 0:
            # death 'animation' by flashing enemy in white before dying
            current_frames = self.frames[self.direction_state]
            current_frame = current_frames[int(self.frame_index)]

            surf = pygame.mask.from_surface(current_frame).to_surface()
            surf.set_colorkey('white')
            self.image = surf
            self.destroy()
            if game:
                game.money += ENEMY_KILL_MONEY_REWARD
                game.kills += 1

            for room in self.game.rooms.values():
                if hasattr(room, 'enemies') and self in room.enemies:
                    room.enemies.remove(self)

    def destroy(self):
        '''When enemy gets killed apply 'damage' effect '''
        # start a timer
        self.death_time = pygame.time.get_ticks()
        # change the image
        current_frames = self.frames[self.direction_state]
        current_frame = current_frames[int(self.frame_index)]

        surf = pygame.mask.from_surface(current_frame).to_surface()
        surf.set_colorkey('black')
        self.image = surf

    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()

    def despawn(self):
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()

    def update(self, dt):
        now = pygame.time.get_ticks()

        if self.death_time == 0:
            self.move(dt)
            self.update_direction_state()
            self.animate(dt)
        else:
            self.death_timer()
        # self.despawn()
        
        if self.is_flashing:
            if now - self.flash_start_time <= self.flash_duration:
                mask_surf = self.mask.to_surface(setcolor=(255,0,0,100), unsetcolor=(0,0,0,0))
                mask_surf.set_colorkey((0,0,0))
                self.image = self.original_image.copy()
                self.image.blit(mask_surf, (0,0))
            else:
                self.is_flashing = False
                self.image = self.original_image

class FlyingEnemy(Enemy):
    def __init__(self, pos, frames, groups, player, collision_sprites, game):
        super().__init__(pos, frames, groups, player, collision_sprites, game)
        self.speed = ENEMY_SPEED * 1.2
        self.health = FLYING_ENEMY_HEALTH
        self.game = game

    def move(self, dt):
        # get direction
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize()

        separation = pygame.Vector2(0,0)
        for other in self.game.enemy_sprites:
            if other == self:
                continue
            offset = pygame.Vector2(self.rect.center) - pygame.Vector2(other.rect.center)
            distance = offset.length()
            if distance < 20 and distance > 0:
                separation += offset.normalize() * (20 - distance)
        
        move_vector = self.direction * self.speed * dt + separation * dt
        self.hitbox_rect.center += move_vector

        self.rect.center = self.hitbox_rect.center
    
    def update(self, dt):
        super().update(dt)

class Skeleton(Enemy):
    def __init__(self, pos, frames, groups, player, collision_sprites, game):
        super().__init__(pos, frames, groups, player, collision_sprites, game)
        self.speed = ENEMY_SPEED * 0.9
        self.health = FLYING_ENEMY_HEALTH

        # stop to shoot mechanic
        self.shoot_pause = SKELETON_SHOOT_PAUSE
        self.shoot_start_time = 0
        self.is_shooting = False
        self.last_attack_time = 0
        self.attack_cooldown = SKELETON_ATTACK_COOLDOWN
        self.game = game
        self.damage = ENEMY_DAMAGE

    def attack(self):
        now = pygame.time.get_ticks()
        if not self.is_shooting and now - self.last_attack_time >= self.attack_cooldown:
            self.is_shooting = True
            self.shoot_start_time = now
            return

        if self.is_shooting and now - self.shoot_start_time >= self.attack_cooldown:
            self.is_shooting = False
            self.last_attack_time = now
            
            direction = pygame.Vector2(self.player.rect.center) - pygame.Vector2(self.rect.center)
            if direction.length() != 0:
                direction = direction.normalize()
            
            Bullet(
                surf=self.game.bone_bullet,
                pos=self.rect.center,
                direction=direction,
                lifetime=SKELETON_BONE_LIFETIME,
                shooter=self,                          # skeleton is shooter
                groups=(self.game.all_sprites, self.game.bullet_sprites),
                collision_sprites=self.game.collision_sprites,
                enemy_sprites=[self.game.player],      # bullet hits only player
                game=self.game,
                speed=BULLET_SPEED * 0.75)
    
    def update(self, dt):
        now = pygame.time.get_ticks()

        if self.death_time == 0:
            if self.is_shooting:
                self.update_direction_state()
                self.animate(dt)
            else:
                self.move(dt)
                self.update_direction_state()
                self.animate(dt)
            
            self.attack()
        else:
            self.death_timer()

        if self.is_flashing:
            if now - self.flash_start_time <= self.flash_duration:
                mask_surf = self.mask.to_surface(setcolor=(255,0,0,100), unsetcolor=(0,0,0,0))
                mask_surf.set_colorkey((0,0,0))
                self.image = self.original_image.copy()
                self.image.blit(mask_surf, (0,0))
            else:
                self.is_flashing = False
                self.image = self.original_image

class Boss(Enemy):
    def __init__(self, pos, idle_frames, throw_frames, smash_frames, groups, player, collision_sprites, game):
        super().__init__(pos, idle_frames, groups, player, collision_sprites, game)

        self.health = BOSS_HEALTH
        self.speed = BOSS_SPEED
        self.damage = BOSS_DAMAGE
        self.is_boss = True

        self.phase = 1
        self.max_health = self.health

        self.state = 'idle'
        self.throw_cooldown = 5000 # ms
        self.last_throw = pygame.time.get_ticks()
        self.idle_frames = idle_frames
        self.throw_frames = throw_frames
        self.smash_frames = smash_frames
        
        self.throw_hit_frame = 3
        self.throw_anim_index = 0
        self.throw_anim_speed = 0.15

        self.smash_hit_frame = 4
        self.smash_anim_speed = 0.05
        self.smash_cooldown = SMASH_COOLDOWN
        
        self.last_smash = pygame.time.get_ticks()

        self.smash_cone_angle = SMASH_ANGLE
        self.smash_cone_range = SMASH_RANGE
        self.show_cone = False
        self.cone_alpha = 120
    
    def update(self, dt):
        if self.health <= 0:
            self.game.boss_defeated()
               
        if self.state == 'idle':
            self.idle_update(dt)
        elif self.state == 'throw_pre':
            self.throw_pre_update(dt)
        elif self.state == 'throw_cast':
            self.throw_cast_update(dt)
        elif self.state == 'throw_recover':
            self.throw_recover_update(dt)

        elif self.state == 'smash_pre':
            self.smash_pre_update(dt)
        elif self.state == 'smash_cast':
            self.smash_cast_update(dt)
        elif self.state == 'smash_recover':
            self.smash_recover_update(dt)

        if self.health < self.max_health * 0.5 and self.phase == 1:
            self.phase = 2
            self.speed *= 1.4

        if self.health < self.max_health * 0.2 and self.phase == 2:
            self.phase = 3
            self.speed *= 1.4
    
    def get_dir_name(self):
        dx, dy = self.direction.x, self.direction.y
        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'down' if dy > 0 else 'up'

    def idle_update(self, dt):
        super().update(dt)
        now = pygame.time.get_ticks()
        self.has_smashed = False
        self.has_thrown = False

        if now - self.last_smash > self.smash_cooldown and self.phase >= 2:
            self.state = 'smash_pre'
            self.smash_anim_index = 0
            self.last_smash = now
            self.show_cone = True
            return

        if now - self.last_throw > self.throw_cooldown:
            self.state = 'throw_pre'
            self.throw_anim_index = 0
            self.last_throw = now

    def throw_pre_update(self, dt):
        dir_name = self.get_dir_name()
        frames = self.throw_frames[dir_name]
        self.throw_anim_index += self.throw_anim_speed
        if self.throw_anim_index >= self.throw_hit_frame:
            self.throw_anim_index = self.throw_hit_frame
            self.state = 'throw_cast'
            return
        self.image = frames[int(self.throw_anim_index)]

    def throw_cast_update(self, dt):
        dir_name = self.get_dir_name()
        frames = self.throw_frames[dir_name]
        self.image = frames[self.throw_hit_frame]

        if not self.has_thrown:
            self.spawn_rock()
            self.has_thrown = True

        self.state = 'throw_recover'
        self.throw_anim_index = self.throw_hit_frame

    def spawn_rock(self):
        player_pos = pygame.Vector2(self.player.rect.center)
        boss_pos = pygame.Vector2(self.rect.center)
        direction = (player_pos - boss_pos).normalize()
        RockProjectile(self.rect.center, direction, self.game)

    def throw_recover_update(self, dt):
        dir_name = self.get_dir_name()
        frames = self.throw_frames[dir_name]
        self.throw_anim_index += self.throw_anim_speed
        if self.throw_anim_index >= len(frames):
            self.throw_anim_index = 0
            self.state = 'idle'
            return
        self.image = frames[int(self.throw_anim_index)]

    def smash_pre_update(self, dt):
        dir_name = self.get_dir_name()
        frames = self.smash_frames[dir_name]

        self.smash_anim_index += self.smash_anim_speed
        if self.smash_anim_index >= self.smash_hit_frame:
            self.smash_anim_index = self.smash_hit_frame
            self.state = 'smash_cast'
            return

        self.image = frames[int(self.smash_anim_index)]

    def smash_cast_update(self, dt):
        dir_name = self.get_dir_name()
        frames = self.smash_frames[dir_name]
        self.image = frames[self.smash_hit_frame]

        if not self.has_smashed:
            self.do_smash_damage()
            self.has_smashed = True
            self.show_cone = False
        self.state = 'smash_recover'
        self.smash_anim_index = self.smash_hit_frame
        

    def smash_recover_update(self, dt):
        dir_name = self.get_dir_name()
        frames = self.smash_frames[dir_name]

        self.smash_anim_index += self.smash_anim_speed
        if self.smash_anim_index >= len(frames):
            self.smash_anim_index = 0
            self.state = 'idle'
            return

        self.image = frames[int(self.smash_anim_index)]

    def do_smash_damage(self):
        player_pos = pygame.Vector2(self.player.rect.center)
        boss_pos = pygame.Vector2(self.rect.center)

        vec = player_pos - boss_pos
        distance = vec.length()

        if distance > SMASH_RANGE:
            return
        
        direction = pygame.Vector2(self.direction)
        if direction.length() == 0:
            return
        
        forward = direction.normalize()
        to_player = vec.normalize()
        
        angle = forward.angle_to(to_player)

        if abs(angle) <= SMASH_ANGLE / 2:
            self.player.take_hit(self.game, SMASH_DAMAGE)
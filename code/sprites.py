from settings import *
# from math import atan2, degrees

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, ground = False):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = ground
        self.old_rect = self.rect.copy()

# class Bullet(pygame.sprite.Sprite):
#     def __init__(self, surf, pos, direction, groups, collision_sprites, enemy_sprites, game):
#         super().__init__(groups)
#         self.image = surf
#         self.rect = self.image.get_frect(center = pos)
#         self.spawn_time = pygame.time.get_ticks()
#         self.lifetime = 3000
#         self.enemy_sprites = enemy_sprites
#         self.game = game

#         self.hitbox_rect = self.rect
#         self.collision_sprites = collision_sprites
#         self.old_rect = self.rect.copy()

#         self.direction = direction
#         self.speed = 350
    
#     def move(self, dt):
#         self.rect.x += self.direction.x * self.speed * dt
#         self.collision('horizontal')
#         self.rect.y += self.direction.y * self.speed * dt
#         self.collision('vertical')
#         # self.rect.center = self.hitbox_rect.center

#     def collision(self, direction):
#         for sprite in self.collision_sprites:
#             if sprite.rect.colliderect(self.hitbox_rect):
#                 if direction == 'horizontal':
#                     if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
#                         self.rect.right = sprite.rect.left
#                         self.direction.x *= -1
#                     if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
#                         self.rect.left = sprite.rect.right
#                         self.direction.x *= -1

#                 else:
#                     if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
#                         self.rect.bottom = sprite.rect.top
#                         self.direction.y *= -1
#                     if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
#                         self.rect.top = sprite.rect.bottom
#                         self.direction.y *= -1

#     def check_enemy_hit(self):
#         for sprite in self.enemy_sprites:
#             if hasattr(sprite, "take_hit"):
#                 if sprite.rect.colliderect(self.rect):
#                     sprite.take_hit(self.game)
#                     self.kill()
#                     break

#     def update(self, dt):
#         self.old_rect = self.rect.copy()
#         # self.rect.center += self.direction * self.speed * dt
#         self.move(dt)
#         self.animate()
#         self.collision(self.direction)

#         self.check_enemy_hit()

#         if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
#             self.kill()

#     def animate(self):
#         self.image = pygame.transform.rotate(self.image, 90)

# class Enemy(pygame.sprite.Sprite):
#     def __init__(self, pos, frames, groups, player, collision_sprites, game):
#         super().__init__(groups)
#         self.player = player
#         self.health = ENEMY_HEALTH

#         # destroy enemy after 20 seconds
#         self.spawn_time = pygame.time.get_ticks()
#         self.lifetime = 20000 # ms

#         # image
#         self.frames, self.frame_index = frames, 1
#         self.image = self.frames[self.frame_index]
#         self.animation_speed = 6

#         # rect
#         self.rect = self.image.get_frect(center = pos)
#         self.hitbox_rect = self.rect.inflate(-10, -10)
#         self.collision_sprites = collision_sprites
#         self.direction = pygame.Vector2()
#         self.speed = 150
#         self.old_rect = self.rect.copy()

#         # timer
#         self.death_time = 0
#         self.death_duration = 1

#         # flash when taking damage
#         self.flash_duration = 100 # ms
#         self.flash_start_time = 0
#         self.is_flashing = False
#         self.mask = pygame.mask.from_surface(self.image)
#         self.original_image = self.image.copy()

#     def animate(self, dt):
#         self.frame_index += self.animation_speed * dt
#         self.image = self.frames[int(self.frame_index) % len(self.frames)]

#         self.original_image = self.image.copy()
#         self.mask = pygame.mask.from_surface(self.image)

#     def move(self, dt):
#         # get direction
#         player_pos = pygame.Vector2(self.player.rect.center)
#         enemy_pos = pygame.Vector2(self.rect.center)
#         self.direction = (player_pos - enemy_pos).normalize()

#         # update the rect position + collision logic
#         self.hitbox_rect.centerx += self.direction.x * self.speed * dt
#         self.collisions('horizontal')
#         self.hitbox_rect.centery += self.direction.y * self.speed * dt
#         self.collisions('vertical')
#         self.rect.center = self.hitbox_rect.center
    
#     def collisions(self, direction):
#         for sprite in self.collision_sprites:
#             if sprite.rect.colliderect(self.hitbox_rect):
#                 if direction == 'horizontal':
#                     if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
#                     if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
#                 else:
#                     if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
#                     if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top
    
#     def take_hit(self, game):
#         self.health -= PLAYER_DAMAGE

#         self.is_flashing = True
#         self.flash_start_time = pygame.time.get_ticks()

#         if self.health <= 0:
#             # death 'animation'
#             surf = pygame.mask.from_surface(self.frames[0]).to_surface()
#             surf.set_colorkey('white')
#             self.image = surf
#             self.destroy()

#             if game:
#                 game.money += ENEMY_KILL_MONEY_REWARD
#                 game.kills += 1

#     def destroy(self):
#         """When enemy gets killed apply "damage" effect """
#         # start a timer
#         self.death_time = pygame.time.get_ticks()
#         # change the image
#         surf = pygame.mask.from_surface(self.frames[0]).to_surface()
#         surf.set_colorkey('black')
#         self.image = surf

#     def death_timer(self):
#         if pygame.time.get_ticks() - self.death_time >= self.death_duration:
#             self.kill()

#     def despawn(self):
#         if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
#             self.kill()

#     def update(self, dt):
#         now = pygame.time.get_ticks()

#         if self.death_time == 0:
#             self.move(dt)
#             self.animate(dt)
#         else:
#             self.death_timer()
#         self.despawn()
        
#         if self.is_flashing:
#             if now - self.flash_start_time <= self.flash_duration:
#                 flash = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
#                 flash.fill((255, 155, 0, 100))
#                 mask_surf = self.mask.to_surface(setcolor=(255,0,0,100), unsetcolor=(0,0,0,0))
#                 mask_surf.set_colorkey((0,0,0))
#                 self.image = self.original_image.copy()
#                 self.image.blit(mask_surf, (0,0))
#             else:
#                 self.is_flashing = False
#                 self.image = self.original_image


# class Turret(pygame.sprite.Sprite):
#     def __init__(self, pos, surf, gun_surf, groups, bullet_surf, bullet_sprites, all_sprites, collision_sprites, enemy_sprites, game):
#         super().__init__(groups)
#         self.image = surf
#         self.rect = self.image.get_frect(center=pos)
#         self.pos = pygame.Vector2(pos)
#         self.old_rect = self.rect.copy()

#         self.bullet_surf = bullet_surf
#         self.collision_sprites = collision_sprites
#         self.bullet_sprites = bullet_sprites
#         self.all_sprites = all_sprites
#         self.enemy_sprites = enemy_sprites
#         self.game = game
        
#         self.range_radius=300
#         self.fire_rate=1
#         self.turret_interval = 100
#         self.last_shot_time = 0

#         self.current_target = None
#         self.nearby_walls = []

#         # gun
#         self.gun_original = gun_surf
#         self.gun_image = gun_surf
#         self.gun_rect = self.gun_image.get_rect(center=self.pos)

#         # timers
#         self.los_timer = 0
#         self.los_check_interval = 500 # ms
#         self.shoot_timer = 0

#         self.last_los_check = pygame.time.get_ticks()
#         self.last_shot_time = pygame.time.get_ticks()
   
#     def find_target(self):
#         closest_enemy = None
#         min_dist = float('inf')

#         for enemy in self.enemy_sprites:
#             enemy_pos = pygame.Vector2(enemy.rect.center)
#             distance = (enemy_pos - self.pos).length()

#             if distance <= self.range_radius and distance < min_dist:
#                 if self.has_line_of_sight(enemy_pos):
#                     min_dist = distance
#                     closest_enemy = enemy
#         self.current_target = closest_enemy
#         if self.current_target:
#             self.nearby_walls = self.get_nearby_walls(pygame.Vector2(self.current_target.rect.center))
#         else:
#             self.nearby_walls = []

#     def update_target(self, dt):
#         self.los_timer += dt
#         if self.los_timer >= self.los_check_interval:
#             self.los_timer = 0
#             if (self.current_target is None or self.current_target not in self.enemy_sprites or
#                 (pygame.Vector2(self.current_target.rect.center) - self.pos).length() > self.range_radius):
#                 self.current_target = self.find_target()
#                 if self.current_target:
#                     self.nearby_walls = self.get_nearby_walls(pygame.Vector2(self.current_target.rect.center))
#                 else:
#                     self.nearby_walls = []

#     def get_nearby_walls(self, target_pos, margin=64):
#         min_x = min(self.pos.x, target_pos.x) - margin
#         max_x = max(self.pos.x, target_pos.x) + margin
#         min_y = min(self.pos.y, target_pos.y) - margin
#         max_y = max(self.pos.y, target_pos.y) + margin

#         nearby_walls = [wall for wall in self.collision_sprites
#                         if min_x <= wall.rect.right and max_x >= wall.rect.left
#                         and min_y <= wall.rect.top and max_y >= wall.rect.bottom]
#         return nearby_walls
    
#     def has_line_of_sight(self, target_pos):
#         if not self.nearby_walls:
#             return True

#         direction = target_pos - self.pos
#         steps = int(direction.length())
#         if steps == 0:
#             return True
        
#         direction = direction.normalize()

#         for i in range(0, steps, 10):
#             check_pos = self.pos + direction * i
#             check_rect = pygame.Rect(check_pos.x, check_pos.y, 2, 2)
#             for wall in self.nearby_walls:
#                 if wall.rect.colliderect(check_rect):
#                     return False
#         return True

#     def shoot(self):
#         if not self.current_target:
#             return
        
#         now = pygame.time.get_ticks()
#         fire_interval = self.turret_interval / self.fire_rate

#         if now - self.last_shot_time >= fire_interval:
#             self.last_shot_time = now 

#             direction = pygame.Vector2(self.current_target.rect.center) - self.pos
#             if direction.length() != 0:
#                 direction = direction.normalize()

#             gun_tip_offset = pygame.Vector2(self.gun_image.get_width(), 0).rotate(-direction.angle_to(pygame.Vector2(1,0)))
#             bullet_pos = self.pos + gun_tip_offset

#             Bullet(self.bullet_surf, bullet_pos, direction, (self.bullet_sprites, self.all_sprites), self.collision_sprites, self.enemy_sprites, self.game)
    
#     def rotate_gun(self, target_pos):
#         dir_vec = pygame.Vector2(target_pos) - self.pos
#         if dir_vec.length() == 0:
#             return
        
#         dx, dy = dir_vec.x, dir_vec.y

#         angle_rad = atan2(dy,dx)
#         angle_deg = degrees(angle_rad)

#         rot_angle = -angle_deg
        
#         rotated_image = pygame.transform.rotate(self.gun_original, rot_angle)
#         rotated_rect = rotated_image.get_frect()

#         orig_rect = self.gun_original.get_frect()
#         pivot = pygame.Vector2(orig_rect.center, orig_rect.height / 2)

#         orig_center = pygame.Vector2(orig_rect.center)
#         vec_center_to_pivot = pivot - orig_center

#         rotated_vec = vec_center_to_pivot.rotate(rot_angle)

#         world_pivot = pygame.Vector2(self.pos)
#         rotated_center = world_pivot - rotated_vec

#         rotated_rect.center = (rotated_center.x, rotated_center.y)

#         self.gun_image = rotated_image
#         self.gun_rect = rotated_rect

    
#     def update(self, dt):
#         now = pygame.time.get_ticks()

#         if now - self.last_los_check >= self.los_check_interval:
#             self.last_los_check = now
#             self.find_target()
        
#         # rotate gun
#         if self.current_target:
#             self.rotate_gun(pygame.Vector2(self.current_target.rect.center))

#         self.shoot()
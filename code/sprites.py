from settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, ground = False):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = ground
        self.old_rect = self.rect.copy()

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups, collision_sprites):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 3000

        self.hitbox_rect = self.rect
        self.collision_sprites = collision_sprites
        self.old_rect = self.rect.copy()

        self.direction = direction
        self.speed = 350
    
    def move(self, dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        # self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left
                        self.direction.x *= -1
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right
                        self.direction.x *= -1

                else:
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top
                        self.direction.y *= -1
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom
                        self.direction.y *= -1
                    
    def update(self, dt):
        self.old_rect = self.rect.copy()
        # self.rect.center += self.direction * self.speed * dt
        self.move(dt)
        self.animate()
        self.collision(self.direction)
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()

    def animate(self):
        self.image = pygame.transform.rotate(self.image, 90)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(groups)
        self.player = player

        # destroy enemy after 20 seconds
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 20000

        # image
        self.frames, self.frame_index = frames, 1
        self.image = self.frames[self.frame_index]
        self.animation_speed = 6

        # rect
        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-10, -10)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 200

        # timer
        self.death_time = 0
        self.death_duration = 25

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def move(self, dt):
        # get direction
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize()

        # update the rect position + collision logic
        self.hitbox_rect.centerx += self.direction.x * self.speed * dt
        self.collisions('horizontal')
        self.hitbox_rect.centery += self.direction.y * self.speed * dt
        self.collisions('vertical')
        self.rect.center = self.hitbox_rect.center
    
    def collisions(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top
    
    def destroy(self):
        """When enemy gets killed apply "damage" effect """
        # start a timer
        self.death_time = pygame.time.get_ticks()
        # change the image
        surf = pygame.mask.from_surface(self.frames[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf

    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()

    def despawn(self):
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()

    def update(self, dt):
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
        else:
            self.death_timer()
        self.despawn()
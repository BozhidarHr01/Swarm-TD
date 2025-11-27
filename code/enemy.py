from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites, game):
        super().__init__(groups)
        self.player = player
        self.health = ENEMY_HEALTH

        # destroy enemy after 20 seconds
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 20000 # ms

        # image
        self.frames, self.frame_index = frames, 1
        self.image = self.frames[self.frame_index]
        self.animation_speed = 6

        # rect
        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-10, -10)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 150
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

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

        self.original_image = self.image.copy()
        self.mask = pygame.mask.from_surface(self.image)

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
    
    def take_hit(self, game):
        self.health -= PLAYER_DAMAGE

        self.is_flashing = True
        self.flash_start_time = pygame.time.get_ticks()

        if self.health <= 0:
            # death 'animation'
            surf = pygame.mask.from_surface(self.frames[0]).to_surface()
            surf.set_colorkey('white')
            self.image = surf
            self.destroy()

            if game:
                game.money += ENEMY_KILL_MONEY_REWARD
                game.kills += 1

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
        now = pygame.time.get_ticks()

        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
        else:
            self.death_timer()
        self.despawn()
        
        if self.is_flashing:
            if now - self.flash_start_time <= self.flash_duration:
                flash = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                flash.fill((255, 155, 0, 100))
                mask_surf = self.mask.to_surface(setcolor=(255,0,0,100), unsetcolor=(0,0,0,0))
                mask_surf.set_colorkey((0,0,0))
                self.image = self.original_image.copy()
                self.image.blit(mask_surf, (0,0))
            else:
                self.is_flashing = False
                self.image = self.original_image
from settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, lifetime, shooter, groups, collision_sprites, enemy_sprites, game, speed = BULLET_SPEED):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = lifetime
        self.enemy_sprites = enemy_sprites
        self.game = game
        self.shooter = shooter

        self.hitbox_rect = self.rect
        self.collision_sprites = collision_sprites
        self.old_rect = self.rect.copy()

        self.direction = direction
        self.speed = speed
    
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

    def check_enemy_hit(self):
        for sprite in self.enemy_sprites:
            if hasattr(sprite, 'take_hit'):
                if sprite.rect.colliderect(self.rect):
                    sprite.take_hit(self.game, self.shooter.damage)
                    self.kill()
                    break

    def update(self, dt):
        self.old_rect = self.rect.copy()
        # self.rect.center += self.direction * self.speed * dt
        self.move(dt)
        self.animate()
        self.collision(self.direction)

        self.check_enemy_hit()

        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()

    def animate(self):
        self.image = pygame.transform.rotate(self.image, 90)

class RockProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, game):
        super().__init__(game.all_sprites, game.bullet_sprites)
        self.game = game
        self.image = pygame.image.load(join('images', 'boss', 'rock.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64,64))
        self.rect = self.image.get_frect(center=pos)
        self.direction = direction
        self.speed = 350
        self.lifetime = 2000
        self.spawn = pygame.time.get_ticks()

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt

        if self.rect.colliderect(self.game.player.rect):
            self.game.player.take_hit(self.game, BOSS_ROCK_DAMAGE)
            self.kill()
        
        if pygame.time.get_ticks() - self.spawn > self.lifetime:
            self.kill()
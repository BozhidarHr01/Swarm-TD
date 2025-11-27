from settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups, collision_sprites, enemy_sprites, game):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.enemy_sprites = enemy_sprites
        self.game = game

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

    def check_enemy_hit(self):
        for sprite in self.enemy_sprites:
            if hasattr(sprite, "take_hit"):
                if sprite.rect.colliderect(self.rect):
                    sprite.take_hit(self.game)
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
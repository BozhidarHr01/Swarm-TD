from settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, ground = False):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = ground
        self.is_floor = False
        self.old_rect = self.rect.copy()

class Trap(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, animation_frames, game):
        super().__init__(groups)
        self.image = surf
        self.game = game
        self.rect = self.image.get_frect(center=pos)
        self.old_rect = self.rect.copy()

        self.pos = pygame.Vector2(pos)
        self.angle = 0
        self.ground = True
        self.is_buildable = True
        
        # trigger
        self.damage = TRAP_DAMAGE
        self.triggered = False
        self.damage_dealt = False

        # animation
        self.animation_frames = animation_frames
        self.frame_index = 0
        self.animation_speed = TRAP_ANIMATION_SPEED
        self.animation_time = TRAP_ANIMATION_TIME
    
    def update(self, dt, enemies):
        if not self.triggered:
            self.check_collision(enemies)
        else:
            self.animate(dt)
            if self.frame_index >= 4 and not self.damage_dealt:
                self.deal_damage(enemies)
                self.damage_dealt = True
    
    def check_collision(self, enemies):
        hits = pygame.sprite.spritecollide(self, enemies, False, pygame.sprite.collide_mask)
        if hits:
            for enemy in hits:
                enemy.take_hit(self.game, self.damage)
            self.triggered = True
            self.frame_index = 0
    
    def deal_damage(self, enemies):
        hits = pygame.sprite.spritecollide(self, enemies, False, pygame.sprite.collide_mask)
        for enemy in hits:
            enemy.take_hit(self.game, self.damage)
    
    def animate(self, dt):
        if self.animation_frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animation_frames):
                self.kill()
            else:
                self.image = self.animation_frames[int(self.frame_index)]

class BarbedWire(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, game, rotation = 0, slow_factor = WIRE_SLOW_FACTOR):
        super().__init__(groups)

        self.game = game
        self.original_image = surf
        self.image = pygame.transform.rotate(self.original_image, rotation)
        self.rect = self.image.get_frect(center=pos)
        self.old_rect = self.rect.copy()
        self.is_buildable = True

        self.pos = pygame.Vector2(pos)
        self.ground = True

        self.slow_factor = slow_factor
        self.affected_enemies = set()

    def update(self, dt, enemies):
        hits = pygame.sprite.spritecollide(self, enemies, False, pygame.sprite.collide_mask)
        current_enemies = set(hits)

        for enemy in current_enemies - self.affected_enemies:
            enemy.speed *= self.slow_factor
        
        for enemy in self.affected_enemies - current_enemies:
            enemy.speed /= self.slow_factor
        
        self.affected_enemies = current_enemies

    def rotate(self, angle):
        self.angle = (self.angle + angle) % 180
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_frect(center=self.rect.center)

class Bomb(pygame.sprite.Sprite):
    def __init__(self, surf, start_pos, target_pos, game, groups, enemy_sprites):
        super().__init__(groups)
        self.game = game
        self.image = surf
        self.rect = self.image.get_frect(center=start_pos)

        self.pos = pygame.Vector2(start_pos)
        self.target_pos = pygame.Vector2(target_pos)
        self.speed = 300
        self.enemy_sprites = enemy_sprites

        self.exploded = False
        self.lifetime = 3000
        self.spawn_time = pygame.time.get_ticks()

    def update(self, dt):
        direction = (self.target_pos - self.pos)
        distance = direction.length()
        if distance > 0:
            direction = direction.normalize()
            move = direction * self.speed * dt
            if move.length() > distance:
                move = direction * distance
            self.pos += move
            self.rect.center = self.pos
        elapsed = pygame.time.get_ticks() - self.spawn_time
        if elapsed >= self.lifetime and not self.exploded:
            self.explode()            


    def draw_countdown(self, surface, cam_offset):
        draw_pos = pygame.Vector2(self.rect.topleft) + cam_offset
        surface.blit(self.image, draw_pos)

        elapsed = pygame.time.get_ticks() - self.spawn_time
        remaining_ratio = max(0, (self.lifetime - elapsed) / self.lifetime)

        bar_width = self.rect.width
        bar_height = 5

        bar_bg_rect = pygame.Rect(draw_pos.x, draw_pos.y - 10, bar_width, bar_height)
        bar_fg_rect = pygame.Rect(draw_pos.x, draw_pos.y - 10, bar_width * remaining_ratio, bar_height)
        pygame.draw.rect(surface, (80,80,80), bar_bg_rect)
        pygame.draw.rect(surface, (255,0,0), bar_fg_rect)
    
    def explode(self):
        explosion_radius = 500
        for enemy in self.enemy_sprites:
            if pygame.Vector2(enemy.rect.center).distance_to(self.pos) <= explosion_radius:
                enemy.take_hit(self.game, BOMB_DAMAGE)
        self.kill()


class Upgrade(pygame.sprite.Sprite):
    def __init__(self, pos, upgrade_type, groups):
        super().__init__(groups)
        self.upgrade_type = upgrade_type

        upgrade_data = next(upgrade for upgrade in UPGRADES if upgrade['name'] == upgrade_type)
        self.icon = pygame.image.load(upgrade_data['image']).convert_alpha()
        self.icon = pygame.transform.scale(self.icon, (25, 25))
        self.image = pygame.Surface((UPGRADE_SIZE, UPGRADE_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_frect(center=pos)
        self.image.set_alpha(120)

        self.color_map = {
            'Heal' : (0,255,0),
            'HealthUp' : (220, 20, 20),
            'Damage' : (100,20,20),
            'Money' : (0,100,20),
            'FireRate' : (0, 255, 255),
            'Speed' : (0,255,0),
            'Range' : (200, 0, 255),
        }
        pygame.draw.ellipse(self.image, self.color_map[upgrade_type], (0,0,30,30))
        self.rect = self.image.get_frect(center=pos)

    def draw(self, surface, offset):
        draw_pos = self.rect.topleft + offset

        # draw base box
        surface.blit(self.image, draw_pos)
        icon_rect = self.icon.get_frect(center=self.rect.center + offset)

        font = pygame.font.Font(FONT_PATH, 12)
        text_surf = font.render(self.upgrade_type, True, (255,255,255))
        text_rect = text_surf.get_frect(midtop=(icon_rect.centerx, icon_rect.bottom ))
        surface.blit(text_surf, text_rect)
        # draw icon centered
        surface.blit(self.icon, icon_rect)


class Portal(pygame.sprite.Sprite):
    def __init__(self, pos, game):
        super().__init__(game.all_sprites)
        self.image = pygame.image.load(join('images', 'portal', 'portal.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (135, 135))
        self.rect = self.image.get_frect(center=pos)
        self.game = game

    def update(self, dt):
        if self.rect.colliderect(self.game.player.rect):
            self.game.enter_boss_room()

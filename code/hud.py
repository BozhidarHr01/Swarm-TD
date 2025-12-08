from settings import *

class HUD:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(FONT_PATH, 18)
        self.hotbar_slots = ['Turret', 'Wire', 'Trap', 'Bomb']
        self.slot_costs = [TURRET_COST, BARBED_WIRE_COST, TRAP_COST, BOMB_COST]
        self.selected_slot = 0
        self.slot_width = 75
        self.slot_height = 75
        self.padding = 10
        
        # health bar settigns
        self.heart_spacing = 5

        self.heart_image = pygame.image.load(join('images', 'health', 'heart.png')).convert_alpha()
        self.heart_bg = pygame.image.load(join('images', 'health', 'background.png')).convert_alpha()
        self.heart_border = pygame.image.load(join('images', 'health', 'border.png')).convert_alpha()

        self.heart_image = pygame.transform.scale(self.heart_image, (50,50))
        self.heart_bg = pygame.transform.scale(self.heart_bg, (50,50))
        self.heart_border = pygame.transform.scale(self.heart_border, (50,50))

        self.heart_width = self.heart_image.get_width()
        self.heart_height = self.heart_image.get_height()
        
        # colors
        self.health_color = (255,0,0)
        self.empty_health_color = (100, 0, 0)
        self.hotbar_bg_color = (50,50,50, 150)
        self.hotbar_border_color = (255,255,255)
        self.text_color = (255,255,255)
        self.kills_color = (255,255,255)
        self.money_color = (255,200,0)

        # slot images 
        self.slot_images = [
            pygame.transform.scale(self.game.turret_base, (35,35)),
            pygame.transform.scale(self.game.barbed_wire_surf, (60,40)),
            pygame.transform.scale(self.game.trap_surf, (40,50)),
            pygame.transform.scale(self.game.bomb_surf, (35,35)),
        ]

        # ready button
        self.show_ready_button = True
        self.ready_button_rect = pygame.Rect(WINDOW_WIDTH - 180, WINDOW_HEIGHT - 100, 170, 80)

        # minimap
        self.minimap_size = 100  # width and height of minimap
        self.room_size = 40      # size of one room square in minimap
        self.bg_color = (30, 30, 30, 90)
        self.room_color = (100, 200, 255, 180)
        self.player_color = (255, 50, 50)

        self.boss_icon = pygame.image.load(join('images','boss','boss_icon.png'))
    
    def phase_progress_bar(self, surface, color, font_color, ratio, msg):
        bar_width = 300
        bar_height = 30
        x = (WINDOW_WIDTH - bar_width) // 2
        y = 10
        
        pygame.draw.rect(surface, (80,80,80), (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, color, (x, y, bar_width * ratio, bar_height))
        wave_text = self.font.render(msg, True, font_color)
        surface.blit(wave_text, (x, y - 15))

    def draw(self, surface):
        # health bar
        for i in range(self.game.player.max_health):
            x = 10 + i*(self.heart_width + self.heart_spacing)
            y = 10
            if i < self.game.player.health:
                surface.blit(self.heart_image, (x,y))
                #color = self.health_color
            else:
                surface.blit(self.heart_bg, (x,y))
                #color = self.empty_health_color
            surface.blit(self.heart_border, (x,y))
            # pygame.draw.rect(surface, color, (x,y,self.heart_width, self.heart_height))

        # health_text = self.font.render(f'Health: {self.game.player.health}', True, (255,0,0))
        # surface.blit(health_text, (10,10))

        kills_text = self.font.render(f'Kills: {self.game.kills}', True, self.kills_color)
        surface.blit(kills_text, (10,50))

        money_text = self.font.render(f'$: {self.game.money}', True, self.money_color)
        surface.blit(money_text, (10,80))

        # HOTBAR
        start_x = WINDOW_HEIGHT // 3 - (len(self.hotbar_slots)*(self.slot_width + self.padding)) // 2
        y = WINDOW_HEIGHT - self.slot_height - 10

        for i, slot in enumerate(self.hotbar_slots):
            rect = pygame.Rect(start_x + i*(self.slot_width + self.padding), y, self.slot_width, self.slot_height)
            temp_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            temp_surf.fill((self.hotbar_bg_color))
            surface.blit(temp_surf, rect.topleft)
            
            if i == self.selected_slot:
                pygame.draw.rect(surface, self.hotbar_border_color, rect, 3)
            
            slot_text_font = pygame.font.Font(FONT_PATH, 12)

            icon_image = self.slot_images[i]
            icon_rect = icon_image.get_rect(center=rect.center)
            surface.blit(icon_image, icon_rect)

            text = slot_text_font.render(slot, True, (255,255,255))
            text_rect = text.get_frect(center = (rect.centerx, rect.centery - 30))
            surface.blit(text, text_rect)

            cost_text = self.font.render(f'${self.slot_costs[i]}', True, self.text_color)
            cost_rect = cost_text.get_frect(midtop=(rect.centerx, rect.bottom - 25))
            surface.blit(cost_text, cost_rect)

            key_text = self.font.render(f'{i + 1}', True, self.text_color)
            key_rect = key_text.get_frect(center = (rect.centerx - 28, rect.centery - 26))
            surface.blit(key_text, key_rect)
        
        self.draw_stats(surface)
        self.draw_minimap(surface)
        self.draw_boss_health(surface)

    def select_slot(self, index):
        if 0 <= index < len(self.hotbar_slots):
            self.selected_slot = index

    # stat tracker
    def draw_stats(self, surface):
        font = pygame.font.Font(FONT_PATH, 18)

        stat_values = {
            'Damage': self.game.player.damage,
            'Speed': self.game.player.speed,
            'FireRate': round(1000 / self.game.attack_cooldown, 2),
            'Range': self.game.bullet_lifetime,
            }

        icons = {}
        for upgrade in UPGRADES:
            name = upgrade['name']
            if name in stat_values:
                img = pygame.image.load(upgrade['image']).convert_alpha()
                img = pygame.transform.smoothscale(img, (24,24))
                icons[name] = img

        x = WINDOW_WIDTH / 4 - 380
        y = 600
        padding = 5
        line_spacing = 10

        for stat_name in ['Damage', 'FireRate', 'Speed', 'Range']:
            icon = icons[stat_name]
            value = str(stat_values[stat_name])

            surface.blit(icon, (x,y))

            text = font.render(value, True, (255,255,255))
            surface.blit(text, (x+ icon.get_width() + padding, y + (icon.get_height() - text.get_height()) // 2))
            
            y += icon.get_height() + line_spacing


    def draw_minimap(self, surface):
            '''Calculates map size from room positions. Rooms are Blue squares and the room that the player is in has a red dot'''

            # calculate map bounds
            room_positions = list(self.game.rooms.keys())
            min_x = min(gx for gx, gy in room_positions)
            max_x = max(gx for gx, gy in room_positions)
            min_y = min(gy for gx, gy in room_positions)
            max_y = max(gy for gx, gy in room_positions)

            # map size
            map_width = (max_x - min_x + 1) * self.room_size
            map_height = (max_y - min_y + 1) * self.room_size

            # transparent background of map
            map_surface = pygame.Surface((map_width + 2*self.padding, map_height + 2*self.padding), pygame.SRCALPHA)
            map_surface.fill(self.bg_color)

            # draw rooms
            for (gx, gy) in room_positions:
                room = self.game.rooms[(gx, gy)]
                x = (gx - min_x) * self.room_size + self.padding
                y = (gy - min_y) * self.room_size + self.padding
                if not room.visited:
                    color = (100, 200, 255, 100)
                elif room.visited and not room.cleared:
                    color = (150, 150, 255, 200)
                elif room.cleared:
                    color = (50, 255, 50, 140)
                if room == self.game.start_room:
                    color = (50, 100, 255, 100)
                
                # room as a square
                pygame.draw.rect(map_surface, color, (x, y, self.room_size, self.room_size))

                # border
                pygame.draw.rect(map_surface, (100, 100, 100, 150), (x,y,self.room_size,self.room_size), 1)

            # Draw player
            player_room = self.game.get_player_room()
            if player_room:
                px = (player_room[0] - min_x) * self.room_size + self.padding
                py = (player_room[1] - min_y) * self.room_size + self.padding
                # player as a red dot
                pygame.draw.rect(map_surface, self.player_color, (px + self.room_size / 4, py + self.room_size / 4, self.room_size / 2, self.room_size / 2), border_radius=25)

            # blit on map surface with offset position
            surface.blit(map_surface, (WINDOW_WIDTH - map_width - 40, 20))

    def draw_boss_health(self, surface):
        boss = getattr(self.game, 'boss', None)
        if not boss or boss.health <= 0:
            return
        
        bar_width = 500
        bar_height = 35
        x = (WINDOW_WIDTH - bar_width) // 2
        y = 20

        ratio = boss.health / boss.max_health
        ratio = max(0, min(1, ratio))

        # bg hp bar
        pygame.draw.rect(surface, (40,40,40), (x,y, bar_width, bar_height), border_radius=10)

        # hp bar
        pygame.draw.rect(surface, (200,50,50), (x,y,bar_width * ratio, bar_height), border_radius=10)

        # border
        pygame.draw.rect(surface, (255,255,255), (x,y,bar_width,bar_height), 3, border_radius=10)

        surface.blit(self.boss_icon, (x - 40, y / 4))
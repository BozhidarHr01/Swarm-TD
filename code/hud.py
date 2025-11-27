from settings import *

class HUD:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(FONT_PATH, 24)
        self.hotbar_slots = ['Turret', 'Wall', 'Trap']
        self.slot_costs = [TURRET_COST, WALL_COST, TRAP_COST]
        self.selected_slot = 0
        self.slot_width = 100
        self.slot_height = 100
        self.padding = 10
        
        # Health bar settigns
        self.heart_spacing = 5

        self.heart_image = pygame.image.load(join('images', 'health', 'heart.png')).convert_alpha()
        self.heart_bg = pygame.image.load(join('images', 'health', 'background.png')).convert_alpha()
        self.heart_border = pygame.image.load(join('images', 'health', 'border.png')).convert_alpha()

        self.heart_image = pygame.transform.scale(self.heart_image, (50,50))
        self.heart_bg = pygame.transform.scale(self.heart_bg, (50,50))
        self.heart_border = pygame.transform.scale(self.heart_border, (50,50))

        self.heart_width = self.heart_image.get_width()
        self.heart_height = self.heart_image.get_height()
        
        # Colors
        self.health_color = (255,0,0)
        self.empty_health_color = (100, 0, 0)
        self.hotbar_bg_color = (50,50,50, 20)
        self.hotbar_border_color = (255,255,255)
        self.text_color = (255,255,255)
        self.kills_color = (0,0,200)
        self.money_color = (255,200,0)

    def draw(self, surface):

        # Health bar
        for i in range(PLAYER_HEALTH):
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

        # health_text = self.font.render(f"Health: {self.game.player.health}", True, (255,0,0))
        # surface.blit(health_text, (10,10))

        kills_text = self.font.render(f"Kills: {self.game.kills}", True, (0,0,255))
        surface.blit(kills_text, (10,50))

        money_text = self.font.render(f"$: {self.game.money}", True, (255,255,0))
        surface.blit(money_text, (10,80))

        start_x = WINDOW_HEIGHT // 3 - (len(self.hotbar_slots)*(self.slot_width + self.padding)) // 2
        y = WINDOW_HEIGHT - self.slot_height - 10

        for i, slot in enumerate(self.hotbar_slots):
            rect = pygame.Rect(start_x + i*(self.slot_width + self.padding), y, self.slot_width, self.slot_height)
            pygame.draw.rect(surface, self.hotbar_bg_color, rect)
            
            if i == self.selected_slot:
                pygame.draw.rect(surface, self.hotbar_border_color, rect, 3)
            
            text = self.font.render(slot, True, (255,255,255))
            text_rect = text.get_frect(center = rect.center)
            surface.blit(text, text_rect)

            cost_text = self.font.render(f"${self.slot_costs[i]}", True, self.text_color)
            cost_rect = cost_text.get_frect(midtop=(rect.centerx, rect.bottom - 30))
            surface.blit(cost_text, cost_rect)

            key_text = self.font.render(f"{i + 1}", True, self.text_color)
            key_rect = key_text.get_frect(center = (rect.centerx - 35, rect.centery - 38))
            surface.blit(key_text, key_rect)
    def select_slot(self, index):
        if 0 <= index < len(self.hotbar_slots):
            self.selected_slot = index
from settings import * 
from turret import Turret

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
    
    def draw(self, target_pos, surface):
        """
        Apply Y-sort to the object_sprites so that they get sorted by the time they are drawn.
        Ensures that the player can go behind walls and in front of walls without overlapping textures.
        ground_sprites selects only the floor tiles, so they get drawn before all other sprites.
        """
        self.offset.x = -(target_pos[0] - surface.get_width() / 2)
        self.offset.y = -(target_pos[1] - surface.get_height() / 2)
        
        ground_sprites = sorted([sprite for sprite in self if getattr(sprite, 'ground', False)], key = lambda s: s.rect.centery)
        object_sprites = sorted([sprite for sprite in self if not getattr(sprite, 'ground', False)], key = lambda s: s.rect.centery)

        for layer in [ground_sprites, object_sprites]:
            for sprite in layer:
                if isinstance(sprite, Turret):
                    base_rect = sprite.rect.topleft + self.offset
                    surface.blit(sprite.image, base_rect)

                    gun_rect = sprite.gun_rect.topleft + self.offset
                    surface.blit(sprite.gun_image, gun_rect)
                else:
                    surface.blit(sprite.image, sprite.rect.topleft + self.offset)
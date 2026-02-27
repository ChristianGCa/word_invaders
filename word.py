import pygame

class Word:
    def __init__(self, text, x, y, speed, color):
        self.original_text = text
        self.remaining_text = text
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.font = pygame.font.SysFont("arial", 28)

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        font = pygame.font.SysFont("consolas", 30, bold=True)

        # Primeira letra destacada
        if self.remaining_text:
            first_letter = self.remaining_text[0]
            rest = self.remaining_text[1:]
        else:
            first_letter = ""
            rest = ""

        first_surface = font.render(first_letter, True, (255, 255, 0))
        rest_surface = font.render(rest, True, (255, 255, 255))

        width = first_surface.get_width() + rest_surface.get_width()
        height = first_surface.get_height()

        rect = pygame.Rect(self.x, self.y, width + 20, height + 20)

        # Caixa arredondada
        pygame.draw.rect(screen, self.color, rect, border_radius=12)
        pygame.draw.rect(screen, (255,255,255), rect, 2, border_radius=12)

        screen.blit(first_surface, (self.x + 10, self.y + 10))
        screen.blit(rest_surface, (self.x + 10 + first_surface.get_width(), self.y + 10))

    def hit_letter(self):
        if len(self.remaining_text) > 0:
            self.remaining_text = self.remaining_text[1:]

    def is_destroyed(self):
        return len(self.remaining_text) == 0

    def get_first_letter(self):
        if self.remaining_text:
            return self.remaining_text[0]
        return None
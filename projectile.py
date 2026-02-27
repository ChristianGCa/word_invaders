import pygame

class Projectile:
    def __init__(self, start_x, start_y, target_x, target_y):
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y

        self.duration = 5  # quantidade de frames visível
        self.timer = 0
        self.active = True

    def update(self):
        self.timer += 1
        if self.timer >= self.duration:
            self.active = False

    def draw(self, screen):
        pygame.draw.line(
            screen,
            (255, 50, 50),  # vermelho mais bonito
            (self.start_x, self.start_y),
            (self.target_x, self.target_y),
            4
        )
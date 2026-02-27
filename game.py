import pygame
import random
from word import Word
from projectile import Projectile
from loader_csv import load_words

WIDTH = 800
HEIGHT = 600

class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Word Defender")

        self.game_over = False
        self.clock = pygame.time.Clock()
        self.words_data = load_words("words.csv")

        self.words = []
        self.projectiles = []

        self.cannon_img_original = pygame.image.load("assets/sprites/cannon.png").convert_alpha()
        self.cannon_img = pygame.transform.scale2x(self.cannon_img_original)
        self.cannon_img = pygame.transform.scale(self.cannon_img_original, (120, 120))

        self.cannon_rect = self.cannon_img.get_rect()
        self.cannon_rect.center = (WIDTH // 2, HEIGHT - 100)

        self.shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.wav")
        self.error_sound = pygame.mixer.Sound("assets/sounds/error.wav")
        self.explosion_sound = pygame.mixer.Sound("assets/sounds/explosion.wav")
        self.life_losted_sound = pygame.mixer.Sound("assets/sounds/life_losted.wav")

        self.shoot_sound.set_volume(0.4)
        self.error_sound.set_volume(0.5)
        self.explosion_sound.set_volume(0.6)
        self.life_losted_sound.set_volume(0.6)

        self.score = 0
        self.lives = 3
        self.level = 1

        self.spawn_timer = 0
        self.running = True

    def spawn_word(self):
        data = random.choice(self.words_data)

        # Escolhe idioma aleatoriamente
        if random.random() < 0.5:
            text = data["pt"]
        else:
            text = data["en"]

        x = random.randint(50, WIDTH - 150)
        speed = 1 + self.level * 0.5

        color = (0, 100, 255) if random.random() < 0.5 else (255, 100, 0)

        word = Word(text, x, 0, speed, color)
        self.words.append(word)

    def update_level(self):
        if self.score > 3:
            self.level = 2
        if self.score > 9:
            self.level = 3
        if self.score > 15:
            self.level = 4

    def handle_input(self, letter):
        for word in self.words:
            if word.get_first_letter() == letter:
                self.shoot_sound.play()
                target_x = word.x + 10
                target_y = word.y + 10

                projectile = Projectile(
                    WIDTH // 2,
                    HEIGHT - 40,
                    target_x,
                    target_y
                )
                self.projectiles.append(projectile)
                word.hit_letter()
                self.score += 1
                return

        self.error_sound.play()
        for word in self.words:
            word.speed *= 1.2

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.screen.fill((30,30,30))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.unicode.isalpha() and not self.game_over:
                        self.handle_input(event.unicode.lower())
                    if event.key == pygame.K_r and self.lives <= 0:
                        self.__init__()

            if not self.game_over:
                self.spawn_timer += 1
                if self.spawn_timer > 120:
                    self.spawn_word()
                    self.spawn_timer = 0

            for word in self.words[:]:
                if not self.game_over:
                    word.update()

                word.draw(self.screen)

                if word.y > HEIGHT-80:
                    self.life_losted_sound.play()
                    self.lives -= 1
                    self.words.remove(word)
                    if self.lives <= 0:
                        self.game_over = True

                if word.is_destroyed():
                    self.explosion_sound.play()
                    self.words.remove(word)

            for projectile in self.projectiles[:]:
                print(self.projectiles)
                projectile.update()
                projectile.draw(self.screen)
                if not projectile.active:
                    self.projectiles.remove(projectile)

            self.update_level()

            # HUD
            font = pygame.font.SysFont("arial", 24)
            hud = font.render(f"Score: {self.score}  Lives: {self.lives}  Level: {self.level}", True, (255,255,255))
            self.screen.blit(hud, (10,10))

            # Plataforma
            pygame.draw.rect(self.screen, (100,255,100), (0, HEIGHT-40, WIDTH, 40))

            if self.lives <= 0:
                gameover = font.render("GAME OVER - Pressione R", True, (255,0,0))
                self.screen.blit(gameover, (250,300))

            self.screen.blit(self.cannon_img, self.cannon_rect)
            pygame.display.flip()

        pygame.quit()
import pygame
import random
from word import Word
from projectile import Projectile
from loader_csv import load_words

WIDTH = 800
HEIGHT = 600

class Game:
    def __init__(self, start_fullscreen=False):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.window_size = (WIDTH, HEIGHT)
        self.is_fullscreen = start_fullscreen
        self.set_display_mode()
        pygame.display.set_caption("Word Defender")

        self.game_over = False
        self.clock = pygame.time.Clock()
        self.words_data = load_words("base_100_palavras.csv")

        self.words = []
        self.projectiles = []

        self.cannon_img_original = pygame.image.load("assets/sprites/cannon.png").convert_alpha()
        self.cannon_img = pygame.transform.scale2x(self.cannon_img_original)
        self.cannon_img = pygame.transform.scale(self.cannon_img_original, (120, 120))

        self.cannon_rect = self.cannon_img.get_rect()
        self.update_cannon_position()

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
        self.next_word_orange = True
        self.running = True

    def set_display_mode(self):
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.window_size)

        self.width, self.height = self.screen.get_size()

    def update_cannon_position(self):
        self.cannon_rect.center = (self.width // 2, self.height - 100)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.set_display_mode()
        self.update_cannon_position()

    def get_level_config(self):
        if self.level <= 1:
            return {"max_words": 1, "spawn_interval": 120, "len_min": 3, "len_max": 5}
        if self.level == 2:
            return {"max_words": 2, "spawn_interval": 95, "len_min": 4, "len_max": 6}
        if self.level == 3:
            return {"max_words": 3, "spawn_interval": 75, "len_min": 5, "len_max": 8}
        return {"max_words": 4, "spawn_interval": 60, "len_min": 6, "len_max": 20}

    def spawn_word(self):
        level_config = self.get_level_config()
        use_pt = random.random() < 0.5
        if use_pt:
            text_key = "pt"
            len_key = "len_pt"
        else:
            text_key = "en"
            len_key = "len_en"

        candidates = [
            word_data for word_data in self.words_data
            if level_config["len_min"] <= word_data[len_key] <= level_config["len_max"]
        ]
        if not candidates:
            candidates = self.words_data

        data = random.choice(candidates)

        # Escolhe idioma aleatoriamente
        text = data[text_key]

        x = random.randint(50, self.width - 150)
        speed = 1 + self.level * 0.5

        if self.next_word_orange:
            color = (255, 100, 0)
        else:
            color = (0, 100, 255)
        self.next_word_orange = not self.next_word_orange

        word = Word(text, x, 0, speed, color)
        self.words.append(word)

    def update_level(self):
        if self.score > 20:
            self.level = 2
        if self.score > 50:
            self.level = 3
        if self.score > 90:
            self.level = 4

    def handle_input(self, letter):
        for word in self.words:
            if word.get_first_letter() == letter:
                self.shoot_sound.play()
                target_x = word.x + 10
                target_y = word.y + 10

                projectile = Projectile(
                    self.width // 2,
                    self.height - 40,
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

            self.update_level()
            level_config = self.get_level_config()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.TEXTINPUT:
                    if event.text.isalpha() and not self.game_over:
                        self.handle_input(event.text.lower())
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.lives <= 0:
                        self.__init__(start_fullscreen=self.is_fullscreen)
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()

            if not self.game_over:
                self.spawn_timer += 1
                if self.spawn_timer > level_config["spawn_interval"]:
                    if len(self.words) < level_config["max_words"]:
                        self.spawn_word()
                        self.spawn_timer = 0
                    else:
                        self.spawn_timer = level_config["spawn_interval"]

            for word in self.words[:]:
                if not self.game_over:
                    word.update()

                word.draw(self.screen)

                if word.y > self.height - 80:
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

            # HUD
            font = pygame.font.Font("assets/fonts/Micro5-Regular.ttf", 34)
            hud = font.render(f"Score: {self.score}  Lives: {self.lives}  Level: {self.level}", True, (255,255,255))
            self.screen.blit(hud, (10,10))

            # Plataforma
            pygame.draw.rect(self.screen, (100,255,100), (0, self.height - 40, self.width, 40))

            if self.lives <= 0:
                gameover_font = pygame.font.Font("assets/fonts/Micro5-Regular.ttf", 64)
                gameover = gameover_font.render("GAME OVER - Pressione R", True, (255,0,0))
                gameover_rect = gameover.get_rect(center=(self.width // 2, self.height // 2))
                self.screen.blit(gameover, gameover_rect)

            self.screen.blit(self.cannon_img, self.cannon_rect)
            pygame.display.flip()

        pygame.quit()
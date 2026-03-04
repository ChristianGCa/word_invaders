import random
import pygame

from word import Word
from projectile import Projectile
from loader_csv import load_words

WIDTH = 800
HEIGHT = 600
FPS = 60

# Constantes de Cores
WHITE = (255, 255, 255)
ORANGE = (255, 100, 0)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
MENU_BG = (20, 20, 40)
YELLOW = (255, 200, 0)
LIGHT_BLUE = (0, 200, 255)
PURPLE = (200, 100, 255)


class Game:
    """Classe principal que gerencia o ciclo de vida, lógica e renderização do jogo."""

    def __init__(self, start_fullscreen=False):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()

        self.window_size = (WIDTH, HEIGHT)
        self.is_fullscreen = start_fullscreen
        self.set_display_mode()
        pygame.display.set_caption("Word Defender")

        self.clock = pygame.time.Clock()
        self.running = True

        self._load_assets()
        self.resize_images()
        self.start_new_game()

    def _load_assets(self):
        """Carrega todos os recursos estáticos (imagens, sons, fontes e dados) uma única vez."""
        # Imagens
        self.background_img_original = pygame.image.load(
            "assets/sprites/background.png"
        ).convert()
        self.base_img_original = pygame.image.load(
            "assets/sprites/base.png"
        ).convert_alpha()

        # Dados
        self.words_data = load_words("base_100_palavras.csv")

        # Sons
        self.shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.wav")
        self.error_sound = pygame.mixer.Sound("assets/sounds/error.wav")
        self.explosion_sound = pygame.mixer.Sound("assets/sounds/explosion.wav")
        self.life_losted_sound = pygame.mixer.Sound("assets/sounds/life_losted.wav")

        self.shoot_sound.set_volume(0.4)
        self.error_sound.set_volume(0.5)
        self.explosion_sound.set_volume(0.6)
        self.life_losted_sound.set_volume(0.6)

        # Fontes (Evita carregar fontes do disco a cada frame)
        self.word_measure_font = pygame.font.Font("assets/fonts/Bitcount.ttf", 30)
        self.title_font = pygame.font.Font("assets/fonts/Micro5-Regular.ttf", 64)
        self.option_font = pygame.font.Font("assets/fonts/Micro5-Regular.ttf", 40)
        self.hud_font = pygame.font.Font("assets/fonts/Micro5-Regular.ttf", 34)
        self.hint_font = pygame.font.Font("assets/fonts/Micro5-Regular.ttf", 28)
        self.gameover_font = pygame.font.Font("assets/fonts/Micro5-Regular.ttf", 64)
        self.powerup_font = pygame.font.Font("assets/fonts/Micro5-Regular.ttf", 26)

    def start_new_game(self):
        """Redefine os status e variáveis dinâmicas para iniciar ou reiniciar o jogo."""
        self.game_over = False
        self.words = []
        self.projectiles = []

        self.score = 0
        self.lives = 3
        self.level = 1

        self.language_mode = None
        self.in_language_menu = True

        self.combo = 0
        self.combo_timer = 0
        self.combo_timeout = 180

        self.active_powerups = []
        self.slow_timer = 0
        self.slow_duration = 300
        self.shield_active = False
        self.powerup_chance = 0.15

        self.spawn_timer = 0
        self.spawn_horizontal_gap = 30
        self.next_word_orange = True

    def set_display_mode(self):
        """Altera o modo de exibição entre tela cheia e janela."""
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.window_size)

        self.width, self.height = self.screen.get_size()

        if hasattr(self, "background_img_original"):
            self.resize_images()

    def resize_images(self):
        """Redimensiona as imagens mantendo o aspecto visual adequado à tela."""
        self.background_img = pygame.transform.scale(
            self.background_img_original, (self.width, self.height)
        )
        base_width = self.width
        base_height = int(base_width * 0.1)
        self.base_img = pygame.transform.scale(
            self.base_img_original, (base_width, base_height)
        )

    def toggle_fullscreen(self):
        """Alterna a flag de tela cheia e atualiza o display."""
        self.is_fullscreen = not self.is_fullscreen
        self.set_display_mode()

    def get_level_config(self):
        """Retorna os parâmetros de dificuldade baseados no nível atual."""
        if self.level <= 1:
            return {"max_words": 1, "spawn_interval": 120, "len_min": 3, "len_max": 5}
        if self.level == 2:
            return {"max_words": 2, "spawn_interval": 95, "len_min": 4, "len_max": 6}
        if self.level == 3:
            return {"max_words": 3, "spawn_interval": 75, "len_min": 5, "len_max": 8}

        return {"max_words": 4, "spawn_interval": 60, "len_min": 6, "len_max": 20}

    def get_word_rect(self, text, x, y):
        """Calcula o retângulo de colisão estimado para a palavra."""
        text_surface = self.word_measure_font.render(text, True, WHITE)
        return pygame.Rect(
            x, y, text_surface.get_width() + 20, text_surface.get_height() + 20
        )

    def has_spawn_collision(self, new_rect):
        """Verifica se a área onde a palavra vai nascer já está ocupada."""
        spaced_rect = new_rect.inflate(self.spawn_horizontal_gap * 2, 0)
        for active_word in self.words:
            active_rect = self.get_word_rect(
                active_word.remaining_text, active_word.x, active_word.y
            )
            if spaced_rect.colliderect(active_rect):
                return True
        return False

    def spawn_word(self):
        """Gera e posiciona uma nova palavra na tela."""
        level_config = self.get_level_config()
        use_pt = self.language_mode == "pt" or (
            self.language_mode == "mix" and random.random() < 0.5
        )

        text_key = "pt" if use_pt else "en"
        len_key = "len_pt" if use_pt else "len_en"

        candidates = [
            word_data
            for word_data in self.words_data
            if level_config["len_min"] <= word_data[len_key] <= level_config["len_max"]
        ]
        if not candidates:
            candidates = self.words_data

        data = random.choice(candidates)
        text = data[text_key]

        base_rect = self.get_word_rect(text, 0, 0)
        min_x = 20
        max_x = self.width - base_rect.width - 20

        if max_x < min_x:
            return

        x = None
        for _ in range(20):
            candidate_x = random.randint(min_x, max_x)
            candidate_rect = self.get_word_rect(text, candidate_x, 0)
            if not self.has_spawn_collision(candidate_rect):
                x = candidate_x
                break

        if x is None:
            return

        speed = 1 + self.level * 0.5
        color = ORANGE if self.next_word_orange else BLUE

        word = Word(text, x, 0, speed, color)
        self.words.append(word)
        self.next_word_orange = not self.next_word_orange

    def update_level(self):
        """Atualiza a dificuldade do jogo baseado na pontuação."""
        if self.score > 4000:
            self.level = 4
        elif self.score > 1000:
            self.level = 3
        elif self.score > 200:
            self.level = 2

    def handle_input(self, letter):
        """Processa a entrada de teclado do usuário durante o jogo."""
        for word in self.words:
            if word.get_first_letter() == letter:
                self.shoot_sound.play()

                target_x = word.x + 10
                target_y = word.y + 10
                projectile = Projectile(
                    self.width // 2,
                    self.height - self.base_img.get_height(),
                    target_x,
                    target_y,
                )
                self.projectiles.append(projectile)
                word.hit_letter()

                self.combo += 1
                self.combo_timer = 0

                points = 1
                word_length = len(word.original_text)
                if word_length >= 8:
                    points += 2
                elif word_length >= 6:
                    points += 1

                points *= 1 + self.combo // 5
                self.score += points
                return

        self.error_sound.play()
        for word in self.words:
            word.speed *= 1.2
            self.combo = 0
            self.combo_timer = 0

    def activate_powerup(self):
        """Aciona um benefício aleatório para o jogador."""
        powerup = random.choice(["slow", "bomb", "shield"])

        if powerup == "slow":
            self.slow_timer = self.slow_duration
            for word in self.words:
                word.speed *= 0.5
        elif powerup == "bomb":
            if self.words:
                self.words.pop(0)
        elif powerup == "shield":
            self.shield_active = True

        self.active_powerups.append(powerup)

    def run(self):
        """Loop principal do jogo."""
        while self.running:
            self.clock.tick(FPS)

            if self.in_language_menu:
                self._handle_menu_events()
                self._draw_menu()
            else:
                self._handle_game_events()
                if not self.game_over:
                    self._update_game()
                self._draw_game()

        pygame.quit()

    def _handle_menu_events(self):
        """Lida com os eventos enquanto está na tela de menu inicial."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.language_mode = "pt"
                    self.in_language_menu = False
                elif event.key == pygame.K_2:
                    self.language_mode = "en"
                    self.in_language_menu = False
                elif event.key == pygame.K_3:
                    self.language_mode = "mix"
                    self.in_language_menu = False

    def _draw_menu(self):
        """Renderiza o menu inicial."""
        self.screen.fill(MENU_BG)

        title = self.title_font.render("Escolha o idioma", True, WHITE)
        pt_option = self.option_font.render("1 - Digitar PT-BR", True, YELLOW)
        en_option = self.option_font.render("2 - Digitar EN", True, LIGHT_BLUE)
        mix_option = self.option_font.render("3 - Modo Misto", True, PURPLE)

        self.screen.blit(
            title, title.get_rect(center=(self.width // 2, self.height // 3))
        )
        self.screen.blit(
            pt_option, pt_option.get_rect(center=(self.width // 2, self.height // 2))
        )
        self.screen.blit(
            en_option,
            en_option.get_rect(center=(self.width // 2, self.height // 2 + 60)),
        )
        self.screen.blit(
            mix_option,
            mix_option.get_rect(center=(self.width // 2, self.height // 2 + 120)),
        )

        pygame.display.flip()

    def _handle_game_events(self):
        """Lida com inputs do teclado e ações de janela durante a partida."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.TEXTINPUT:
                if event.text.isalpha() and not self.game_over:
                    self.handle_input(event.text.lower())

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.start_new_game()
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()

    def _update_game(self):
        """Atualiza a lógica de entidades do jogo."""
        self.update_level()

        # Gerenciamento do temporizador de lentidão
        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer == 0:
                for word in self.words:
                    word.speed *= 2

        # Gerenciamento de combo
        if self.combo > 0:
            self.combo_timer += 1
            if self.combo_timer > self.combo_timeout:
                self.combo = 0
                self.combo_timer = 0

        # Gerenciamento de Spawn
        level_config = self.get_level_config()
        self.spawn_timer += 1
        if self.spawn_timer > level_config["spawn_interval"]:
            if len(self.words) < level_config["max_words"]:
                self.spawn_word()
                self.spawn_timer = 0
            else:
                self.spawn_timer = level_config["spawn_interval"]

        # Atualiza palavras
        for word in self.words[:]:
            word.update()

            # Checa se atingiu a base
            if word.y > self.height - self.base_img.get_height():
                if self.shield_active:
                    self.shield_active = False
                else:
                    self.life_losted_sound.play()
                    self.lives -= 1

                if word in self.words:
                    self.words.remove(word)
                if self.lives <= 0:
                    self.game_over = True

            # Checa se a palavra foi destruída
            elif word.is_destroyed():
                self.explosion_sound.play()
                if random.random() < self.powerup_chance:
                    self.activate_powerup()
                if word in self.words:
                    self.words.remove(word)

        # Atualiza projéteis
        for projectile in self.projectiles[:]:
            projectile.update()
            if not projectile.active:
                self.projectiles.remove(projectile)

    def _draw_game(self):
        """Renderiza os componentes do jogo na tela."""
        self.screen.blit(self.background_img, (0, 0))

        # Desenha palavras e projéteis
        for word in self.words:
            word.draw(self.screen)

        for projectile in self.projectiles:
            projectile.draw(self.screen)

        # Base do Jogador
        base_x = (self.width - self.base_img.get_width()) // 2
        self.screen.blit(
            self.base_img, (base_x, self.height - self.base_img.get_height())
        )

        # HUD Principal
        mode_texts = {"pt": "PT-BR", "en": "EN", "mix": "MIX"}
        language_text = mode_texts.get(self.language_mode, "")

        hud_text = f"Score: {self.score}  Combo: {self.combo}  Lives: {self.lives}  Level: {self.level}  Mode: {language_text}"
        hud_surface = self.hud_font.render(hud_text, True, WHITE)
        self.screen.blit(hud_surface, (10, 10))

        # Dica de Tela Cheia
        hint_text = (
            "F11 para modo janela" if self.is_fullscreen else "F11 para tela cheia"
        )
        hint_surface = self.hint_font.render(hint_text, True, WHITE)
        hint_rect = hint_surface.get_rect(topright=(self.width - 10, 10))
        self.screen.blit(hint_surface, hint_rect)

        # HUD de Powerups
        active_text = []
        if self.slow_timer > 0:
            active_text.append("SLOW")
        if self.shield_active:
            active_text.append("SHIELD")

        if active_text:
            pu_surface = self.powerup_font.render(
                "Power: " + " | ".join(active_text), True, GREEN
            )
            self.screen.blit(pu_surface, (10, 50))

        # Tela de Game Over
        if self.game_over:
            gameover_surface = self.gameover_font.render(
                "GAME OVER - Pressione R", True, RED
            )
            gameover_rect = gameover_surface.get_rect(
                center=(self.width // 2, self.height // 2)
            )
            self.screen.blit(gameover_surface, gameover_rect)

        pygame.display.flip()

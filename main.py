import random
import pygame

from persistence.record_store import RecordStore
from repositories import ProfileRepository, SettingsRepository, LeaderboardRepository


WIDTH = 900
HEIGHT = 400
GROUND_Y = 320
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (210, 210, 210)
GREEN = (40, 140, 70)
RED = (180, 60, 60)
BROWN = (120, 90, 60)


class Jugador:
    def __init__(self):
        self.x = 90
        self.w = 120
        self.h = 140
        self.y = GROUND_Y - self.h
        self.draw_offset_y = 35
        self.vel_y = 0
        self.jump_force = -15
        self.gravity = 0.8
        self.is_jumping = False

        sprite_sheet = pygame.image.load("assets/miku_caminando.png").convert_alpha()
        frame_width = sprite_sheet.get_width() // 4
        frame_height = sprite_sheet.get_height()

        self.run_frames = []
        for i in range(4):
            frame = sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (self.w, self.h))
            self.run_frames.append(frame)

        self.jump_frame = self.run_frames[0]
        self.frame_index = 0
        self.anim_counter = 0
        self.image = self.run_frames[0]

    def jump(self):
        if not self.is_jumping:
            self.vel_y = self.jump_force
            self.is_jumping = True

    def update(self):
        self.y += self.vel_y
        self.vel_y += self.gravity

        if self.y >= GROUND_Y - self.h:
            self.y = GROUND_Y - self.h
            self.vel_y = 0
            self.is_jumping = False
        else:
            self.is_jumping = True

        if not self.is_jumping:
            self.anim_counter += 1
            if self.anim_counter >= 6:
                self.anim_counter = 0
                self.frame_index = (self.frame_index + 1) % len(self.run_frames)
            self.image = self.run_frames[self.frame_index]
        else:
            self.image = self.jump_frame

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y + self.draw_offset_y))


class Obstaculo:
    def __init__(self, speed):
        self.image = pygame.image.load("assets/cactus.png").convert_alpha()
        self.w = 55
        self.h = 95
        self.image = pygame.transform.scale(self.image, (self.w, self.h))
        self.x = WIDTH + random.randint(0, 180)
        self.y = GROUND_Y - self.h + 20
        self.speed = speed

    def update(self, speed):
        self.speed = speed
        self.x -= self.speed

    def rect(self):
        hitbox_x = self.x + self.w * 0.28
        hitbox_y = self.y + self.h * 0.12
        hitbox_w = self.w * 0.44
        hitbox_h = self.h * 0.78

        return pygame.Rect(
            int(hitbox_x),
            int(hitbox_y),
            int(hitbox_w),
            int(hitbox_h)
        )

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


def draw_text(screen, text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


class jugadorGame:
    def __init__(self):
        pygame.init()

        self.store = RecordStore()
        self.profile_repo = ProfileRepository(self.store)
        self.settings_repo = SettingsRepository(self.store)
        self.leaderboard_repo = LeaderboardRepository(self.store)

        self.settings = self.settings_repo.get_settings()
        if self.settings is None:
            self.settings = [50, "Normal", 0]
            self.settings_repo.save_settings(self.settings[0], self.settings[1], self.settings[2])
        else:
            self.settings[2] = 0
            self.settings_repo.save_settings(self.settings[0], self.settings[1], self.settings[2])

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Jugador Hash Game")
        self.clock = pygame.time.Clock()

        self.big_font = pygame.font.SysFont("arial", 34, bold=True)
        self.font = pygame.font.SysFont("arial", 24)
        self.small_font = pygame.font.SysFont("arial", 18)

        self.background = pygame.image.load("assets/fondo_desierto.png").convert()
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))

        self.menu_jugador = Jugador()
        self.menu_jugador.x = 180
        self.menu_jugador.y = GROUND_Y - self.menu_jugador.h

        self.menu_obstaculo = Obstaculo(0)
        self.menu_obstaculo.x = 680
        self.menu_obstaculo.y = GROUND_Y - self.menu_obstaculo.h + 20

        self.state = "login"
        self.username_input = ""
        self.password_input = ""
        self.active_field = "username"
        self.login_message = "Escribe usuario y contraseña"
        self.current_user = ""
        self.profile = None

        self.menu_index = 0
        self.menu_options = ["Start Game", "Continue Game", "Leaderboard", "Settings", "Quit"]

        self.reset_game_objects()

    def reset_game_objects(self):
        self.Jugador = Jugador()
        self.obstacles = [Obstaculo(7)]
        self.score = 0
        self.speed = 7
        self.frame_count = 0

    def handle_login_key(self, key, unicode_char):
        if key == pygame.K_TAB:
            if self.active_field == "username":
                self.active_field = "password"
            else:
                self.active_field = "username"

        elif key == pygame.K_BACKSPACE:
            if self.active_field == "username":
                self.username_input = self.username_input[:-1]
            else:
                self.password_input = self.password_input[:-1]

        elif key == pygame.K_RETURN:
            username = self.username_input.strip()
            password = self.password_input.strip()

            if username == "":
                self.login_message = "Escribe un usuario"
                return

            if password == "":
                self.login_message = "Escribe una contraseña"
                return

            profile = self.profile_repo.login_user(username, password)

            if profile is None:
                self.login_message = "Usuario o contraseña incorrecta"
            else:
                self.current_user = username
                self.profile = profile
                self.login_message = "Bienvenido " + username
                self.state = "menu"

        elif key == pygame.K_LSHIFT or key == pygame.K_RSHIFT:
            username = self.username_input.strip()
            password = self.password_input.strip()

            if username == "":
                self.login_message = "Escribe un usuario"
                return

            if password == "":
                self.login_message = "Escribe una contraseña"
                return

            created = self.profile_repo.create_user(username, password)

            if created:
                self.login_message = "Cuenta creada. Ahora presiona ENTER"
            else:
                self.login_message = "Ese usuario ya existe"

        else:
            if unicode_char.isprintable() and len(unicode_char) == 1:
                if self.active_field == "username":
                    if len(self.username_input) < 15:
                        self.username_input += unicode_char
                else:
                    if len(self.password_input) < 15:
                        self.password_input += unicode_char

    def draw_login(self):
        self.screen.fill((240, 240, 240))

        title = self.big_font.render("LOGIN / REGISTER", True, BLACK)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 35))

        username_label = self.font.render("Usuario:", True, BLACK)
        password_label = self.font.render("Contraseña:", True, BLACK)

        self.screen.blit(username_label, (WIDTH // 2 - 230, 100))
        self.screen.blit(password_label, (WIDTH // 2 - 230, 165))

        username_box = pygame.Rect(WIDTH // 2 - 120, 95, 240, 40)
        password_box = pygame.Rect(WIDTH // 2 - 120, 160, 240, 40)

        color_user = (0, 120, 255) if self.active_field == "username" else BLACK
        color_pass = (0, 120, 255) if self.active_field == "password" else BLACK

        pygame.draw.rect(self.screen, color_user, username_box, 2)
        pygame.draw.rect(self.screen, color_pass, password_box, 2)

        username_text = self.font.render(self.username_input, True, BLACK)
        hidden_password = "*" * len(self.password_input)
        password_text = self.font.render(hidden_password, True, BLACK)

        self.screen.blit(username_text, (WIDTH // 2 - 110, 103))
        self.screen.blit(password_text, (WIDTH // 2 - 110, 168))

        hint1 = self.small_font.render("TAB cambia campo", True, BLACK)
        hint2 = self.small_font.render("ENTER inicia sesión", True, BLACK)
        hint3 = self.small_font.render("SHIFT registra cuenta nueva", True, BLACK)

        self.screen.blit(hint1, (WIDTH // 2 - hint1.get_width() // 2, 230))
        self.screen.blit(hint2, (WIDTH // 2 - hint2.get_width() // 2, 255))
        self.screen.blit(hint3, (WIDTH // 2 - hint3.get_width() // 2, 280))

        if self.login_message != "":
            msg = self.small_font.render(self.login_message, True, (200, 0, 0))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 345))

    def save_after_game(self):
        if self.profile is None:
            return

        username = self.profile[0]
        password = self.profile[1]
        best_score = self.profile[2]
        total_games = self.profile[3]

        if self.score > best_score:
            best_score = self.score

        total_games += 1
        last_score = self.score

        self.profile = [username, password, best_score, total_games, last_score]
        self.profile_repo.save_profile(username, password, best_score, total_games, last_score)
        self.leaderboard_repo.save_score(username, self.score)

    def start_new_game(self):
        self.reset_game_objects()
        self.state = "playing"

    def continue_game(self):
        self.reset_game_objects()
        self.state = "playing"

    def update_playing(self):
        self.frame_count += 1
        self.score += 1

        if self.frame_count % 300 == 0:
            self.speed += 0.5

        self.Jugador.update()

        for obstacle in self.obstacles:
            obstacle.update(self.speed)

        self.obstacles = [ob for ob in self.obstacles if ob.x > -80]

        if len(self.obstacles) == 0 or self.obstacles[-1].x < WIDTH - random.randint(240, 340):
            self.obstacles.append(Obstaculo(self.speed))

        jugador_rect = self.Jugador.rect()

        for obstacle in self.obstacles:
            if jugador_rect.colliderect(obstacle.rect()):
                self.save_after_game()
                self.state = "game_over"
                break

    def draw_background(self):
        self.screen.blit(self.background, (0, 0))

    def draw_menu(self):
        self.draw_background()

        title = self.big_font.render("RUNNING GAME", True, BLACK)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        help_text = self.small_font.render("Usa flechas y ENTER", True, BLACK)
        self.screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, 100))

        for i, option in enumerate(self.menu_options):
            color = RED if i == self.menu_index else BLACK
            option_text = self.font.render(option, True, color)
            self.screen.blit(option_text, (WIDTH // 2 - option_text.get_width() // 2, 155 + i * 34))

        if self.profile is not None:
            draw_text(self.screen, "Usuario: " + self.profile[0], self.small_font, BLACK, WIDTH - 255, 20)
            draw_text(self.screen, "Best Score: " + str(self.profile[2]), self.small_font, BLACK, WIDTH - 255, 45)
            draw_text(self.screen, "Games: " + str(self.profile[3]), self.small_font, BLACK, WIDTH - 255, 70)

        self.menu_jugador.draw(self.screen)
        self.menu_obstaculo.draw(self.screen)

    def draw_playing(self):
        self.draw_background()
        self.Jugador.draw(self.screen)

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        draw_text(self.screen, "SPACE / UP = jump", self.font, BLACK, 20, 20)
        draw_text(self.screen, "Score: " + str(self.score), self.font, BLACK, WIDTH // 2 - 30, 20)

        if self.profile is not None:
            draw_text(self.screen, "Best: " + str(self.profile[2]), self.font, BLACK, WIDTH // 2 - 25, 50)
            draw_text(self.screen, "Jugador: " + self.profile[0], self.font, BLACK, 20, 50)

    def draw_leaderboard(self):
        self.draw_background()
        draw_text(self.screen, "LEADERBOARD", self.big_font, BLACK, 300, 50)

        scores = self.leaderboard_repo.get_top_scores(5)

        if len(scores) == 0:
            draw_text(self.screen, "Aún no hay puntajes guardados", self.font, BLACK, 240, 150)
        else:
            for i, item in enumerate(scores):
                text = str(i + 1) + ". " + item[0] + " - " + str(item[1])
                draw_text(self.screen, text, self.font, BLACK, 280, 120 + i * 35)

        draw_text(self.screen, "ESC para volver", self.small_font, BLACK, 20, 20)

    def draw_settings(self):
        self.draw_background()
        draw_text(self.screen, "SETTINGS", self.big_font, BLACK, WIDTH // 2 - 50, 50)
        draw_text(self.screen, "Volume: " + str(self.settings[0]), self.font, BLACK, WIDTH // 2 - 50, 140)
        draw_text(self.screen, "Difficulty: " + self.settings[1], self.font, BLACK, WIDTH // 2 - 50, 180)
        draw_text(self.screen, "Fullscreen: OFF", self.font, BLACK, WIDTH // 2 - 50, 220)

        draw_text(self.screen, "LEFT/RIGHT cambia volumen", self.small_font, BLACK, WIDTH // 2 - 50, 280)
        draw_text(self.screen, "D cambia dificultad", self.small_font, BLACK, WIDTH // 2 - 50, 305)
        draw_text(self.screen, "S guarda y ESC vuelve", self.small_font, BLACK, WIDTH // 2 - 50, 330)

    def draw_game_over(self):
        self.draw_background()
        self.Jugador.draw(self.screen)

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        draw_text(self.screen, "GAME OVER", self.big_font, RED, WIDTH // 2 - 100, 70)
        draw_text(self.screen, "Score: " + str(self.score), self.font, BLACK, WIDTH // 2 - 50, 140)

        if self.profile is not None:
            draw_text(self.screen, "Best Score: " + str(self.profile[2]), self.font, BLACK, WIDTH // 2 - 80, 180)

        draw_text(self.screen, "ENTER para volver al menu", self.font, BLACK, WIDTH // 2 - 150, 240)
        draw_text(self.screen, "R para jugar otra vez", self.font, BLACK, WIDTH // 2 - 110, 280)

    def change_difficulty(self):
        current = self.settings[1]

        if current == "Easy":
            self.settings[1] = "Normal"
        elif current == "Normal":
            self.settings[1] = "Hard"
        else:
            self.settings[1] = "Easy"

    def handle_menu_key(self, key):
        if key == pygame.K_UP:
            self.menu_index = (self.menu_index - 1) % len(self.menu_options)
        elif key == pygame.K_DOWN:
            self.menu_index = (self.menu_index + 1) % len(self.menu_options)
        elif key == pygame.K_RETURN:
            option = self.menu_options[self.menu_index]

            if option == "Start Game":
                self.start_new_game()
            elif option == "Continue Game":
                self.continue_game()
            elif option == "Leaderboard":
                self.state = "leaderboard"
            elif option == "Settings":
                self.state = "settings"
            elif option == "Quit":
                return False

        return True

    def handle_settings_key(self, key):
        if key == pygame.K_LEFT:
            self.settings[0] = max(0, self.settings[0] - 5)
        elif key == pygame.K_RIGHT:
            self.settings[0] = min(100, self.settings[0] + 5)
        elif key == pygame.K_d:
            self.change_difficulty()
        elif key == pygame.K_s:
            self.settings_repo.save_settings(self.settings[0], self.settings[1], self.settings[2])
        elif key == pygame.K_ESCAPE:
            self.settings_repo.save_settings(self.settings[0], self.settings[1], self.settings[2])
            self.state = "menu"

    def run(self):
        running = True

        while running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if self.state == "login":
                        self.handle_login_key(event.key, event.unicode)

                    elif self.state == "menu":
                        running = self.handle_menu_key(event.key)

                    elif self.state == "playing":
                        if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                            self.Jugador.jump()
                        elif event.key == pygame.K_ESCAPE:
                            self.state = "menu"

                    elif self.state == "leaderboard":
                        if event.key == pygame.K_ESCAPE:
                            self.state = "menu"

                    elif self.state == "settings":
                        self.handle_settings_key(event.key)

                    elif self.state == "game_over":
                        if event.key == pygame.K_RETURN:
                            self.state = "menu"
                        elif event.key == pygame.K_r:
                            self.start_new_game()

            if self.state == "playing":
                self.update_playing()

            if self.state == "login":
                self.draw_login()
            elif self.state == "menu":
                self.draw_menu()
            elif self.state == "playing":
                self.draw_playing()
            elif self.state == "leaderboard":
                self.draw_leaderboard()
            elif self.state == "settings":
                self.draw_settings()
            elif self.state == "game_over":
                self.draw_game_over()

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = jugadorGame()
    game.run()

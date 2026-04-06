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
YELLOW = (230, 200, 60)


class Dino:
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

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y+self.draw_offset_y))
        # body = self.rect()
        #pygame.draw.rect(screen, BLACK, body)
        #pygame.draw.rect(screen, WHITE, (body.x + 28, body.y + 10, 7, 7))
        #pygame.draw.rect(screen, WHITE, (body.x + 31, body.y + 13, 2, 2))
        #pygame.draw.rect(screen, BLACK, (body.x + 24, body.y + 18, 16, 4))
        #pygame.draw.rect(screen, BLACK, (body.x + 5, body.y - 10, 14, 14))
        #pygame.draw.rect(screen, BLACK, (body.x + 2, body.y + 46, 8, 14))
        #pygame.draw.rect(screen, BLACK, (body.x + 18, body.y + 46, 8, 14))


class Cactus:
    def __init__(self, speed):
        self.w = random.choice([20, 26, 32])
        self.h = random.choice([40, 55, 70])
        self.x = WIDTH + random.randint(0, 180)
        self.y = GROUND_Y - self.h
        self.speed = speed

    def update(self, speed):
        self.speed = speed
        self.x -= self.speed

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def draw(self, screen):
        r = self.rect()
        pygame.draw.rect(screen, GREEN, r)
        pygame.draw.rect(screen, GREEN, (r.x - 6, r.y + 10, 6, 18))
        pygame.draw.rect(screen, GREEN, (r.x + r.w, r.y + 14, 6, 18))


class Cloud:
    def __init__(self):
        self.x = WIDTH + random.randint(0, 300)
        self.y = random.randint(40, 130)
        self.speed = random.uniform(1.0, 2.0)

    def update(self):
        self.x -= self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, GRAY, (int(self.x), int(self.y)), 16)
        pygame.draw.circle(screen, GRAY, (int(self.x + 18), int(self.y + 2)), 14)
        pygame.draw.circle(screen, GRAY, (int(self.x + 34), int(self.y)), 16)


def draw_text(screen, text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


class DinoGame:
    def __init__(self):
        pygame.init()
        self.settings = [50, 'Normal', 0]   # volumen, dificultad, fullscreen
        
        self.screen = None
        self.apply_display_mode()
        
        pygame.display.set_caption('Dino Hash Game')
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load("assets/pared.png").convert()
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
        sprite_sheet = pygame.image.load("assets/miku_caminando.png").convert_alpha()
        frame_width = sprite_sheet.get_width() // 4
        frame_height = sprite_sheet.get_height()
        self.dino_run_frames = []
        for i in range(4):
            frame = sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (120, 140))
            self.dino_run_frames.append(frame)
        self.dino_jump_frame = self.dino_run_frames[0]
        self.dino_frame_index = 0
        self.dino_anim_counter = 0
        self.dino_image = self.dino_run_frames[0]
        
        
        self.big_font = pygame.font.SysFont('arial', 34, bold=True)
        self.font = pygame.font.SysFont('arial', 24)
        self.small_font = pygame.font.SysFont('arial', 18)

        self.store = RecordStore()
        self.profile_repo = ProfileRepository(self.store)
        self.settings_repo = SettingsRepository(self.store)
        self.leaderboard_repo = LeaderboardRepository(self.store)

        self.player_id = '1'
        self.player_name = 'Player1'

        self.settings = self.settings_repo.get_settings()
        if self.settings is None:
            self.settings = [50, 'Normal', 0]
            self.settings_repo.save_settings(self.settings[0], self.settings[1], self.settings[2])

        self.profile = self.profile_repo.get_profile(self.player_id)
        if self.profile is None:
            self.profile = [self.player_id, self.player_name, 0, 0, 0]
            self.profile_repo.save_profile(self.player_id, self.player_name, 0, 0, 0)
            
        self.state = 'login'
        self.username_input = ''
        self.password_input = ''
        self.active_field = 'username'
        self.login_message = ''
        self.player_id = ''
        self.player_name = ''
        self.state = 'menu'
        self.menu_index = 0
        self.menu_options = ['Start Game', 'Continue Game', 'Leaderboard', 'Settings', 'Quit']
        self.reset_game_objects()
        
    def handle_login_key(self, key, unicode_char):
        if key == pygame.K_TAB:
            if self.active_field == 'username':
                self.active_field = 'password'
            else:
                self.active_field = 'username'

        elif key == pygame.K_BACKSPACE:
            if self.active_field == 'username':
                self.username_input = self.username_input[:-1]
            else:
                self.password_input = self.password_input[:-1]

        elif key == pygame.K_RETURN:
            self.try_login()

        else:
            if unicode_char.isprintable() and len(unicode_char) == 1:
                if self.active_field == 'username':
                    if len(self.username_input) < 15:
                        self.username_input += unicode_char
                else:
                    if len(self.password_input) < 15:
                        self.password_input += unicode_char
    
    def try_login(self):
        username = self.username_input.strip()
        password = self.password_input.strip()

        if username == '':
            self.login_message = 'Escribe un usuario'
            return

        if password == '':
            self.login_message = 'Escribe una contrasena'
            return

        self.player_id = username
        self.player_name = username
        self.login_message = ''
        self.state = 'menu'
        
    def draw_login(self):
        self.screen.fill((240, 240, 240))

        title = self.big_font.render('LOGIN', True, (0, 0, 0))
        self.screen.blit(title, (330, 70))

        username_label = self.font.render('Usuario:', True, (0, 0, 0))
        password_label = self.font.render('Contrasena:', True, (0, 0, 0))

        self.screen.blit(username_label, (210, 170))
        self.screen.blit(password_label, (210, 250))

        username_box = pygame.Rect(350, 165, 220, 45)
        password_box = pygame.Rect(350, 245, 220, 45)

        color_user = (0, 120, 255) if self.active_field == 'username' else (0, 0, 0)
        color_pass = (0, 120, 255) if self.active_field == 'password' else (0, 0, 0)

        pygame.draw.rect(self.screen, color_user, username_box, 2)
        pygame.draw.rect(self.screen, color_pass, password_box, 2)

        username_text = self.font.render(self.username_input, True, (0, 0, 0))
        hidden_password = '*' * len(self.password_input)
        password_text = self.font.render(hidden_password, True, (0, 0, 0))

        self.screen.blit(username_text, (360, 175))
        self.screen.blit(password_text, (360, 255))

        hint1 = self.small_font.render('TAB cambia campo', True, (0, 0, 0))
        hint2 = self.small_font.render('ENTER inicia sesion', True, (0, 0, 0))

        self.screen.blit(hint1, (295, 340))
        self.screen.blit(hint2, (280, 365))

        if self.login_message != '':
            msg = self.small_font.render(self.login_message, True, (200, 0, 0))
            self.screen.blit(msg, (300, 410))
        
    def apply_display_mode(self):
        if self.settings[2] == 1:
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
    def reset_game_objects(self):
        self.dino = Dino()
        self.obstacles = [Cactus(7)]
        self.clouds = [Cloud(), Cloud()]
        self.score = 0
        self.speed = 7
        self.frame_count = 0
        self.game_started_before = self.profile[4] > 0 or self.profile[2] > 0

    def save_after_game(self):
        best_score = self.profile[2]
        total_games = self.profile[3]

        if self.score > best_score:
            best_score = self.score

        total_games += 1
        last_score = self.score

        self.profile = [self.player_id, self.player_name, best_score, total_games, last_score]
        self.profile_repo.save_profile(self.player_id, self.player_name, best_score, total_games, last_score)
        self.leaderboard_repo.save_score(self.player_name, self.score)

    def start_new_game(self):
        self.reset_game_objects()
        self.state = 'playing'

    def continue_game(self):
        self.reset_game_objects()
        self.state = 'playing'

    def update_playing(self):
        self.frame_count += 1
        self.score += 1

        if self.frame_count % 300 == 0:
            self.speed += 0.5

        self.dino.update()

        for cloud in self.clouds:
            cloud.update()
        self.clouds = [cloud for cloud in self.clouds if cloud.x > -80]
        if len(self.clouds) < 3 and random.randint(0, 100) < 2:
            self.clouds.append(Cloud())

        for obstacle in self.obstacles:
            obstacle.update(self.speed)

        self.obstacles = [ob for ob in self.obstacles if ob.x > -80]
        if len(self.obstacles) == 0 or self.obstacles[-1].x < WIDTH - random.randint(240, 340):
            self.obstacles.append(Cactus(self.speed))

        dino_rect = self.dino.rect()
        for obstacle in self.obstacles:
            if dino_rect.colliderect(obstacle.rect()):
                self.save_after_game()
                self.state = 'game_over'
                break

    def draw_background(self):
        self.screen.blit(self.background, (0, 0))
        pygame.draw.line(self.screen, BROWN, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)
        for cloud in self.clouds:
            cloud.draw(self.screen)
            
    def draw_menu(self):
        self.draw_background()
        draw_text(self.screen, 'RUNNING GAME', self.big_font, BLACK, 290, 60)
        draw_text(self.screen, 'Versión 0.3', self.font, BLACK, 300, 105)
        draw_text(self.screen, 'Usa flechas y ENTER', self.small_font, BLACK, 360, 140)

        for i, option in enumerate(self.menu_options):
            color = RED if i == self.menu_index else BLACK
            draw_text(self.screen, option, self.font, color, 360, 190 + i * 40)

        draw_text(self.screen, 'Best Score: ' + str(self.profile[2]), self.small_font, BLACK, 20, 20)
        draw_text(self.screen, 'Games: ' + str(self.profile[3]), self.small_font, BLACK, 20, 45)
        
        temp_dino = Dino()
        temp_dino.x = 180
        temp_dino.y = 220
        temp_dino.draw(self.screen)
        cactus = Cactus(0)
        cactus.x = 680
        cactus.y = GROUND_Y - cactus.h
        cactus.draw(self.screen)

    def draw_playing(self):
        self.screen.blit(self.background, (0, 0))
        self.dino.draw(self.screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        draw_text(self.screen, 'Score: ' + str(self.score), self.font, BLACK, 20, 20)
        draw_text(self.screen, 'Best: ' + str(self.profile[2]), self.font, BLACK, 20, 50)
        draw_text(self.screen, 'SPACE / UP = jump', self.small_font, BLACK, 20, 80)

    def draw_leaderboard(self):
        self.draw_background()
        draw_text(self.screen, 'LEADERBOARD', self.big_font, BLACK, 320, 50)
        scores = self.leaderboard_repo.get_top_scores(5)
        if len(scores) == 0:
            draw_text(self.screen, 'Aun no hay puntajes guardados', self.font, BLACK, 270, 150)
        else:
            for i, item in enumerate(scores):
                text = str(i + 1) + '. ' + item[0] + '  ' + str(item[1])
                draw_text(self.screen, text, self.font, BLACK, 320, 120 + i * 28)
        draw_text(self.screen, 'ESC para volver', self.small_font, BLACK, 20, 20)

    def draw_settings(self):
        self.draw_background()
        draw_text(self.screen, 'SETTINGS', self.big_font, BLACK, 360, 50)
        draw_text(self.screen, 'Volume: ' + str(self.settings[0]), self.font, BLACK, 320, 140)
        draw_text(self.screen, 'Difficulty: ' + self.settings[1], self.font, BLACK, 320, 180)
        fullscreen_text = 'ON' if self.settings[2] == 1 else 'OFF'
        draw_text(self.screen, 'Fullscreen: ' + fullscreen_text, self.font, BLACK, 320, 220)
        draw_text(self.screen, 'LEFT/RIGHT cambia volumen', self.small_font, BLACK, 280, 280)
        draw_text(self.screen, 'D cambia dificultad', self.small_font, BLACK, 310, 305)
        draw_text(self.screen, 'F cambia fullscreen', self.small_font, BLACK, 308, 330)
        draw_text(self.screen, 'S guarda y ESC vuelve', self.small_font, BLACK, 320, 355)

    def draw_game_over(self):
        self.draw_background()
        self.dino.draw(self.screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        draw_text(self.screen, 'GAME OVER', self.big_font, RED, 340, 70)
        draw_text(self.screen, 'Score: ' + str(self.score), self.font, BLACK, 375, 140)
        draw_text(self.screen, 'Best Score: ' + str(self.profile[2]), self.font, BLACK, 345, 180)
        draw_text(self.screen, 'ENTER para volver al menu', self.font, BLACK, 275, 240)
        draw_text(self.screen, 'R para jugar otra vez', self.font, BLACK, 330, 280)

    def change_difficulty(self):
        current = self.settings[1]
        if current == 'Easy':
            self.settings[1] = 'Normal'
        elif current == 'Normal':
            self.settings[1] = 'Hard'
        else:
            self.settings[1] = 'Easy'

    def handle_menu_key(self, key):
        if key == pygame.K_UP:
            self.menu_index = (self.menu_index - 1) % len(self.menu_options)
        elif key == pygame.K_DOWN:
            self.menu_index = (self.menu_index + 1) % len(self.menu_options)
        elif key == pygame.K_RETURN:
            option = self.menu_options[self.menu_index]
            if option == 'Start Game':
                self.start_new_game()
            elif option == 'Continue Game':
                self.continue_game()
            elif option == 'Leaderboard':
                self.state = 'leaderboard'
            elif option == 'Settings':
                self.state = 'settings'
            elif option == 'Quit':
                return False
        return True

    def handle_settings_key(self, key):
        if key == pygame.K_LEFT:
            self.settings[0] = max(0, self.settings[0] - 5)
        elif key == pygame.K_RIGHT:
            self.settings[0] = min(100, self.settings[0] + 5)
        elif key == pygame.K_d:
            self.change_difficulty()
        elif key == pygame.K_f:
            self.settings[2] = 0 if self.settings[2] == 1 else 1
            self.apply_display_mode()
        elif key == pygame.K_s:
            self.settings_repo.save_settings(self.settings[0], self.settings[1], self.settings[2])
        elif key == pygame.K_ESCAPE:
            self.settings_repo.save_settings(self.settings[0], self.settings[1], self.settings[2])
            self.state = 'menu'

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state=='login':
                        self.handle_login_key(event.key, event.unicode)
                    elif self.state == 'menu':
                        running = self.handle_menu_key(event.key)
                    elif self.state == 'playing':
                        if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                            self.dino.jump()
                        elif event.key == pygame.K_ESCAPE:
                            self.state = 'menu'
                    elif self.state == 'leaderboard':
                        if event.key == pygame.K_ESCAPE:
                            self.state = 'menu'
                    elif self.state == 'settings':
                        self.handle_settings_key(event.key)
                    elif self.state == 'game_over':
                        if event.key == pygame.K_RETURN:
                            self.state = 'menu'
                        elif event.key == pygame.K_r:
                            self.start_new_game()

            if self.state == 'playing':
                self.update_playing()
            if self.state == 'login':
                self.draw_login()
            elif self.state == 'menu':
                self.draw_menu()
            elif self.state == 'playing':
                self.draw_playing()
            elif self.state == 'leaderboard':
                self.draw_leaderboard()
            elif self.state == 'settings':
                self.draw_settings()
            elif self.state == 'game_over':
                self.draw_game_over()

            pygame.display.flip()

        pygame.quit()


if __name__ == '__main__':
    game = DinoGame()
    game.run()

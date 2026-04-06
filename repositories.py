import asyncio
import random
import time
import pygame
from persistence.record_store import RecordStore
from repositories import ProfileRepository, SettingsRepository, LeaderboardRepository


pygame.init()
pygame.font.init()

WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BLUE = (70, 120, 255)
YELLOW = (255, 220, 50)
RED = (220, 70, 70)
GREEN = (60, 180, 90)
GRAY = (180, 180, 180)

font_big = pygame.font.SysFont(None, 48)
font_mid = pygame.font.SysFont(None, 32)
font_small = pygame.font.SysFont(None, 24)

PLAYER_ID = '1'
PLAYER_NAME = 'Player1'

store = RecordStore('data/data.log', 'data/index.bin')
profile_repo = ProfileRepository(store)
settings_repo = SettingsRepository(store)
leaderboard_repo = LeaderboardRepository(store)


class App:
    def __init__(self):
        self.settings = settings_repo.get_settings(PLAYER_ID)
        if self.settings is None:
            self.settings = [PLAYER_ID, 80, 'Normal', 0]
            settings_repo.save_settings(PLAYER_ID, 80, 'Normal', 0)

        self.screen = self.build_screen()
        pygame.display.set_caption('Hash Game')
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene = 'menu'
        self.menu_index = 0
        self.menu_options = ['Start Game', 'Continue Game', 'Leaderboard', 'Settings', 'Exit']
        self.settings_index = 0
        self.setting_names = ['Volume', 'Difficulty', 'Fullscreen', 'Back']
        self.difficulties = ['Easy', 'Normal', 'Hard']
        self.message = ''
        self.message_time = 0

        self.reset_game_data(1, 0)

    def build_screen(self):
        fullscreen = False
        if self.settings is not None:
            fullscreen = self.settings[3] == 1
        flags = 0
        if fullscreen:
            flags = pygame.FULLSCREEN
        try:
            return pygame.display.set_mode((WIDTH, HEIGHT), flags)
        except Exception:
            return pygame.display.set_mode((WIDTH, HEIGHT))

    def reset_game_data(self, level, coins):
        self.player_x = 100
        self.player_y = 100
        self.player_size = 40
        self.coin_x = random.randint(80, WIDTH - 80)
        self.coin_y = random.randint(120, HEIGHT - 80)
        self.score = 0
        self.level = level
        self.total_coins = coins
        self.game_start = time.time()
        self.game_duration = 20

    def start_new_game(self):
        self.reset_game_data(1, 0)
        self.scene = 'game'

    def continue_game(self):
        profile = profile_repo.get_profile(PLAYER_ID)
        if profile is None:
            self.reset_game_data(1, 0)
        else:
            self.reset_game_data(profile[2], profile[3])
        self.scene = 'game'

    def save_game_result(self):
        run_id = str(int(time.time() * 1000))
        self.total_coins += self.score // 10
        self.level = 1 + self.total_coins // 5
        profile_repo.save_profile(PLAYER_ID, PLAYER_NAME, self.level, self.total_coins, self.score)
        leaderboard_repo.add_score(run_id, PLAYER_ID, PLAYER_NAME, self.score)
        self.message = 'Partida guardada automaticamente'
        self.message_time = time.time()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.scene == 'menu':
                    self.handle_menu_keys(event.key)
                elif self.scene == 'settings':
                    self.handle_settings_keys(event.key)
                elif self.scene == 'leaderboard':
                    if event.key == pygame.K_ESCAPE:
                        self.scene = 'menu'
                elif self.scene == 'gameover':
                    if event.key == pygame.K_RETURN:
                        self.scene = 'menu'

    def handle_menu_keys(self, key):
        if key == pygame.K_UP:
            self.menu_index -= 1
            if self.menu_index < 0:
                self.menu_index = len(self.menu_options) - 1
        elif key == pygame.K_DOWN:
            self.menu_index += 1
            if self.menu_index >= len(self.menu_options):
                self.menu_index = 0
        elif key == pygame.K_RETURN:
            option = self.menu_options[self.menu_index]
            if option == 'Start Game':
                self.start_new_game()
            elif option == 'Continue Game':
                self.continue_game()
            elif option == 'Leaderboard':
                self.scene = 'leaderboard'
            elif option == 'Settings':
                self.scene = 'settings'
            elif option == 'Exit':
                self.running = False

    def handle_settings_keys(self, key):
        if key == pygame.K_UP:
            self.settings_index -= 1
            if self.settings_index < 0:
                self.settings_index = len(self.setting_names) - 1
        elif key == pygame.K_DOWN:
            self.settings_index += 1
            if self.settings_index >= len(self.setting_names):
                self.settings_index = 0
        elif key == pygame.K_LEFT:
            self.change_setting(-1)
        elif key == pygame.K_RIGHT:
            self.change_setting(1)
        elif key == pygame.K_RETURN:
            if self.setting_names[self.settings_index] == 'Back':
                self.scene = 'menu'

    def change_setting(self, direction):
        name = self.setting_names[self.settings_index]

        if name == 'Volume':
            self.settings[1] += direction * 10
            if self.settings[1] < 0:
                self.settings[1] = 0
            if self.settings[1] > 100:
                self.settings[1] = 100

        elif name == 'Difficulty':
            current = 0
            for i in range(len(self.difficulties)):
                if self.difficulties[i] == self.settings[2]:
                    current = i
            current += direction
            if current < 0:
                current = 0
            if current >= len(self.difficulties):
                current = len(self.difficulties) - 1
            self.settings[2] = self.difficulties[current]

        elif name == 'Fullscreen':
            if direction != 0:
                if self.settings[3] == 0:
                    self.settings[3] = 1
                else:
                    self.settings[3] = 0
                self.screen = self.build_screen()

        settings_repo.save_settings(PLAYER_ID, self.settings[1], self.settings[2], self.settings[3])

    def update_game(self):
        keys = pygame.key.get_pressed()

        speed = 5
        if self.settings[2] == 'Easy':
            speed = 4
        elif self.settings[2] == 'Normal':
            speed = 5
        elif self.settings[2] == 'Hard':
            speed = 7

        if keys[pygame.K_LEFT]:
            self.player_x -= speed
        if keys[pygame.K_RIGHT]:
            self.player_x += speed
        if keys[pygame.K_UP]:
            self.player_y -= speed
        if keys[pygame.K_DOWN]:
            self.player_y += speed

        if self.player_x < 0:
            self.player_x = 0
        if self.player_y < 90:
            self.player_y = 90
        if self.player_x > WIDTH - self.player_size:
            self.player_x = WIDTH - self.player_size
        if self.player_y > HEIGHT - self.player_size:
            self.player_y = HEIGHT - self.player_size

        player_rect = pygame.Rect(self.player_x, self.player_y, self.player_size, self.player_size)
        coin_rect = pygame.Rect(self.coin_x, self.coin_y, 25, 25)

        if player_rect.colliderect(coin_rect):
            self.score += 10
            self.coin_x = random.randint(40, WIDTH - 40)
            self.coin_y = random.randint(110, HEIGHT - 40)

        elapsed = time.time() - self.game_start
        remaining = self.game_duration - int(elapsed)
        if remaining <= 0:
            self.save_game_result()
            self.scene = 'gameover'

    def draw_text_center(self, text, font, color, y):
        img = font.render(text, True, color)
        rect = img.get_rect(center=(WIDTH // 2, y))
        self.screen.blit(img, rect)

    def draw_menu(self):
        self.screen.fill(BLACK)
        self.draw_text_center('HASH GAME', font_big, WHITE, 80)
        self.draw_text_center('Menu principal', font_mid, GRAY, 130)

        for i in range(len(self.menu_options)):
            color = WHITE
            prefix = '  '
            if i == self.menu_index:
                color = YELLOW
                prefix = '> '
            self.draw_text_center(prefix + self.menu_options[i], font_mid, color, 220 + i * 50)

        self.draw_text_center('Usa flechas y ENTER', font_small, GRAY, 540)
        self.draw_message()

    def draw_settings(self):
        self.screen.fill((25, 35, 55))
        self.draw_text_center('SETTINGS', font_big, WHITE, 70)

        values = [
            'Volume: ' + str(self.settings[1]),
            'Difficulty: ' + self.settings[2],
            'Fullscreen: ' + ('ON' if self.settings[3] == 1 else 'OFF'),
            'Back'
        ]

        for i in range(len(values)):
            color = WHITE
            prefix = '  '
            if i == self.settings_index:
                color = YELLOW
                prefix = '> '
            self.draw_text_center(prefix + values[i], font_mid, color, 200 + i * 60)

        self.draw_text_center('Flechas izquierda/derecha para cambiar', font_small, GRAY, 540)

    def draw_leaderboard(self):
        self.screen.fill((40, 20, 20))
        self.draw_text_center('TOP SCORES', font_big, WHITE, 70)

        top = leaderboard_repo.get_top_scores()
        if len(top) == 0:
            self.draw_text_center('No hay puntajes todavia', font_mid, GRAY, 180)
        else:
            for i in range(len(top)):
                line = str(i + 1) + '. ' + str(top[i][0]) + '   ' + str(top[i][1])
                self.draw_text_center(line, font_mid, WHITE, 170 + i * 35)

        self.draw_text_center('ESC para volver', font_small, GRAY, 540)

    def draw_game(self):
        self.screen.fill((15, 60, 40))
        pygame.draw.rect(self.screen, BLUE, (self.player_x, self.player_y, self.player_size, self.player_size))
        pygame.draw.rect(self.screen, YELLOW, (self.coin_x, self.coin_y, 25, 25))

        elapsed = time.time() - self.game_start
        remaining = self.game_duration - int(elapsed)
        if remaining < 0:
            remaining = 0

        text1 = font_mid.render('Score: ' + str(self.score), True, WHITE)
        text2 = font_mid.render('Coins: ' + str(self.total_coins), True, WHITE)
        text3 = font_mid.render('Level: ' + str(self.level), True, WHITE)
        text4 = font_mid.render('Time: ' + str(remaining), True, WHITE)
        self.screen.blit(text1, (20, 20))
        self.screen.blit(text2, (180, 20))
        self.screen.blit(text3, (340, 20))
        self.screen.blit(text4, (500, 20))

        help_text = font_small.render('Muevete con flechas y recoge el cuadro amarillo', True, WHITE)
        self.screen.blit(help_text, (20, 60))

    def draw_gameover(self):
        self.screen.fill((60, 20, 20))
        self.draw_text_center('GAME OVER', font_big, WHITE, 100)
        self.draw_text_center('Score final: ' + str(self.score), font_mid, YELLOW, 200)

        profile = profile_repo.get_profile(PLAYER_ID)
        if profile is not None:
            self.draw_text_center('Level guardado: ' + str(profile[2]), font_mid, WHITE, 260)
            self.draw_text_center('Coins guardadas: ' + str(profile[3]), font_mid, WHITE, 310)

        self.draw_text_center('ENTER para volver al menu', font_small, GRAY, 520)
        self.draw_message()

    def draw_message(self):
        if self.message != '':
            if time.time() - self.message_time < 3:
                self.draw_text_center(self.message, font_small, GREEN, 580)
            else:
                self.message = ''

    async def run(self):
        while self.running:
            self.handle_events()

            if self.scene == 'game':
                self.update_game()

            if self.scene == 'menu':
                self.draw_menu()
            elif self.scene == 'settings':
                self.draw_settings()
            elif self.scene == 'leaderboard':
                self.draw_leaderboard()
            elif self.scene == 'game':
                self.draw_game()
            elif self.scene == 'gameover':
                self.draw_gameover()

            pygame.display.flip()
            self.clock.tick(60)
            await asyncio.sleep(0)

        pygame.quit()


async def main():
    app = App()
    await app.run()


if __name__ == '__main__':
    asyncio.run(main())

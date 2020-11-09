##
#   UNIVERSIDAD DEL VALLE DE GUATEMALA
#   GRÁFICAS POR COMPUTADORA
#   
#   PROYECTO 3: RAY CASTING
#   INSPIRACIÓN: SPACE INVADERS
#
#   LUIS PEDRO CUÉLLAR - 18220
#
#   GAME INSPIRATION - TIM - SPACE INVADERS
##

import pygame
import os
import time
import random

pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 750, 750
HALF_WIDTH = int(WIDTH / 2)
HALF_HEIGHT = int(HEIGHT / 2)
BLOCK_SIZE = 50

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Proyecto 4 - Ray Casting')

mapRender = []
BLOCK_SIZE = 50

##  DECLARE BG COLOR
BG = (20, 20, 20)

##  LOAD IMAGES
#   ENEMY SPACE SHIPS
RED_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_red_small.png'))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_green_small.png'))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_blue_small.png'))

#   PLAYER SPACE SHIPS
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_yellow.png'))

#   ENEMY LASERS
RED_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_red.png'))
GREEN_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_green.png'))
BLUE_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_blue.png'))

#   PLAYER LASER
YELLOW_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_yellow.png'))

#   LOAD BACKGROUND TEXTURES
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))
MENU_BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "menu_bg.png")), (WIDTH, HEIGHT))

TEXTURES = {
    '1': pygame.image.load(os.path.join('assets', 'pixel_blue_dot.png')),
    '2': pygame.image.load(os.path.join('assets', 'pixel_green_dot.png')),
    '3': pygame.image.load(os.path.join('assets', 'pixel_red_dot.png')),
    '4': pygame.image.load(os.path.join('assets', 'pixel_pink_dot.png')),
    '5': pygame.image.load(os.path.join('assets', 'pixel_blue_star.png')),
    '6': pygame.image.load(os.path.join('assets', 'pixel_red_star.png')),
    '7': pygame.image.load(os.path.join('assets', 'pixel_yellow_star.png')),
}

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 45

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))

        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()

        for laser in self.lasers:
            laser.move(vel)

            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)

            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0

        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)

        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()

        for laser in self.lasers:
            laser.move(vel)

            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)

            else:
                for obj in objs:

                    if laser.collision(obj):
                        objs.remove(obj)

                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                    "red": (RED_SPACE_SHIP, RED_LASER),
                    "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                    "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y

    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    pygame.mixer.music.load('music/SI_game.mp3')
    pygame.mixer.music.play(-1)

    isRunning = True
    isPlaying = True
    onPaused = False
    
    FPS = 60
    level = 0
    lives = 5
    
    main_font = pygame.font.Font("visitor2.ttf", 40)
    lost_font = pygame.font.Font("visitor2.ttf", 75)
    options_font = pygame.font.Font("visitor2.ttf", 40)



    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))

        # draw text
        fps_label = main_font.render(f"FPS: {str(FPS)}", 1, (255, 255, 255))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))


        WIN.blit(fps_label, (10, 10))
        WIN.blit(lives_label, (10, 50))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))


        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("Has Perdido!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        if onPaused:
            pause_label = lost_font.render("En pausa", 1, (255,255,255))
            resume_label = options_font.render("Presione MOUSE IZQUIERDO para resumir", 1, (255,255,255))
            exit_label = options_font.render("Presione Q para regresar el menu", 1, (255,255,255))

            WIN.blit(pause_label, (370 - pause_label.get_width()/2, 225))
            WIN.blit(resume_label, (370 - resume_label.get_width()/2, 355))
            WIN.blit(exit_label, (370 - exit_label.get_width()/2, 405))


        pygame.display.update()

    while isRunning:
        while isPlaying:
            clock.tick(FPS)

            redraw_window()

            if lives <= 0 or player.health <= 0:
                lost = True
                lost_count += 1

            if lost:
                if lost_count > FPS * 3:
                    pygame.mixer.music.stop()
                    isRunning = False

                    pygame.mixer.music.load('music/SI_menu.mp3')
                    pygame.mixer.music.play(-1)

                else:
                    continue

            if onPaused:
                isPlaying = False

            if len(enemies) == 0:
                level += 1
                wave_length += 5

                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                    enemies.append(enemy)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] and player.x - player_vel > 0: # left
                player.x -= player_vel

            if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
                player.x += player_vel

            if keys[pygame.K_w] and player.y - player_vel > 0: # up
                player.y -= player_vel

            if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
                player.y += player_vel

            if keys[pygame.K_SPACE]:
                player.shoot()

            if keys[pygame.K_ESCAPE]:
                onPaused = True

            for enemy in enemies[:]:
                enemy.move(enemy_vel)
                enemy.move_lasers(laser_vel, player)

                if random.randrange(0, 2*60) == 1:
                    enemy.shoot()

                if collide(enemy, player):
                    player.health -= 10
                    enemies.remove(enemy)

                elif enemy.y + enemy.get_height() > HEIGHT:
                    lives -= 1
                    enemies.remove(enemy)

            player.move_lasers(-laser_vel, enemies)

        if isPlaying == False:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    onPaused = False
                    isPlaying = True
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        onPaused = False
                        isRunning = False

def main_menu():
    pygame.mixer.music.load('music/SI_menu.mp3')
    pygame.mixer.music.play(-1)

    title_font = pygame.font.Font("visitor2.ttf", 75)
    options_font = pygame.font.Font("visitor2.ttf", 40)

    isRunning = True

    while isRunning:
        WIN.blit(MENU_BG, (0,0))

        title_label = title_font.render("SPACE INVADERS", 1, (255,255,255))
        play_label = options_font.render("Presione MOUSE IZQUIERDO para empezar", 1, (255,255,255))
        exit_label = options_font.render("Presione Q para salir", 1, (255,255,255))

        WIN.blit(title_label, (370 - title_label.get_width()/2, 225))
        WIN.blit(play_label, (370 - play_label.get_width()/2, 355))
        WIN.blit(exit_label, (370 - exit_label.get_width()/2, 405))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRunning = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mixer.music.stop()
                main()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pygame.mixer.music.stop()
                    main()

                if event.key == pygame.K_q:
                    isRunning = False

    pygame.quit()


main_menu()
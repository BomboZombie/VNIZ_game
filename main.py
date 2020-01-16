import pygame
import os
import math
import random
import re
import sys
from Box2D import *

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 910
FPS = 60
TIME_STEP = 1 / FPS
BG_COLOR = pygame.Color('black')

PPM = 20.0  # pixels per meter


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        square = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(square, pygame.Color("#bd00ff"), (10, 10), 10)
        self.image = square
        self.rect = self.image.get_rect()
        self.rect.center = x, y

        # не будем уж совсем загружать комп.
        # для функционирования достаточно, чтобы между шариками были пробелы
        if pygame.sprite.spritecollideany(self, path_group) is not None:
            # return super().__init__(fake_path, all_sprites)
            return None
        super().__init__(path_group, all_sprites)
        self.body = world.CreateStaticBody(
            position=coords_pixels_to_world((x, y)),
            fixtures=b2FixtureDef(
                shape=b2CircleShape(radius=pixels_to_world(10)),
                density=1,
                restitution=0,
                friction=1))

    def update(self):
        if pygame.sprite.collide_mask(self, eraser):
            return remove_sprite_from_game(self)
        col = pygame.sprite.spritecollideany(self, obstacle_group)
        if col and pygame.sprite.collide_mask(self, col):
            return remove_sprite_from_game(self)


class Eraser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        im = load_image("erase.jpg", -1)  # COMPLETE THIS
        im = pygame.transform.scale(im, (100, 100))
        self.image = im
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.center = x, y

    def move(self, x, y):
        self.rect.center = x, y

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        im = load_image("player.png", -1)  # COMPLETE THIS
        im = pygame.transform.scale(im, (100, 100))
        self.original_image = im.copy()
        self.image = im.copy()
        self.rect = self.image.get_rect()
        self.rect.center = x, y

        self.mask = pygame.mask.from_surface(self.image)

        self.body = world.CreateDynamicBody(
            position=coords_pixels_to_world((x, y)),
            bullet=True,
            fixtures=b2FixtureDef(
                shape=b2CircleShape(radius=pixels_to_world(50)),
                density=1.0,
                restitution=0.5,
                friction=0.1))

        self.score = 0

    def update(self):
        # вращение
        self.image = pygame.transform.rotate(
            self.original_image, 2 * self.body.transform.angle * 180 / Box2D.b2_pi)
        self.rect = self.image.get_rect()

        # перемещение
        self.rect.center = coords_world_to_pixels(
            tuple(self.body.transform.position))
        self.mask = pygame.mask.from_surface(self.image)

        # обработка положения
        col = pygame.sprite.spritecollideany(self, obstacle_group)
        global running
        if col and pygame.sprite.collide_mask(self, col):
            running = False
        if self.rect.centerx < 0 or self.rect.centerx > WINDOW_WIDTH:
            running = False

        if list(self.body.transform.position)[1] <= 0:
            self.update_score(ob_man.last_score)
            upgrade_world(self)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def display_score(self):
        font = pygame.font.Font(None, 30)
        text = font.render(f"SCORE: {self.score}", 1, pygame.Color('#cdba89'))
        text_x = (WINDOW_WIDTH - 100) - text.get_width() // 2
        text_y = 50 - text.get_height() // 2
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (text_x, text_y))
        pygame.draw.rect(screen, (0, 255, 0), (text_x - 10, text_y - 10,
                                               text_w + 20, text_h + 20), 1)

    def update_score(self, points):
        self.score += points


class Spikes(pygame.sprite.Sprite):
    def __init__(self, center_coords):
        super().__init__(obstacle_group, all_sprites)
        self.image = load_image("spikes.png", -1)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = center_coords

        self.body = world.CreateStaticBody(
            position=coords_pixels_to_world(
                (center_coords[0], center_coords[1] + 16)),
            fixtures=b2FixtureDef(
                shape=b2.polygonShape(box=(pixels_to_world(self.rect.w / 2 - 5),
                                           pixels_to_world(self.rect.h / 2 - 15))),
                density=0,
                restitution=0.0,
                friction=0.0))


class Blade(pygame.sprite.Sprite):
    def __init__(self, center_coords, velocity=100):
        super().__init__(obstacle_group, all_sprites)
        if center_coords[0] > WINDOW_WIDTH // 2:
            self.original_image = load_image("right_blade.png", -1)
            clockwise = 1
        else:
            self.original_image = load_image("left_blade.png", -1)
            clockwise = -1
        self.original_image = pygame.transform.scale(
            self.original_image, (130, 130))

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = center_coords

        self.velocity = velocity
        self.body = world.CreateKinematicBody(
            position=coords_pixels_to_world(center_coords),
            angularVelocity=3 * clockwise,
            linearVelocity=(pixels_to_world(velocity), 0),
            fixtures=b2FixtureDef(
                shape=b2CircleShape(
                    radius=pixels_to_world(self.rect.w // 2 - 60)),
                density=0,
                restitution=0.0,
                friction=0.0))

    def update(self):
        # перемещение
        self.image = pygame.transform.rotate(
            self.original_image, 2 * self.body.transform.angle * 180 / Box2D.b2_pi)
        self.rect = self.image.get_rect()
        self.rect.center = coords_world_to_pixels(
            tuple(self.body.transform.position))
        self.mask = pygame.mask.from_surface(self.image)

        # столкновение с др спрайтами
        col = obstacles_collide(self)
        if col is False:
            pass
        elif col is True:
            if (self.rect.right >= WINDOW_WIDTH - 20 and self.body.linearVelocity[0] > 0) or \
                    (self.rect.left <= 20 and self.body.linearVelocity[0] < 0):
                self.change_direction()
        else:
            x_center = (self.rect.centerx + col.rect.centerx) // 2
            if (x_center - self.rect.centerx) / self.velocity > 0:
                self.change_direction()

    def set_velocity(self, v):
        self.velocity = v
        self.body.linearVelocity = (pixels_to_world(v), 0)

    def change_direction(self):
        self.set_velocity(-1 * self.velocity)


class ObstacleManager():
    def __init__(self):
        self.start = 370
        self.step = 240
        self.last_score = 3

    def get_sequence(self):
        f = open("obstacles.txt", mode="r", encoding="utf8")
        data = list(f.readlines())
        f.close()
        line = data[random.randrange(0, len(data))].strip()

        res = list()
        for chunk in re.finditer(r"((?P<amnt>\d*)?(?P<name>\w+))", line):
            res.append((chunk.group('name'), int(chunk.group('amnt'))
                        if chunk.group('amnt') != "" else 1))
        return res

    def put_blade(self, y, amnt):
        # y - для центра
        for _ in range(amnt):
            b = Blade((random.randint(0, WINDOW_WIDTH), y))
            while obstacles_collide(b):
                remove_sprite_from_game(b)
                b = Blade((random.randint(0, WINDOW_WIDTH), y))

            velocity = random.gauss(120, 50)
            sign = random.choice([-1, 1])
            b.set_velocity(sign * velocity)

    def put_spikes(self, y, amnt):
        # y - для центра
        for _ in range(amnt):
            s = Spikes((random.randint(0, WINDOW_WIDTH), y))
            while obstacles_collide(s):
                remove_sprite_from_game(s)
                s = Spikes((random.randint(0, WINDOW_WIDTH), y))

    def insert_sequence(self):
        seq = self.get_sequence()
        for i in range(len(seq)):
            y = self.start + i * self.step
            name, amnt = seq.pop(0)
            {
                "S": self.put_spikes,
                "B": self.put_blade
            }.get(name)(y, amnt)
            self.update_score({"S": 1,
                                 "B": 2}.get(name))

    def update_score(self, num):
        self.last_score += num


def load_image(name, colorkey=None):
    fullname = os.path.join(os.path.dirname(__file__), 'data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def upgrade_world(player):
    # тело наверх
    current_position = player.rect.center
    player.rect.center = (current_position[0], 10)
    player.body.position = coords_pixels_to_world(player.rect.center)

    # уберём старые спрайты
    for s in path_group.sprites():
        remove_sprite_from_game(s)
    for s in obstacle_group.sprites():
        remove_sprite_from_game(s)

    # сгенерируем новые спрайты
    ob_man.insert_sequence()


def remove_sprite_from_game(sprite):
    world.DestroyBody(sprite.body)
    sprite.kill()
    sprite = None


def obstacles_collide(s):
    for suspect in pygame.sprite.spritecollide(s, obstacle_group, False):
        if suspect is not s and pygame.sprite.collide_mask(s, suspect):
            return suspect
    if s.rect.left < 20 or s.rect.right > WINDOW_WIDTH:
        return True
    return False


def pixels_to_world(num):
    return num / PPM


def world_to_pixels(num):
    return num * PPM


def coords_pixels_to_world(coords):
    x, y = coords
    new_x, new_y = x, WINDOW_HEIGHT - y
    return tuple(map(pixels_to_world, (new_x, new_y)))


def coords_world_to_pixels(coords):
    x, y = tuple(map(world_to_pixels, coords))
    new_x, new_y = x, WINDOW_HEIGHT - y
    return (new_x, new_y)


def interval_points(p0, p1):
    x0, y0 = p0
    x1, y1 = p1
    delta_x, delta_y = x1 - x0, y1 - y0
    if delta_x != 0:
        k = delta_y / delta_x
        for x in range(min(0, delta_x), max(0, delta_x)):
            yield (x + x0, int(y0 + k * x))
    else:
        for y in range(min(y0, y0 + delta_y), max(y0, y0 + delta_y)):
            yield (x0, y)
    yield p1


def draw_walls(screen):
    pygame.draw.rect(screen, pygame.Color("#ff8200"),
                     (0, 0, 20, WINDOW_HEIGHT), 0)
    pygame.draw.rect(screen, pygame.Color("#ff8200"),
                     (WINDOW_WIDTH - 20, 0, 20, WINDOW_HEIGHT), 0)


#    -- WINDOWS --    #

def start_window():
    screen = pygame.display.set_mode(WINDOW_SIZE)

    bg = pygame.transform.scale(load_image(
        'start_image.png'), WINDOW_SIZE)
    screen.blit(bg, (0, 0))

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def end_window():
    run = True

    fg = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
    fg.fill((224, 99, 201, 128))
    screen.blit(fg, (0, 0))

    text = ["GAME OVER", ""
            f"Your score: {player.score}"]
    font = pygame.font.Font(None, 100)
    text_coord = 50
    for line in text:
        string_rendered = font.render(line, 1, pygame.Color('#fff500'))
        line_rect = string_rendered.get_rect()
        text_coord += 10
        line_rect.top = text_coord
        line_rect.x = (WINDOW_WIDTH - string_rendered.get_width()) // 2
        text_coord += line_rect.height
        screen.blit(string_rendered, line_rect)

    clock = pygame.time.Clock()
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                run = False
        pygame.display.flip()
        clock.tick(FPS)


##########################################################################


def my_draw_polygon(polygon, body, fixture):
    vertices = [(body.transform * v) * PPM for v in polygon.vertices]
    vertices = [(v[0], WINDOW_HEIGHT - v[1]) for v in vertices]
    pygame.draw.polygon(screen, colors[body.type], vertices)


Box2D.b2.polygonShape.draw = my_draw_polygon


def my_draw_circle(circle, body, fixture):
    # help(body.transform)
    # exit()
    position = body.transform * circle.pos * PPM
    position = (position[0], WINDOW_HEIGHT - position[1])
    pygame.draw.circle(screen, colors.get(body.type, (0, 0, 0)), [int(
        x) for x in position], int(circle.radius * PPM))


    # Note: Python 3.x will enforce that pygame get the integers it requests,
    #       and it will not convert from float.
Box2D.b2.circleShape.draw = my_draw_circle

colors = {
    Box2D.b2.staticBody: (0, 255, 25, 50),
    Box2D.b2.dynamicBody: (127, 127, 127, 50),
}
##################################################

# main game loop
pygame.init()

start_window()
loop = True
while loop:
    screen = pygame.display.set_mode(WINDOW_SIZE)

    bg = pygame.transform.scale(load_image('background.jpg'), WINDOW_SIZE)
    screen.blit(bg, (0, 0))

    world = b2World(gravity=(0, -10), doSleep=True)

    all_sprites = pygame.sprite.Group()
    path_group = pygame.sprite.Group()
    obstacle_group = pygame.sprite.Group()

    eraser = Eraser(-100, -100)
    cursor = None

    player = Player(100, 1)
    ob_man = ObstacleManager()

    world.CreateStaticBody(
        position=coords_pixels_to_world((0, 0)),
        fixtures=b2FixtureDef(
            shape=b2.polygonShape(
                box=(pixels_to_world(20), pixels_to_world(WINDOW_HEIGHT))),
            density=100,
            restitution=1.0,
            friction=0.0)
    )
    world.CreateStaticBody(
        position=coords_pixels_to_world((WINDOW_WIDTH, 0)),
        fixtures=b2FixtureDef(
            shape=b2.polygonShape(
                box=(pixels_to_world(20), pixels_to_world(WINDOW_HEIGHT))),
            density=100,
            restitution=1.0,
            friction=0.0)
    )
    world.CreateStaticBody(
        position=coords_pixels_to_world((0, -20)),
        fixtures=b2FixtureDef(
            shape=b2.polygonShape(
                box=(pixels_to_world(WINDOW_WIDTH), pixels_to_world(10))),
            density=100,
            restitution=1.0,
            friction=0.0)
    )

    Spikes((300, 700))
    Blade((700, 700))

    clock = pygame.time.Clock()
    running = True

    drawing_on = False
    erasing_on = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_btn = pygame.mouse.get_pressed()
                if mouse_btn[0]:
                    drawing_on = True
                    erasing_on = False
                    prev_point = event.pos
                    cur_point = None
                elif mouse_btn[2]:
                    erasing_on = True
                    drawing_on = False
                    eraser.move(*event.pos)
            if event.type == pygame.MOUSEMOTION:
                if drawing_on:
                    cur_point = event.pos
                    for pt in interval_points(prev_point, cur_point):
                        Ball(*pt)
                    prev_point = cur_point
                elif erasing_on:
                    eraser.move(*event.pos)
            if event.type == pygame.MOUSEBUTTONUP:
                if drawing_on:
                    Ball(*event.pos)
                drawing_on = False
                erasing_on = False
                eraser.move(-100, -100)
            if event.type == pygame.KEYDOWN:
                mouse_coords = pygame.mouse.get_pos()
                btn_pressed = pygame.key.get_pressed()
                if btn_pressed[pygame.K_w]:
                    player = Player(*mouse_coords)

        # обновимся
        world.Step(TIME_STEP, 10, 10)
        player.update()
        all_sprites.update()

        # порисуем
        screen.blit(bg, (0, 0))
        for obg in [path_group, eraser, player, obstacle_group]:
            obg.draw(screen)
        draw_walls(screen)
        player.display_score()

        # for body in world.bodies:
        #     for fixture in body.fixtures:
        #         fixture.shape.draw(body, fixture)

        pygame.display.flip()
        clock.tick(FPS)

    end_window()
    start_window()

pygame.quit()
sys.exit()

import pygame
import os
import math
from Box2D import *

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 800
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
        if pygame.sprite.spritecollideany(self, path_group) is not None:
            return None
        super().__init__(path_group, all_sprites)
        self.body = world.CreateStaticBody(
            position=coords_pixels_to_world((x, y)),
            fixtures=b2FixtureDef(
                shape=b2CircleShape(radius=pixels_to_world(10)),
                density=0,
                restitution=0.2,
                friction=0.2))

    def update(self):
        if pygame.sprite.collide_mask(self, eraser):
            self.remove_from_game()

    def remove_from_game(self):
        world.DestroyBody(self.body)
        self.kill()


class Eraser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(eraser_group, all_sprites)
        im = load_image("erase.jpg", -1)
        im = pygame.transform.scale(im, (100, 100))
        self.image = im
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.center = x, y

    def move(self, x, y):
        self.rect.center = x, y


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player_group, all_sprites)
        im = load_image("player.png", -1)
        im = pygame.transform.scale(im, (100, 100))
        self.original_image = im.copy()
        self.image = im.copy()
        self.rect = self.image.get_rect()
        self.rect.center = x, y

        self.body = world.CreateDynamicBody(
            position=coords_pixels_to_world((x, y)),
            bullet=True,
            fixtures=b2FixtureDef(
                shape=b2CircleShape(radius=pixels_to_world(50)),
                density=1.0,
                restitution=0.3,
                friction=0.5)
        )

    def update(self):
        self.image = pygame.transform.rotate(
            self.original_image, 2 * self.body.transform.angle * 180 / Box2D.b2_pi)
        self.rect = self.image.get_rect()

        position = coords_world_to_pixels(tuple(self.body.transform.position))
        self.rect.center = position

        # print(self.body.transform.position)
        if list(self.body.transform.position)[1] <= 0:
            upgrade_world(self)


def upgrade_world(player):
    current_position = player.rect.center
    player.rect.center = (current_position[0], 10)
    player.body.position = coords_pixels_to_world(player.rect.center)
    for s in path_group.sprites():
        s.remove_from_game()


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


# def create_path_ball(pos):
#     b = Ball(*pos)
#     b.body = world.CreateStaticBody(position=coords_pixels_to_world(pos),
#                                     fixtures=b2FixtureDef(
#                                         shape=b2CircleShape(
#                                             radius=pixels_to_world(10)),
#                                         density=1.0,
#                                         restitution=0,
#                                         friction=0))


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
    pygame.draw.circle(screen, colors[body.type], [int(
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

global screen
screen = pygame.display.set_mode(WINDOW_SIZE)

bg = pygame.transform.scale(load_image('tom_jerry.jpg'), WINDOW_SIZE)
screen.blit(bg, (0, 0))

# INIT STUFF
world = b2World(gravity=(0, -20), doSleep=True)

all_sprites = pygame.sprite.Group()
path_group = pygame.sprite.Group()
eraser_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

eraser = Eraser(-100, -100)
cursor = None

player = Player(100, 1)


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

clock = pygame.time.Clock()
running = True

drawing_on = False
erasing_on = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # if player is None:
            #     player = Player(*event.pos)
            #     continue
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

    world.Step(TIME_STEP, 10, 10)

    screen.blit(bg, (0, 0))

    path_group.draw(screen)
    eraser_group.draw(screen)
    player_group.draw(screen)

    draw_walls(screen)
    # for body in world.bodies:
    #     for fixture in body.fixtures:
    #         fixture.shape.draw(body, fixture)

    all_sprites.update()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

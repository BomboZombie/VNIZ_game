import pygame
from Box2D import *













def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((600, 450))
    clock = pygame.time.Clock()

    running = True

    world = b2World()
    world.gravity = (0, -5)
    ground = world.CreateStaticBody(
            position=(0,-5), shapes=b2PolygonShape(box=(60,5)))
    obj = world.CreateDynamicBody(
            angle=15, position=(30,22), shapes=b2PolygonShape(box=(5,5)))

    while running:
        screen.fill((0, 0, 0))
        events = pygame.event.get()
        if any(map(lambda e:e.type == pygame.QUIT, events)):
            running = False

        drawPolygons(screen, obj)

        world.Step(1/60, 10, 10)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


def drawPolygons(screen, body):
    for fixture in body.fixtures:
        shape = fixture.shape
        vertices = [body.transform * v * 10 for v in shape.vertices]
        vertices = [(v[0], 450-v[1]) for v in vertices]
        pygame.draw.polygon(screen, (255,255,255), vertices)


if __name__ == '__main__':
    main()
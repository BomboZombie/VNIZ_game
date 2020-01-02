import pygame
pygame.init()

BACKGROUND_COLOR = (0, 0, 0)


class Player(pygame.sprite.Sprite):

    def __init__(self, position=(0, 0)):
        super(Player, self).__init__()
        self.original_image = pygame.Surface((32, 32))
        pygame.draw.lines(self.original_image, (255, 255, 255), True, [(16, 0), (0, 31), (31, 31)])
        self.image = self.original_image  # This will reference our rotated copy.
        self.rect  = self.image.get_rect()
        self.position = pygame.math.Vector2(*position)

    def update(self):
        """Updates the players orientation."""
        # Create a vector pointing at the mouse position.
        mouse_position = pygame.math.Vector2(*pygame.mouse.get_pos())

        # Create a vector pointing from the image towards the mouse position.
        relative_mouse_position = mouse_position - self.position

        # Calculate the angle between the y_axis and the vector pointing from the image towards the mouse position.
        y_axis = pygame.math.Vector2(0, -1)
        angle  = -y_axis.angle_to(relative_mouse_position )  # Subtracting because pygame rotates counter-clockwise.

        # Create the rotated copy.
        self.image = pygame.transform.rotate(self.original_image, angle).convert()  # Angle is absolute value!

        # Make sure your rect represent the actual Surface.
        self.rect = self.image.get_rect()

        # Since the dimension probably changed you should move its center back to where it was.
        self.rect.center = self.position.x, self.position.y


screen = pygame.display.set_mode((720, 480))
player = Player(position=(300, 250))

while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()

    # Update
    player.update()

    # Render
    screen.fill(BACKGROUND_COLOR)
    screen.blit(player.image, player.rect)
    pygame.display.update()
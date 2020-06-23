import pygame


class Brick:
    def __init__(self):
        self.p1 = pygame.Vector2()
        self.p2 = pygame.Vector2()
        self.width = None
        self.height = None
        self.id = 0
        self.angle = 0
        self.collided = False
        self.player_connected = False

    def set_brick(self, p1, p2):
        # creates the various data for the brick  from two (x,y) points for the brick (top left and bottom right
        self.p1.x, self.p1.y = p1[0], p1[1]
        self.p2.x, self.p2.y = p2[0], p2[1]
        self.width = self.p2.x - self.p1.x
        self.height = self.p2.y - self.p1.y

    def render(self, screen):
        # draw the brick, angled bricks are a line, all other bricks are just a filled rect.
        color = (110, 102, 93)
        if self.player_connected:
            color = (229, 156, 27)

        if self.angle % 90 == 0:
            pygame.draw.rect(screen, color, self.get_pygame_rect(), 0)
        elif self.angle != 0:
            if self.angle == 45:
                pygame.draw.line(screen, color, (self.p1.x, self.p2.y), (self.p2.x, self.p1.y), 1)
            elif self.angle == 135:
                pygame.draw.line(screen, color, (self.p1.x, self.p1.y), (self.p2.x, self.p2.y), 1)

    def get_pygame_rect(self):
        # returns the pygame rect representing this brick
        return (int(self.p1.x), int(self.p1.y), int(self.width), int(self.height))

    def brick_point_collide(self, p):
        # test if a Vector2 point is within the brick area
        self.collided = False
        if self.p1.x <= p[0] <= self.p2.x and self.p1.y <= p[1] <= self.p2.y:
            self.collided = True
        return self.collided

    def clear_player_connected(self):
        self.player_connected = False

    #def brick_rect_collide(self, p1, p2):
    #    # check if two points (representing a brick) collides with this rect
    #    self.collided = True
    #    if self.p1.x >= p2.x or p1.x >= self.p2.x:
    #        self.collided = False
    #    if self.p1.y >= p2.y or p1.y >= self.p2.y:
    #        self.collided = False
    #    return self.collided
    #    # return True

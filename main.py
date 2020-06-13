
# by no means perfect but learning to do physics in 2d platfomers
#
#
#
#
import pygame
import math

from world import World


def main():
    running = True
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    font = pygame.font.SysFont("monospace", 14)
    w = World()
    w.add_brick(1, (0, 790), (800, 800), 0)
    w.add_brick(2, (0, 700), (100, 710), 0)
    w.add_brick(3, (200, 600), (300, 610), 0)
    w.add_brick(4, (350, 600), (450, 610), 0)
    w.add_brick(5, (500, 350), (600, 700), 0)
    w.add_brick(6, (0, 0), (10, 800), 90)  # wall on left
    w.add_brick(7, (790, 0), (800, 800), 90)  # wall on right
    w.add_brick_slanted(8, (700, 700), (790, 790), 45)  # slanted block

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE :
                    w.player.apply_action("SPACE", "DOWN")
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    w.player.apply_action("LEFT", "DOWN")
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    w.player.apply_action("RIGHT", "DOWN")
                if event.key == pygame.K_r:
                    w.reset_player()
                if event.key == pygame.K_y:
                    w.player.position.y = 0

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    w.player.apply_action("SPACE", "UP")
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    w.player.apply_action("LEFT", "UP")
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    w.player.apply_action("RIGHT", "UP")
        # time step
        screen.fill((0, 0, 0))
        w.update(screen, font)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
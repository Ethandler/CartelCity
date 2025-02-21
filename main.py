import pygame
import math
import sys

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.size = 32

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed

class Game:
    def __init__(self):
        # Set up the display
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Top Down Game")

        # Create player in the center of the screen
        self.player = Player(self.width/2, self.height/2)

        # Game state
        self.running = True
        self.dragging = False
        self.last_mouse_pos = None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.dragging = True
                self.last_mouse_pos = pygame.mouse.get_pos()

            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False

            elif event.type == pygame.MOUSEMOTION and self.dragging:
                current_pos = pygame.mouse.get_pos()
                if self.last_mouse_pos:
                    # Calculate movement direction
                    dx = current_pos[0] - self.last_mouse_pos[0]
                    dy = current_pos[1] - self.last_mouse_pos[1]
                    # Normalize the movement vector
                    length = math.sqrt(dx * dx + dy * dy)
                    if length > 0:
                        dx /= length
                        dy /= length
                        self.player.move(dx, dy)
                self.last_mouse_pos = current_pos

    def draw(self):
        # Clear the screen
        self.screen.fill((211, 211, 211))  # Light gray background

        # Draw the player as a red rectangle
        pygame.draw.rect(self.screen, (255, 0, 0),
                        (self.player.x - self.player.size/2,
                         self.player.y - self.player.size/2,
                         self.player.size,
                         self.player.size))

        # Update the display
        pygame.display.flip()

    def run(self):
        # Game loop
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            self.draw()
            clock.tick(60)  # 60 FPS

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    pygame.init()
    game = Game()
    game.run()
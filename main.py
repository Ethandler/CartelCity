import pygame
from game_scene import GameScene

# Initialize and run the game
if __name__ == '__main__':
    pygame.init()

    # Set up the display
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Top Down Game")

    # Create game instance
    game = GameScene(screen)

    # Game loop
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)

        # Update game state
        game.update()

        # Draw everything
        screen.fill((51, 51, 51))  # Dark gray background
        game.draw()
        pygame.display.flip()

        # Cap at 60 FPS
        clock.tick(60)

    pygame.quit()
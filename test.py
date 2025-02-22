import pygame
import asyncio

# Initialize only the required Pygame modules for web
pygame.display.init()
pygame.font.init()

# Set up the display with SCALED flag for better web compatibility
screen = pygame.display.set_mode((800, 600), pygame.SCALED)
pygame.display.set_caption("Simple Test")

async def main():
    clock = pygame.time.Clock()
    running = True
    x = 400
    y = 300

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear screen
        screen.fill((255, 255, 255))

        # Draw a simple circle
        pygame.draw.circle(screen, (255, 0, 0), (x, y), 30)

        # Update display
        pygame.display.flip()

        # Cap at 60 FPS and allow other async operations
        clock.tick(60)
        await asyncio.sleep(0)

if __name__ == '__main__':
    asyncio.run(main())
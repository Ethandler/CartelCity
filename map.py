import pygame

class GameMap:
    def __init__(self, screen):
        self.screen = screen
        self.walls = []
        self.buildings = []
        self.setup_map()

    def setup_map(self):
        # Create basic map layout
        # Outer walls
        self.walls.extend([
            pygame.Rect(0, 0, 800, 20),      # Bottom
            pygame.Rect(0, 580, 800, 20),    # Top
            pygame.Rect(0, 0, 20, 600),      # Left
            pygame.Rect(780, 0, 20, 600)     # Right
        ])

        # Add some buildings
        self.buildings.extend([
            pygame.Rect(100, 100, 100, 100),
            pygame.Rect(300, 200, 150, 100),
            pygame.Rect(500, 300, 120, 120),
            pygame.Rect(200, 400, 80, 80)
        ])

        self.walls.extend(self.buildings)

    def draw(self, screen):
        # Draw ground
        screen.fill((85, 85, 85))

        # Draw buildings
        for building in self.buildings:
            pygame.draw.rect(screen, (136, 136, 136), building)

        # Draw roads
        pygame.draw.rect(screen, (51, 51, 51), pygame.Rect(250, 0, 60, 600))    # Vertical road
        pygame.draw.rect(screen, (51, 51, 51), pygame.Rect(0, 250, 800, 60))    # Horizontal road
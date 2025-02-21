import scene

class GameMap:
    def __init__(self):
        self.walls = []
        self.buildings = []
        self.setup_map()
    
    def setup_map(self):
        # Create basic map layout
        # Outer walls
        self.walls.extend([
            scene.Rect(0, 0, 800, 20),      # Bottom
            scene.Rect(0, 580, 800, 20),    # Top
            scene.Rect(0, 0, 20, 600),      # Left
            scene.Rect(780, 0, 20, 600)     # Right
        ])
        
        # Add some buildings
        self.buildings.extend([
            scene.Rect(100, 100, 100, 100),
            scene.Rect(300, 200, 150, 100),
            scene.Rect(500, 300, 120, 120),
            scene.Rect(200, 400, 80, 80)
        ])
        
        self.walls.extend(self.buildings)
    
    def draw(self):
        # Draw ground
        scene.fill('#555555')
        scene.rect(0, 0, 800, 600)
        
        # Draw buildings
        scene.fill('#888888')
        for building in self.buildings:
            scene.rect(building.x, building.y,
                      building.w, building.h)
        
        # Draw roads
        scene.fill('#333333')
        scene.rect(250, 0, 60, 600)    # Vertical road
        scene.rect(0, 250, 800, 60)    # Horizontal road

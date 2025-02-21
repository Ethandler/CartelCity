import scene
import random
import math

class NPC(scene.Node):
    def __init__(self, x, y):
        super().__init__()
        self.position = (x, y)
        self.size = (30, 30)
        self.speed = 2
        self.direction = 0
        self.target_position = self.get_random_target()
        self.waiting = 0
    
    def get_random_target(self):
        # Get a random position on screen
        x = random.randint(50, 750)
        y = random.randint(50, 550)
        return (x, y)
    
    def update(self):
        if self.waiting > 0:
            self.waiting -= 1
            return
        
        # Move towards target
        dx = self.target_position[0] - self.position[0]
        dy = self.target_position[1] - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 5:
            # Reached target, get new one and wait
            self.target_position = self.get_random_target()
            self.waiting = random.randint(60, 180)  # 1-3 seconds at 60 fps
        else:
            # Move towards target
            self.direction = math.atan2(dy, dx)
            self.position = (
                self.position[0] + (dx/distance) * self.speed,
                self.position[1] + (dy/distance) * self.speed
            )
    
    def draw(self):
        # Draw NPC sprite
        scene.push_matrix()
        scene.translate(self.position[0], self.position[1])
        scene.rotate(self.direction)
        
        # Draw NPC triangle (replace with sprite)
        scene.fill('#0000ff')
        scene.triangle(-15, -15, 15, 0, -15, 15)
        
        scene.pop_matrix()

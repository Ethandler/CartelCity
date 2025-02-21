import scene
import math

class Player(scene.Node):
    def __init__(self, x, y):
        super().__init__()
        self.position = (x, y)
        self.size = (30, 30)
        self.speed = 5
        self.velocity = (0, 0)
        self.direction = 0  # angle in radians
        
        # Animation states
        self.walking = False
        self.frame_count = 0
        self.current_frame = 0
        self.frames = ['assets/player.svg']  # Using single SVG for now
    
    def update(self):
        # Update position based on velocity
        self.position = (
            self.position[0] + self.velocity[0] * self.speed,
            self.position[1] + self.velocity[1] * self.speed
        )
        
        # Update animation
        if self.walking:
            self.frame_count += 1
            if self.frame_count % 10 == 0:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
    
    def move(self, dx, dy):
        # Update velocity based on input
        self.velocity = (dx, dy)
        magnitude = math.sqrt(dx*dx + dy*dy)
        if magnitude > 1:
            self.velocity = (dx/magnitude, dy/magnitude)
        
        # Update direction
        if magnitude > 0.1:
            self.direction = math.atan2(dy, dx)
            self.walking = True
    
    def stop(self):
        self.velocity = (0, 0)
        self.walking = False
    
    def handle_collision(self):
        # Basic collision response
        self.velocity = (0, 0)
    
    def perform_action(self):
        # Placeholder for action (e.g., shooting, interaction)
        pass
    
    def draw(self):
        # Draw player sprite
        scene.push_matrix()
        scene.translate(self.position[0], self.position[1])
        scene.rotate(self.direction)
        
        # Draw character triangle for now (replace with sprite)
        scene.fill('#ff0000')
        scene.triangle(-15, -15, 15, 0, -15, 15)
        
        scene.pop_matrix()

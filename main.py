import scene
import sound
import ui
import math

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.size = 32
        
    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed

class GameScene(scene.Scene):
    def setup(self):
        # Set up the game scene
        self.background_color = 'lightgray'
        # Create player in the center of the screen
        center = self.bounds.center()
        self.player = Player(center.x, center.y)
        
    def touch_began(self, touch):
        # Store the initial touch position
        self.touch_start = touch.location
        
    def touch_moved(self, touch):
        # Calculate movement direction based on touch movement
        dx = touch.location.x - self.touch_start.x
        dy = touch.location.y - self.touch_start.y
        # Normalize the movement vector
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length
            self.player.move(dx, dy)
        # Update touch start position
        self.touch_start = touch.location
        
    def draw(self):
        # Clear the screen
        scene.background(0, 0, 0)
        
        # Draw the player as a red rectangle
        scene.fill('red')
        scene.rect(self.player.x - self.player.size/2,
                  self.player.y - self.player.size/2,
                  self.player.size,
                  self.player.size)

if __name__ == '__main__':
    # Run the game
    game_scene = GameScene()
    scene.run(game_scene)

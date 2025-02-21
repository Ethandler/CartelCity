import scene
import sound
from player import Player
from npc import NPC
from map import GameMap
import ui

class GameScene(scene.Scene):
    def setup(self):
        # Set up the game scene
        self.background_color = '#333333'
        
        # Initialize game map
        self.game_map = GameMap()
        
        # Initialize player
        self.player = Player(self.size.w / 2, self.size.h / 2)
        
        # Initialize NPCs
        self.npcs = [
            NPC(100, 100),
            NPC(200, 200),
            NPC(300, 300)
        ]
        
        # Touch controls
        self.touch_start = None
        self.joystick_center = None
        self.joystick_current = None
        
        # Load sounds
        sound.load_effect('footstep.wav')
    
    def update(self):
        # Update player position and state
        self.player.update()
        
        # Update NPCs
        for npc in self.npcs:
            npc.update()
        
        # Check collisions
        self.check_collisions()
    
    def check_collisions(self):
        # Check player collision with map objects
        for wall in self.game_map.walls:
            if self.player.frame.intersects(wall):
                self.player.handle_collision()
        
        # Check player collision with NPCs
        for npc in self.npcs:
            if self.player.frame.intersects(npc.frame):
                self.player.handle_collision()
    
    def draw(self):
        # Clear the screen
        scene.background(0, 0, 0)
        
        # Draw map
        self.game_map.draw()
        
        # Draw NPCs
        for npc in self.npcs:
            npc.draw()
        
        # Draw player
        self.player.draw()
        
        # Draw touch controls
        self.draw_controls()
    
    def draw_controls(self):
        if self.joystick_center and self.joystick_current:
            # Draw virtual joystick
            scene.fill('#ffffff33')
            scene.ellipse(self.joystick_center.x - 40,
                         self.joystick_center.y - 40,
                         80, 80)
            scene.fill('#ffffff66')
            scene.ellipse(self.joystick_current.x - 20,
                         self.joystick_current.y - 20,
                         40, 40)
    
    def touch_began(self, touch):
        if touch.location.x < self.size.w / 2:
            # Left side - movement control
            self.joystick_center = touch.location
            self.joystick_current = touch.location
        else:
            # Right side - action control
            self.player.perform_action()
    
    def touch_moved(self, touch):
        if self.joystick_center and touch.location.x < self.size.w / 2:
            self.joystick_current = touch.location
            # Calculate movement direction
            dx = touch.location.x - self.joystick_center.x
            dy = touch.location.y - self.joystick_center.y
            self.player.move(dx / 50, dy / 50)
    
    def touch_ended(self, touch):
        if touch.location.x < self.size.w / 2:
            self.joystick_center = None
            self.joystick_current = None
            self.player.stop()

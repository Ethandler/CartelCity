import scene
import sound
from game_scene import GameScene

# Initialize and run the game
if __name__ == '__main__':
    # Set up the game scene
    game = GameScene()
    
    # Run the scene in full screen mode
    scene.run(game, orientation=scene.LANDSCAPE, show_fps=True)

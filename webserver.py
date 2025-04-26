import os
import time
import threading
import subprocess
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# Create directories if they don't exist
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

def run_game():
    # Give the web server a moment to start
    time.sleep(2)
    # Start the game in a separate process using the VNC launcher
    subprocess.Popen(['python', 'run_in_vnc.py'])

if __name__ == '__main__':
    # Start the game in a separate thread
    game_thread = threading.Thread(target=run_game)
    game_thread.daemon = True
    game_thread.start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
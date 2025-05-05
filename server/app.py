from flask import Flask, send_file
from svgedit import update_svg
from svg2png import convert 
import threading
import time

app = Flask(__name__)

def background_updater():
    while True:
        try:
            update_svg()
            convert("static/dash.svg", "static/dash.png")
        except Exception as e:
            print(f"Error updating chart: {e}")
        time.sleep(3600)

@app.route('/dash')
def serve_chart():
    return send_file("static/dash.png", mimetype='image/png')

if __name__ == '__main__':
    threading.Thread(target=background_updater, daemon=True).start()
    app.run(debug=True)
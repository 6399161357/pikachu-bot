from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
    return "I am alive! ⚡ Pikachu Bot is running!"


def run():
    app.run(host='0.0.0.0', port=8099)


def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

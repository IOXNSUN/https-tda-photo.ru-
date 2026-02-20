from flask import Flask, render_template, url_for, abort, request
import os
import time
import sys
from flask import g

app = Flask(__name__)

PHOTO_DIR = os.path.join(app.static_folder, 'photos')
ALLOWED_EXT = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

# Русские названия жанров
GENRES = {
    "landscapes": "Пейзажи",
    "portraits": "Портреты",
    "subject": "Предметная",
    "city": "Город",
    "other": "Разное"
}

def list_genres():
    """Возвращает список существующих папок жанров, кроме 'main'."""
    try:
        return [g for g in GENRES.keys() if os.path.isdir(os.path.join(PHOTO_DIR, g))]
    except Exception as e:
        print(f"ERROR in list_genres: {e}", file=sys.stderr, flush=True)
        return []

def images_in_genre(genre):
    try:
        folder = os.path.join(PHOTO_DIR, genre)
        if not os.path.isdir(folder):
            return []
        files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in ALLOWED_EXT]
        files.sort()
        return files
    except Exception as e:
        print(f"ERROR in images_in_genre: {e}", file=sys.stderr, flush=True)
        return []

def list_slider_images():
    """Возвращает список изображений для слайдера на главной странице (из папки main)."""
    try:
        folder = os.path.join(PHOTO_DIR, 'main')
        if not os.path.isdir(folder):
            return []
        files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in ALLOWED_EXT]
        files.sort()
        return [url_for('static', filename=f'photos/main/{f}') for f in files]
    except Exception as e:
        print(f"ERROR in list_slider_images: {e}", file=sys.stderr, flush=True)
        return []

@app.context_processor
def inject_year():
    from datetime import datetime
    return {'year': datetime.now().year, 'GENRES': GENRES}

@app.before_request
def before_request():
    g.start = time.time()

@app.after_request
def after_request(response):
    diff = time.time() - g.start
    print(f"Request {request.path} took: {diff:.2f}s", file=sys.stderr, flush=True)
    return response

@app.route('/')
def index():
    try:
        slider_images = list_slider_images()
        genres = list_genres()
        return render_template('index.html', slider_images=slider_images, genres=genres)
    except Exception as e:
        print(f"ERROR in index route: {e}", file=sys.stderr, flush=True)
        return "Error loading page", 500

@app.route('/portfolio')
def portfolio():
    try:
        genres = list_genres()
        genre_images = {}
        for g in genres:
            imgs = images_in_genre(g)
            if imgs:
                genre_images[g] = url_for('static', filename=f'photos/{g}/{imgs[0]}')
        return render_template('portfolio.html', genres=genres, genre_images=genre_images)
    except Exception as e:
        print(f"ERROR in portfolio route: {e}", file=sys.stderr, flush=True)
        return "Error loading portfolio", 500

@app.route('/portfolio/<genre>')
def portfolio_genre(genre):
    try:
        genres = list_genres()
        if genre not in genres:
            abort(404)
        imgs = images_in_genre(genre)
        img_urls = [url_for('static', filename=f'photos/{genre}/{i}') for i in imgs]
        return render_template('portfolio_genre.html', genre=genre, images=img_urls, genres=genres)
    except Exception as e:
        print(f"ERROR in portfolio_genre route: {e}", file=sys.stderr, flush=True)
        return "Error loading genre", 500

@app.route('/about')
def about():
    try:
        genres = list_genres()
        return render_template('about.html', genres=genres)
    except Exception as e:
        print(f"ERROR in about route: {e}", file=sys.stderr, flush=True)
        return "Error loading about", 500

@app.route('/contact')
def contact():
    try:
        genres = list_genres()
        return render_template('contact.html', genres=genres)
    except Exception as e:
        print(f"ERROR in contact route: {e}", file=sys.stderr, flush=True)
        return "Error loading contact", 500

# Импортируем и регистрируем blueprint для тестера
try:
    from tester import tester_bp
    app.register_blueprint(tester_bp, url_prefix="/tester")
    print("Tester blueprint registered successfully", file=sys.stderr, flush=True)
except Exception as e:
    print(f"ERROR registering tester blueprint: {e}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    print("Starting Flask server...", file=sys.stderr, flush=True)
    app.run(host='0.0.0.0', port=8081, debug=True)

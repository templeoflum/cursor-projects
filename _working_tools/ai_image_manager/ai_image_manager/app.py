# app.py

import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from math import ceil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
app.secret_key = 'your_secure_secret_key'  # Replace with a strong secret key

DATABASE = 'ai_images.db'

def init_db():
    """Initialize the SQLite database and create the images table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            prompt TEXT,
            seed INTEGER,
            model TEXT,
            additional_params TEXT,
            tags TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Display the initial image gallery with the first set of images."""
    page = 1  # Initial page
    per_page = 20  # Number of images per page

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM images ORDER BY id DESC LIMIT ? OFFSET ?', (per_page, (page - 1) * per_page))
    rows = cursor.fetchall()
    conn.close()

    images = []
    for row in rows:
        images.append({
            'id': row[0],
            'image_path': row[1],
            'prompt': row[2],
            'seed': row[3],
            'model': row[4],
            'additional_params': row[5],
            'tags': row[6]
        })

    total_images = get_total_images()
    total_pages = ceil(total_images / per_page) if per_page else 1

    return render_template('index.html', images=images, page=page, total_pages=total_pages)

def get_total_images(search_query=None):
    """Get the total number of images, optionally filtered by a search query."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    if search_query:
        cursor.execute('SELECT COUNT(*) FROM images WHERE prompt LIKE ? OR tags LIKE ?', (f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute('SELECT COUNT(*) FROM images')
    total = cursor.fetchone()[0]
    conn.close()
    return total

@app.route('/load_images')
def load_images():
    """API endpoint to load more images for infinite scroll."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search_query = request.args.get('search', '', type=str)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if search_query:
        query = 'SELECT * FROM images WHERE prompt LIKE ? OR tags LIKE ? ORDER BY id DESC LIMIT ? OFFSET ?'
        params = (f'%{search_query}%', f'%{search_query}%', per_page, (page - 1) * per_page)
    else:
        query = 'SELECT * FROM images ORDER BY id DESC LIMIT ? OFFSET ?'
        params = (per_page, (page - 1) * per_page)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    images = []
    for row in rows:
        images.append({
            'id': row[0],
            'image_path': row[1],
            'prompt': row[2],
            'seed': row[3],
            'model': row[4],
            'additional_params': row[5],
            'tags': row[6]
        })

    # Determine if there are more images to load
    total_images = get_total_images(search_query)
    total_pages = ceil(total_images / per_page) if per_page else 1
    has_more = page < total_pages

    return jsonify({'images': images, 'has_more': has_more})

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Handle image uploads and metadata storage."""
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part in the form.', 'error')
            return redirect(request.url)
        file = request.files['image']

        prompt = request.form.get('prompt', '')
        seed = request.form.get('seed', '')
        model = request.form.get('model', '')
        additional_params = request.form.get('additional_params', '')
        tags = request.form.get('tags', '')  # Manual tags input

        if file.filename == '':
            flash('No selected file.', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Ensure filename uniqueness to prevent overwriting
            counter = 1
            original_filename, extension = os.path.splitext(filename)
            while os.path.exists(save_path):
                filename = f"{original_filename}_{counter}{extension}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                counter += 1

            file.save(save_path)

            # Insert metadata into the database
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO images (image_path, prompt, seed, model, additional_params, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (filename, prompt, seed, model, additional_params, tags))
            conn.commit()
            conn.close()

            flash('Image uploaded successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Unsupported file type. Allowed types: png, jpg, jpeg, gif, webp.', 'error')
            return redirect(request.url)

    return render_template('upload.html')

@app.route('/edit/<int:image_id>', methods=['GET', 'POST'])
def edit(image_id):
    """Allow users to edit tags for a specific image."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if request.method == 'POST':
        new_tags = request.form.get('tags', '')
        cursor.execute('UPDATE images SET tags = ? WHERE id = ?', (new_tags, image_id))
        conn.commit()
        conn.close()
        flash('Tags updated successfully!', 'success')
        return redirect(url_for('index'))

    # For GET request, fetch current tags
    cursor.execute('SELECT tags FROM images WHERE id = ?', (image_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        current_tags = result[0]
        return render_template('edit.html', image_id=image_id, current_tags=current_tags)
    else:
        flash('Image not found.', 'error')
        return redirect(url_for('index'))

@app.route('/delete/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    """Handle deletion of an image and its metadata."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Fetch the image path from the database
    cursor.execute('SELECT image_path FROM images WHERE id = ?', (image_id,))
    result = cursor.fetchone()
    
    if result:
        image_path = result[0]
        # Define the full path to the image
        full_image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
        
        try:
            # Delete the image file
            if os.path.exists(full_image_path):
                os.remove(full_image_path)
            
            # Delete the database record
            cursor.execute('DELETE FROM images WHERE id = ?', (image_id,))
            conn.commit()
            flash('Image deleted successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred while deleting the image: {e}', 'error')
    else:
        flash('Image not found.', 'error')
    
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure the images folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.run(debug=True)

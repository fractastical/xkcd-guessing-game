from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Connect to SQLite database
def connect_db():
    conn = sqlite3.connect('xkcd_game.db')
    return conn

# Home page with the AI-generated image and guess options
@app.route('/')
def home():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Fetch a random image and corresponding comics for guessing
    cursor.execute("SELECT * FROM images ORDER BY RANDOM() LIMIT 1")
    image = cursor.fetchone()
    
    # Fetch options (including the correct comic)
    correct_comic_id = image[1]
    cursor.execute("SELECT * FROM comics WHERE comic_id != ? ORDER BY RANDOM() LIMIT 3", (correct_comic_id,))
    wrong_comics = cursor.fetchall()
    
    # Add the correct comic to the options and shuffle
    cursor.execute("SELECT * FROM comics WHERE comic_id = ?", (correct_comic_id,))
    correct_comic = cursor.fetchone()
    options = wrong_comics + [correct_comic]
    random.shuffle(options)
    
    conn.close()
    return render_template('index.html', image=image, options=options)

# Handle user's guess
@app.route('/guess', methods=['POST'])
def guess():
    user_id = request.form['user_id']
    image_id = request.form['image_id']
    guessed_comic_id = request.form['guessed_comic_id']
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Check if guess is correct
    cursor.execute("SELECT correct_comic_id FROM images WHERE image_id = ?", (image_id,))
    correct_comic_id = cursor.fetchone()[0]
    is_correct = (int(guessed_comic_id) == correct_comic_id)
    
    # Update image stats
    cursor.execute("UPDATE images SET total_attempts = total_attempts + 1 WHERE image_id = ?", (image_id,))
    if is_correct:
        cursor.execute("UPDATE images SET correct_attempts = correct_attempts + 1 WHERE image_id = ?", (image_id,))
    
    # Calculate difficulty (lower percentage correct -> higher score)
    cursor.execute("SELECT correct_attempts, total_attempts FROM images WHERE image_id = ?", (image_id,))
    correct_attempts, total_attempts = cursor.fetchone()
    percentage_correct = correct_attempts / total_attempts if total_attempts > 0 else 0
    base_score = 100
    score = base_score / (percentage_correct + 0.1)
    
    # Update user's score
    if is_correct:
        cursor.execute("UPDATE users SET total_score = total_score + ? WHERE user_id = ?", (score, user_id))
    
    # Log the guess
    cursor.execute("INSERT INTO guesses (user_id, image_id, guessed_comic_id, is_correct) VALUES (?, ?, ?, ?)",
                   (user_id, image_id, guessed_comic_id, is_correct))
    
    conn.commit()
    conn.close()
    
    # Redirect to home page with feedback
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

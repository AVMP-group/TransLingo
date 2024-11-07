import bcrypt
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import speech_recognition as sr
from googletrans import Translator

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# SQLite configuration
DATABASE = 'user_info_db.db'

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/text_to_text')
def text_to_text():
    return render_template('text_to_text.html')

@app.route('/voice_to_text', methods=['GET', 'POST'])
def voice_to_text():
    original_text = ""
    translation = ""
    target_language = "en"  # Default to English

    if request.method == 'POST':
        audio_file = request.files.get('audio_file')
        if audio_file:
            r = sr.Recognizer()
            with sr.AudioFile(audio_file) as source:
                audio_data = r.record(source)
            try:
                original_text = r.recognize_google(audio_data)
                translator = Translator()
                translation = translator.translate(original_text, dest=target_language).text
            except sr.UnknownValueError:
                original_text = "Could not understand audio"
            except sr.RequestError as e:
                original_text = f"Could not request results from Google Speech Recognition service; {e}"
            except ValueError as e:
                original_text = f"Error processing audio file: {e}"

    return render_template('voice_to_text.html', originalText=original_text, translation=translation, selected_language=target_language)

@app.route('/image_to_text')
def image_to_text():
    return render_template('image_to_text.html')

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fetch user from SQLite database
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and user['password_hash']:
            flash('Successfully logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('sign_in.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            conn = get_db_connection()
            conn.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", 
                                            (username, email, hashed_password))
            conn.commit()
            conn.close()

            flash('You have successfully signed up! Please log in.', 'success')
            return redirect(url_for('sign_in'))

        except Exception as e:
            flash(f"An error occurred: {e}", 'danger')

    return render_template('sign_up.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    # Create tables if they don't exist
    # conn = get_db_connection()
    # conn.execute('''CREATE TABLE IF NOT EXISTS users (
    #                 user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                 username TEXT NOT NULL,
    #                 email TEXT UNIQUE NOT NULL,
    #                 password_hash TEXT NOT NULL,
    #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    #             )''')
    # conn.close()
    
    app.run(debug=True)

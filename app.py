import bcrypt
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
# from datetime import datetime
import speech_recognition as sr
from googletrans import Translator
from PIL import Image
import pytesseract

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

@app.route('/text_to_text',methods =['GET','POST'])
def text_to_text():
    original_text = ""
    translation = ""
    target_language = "en"  # Default to English

    if request.method == 'POST':
        # Get the text from the input field
        original_text = request.form.get('originalText')
        target_language = request.form.get('language')
        translator = Translator()
        translation = translator.translate(original_text, dest=target_language).text
    return render_template('text_to_text.html',originalText=original_text, translation=translation, selected_language=target_language)

@app.route('/voice_to_text', methods=['GET', 'POST'])
def voice_to_text():
    original_text = ""
    translation = ""
    target_language = "en"  # Default to English

    if request.method == 'POST':
        # Get the text from the input field
        original_text = request.form.get('originalText')
        target_language = request.form.get('language')

        if original_text:
            # Translate the text
            translator = Translator()
            translation = translator.translate(original_text, dest=target_language).text
        else:
            # Check for an uploaded audio file
            audio_file = request.files.get('audio_file')
            if audio_file:
                r = sr.Recognizer()
                with sr.AudioFile(audio_file) as source:
                    audio_data = r.record(source)
                try:
                    original_text = r.recognize_google(audio_data)
                    translation = translator.translate(original_text, dest=target_language).text
                except sr.UnknownValueError:
                    original_text = "Could not understand audio"
                except sr.RequestError as e:
                    original_text = f"Could not request results from Google Speech Recognition service; {e}"
                except ValueError as e:
                    original_text = f"Error processing audio file: {e}"

    return render_template('voice_to_text.html', originalText=original_text, translation=translation, selected_language=target_language)

@app.route('/image_to_text', methods=['GET', 'POST'])
def image_to_text():
    extracted_text = None
    translated_text = None

    pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'


    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        target_language = request.form['language']  # Get selected language for translation

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file:
            # Process the file directly without saving it to disk
            img = Image.open(file.stream)  # Open the uploaded image file
            extracted_text = pytesseract.image_to_string(img)  # Extracting text from the image

            # Translate the extracted text
            if extracted_text.strip():
                translator = Translator()
                translated = translator.translate(extracted_text, dest=target_language)
                translated_text = translated.text

            return render_template('image_to_text.html', extracted_text=extracted_text, translated_text=translated_text, selected_language=target_language)

    return render_template('image_to_text.html', extracted_text=extracted_text, translated_text=translated_text)


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
    app.run(debug=True)

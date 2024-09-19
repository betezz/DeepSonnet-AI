import os
from flask import Flask, request, jsonify, render_template
from random import choice
import nltk
from nltk.corpus import cmudict
import ssl
from openai import OpenAI
from example import initialize_openai_client, analyze_poem # ensure_nltk_data Import the functions from your example.py
from poems import get_poem
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

# Ensure NLTK resources are downloaded (e.g., for Sentiment Analysis)
try:
    _create_unverified_https_context = ssl._create_unverified_context
    ssl._create_default_https_context = _create_unverified_https_context
except AttributeError:
    pass

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poems.db'
db = SQLAlchemy(app)

# Define Poem model
class Poem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    total_rating = db.Column(db.Float, default=0)
    num_ratings = db.Column(db.Integer, default=0)

    @property
    def average_rating(self):
        if self.num_ratings > 0:
            return self.total_rating / self.num_ratings
        return 0

def fetch_top_poems():
    return Poem.query.order_by((Poem.total_rating / Poem.num_ratings).desc()).limit(10).all()

def update_poem_rating(poem_id, rating):
    poem = Poem.query.get(poem_id)
    if poem:
        poem.total_rating += rating
        poem.num_ratings += 1
        db.session.commit()

# Initialize the OpenAI client
client = initialize_openai_client()

@app.route('/')
def index():
    """
    Render the homepage with the poem analysis form.
    """
    return render_template('index.html')  # Serve index.html from the templates folder

@app.route('/analyze_poem', methods=['POST'])
def analyze_poem_endpoint():
    try:
        data = request.json
        poem_text = data.get('poem_text')
        poem_title = data.get('poem_title', 'Untitled')
        analysis_type = data.get('analysis_type', 'sentiment')

        result = analyze_poem(client, poem_text, poem_title, analysis_type)
        
        return jsonify(result)  # The result is already formatted in HTML

    except Exception as e:
        app.logger.error(f"Error in analyze_poem_endpoint: {str(e)}")
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

@app.route('/leaderboard')
def leaderboard():
    top_poems = fetch_top_poems()
    return render_template('leaderboard.html', poems=top_poems)

@app.route('/submit_rating', methods=['POST'])
def submit_rating():
    data = request.json
    poem_id = data.get('poem_id')
    rating = data.get('rating')
    # Update the poem's rating in the database
    update_poem_rating(poem_id, rating)  # Implement this function
    return jsonify({'success': True})

@app.route('/get_random_poem')
def get_random_poem():
    poem = choice(Poem.query.all())
    return jsonify({
        'id': poem.id,
        'title': poem.title,
        'author': poem.author,
        'content': poem.content
    })

# Add this function to create tables
def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()  # Call this function before running the app
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)


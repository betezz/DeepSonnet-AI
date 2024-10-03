import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from random import choice
import nltk
from nltk.corpus import cmudict
from werkzeug.utils import secure_filename
import ssl
from openai import OpenAI
from example import initialize_openai_client, analyze_poem, calculate_poem_score
from shortstory import analyze_shortstory, initialize_openai_client as init_shortstory_client
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from concurrent.futures import ThreadPoolExecutor
import PyPDF2
import io

# Ensure NLTK resources are downloaded (e.g., for Sentiment Analysis)
try:
    _create_unverified_https_context = ssl._create_unverified_context
    ssl._create_default_https_context = _create_unverified_https_context
except AttributeError:
    pass

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

# Configure the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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

# Initialize the OpenAI clients
poetry_client = initialize_openai_client()
shortstory_client = init_shortstory_client()

@app.route('/')
def index():
    """
    Render the homepage with the poem analysis form.
    """
    return render_template('index.html')  # Serve index.html from the templates folder

@app.route('/short_story')
def short_story():
    """
    Render the short story analysis page.
    """
    return render_template('s-story.html')

@app.route('/analyze_poem', methods=['POST'])
def analyze_poem_endpoint():
    app.logger.info("Received analyze_poem request")
    try:
        data = request.json
        app.logger.info(f"Request data: {data}")
        poem_text = data.get('poem_text')
        poem_title = data.get('poem_title', 'Untitled')
        analysis_type = data.get('analysis_type', 'sentiment')
        
        if poem_text == "<test>":
            poem_title = "Malvern Prep March"
            poem_text = """
            Yo Laville, you're soft as fluff,
            Out here actin' like you're tough.
            Talkin' smack, but can't keep pace,
            You're just background noise in this race.

            Your sticks? Weak. Your shots? A joke.
            We torch your D like you're a smoke.
            Watch us rip it—top-shelf, clean—
            Your goalie? Can't even be seen.

            You rock those ties, think you're elite,
            But on the turf? We run the street.
            You pull up scared, we see you sweat,
            By halftime, you're not a threat.

            Your "legacy" don't mean a thing,
            When Malvern's kings, we own this ring.
            We dominate, you fake the grind,
            Your glory days? All left behind.

            Your prissy ways, your fancy crest,
            Still can't hang with Philly's best.
            So go on, Laville, talk that smack,
            But we'll leave you flat on your back
            """
            print(f"DeepSonnet AI: Analyzing poem: {poem_title}, Analysis type: {analysis_type}")

        # Use ThreadPoolExecutor to run analysis in parallel
        with ThreadPoolExecutor() as executor:
            analysis_future = executor.submit(analyze_poem, poetry_client, poem_text, poem_title, analysis_type)
            score_future = executor.submit(calculate_poem_score, poetry_client, poem_text, poem_title)

            result = analysis_future.result()
            score = score_future.result()

        response_data = {'result': result['result'], 'score': score}
        if 'word_details' in result:
            response_data['word_details'] = result['word_details']

        return jsonify(response_data)

    except Exception as e:
        app.logger.error(f"Error in analyze_poem_endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
       
@app.route('/analyze_shortstory', methods=['POST'])
def analyze_shortstory_endpoint():
    try:
        story_title = request.form.get('story_title', 'Untitled')
        story_text = request.form.get('story_text', '')
        analysis_type = request.form.get('analysis_type', 'general')

        if 'story_file' in request.files:
            file = request.files['story_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                story_text = extract_text_from_pdf(filepath)
                os.remove(filepath)  # Remove the file after extraction
            else:
                return jsonify({'error': 'Invalid file type. Please upload a PDF.'}), 400
            
        if story_text == "<test>":
            story_title = "The Rise of Malvern Prep"
            story_text = """
            It was a crisp spring afternoon when Malvern Prep's lacrosse team faced off against their arch-rivals, Lawrenceville. The energy on the field was electric as the two teams clashed in a battle for supremacy.

            Malvern Prep's players, fueled by their determination to emerge victorious, dominated the game from the start. Their sticks moved in perfect sync, cradling and passing the ball with precision. The Lawrenceville defense was no match for Malvern's lightning-fast attacks, and the scoreboard reflected the Prep's superiority.

            As the final whistle blew, the Malvern Prep team erupted in cheers, celebrating their hard-fought win. The players hugged each other, grinning from ear to ear, as their coaches beamed with pride. It was a moment that would be etched in the memories of the team and their fans forever.

            The victory was not just about winning a game; it was about the culmination of months of hard work, dedication, and teamwork. It was a testament to the Prep's commitment to excellence, both on and off the field. As the team celebrated their triumph, they knew that this was just the beginning of their journey to greatness.

            The legacy of Malvern Prep's lacrosse team would live on, inspiring future generations to strive for excellence and push beyond their limits. The Prep's spirit, forged in the fire of competition, would continue to burn bright, guiding its students towards a brighter future.
            """

        result = analyze_shortstory(shortstory_client, story_text, story_title, analysis_type)
        return jsonify({'result': result, 'story_text': story_text})

    except Exception as e:
        app.logger.error(f"Error in analyze_shortstory_endpoint: {str(e)}", exc_info=True)
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
    update_poem_rating(poem_id, rating)
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

@app.route('/about')
def about():
    return render_template('about.html')

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
    return text

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# Add this function to create tables
def create_tables():
    with app.app_context():
        db.create_all()
        # Check if the database is empty
        if Poem.query.count() == 0:
            # Add some initial poems
            initial_poems = [
                Poem(title="Sample Poem 1", author="Author 1", content="This is a sample poem..."),
                Poem(title="Sample Poem 2", author="Author 2", content="Another sample poem..."),
                # Add more sample poems as needed
            ]
            db.session.add_all(initial_poems)
            db.session.commit()
       
if __name__ == '__main__':
    create_tables()  # Call this function before running the app
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
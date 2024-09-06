import os
from flask import Flask, request, jsonify
import nltk
import ssl
from openai import OpenAI
from example import initialize_openai_client, analyze_poem  # Import the functions from your example.py
from poems import get_poem
from flask_cors import CORS

# Ensure NLTK resources are downloaded (e.g., for Sentiment Analysis)
try:
    _create_unverified_https_context = ssl._create_unverified_context
    ssl._create_default_https_context = _create_unverified_https_context
except AttributeError:
    pass
# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize the OpenAI client
client = initialize_openai_client()

@app.route('/analyze_poem', methods=['POST'])
def analyze_poem_endpoint():
    """
    Endpoint to analyze a poem based on the provided analysis type.
    """
    try:
        # Extract data from the request
        data = request.json
        poem_text = data.get('poem_text')
        poem_title = data.get('poem_title', 'Untitled')
        analysis_type = data.get('analysis_type', 'sentiment')

        # Call the analyze_poem function from example.py
        result = analyze_poem(client, poem_text, poem_title, analysis_type)

        # Return the result as a JSON response
        return jsonify({'result': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
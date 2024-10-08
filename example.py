import os
from openai import OpenAI
import ssl
import nltk
from nltk.corpus import cmudict
from nltk.metrics.distance import edit_distance
from dotenv import load_dotenv
import concurrent.futures
import re
from difflib import SequenceMatcher
import string
import itertools

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

nltk.data.path.append("/tmp/nltk_data")

nltk_data_downloaded = False

'''

def ensure_nltk_data():
    global nltk_data_downloaded
    if not nltk_data_downloaded:
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/cmudict')
            nltk.data.find('tokenizers/punkt_tab')  # Add this line
            nltk_data_downloaded = True
        except LookupError:
            try:
                nltk.download('punkt', download_dir="/tmp/nltk_data", quiet=True)
                nltk.download('cmudict', download_dir="/tmp/nltk_data", quiet=True)
                nltk.download('punkt_tab', download_dir="/tmp/nltk_data", quiet=True)  # Add this line
                nltk_data_downloaded = True
            except Exception as e:
                print(f"Error downloading NLTK data: {e}")
                
'''
                

def initialize_openai_client(): 
    client = OpenAI(api_key=api_key)
    return client

def get_openai_completion(client, model, system_content, user_content):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error fetching completion: {e}")
        return None
    
def analyze_poem(client, poem_text, poem_title, analysis_type):
    """
    Analyzes a given poem based on the specified analysis type.

    Parameters:
    - client: An instance of the OpenAI API client.
    - poem_text (str): The text of the poem to analyze.
    - analysis_type (str): The type of analysis to perform. Supported values:
        - 'sentiment' or 's': Analyze the sentiment of the poem.
        - 'themes' or 't': Analyze the main themes of the poem.
        - 'style' or 'st': Determine the style or movement (e.g., Romanticism, Modernism) of the poem.

    Returns:
    - dict: The API response containing the analysis of the poem.
    """
    # Add this block at the beginning of the function
    print(f"Analyzing poem: {poem_title}, Analysis type: {analysis_type}")
    # Ensure poem_text is not empty or None
    if not poem_text or not isinstance(poem_text, str):
        raise ValueError("Poem text must be a non-empty string.")

    # Standardize analysis type to lowercase for consistent comparison
    analysis_type = analysis_type.lower().strip()


    # Map of supported analysis types to system prompts
    prompts = {
        "sentiment": (
            "You are an expert in poetry analysis. Begin by identifying the primary sentiment or emotion in each stanza of the following poem, "
            "using specific textual evidence. Then, analyze how these sentiments evolve throughout the poem and contribute to the overall emotional arc and tone. "
            "Consider any shifts in mood and discuss their potential impact on different readers. "
        ),
        "s": (
            "You are an expert in poetry analysis. Begin by identifying the primary sentiment or emotion in each stanza of the following poem, "
            "using specific textual evidence. Then, analyze how these sentiments evolve throughout the poem and contribute to the overall emotional arc and tone. "
            "Consider any shifts in mood and discuss their potential impact on different readers."
        ),
        "themes": (
            "You are a seasoned poetry critic. Identify and discuss the primary themes of the following poem, using examples to support your analysis. "
            "After identifying the central themes, explain how they interrelate and contribute to the poem's overall meaning. "
            "Discuss any potential underlying symbolism or secondary themes."
        ),
        "t": (
            "You are a seasoned poetry critic. Identify and discuss the primary themes of the following poem, using examples to support your analysis. "
            "After identifying the central themes, explain how they interrelate and contribute to the poem's overall meaning. "
            "Discuss any potential underlying symbolism or secondary themes."
        ),
        "style": (
            "You are a poetry expert. Based on the language, tone, and structure of the following poem, determine which literary movement or style it belongs to "
            "(e.g., Romanticism, Modernism, etc.). Provide three specific reasons, with evidence from the poem, to support your determination. "
            "Analyze how the style influences the poem's themes and tone."
        ),
        "st": (
            "You are a poetry expert. Based on the language, tone, and structure of the following poem, determine which literary movement or style it belongs to "
            "(e.g., Romanticism, Modernism, etc.). Provide three specific reasons, with evidence from the poem, to support your determination. "
            "Analyze how the style influences the poem's themes and tone."
        ),
        "rhyme": (
            "You are a poetry expert. Examine the rhyme scheme of the following poem, identifying any specific patterns (e.g., ABAB, AABB). "
            "If there is no consistent rhyme scheme, analyze whether the absence of rhyme contributes to the poem's tone or themes. "
            "If no rhyme scheme exists, simply respond 'no rhyme scheme detected'."
        ),
        "r": (
            "You are a poetry expert. Examine the rhyme scheme of the following poem, identifying any specific patterns (e.g., ABAB, AABB). "
            "If there is no consistent rhyme scheme, analyze whether the absence of rhyme contributes to the poem's tone or themes. "
            "If no rhyme scheme exists, simply respond 'no rhyme scheme detected'."
        ),
        "meter": (
            "You are an expert in poetry structure. Identify any specific meter in the following poem (e.g., iambic pentameter, trochaic tetrameter). "
            "If a particular meter is used, explain how it reinforces the poem's themes or tone. If no meter is detected, explain whether the free verse style influences the poem's overall structure."
        ),
        "m": (
            "You are an expert in poetry structure. Identify any specific meter in the following poem (e.g., iambic pentameter, trochaic tetrameter). "
            "If a particular meter is used, explain how it reinforces the poem's themes or tone. If no meter is detected, explain whether the free verse style influences the poem's overall structure."
        ),
        "general": (
        "You are an expert poetry analyst. Provide a comprehensive analysis of the following poem, addressing its themes, tone, structure, style, and any notable literary devices. "
        "Discuss how these elements work together to create the poem's overall effect. Consider the poem's potential cultural or historical context, and offer multiple interpretations where relevant. "
        "Your analysis should cover how the poem's language, imagery, and structure contribute to its meaning and emotional impact."
    )
    }

    # Validate analysis_type and get the corresponding system prompt
    if analysis_type in prompts:
        system_prompt = prompts.get(analysis_type)
        if not system_prompt:
            raise ValueError(f"Invalid analysis type '{analysis_type}'. Supported types are: 'sentiment', 'themes', 'style', 'rhyme', 'meter', 's', 't', 'st', 'r', 'm'.")

        # Prepare the message payload
        system_prompt = system_prompt + f" The name of the poem is '{poem_title}' and it is provided below."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": poem_text}
        ]

        # Make the API call and return the response
        if analysis_type == "general":
            max_toks = 1000
            # Add detailed analysis for each word
            lines = poem_text.split('\n')
            word_details = {}
            for i, line in enumerate(lines):
                words = line.split()
                for word in words:
                    word_details[word] = {
                        "poetic_device": identify_poetic_device(word, line, lines[i-1] if i > 0 else None)
                    }
        else:
            max_toks = 600
            
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",  # Switch to a more powerful model if available
                messages=messages,
                temperature=0.75,  # Adjust temperature to balance creativity and accuracy
                max_tokens=max_toks,   # Limit the number of tokens for the response
                top_p=0.95,        # Consider the most likely outputs
                frequency_penalty=0.2,  # Adjust penalties to control repetitive outputs
                presence_penalty=0.2
            )
            print("API call successful")
            result = completion.choices[0].message.content.strip()  # Return the cleaned response content

            # Calculate a score based on the analysis
            score = calculate_poem_score(client, poem_text, poem_title)

            # Format the analysis result
            formatted_result = format_analysis_result(result, analysis_type)

            # Return both the analysis result and the score
            if analysis_type == "general":
                return {'result': formatted_result, 'score': score, 'word_details': word_details}
            else:
                return {'result': formatted_result, 'score': score}

        except Exception as e:
            # Handle API errors gracefully
            print(f"Error in API call: {str(e)}")
            raise RuntimeError(f"An error occurred while analyzing the poem: {str(e)}")
    else: 
        king_result = king_analysis(client, poem_text, poem_title, analysis_type)
        formatted_result = format_analysis_result(king_result['result'], king_result['analysis_type'])
        score = calculate_poem_score(client, poem_text, poem_title)
        return {'result': formatted_result, 'score': score}
    
def calculate_poem_score(client, poem_text, poem_title):
    system_prompt = (
        "You are a harsh poetry critic. Analyze the given poem and assign a score from 0 to 100. "
        "Consider the following aspects: originality, imagery, emotional impact, technical skill, and overall coherence. "
        "Be extremely critical and demanding. A score above 90 should be extremely rare and reserved only for truly exceptional poems. "
        "Most poems should score between 40 and 70. Provide a brief justification for your score."
        "Justifications should be around 100 words"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Title: {poem_title}\n\n{poem_text}"}
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Using a more advanced model for critical analysis
            messages=messages,
            temperature=0.5,  # Lower temperature for more consistent scoring
            max_tokens=150,   # Limit response length
            top_p=0.95,
            frequency_penalty=0.1,
            presence_penalty=0.1
        )

        response = completion.choices[0].message.content.strip()
        
        # Extract score from the response
        score_match = re.search(r'\b(\d{1,3})\b', response)
        if score_match:
            score = int(score_match.group(1))
            # Ensure score is within 0-100 range
            score = max(0, min(score, 100))
        else:
            # Default score if no number is found
            score = 50

        return score

    except Exception as e:
        print(f"Error in calculate_poem_score: {str(e)}")
        # Return a default score in case of error
        return 50
def king_analysis(client, poem_text, poem_title, analysis_type):
    # Use concurrent.futures to run analyses in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        rhyme_future = executor.submit(king_rhyme_scheme, client, poem_text)
        meter_future = executor.submit(king_meter_analysis, client, poem_text)
        theme_future = executor.submit(king_theme_analysis, client, poem_text, poem_title)

        rhyme_scheme = rhyme_future.result()
        poem_meter = meter_future.result()
        poem_analysis = theme_future.result()

    return {
        "result": {
            "Rhyme Scheme": rhyme_scheme,
            "Poem Meter": poem_meter,
            "Poem Analysis": poem_analysis
        },
        "analysis_type": analysis_type
    }
    
'''

def is_slant_rhyme(sound1, sound2, threshold=2):
    """Determine if two phonetic transcriptions are close enough to be considered slant rhymes."""
    return edit_distance(sound1, sound2) <= threshold

def fuzzy_rhyme(sound1, sound2):
    """Return True if sounds are considered close enough to be near rhymes."""
    ratio = SequenceMatcher(None, sound1, sound2).ratio()
    return ratio > 0.75  # Adjust the ratio threshold as needed

def get_best_pronunciation(word):
    """Choose the pronunciation with the highest similarity to existing rhymes."""
    pronunciations = pronouncing_dict.get(word, [])
    best_score = float('inf')
    best_pronunciation = None
    for pronunciation in pronunciations:

        
        for known_pron in unique_sounds:
            score = edit_distance(pronunciation, known_pron)
            if score < best_score:
                best_score = score
                best_pronunciation = pronunciation

    return best_pronunciation
    
'''

def king_rhyme_scheme(client, poem_text):
    #ensure_nltk_data()
    
    # Preprocess the poem
    '''
    lines = [line.strip() for line in poem_text.split('\n') if line.strip()]
    last_words = [word_tokenize(line)[-1].lower() for line in lines]
    
    # Get rhyme sounds
    rhyme_sounds = [get_rhyme_sound(word) for word in last_words]
    
    # Identify unique rhyme sounds and assign letters
    unique_sounds = {}
    rhyme_scheme = []
    current_letter = 'A'
    
    for sound in rhyme_sounds:
        if sound is None:
            rhyme_scheme.append('X')  # Non-rhyming line
        else:
            found_rhyme = False
            for known_sound in unique_sounds:
                if sound == known_sound or is_slant_rhyme(sound, known_sound) or fuzzy_rhyme(sound, known_sound):
                    rhyme_scheme.append(unique_sounds[known_sound])
                    found_rhyme = True
                    break
            
            if not found_rhyme:
                unique_sounds[sound] = current_letter
                rhyme_scheme.append(current_letter)
                current_letter = chr(ord(current_letter) + 1)
    
    # Detect stanzas (assuming blank lines separate stanzas)
    stanzas = re.split(r'\n\s*\n', poem_text)
    stanza_lengths = [len([line for line in stanza.split('\n') if line.strip()]) for stanza in stanzas]
    
    # Construct the final rhyme scheme with stanza separators
    final_scheme = []
    current_index = 0
    for length in stanza_lengths:
        final_scheme.extend(rhyme_scheme[current_index:current_index + length])
        if current_index + length < len(rhyme_scheme):
            final_scheme.append('--')
        current_index += length
    
    # Prepare the result
    result = ''.join(final_scheme)
    
    '''
    
    # Modify the system prompt to give more emphasis on manual analysis
    system_prompt = (
        "You are an Expert Poet assisting in rhyme scheme analysis. Your task is to analyze the rhyme scheme of the given poem. "
        #f"A preliminary analysis suggests the following scheme: {result}\n"
        #"However, this may not be accurate. Please perform your own analysis and provide the correct rhyme scheme. "
        "1. Analyze the poem's rhyme structure carefully, considering near rhymes and slant rhymes. "
        "2. Provide the rhyme scheme using capital letters (A, B, C, etc.) for each unique rhyme sound, in basic standard notation."
        "for instance, if the last words of the lines in the first stanza were 'love', 'hate', 'dove', 'fate', in that order, the rhyme scheme would be ABAB"
        "3. Use '--' to separate stanzas. "
        "4. If there's no consistent rhyme scheme, state 'No consistent rhyme scheme detected'. "
        "Your output should only contain the final rhyme scheme or 'No consistent rhyme scheme detected', nothing else."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": poem_text}
    ]
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-3.5-turbo" depending on your budget
            messages=messages,
            temperature=0.3,
            max_tokens=200,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return completion.choices[0].message.content.strip()
    
    except Exception as e:
        raise RuntimeError(f"An error occurred while analyzing the rhyme scheme: {str(e)}")

def king_meter_analysis(client, poem_text):
    system_prompt = (
        "You are an Expert Poet specializing in metrical analysis. Your task is to: "
        "1. Identify the predominant meter of the poem (e.g., iambic pentameter, trochaic tetrameter). "
        "2. Provide a line-by-line scansion of the poem using the following notation: "
        "   - Use '˘' for unstressed syllables and '′' for stressed syllables. "
        "   - Separate each foot with a vertical bar '|'. "
        "   - Use '--' to indicate line breaks. "
        "3. If the poem does not have a consistent meter, state 'No consistent meter detected' "
        "   and provide the scansion as described above. "
        "4. Your output should be in the following format: "
        "   METER: [Identified meter or 'No consistent meter detected'] "
        "   SCANSION: [Line-by-line scansion] "
        "Provide only the requested information without additional analysis or interpretation."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": poem_text}
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,  # Lower temperature for more consistent, objective output
            max_tokens=500,   # Increased to accommodate longer poems
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return completion.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"An error occurred during meter analysis: {str(e)}")
    
def king_theme_analysis(client, poem_text, poem_title):
    """
    Provides a detailed theme analysis for the given poem.
    
    Parameters:
    - client: An instance of the OpenAI API client.
    - poem_text (str): The text of the poem to analyze.

    Returns:
    - str: The detailed theme analysis of the poem.
    """
    system_prompt = (
        "You are an expert poetry critic. Conduct a deep thematic analysis of the following poem, identifying both primary and secondary themes. "
        "Explain how these themes interact with one another and how they are developed throughout the poem. "
        "Pay close attention to symbolism, imagery, and any recurring motifs that support the thematic structure. "
        "Also, consider how the poem's cultural, historical, or philosophical context might influence its thematic message."
        f"the poems title is {poem_title}, you should mention this atleast once in your analysis"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": poem_text}
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7, 
            max_tokens=500,   
            top_p=0.95,
            frequency_penalty=0.2,
            presence_penalty=0.2
        )
        return completion.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"An error occurred during theme analysis: {str(e)}")
    
    
def format_analysis_result(result, analysis_type):
    """
    Formats the analysis results into HTML for easy display in the frontend.

    Parameters:
    - result: The analysis result (string or dictionary)
    - analysis_type: The type of analysis performed

    Returns:
    - str: The formatted analysis as HTML
    """
    def markdown_to_html(text):
        # Convert ### headings to <h3> tags
        text = re.sub(r'^###\s*(.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        
        # Convert # headings to <h4> tags
        text = re.sub(r'^#\s*(.*?)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
        
        # Convert **bold** to <strong>bold</strong>
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # Convert *italic* to <em>italic</em>
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # Convert newlines to <br> tags
        text = text.replace('\n', '<br>')
        
        return text

    if analysis_type == "king":
        formatted_output = (
            f"<h3>Rhyme Scheme</h3><p>{markdown_to_html(result['Rhyme Scheme'])}</p>"
            f"<h3>Meter Analysis</h3><p>{markdown_to_html(result['Poem Meter'])}</p>"
            f"<h3>Thematic Analysis</h3><p>{markdown_to_html(result['Poem Analysis'])}</p>"
        )
    else:
        formatted_output = f"<h3>{analysis_type.capitalize()} Analysis</h3><p>{markdown_to_html(result)}</p>"

    return formatted_output

def identify_poetic_device(word, line, prev_line=None):
    def consecutive_alliteration(words):
        count = 1
        for i in range(1, len(words)):
            if words[i][0].lower() == words[i-1][0].lower() and words[i][0].lower() not in 'aeiou':
                count += 1
                if count >= 2:
                    return True
            else:
                count = 1
        return False

    def consecutive_assonance(words):
        def word_vowels(word):
            return ''.join([char for char in word if char.lower() in 'aeiou'])

        count = 1
        for i in range(1, len(words)):
            if word_vowels(words[i]) == word_vowels(words[i-1]) and word_vowels(words[i]):
                count += 1
                if count >= 2:
                    return True
            else:
                count = 1
        return False

    words = line.lower().split()
    word_index = words.index(word.lower())

    # Check for alliteration
    if word_index > 0 and consecutive_alliteration(words[word_index-1:word_index+1]):
        return "alliteration"
    elif word_index < len(words) - 1 and consecutive_alliteration(words[word_index:word_index+2]):
        return "alliteration"

    # Check for assonance
    if word_index > 0 and consecutive_assonance(words[word_index-1:word_index+1]):
        return "assonance"
    elif word_index < len(words) - 1 and consecutive_assonance(words[word_index:word_index+2]):
        return "assonance"

    return "none"

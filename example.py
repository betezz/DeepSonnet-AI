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
            "Consider any shifts in mood and discuss their potential impact on different readers."
        ),
        "s": (
            "You are an expert in poetry analysis. Begin by identifying the primary sentiment or emotion in each stanza of the following poem, "
            "using specific textual evidence. Then, analyze how these sentiments evolve throughout the poem and contribute to the overall emotional arc and tone. "
            "Consider any shifts in mood and discuss their potential impact on different readers."
        ),
        "themes": (
            "You are a seasoned poetry critic. Identify and discuss the primary themes of the following poem, using examples to support your analysis. "
            "After identifying the central themes, explain how they interrelate and contribute to the poem’s overall meaning. "
            "Discuss any potential underlying symbolism or secondary themes."
        ),
        "t": (
            "You are a seasoned poetry critic. Identify and discuss the primary themes of the following poem, using examples to support your analysis. "
            "After identifying the central themes, explain how they interrelate and contribute to the poem’s overall meaning. "
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
            "If there is no consistent rhyme scheme, analyze whether the absence of rhyme contributes to the poem’s tone or themes. "
            "If no rhyme scheme exists, simply respond 'no rhyme scheme detected'."
        ),
        "r": (
            "You are a poetry expert. Examine the rhyme scheme of the following poem, identifying any specific patterns (e.g., ABAB, AABB). "
            "If there is no consistent rhyme scheme, analyze whether the absence of rhyme contributes to the poem’s tone or themes. "
            "If no rhyme scheme exists, simply respond 'no rhyme scheme detected'."
        ),
        "meter": (
            "You are an expert in poetry structure. Identify any specific meter in the following poem (e.g., iambic pentameter, trochaic tetrameter). "
            "If a particular meter is used, explain how it reinforces the poem’s themes or tone. If no meter is detected, explain whether the free verse style influences the poem's overall structure."
        ),
        "m": (
            "You are an expert in poetry structure. Identify any specific meter in the following poem (e.g., iambic pentameter, trochaic tetrameter). "
            "If a particular meter is used, explain how it reinforces the poem’s themes or tone. If no meter is detected, explain whether the free verse style influences the poem's overall structure."
        ),
        "general": (
        "You are an expert poetry analyst. Provide a comprehensive analysis of the following poem, addressing its themes, tone, structure, style, and any notable literary devices. "
        "Discuss how these elements work together to create the poem's overall effect. Consider the poem’s potential cultural or historical context, and offer multiple interpretations where relevant. "
        "Your analysis should cover how the poem’s language, imagery, and structure contribute to its meaning and emotional impact."
    )
    }

    # Validate analysis_type and get the corresponding system prompt
    if analysis_type != "king":
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
            return completion.choices[0].message.content.strip()  # Return the cleaned response content

        except Exception as e:
            # Handle API errors gracefully
            raise RuntimeError(f"An error occurred while analyzing the poem: {str(e)}")
    else: 
        return format_king_analysis(king_analysis(client, poem_text, poem_title))
    
def king_analysis(client, poem_text, poem_title):
    # Use concurrent.futures to run analyses in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        rhyme_future = executor.submit(king_rhyme_scheme, client, poem_text)
        meter_future = executor.submit(king_meter_analysis, client, poem_text)
        theme_future = executor.submit(king_theme_analysis, client, poem_text, poem_title)

        rhyme_scheme = rhyme_future.result()
        poem_meter = meter_future.result()
        poem_analysis = theme_future.result()

    total = {
        "Rhyme Scheme": rhyme_scheme,
        "Poem Meter": poem_meter,
        "Poem Analysis": poem_analysis
    }

    return total
    
    
pronouncing_dict = cmudict.dict()

def get_rhyme_sound(word):
    """Extract the stressed vowel and following sounds."""
    word = word.lower().strip(string.punctuation)
    if word in pronouncing_dict:
        pronunciation = pronouncing_dict[word][0]
        for i in reversed(range(len(pronunciation))):
            if any(char.isdigit() for char in pronunciation[i]):
                return pronunciation[i:]
    return None

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
        '''
        
        for known_pron in unique_sounds:
            score = edit_distance(pronunciation, known_pron)
            if score < best_score:
                best_score = score
                best_pronunciation = pronunciation
        '''
    return best_pronunciation

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
    
    
def format_king_analysis(result_dict):
    """
    Formats the analysis results into a single string for easy scrolling display,
    converting Markdown-style formatting to HTML.

    Parameters:
    - result_dict: The dictionary containing the different parts of the analysis.
    
    Returns:
    - str: The formatted analysis as a single string with HTML formatting.
    """
    def markdown_to_html(text):
        # Convert **bold** to <strong>bold</strong>
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        # Convert --text-- to <em>text</em> (assuming -- is used for emphasis)
        text = re.sub(r'\-\-(.*?)\-\-', r'<em>\1</em>', text)
        return text

    formatted_output = (
        f"<h3>Rhyme Scheme</h3>\n<p>{markdown_to_html(result_dict['Rhyme Scheme'])}</p>\n\n"
        f"<h3>Meter Analysis</h3>\n<p>{markdown_to_html(result_dict['Poem Meter'])}</p>\n\n"
        f"<h3>Thematic Analysis</h3>\n<p>{markdown_to_html(result_dict['Poem Analysis'])}</p>\n"
    )
    return formatted_output.replace('\n', '<br>')

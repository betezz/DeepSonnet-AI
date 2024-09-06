import os
from openai import OpenAI
import nltk
import ssl
from nltk.sentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

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
        return completion.choices[0].message['content']
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
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(poem_text)


    # Map of supported analysis types to system prompts
    prompts = {
        "sentiment": f"You are a poetry expert. First, identify the primary sentiment in each stanza of the following poem, providing examples from the text. Then, explain how these sentiments contribute to the overall mood of the poem. The sentiment scores of this poem are as follows: {sentiment_scores}. Use this information in your analysis.",
        "s": f"You are a poetry expert. First, identify the primary sentiment in each stanza of the following poem, providing examples from the text. Then, explain how these sentiments contribute to the overall mood of the poem. The sentiment scores of this poem are as follows: {sentiment_scores}. Use this information in your analysis.",
        "themes": "You are a poetry expert. Identify and discuss the main themes of the following poem.",
        "t": "You are a poetry expert. Identify and discuss the main themes of the following poem.",
        "style": "You are a poetry expert. Determine the style or literary movement (e.g., Romanticism, Modernism) of the following poem, providing three reasons for your determination.",
        "st": "You are a poetry expert. Determine the style or literary movement (e.g., Romanticism, Modernism) of the following poem, providing three reasons for your determination.",
        "r": "You are a poetry expert. Determine if the following poem displays any specific end rhyme schemes (e.g., ABAB, AABB). If it does not display any, just output 'no rhyme scheme detected' .", 
        "rhyme": "You are a poetry expert. Determine if the following poem displays any specific end rhyme schemes (e.g., ABAB, AABB). If it does not display any, just output 'no rhyme scheme detected' .",
        "m": "You are a poetry expert. Determine if the following poem displays any specific meter (e.g., iambic pentameter). If it does not display any, just output 'no meter detected' .",
        "meter": "You are a poetry expert. Determine if the following poem displays any specific meter (e.g., iambic pentameter). If it does not display any, just output 'no meter detected' ."
    }

    # Validate analysis_type and get the corresponding system prompt
    system_prompt = prompts.get(analysis_type)
    if not system_prompt:
        raise ValueError(f"Invalid analysis type '{analysis_type}'. Supported types are: 'sentiment', 'themes', 'style', 's', 't', 'st'.")

    # Prepare the message payload
    system_prompt = system_prompt + (f" the name of the poem is {poem_title}")
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": poem_text}
    ]

    # Make the API call and return the response
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Switch to a more powerful model if available
            messages=messages,
            temperature=0.75,  # Adjust temperature to balance creativity and accuracy
            max_tokens=300,   # Limit the number of tokens for the response
            top_p=0.95,        # Consider the most likely outputs
            frequency_penalty=0.1,  # Adjust penalties to control repetitive outputs
            presence_penalty=0.1
        )
        return completion.choices[0].message.content.strip()  # Return the cleaned response content

    except Exception as e:
        # Handle API errors gracefully
        raise RuntimeError(f"An error occurred while analyzing the poem: {str(e)}")



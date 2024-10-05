import os
from openai import OpenAI
from dotenv import load_dotenv
import concurrent.futures
import re
import tiktoken

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

def initialize_openai_client():
    return OpenAI(api_key=api_key)

def analyze_shortstory(client, story_text, story_title, analysis_type):
    # Add this block at the beginning of the function
    max_tokens = 7500  # Set a safe limit below the 8192 maximum
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    token_count = len(encoding.encode(story_text))

    if token_count > max_tokens:
        return {
            'error': f"The submitted text is too long ({token_count} tokens). Please reduce it to approximately {max_tokens} tokens or less."
        }

    prompts = {
        "sentiment": "Analyze the sentiment of the following short story. Provide a detailed explanation of the overall mood and emotional tone, supported by specific examples from the text.",
        "themes": "Identify and analyze the main themes in the following short story. Explain how these themes are developed throughout the narrative.",
        "style": "Analyze the writing style of the following short story. Consider elements such as narrative voice, sentence structure, figurative language, and any unique stylistic choices made by the author.",
        "character": "Provide a detailed character analysis for the main characters in the following short story. Consider their development, motivations, and relationships.",
        "plot": "Analyze the plot structure of the following short story. Identify key elements such as exposition, rising action, climax, falling action, and resolution.",
        "general": "Provide a comprehensive analysis of the following short story, covering its themes, sentiment, style, character development, and plot structure. Discuss how these elements interact to create the story's overall impact and effectiveness."
    }

    system_prompt = prompts.get(analysis_type, prompts["general"])
    system_prompt += f" The title of the short story is '{story_title}' and it is provided below."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": story_text}
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        result = completion.choices[0].message.content.strip()

        # Additional analysis based on type
        if analysis_type == "sentiment":
            sentiment_score = analyze_sentiment(client, story_text)
            result += f"\n\nSentiment Score: {sentiment_score}"
        elif analysis_type == "themes":
            themes = extract_themes(client, result)
            result += f"\n\nMain Themes: {', '.join(themes)}"

    except Exception as e:
        print(f"Error in API call for short story analysis: {str(e)}")
        return {'error': "An error occurred while analyzing the short story. Please try again with a shorter text."}

    return format_analysis_result(result, analysis_type)

def analyze_sentiment(client, text):
    system_prompt = "Analyze the sentiment of the following short story. Provide a sentiment score between -1 (very negative) and 1 (very positive)."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=10
    )
    try:
        sentiment_score = float(completion.choices[0].message.content.strip())
        return round(sentiment_score, 2)
    except ValueError:
        return 0  # Default to neutral if unable to parse score

def extract_themes(client, analysis):
    system_prompt = "Extract the main themes from the following story analysis. Provide a list of 3-5 key themes, each as a short phrase."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": analysis}
    ]
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=100
    )
    themes = completion.choices[0].message.content.strip().split('\n')
    return [theme.strip() for theme in themes if theme.strip()]

def format_analysis_result(result, analysis_type):
    # Return HTML-formatted result
    return f"<h4>{analysis_type.capitalize()} Analysis</h4><p>{result}</p>"
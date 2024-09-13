import os
from openai import OpenAI
import ssl
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
    
    #functionality for king analysis
    rhyme_scheme = king_rhyme_scheme(client, poem_text)
    poem_meter = king_meter_analysis(client, poem_text)
    poem_analysis = king_theme_analysis(client, poem_text, poem_title)
    
    total = {
        "Rhyme Scheme" : rhyme_scheme,
        "Poem Meter" : poem_meter,
        "Poem Analysis" : poem_analysis
    }
    
    return total
    
        


def king_rhyme_scheme(client,poem_text):
    
    system_prompt = (
        "You are an Expert Poet. Your task is to transcribe the rhyme scheme of the given poem. "
        "Analyze the main body of the poem and output the rhyme scheme without line breaks, using '--' where line breaks may occur. "
        "The rhyme scheme should be in standard form (e.g., ABAB, AABB). "
        "If there is no detectable rhyme scheme, simply output 'No rhyme scheme detected'. "
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": poem_text}
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Use the most recent model for best results
            messages=messages,
            temperature=0.3,  # Lower temperature for more consistent output
            max_tokens=100,   # 100 tokens should be sufficient for rhyme scheme
            top_p=0.95,       # Slightly lower top_p for more focused outputs
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
        return completion.choices[0].message['content'].strip()

    except Exception as e:
        raise RuntimeError(f"An error occurred during theme analysis: {str(e)}")
    
    
def format_king_analysis(result_dict):
    """
    Formats the analysis results into a single string for easy scrolling display.

    Parameters:
    - result_dict: The dictionary containing the different parts of the analysis.
    
    Returns:
    - str: The formatted analysis as a single string.
    """
    formatted_output = (
        f"--- Rhyme Scheme ---\n{result_dict['Rhyme Scheme']}\n\n"
        f"--- Meter Analysis ---\n{result_dict['Poem Meter']}\n\n"
        f"--- Thematic Analysis ---\n{result_dict['Poem Analysis']}\n"
    )
    return formatted_output

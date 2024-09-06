import openai
import os
from example import initialize_openai_client, analyze_poem
from poems import get_poem

client = initialize_openai_client()
print("OpenAI client initialized successfully.")

poem_title, poem = get_poem("sonnet 18")
sentiment = analyze_poem(client, poem, poem_title, "sentiment")
style = analyze_poem(client, poem, poem_title,"style")
rhyme = analyze_poem(client, poem, poem_title, "r")
print(f"sentiment: {sentiment}\n \n")
print(f"style: {style}\n \n")
print(f"rhyme: {rhyme}")


import os
import json
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini Client
# Try Streamlit secrets first (for cloud deployment), then fallback to local .env
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
You are an expert podcast scriptwriter. 
Your job is to generate a highly engaging, informative, and natural-sounding conversational podcast script based on a given topic.

The podcast has two speakers:
1. "Host": The enthusiastic host who asks good questions, guides the conversation, and provides energetic commentary.
2. "Guest": The expert who provides deep insights, explains complex concepts simply, and tells interesting anecdotes.

Rules:
1. The script should be around 2-3 minutes of spoken audio (roughly 15-20 lines of dialogue total).
2. The dialogue must be natural, with 'ums', 'ahs', and conversational interruptions if it feels right. No robotic text.
3. Don't use sound effects or music cues in the dialogue text.
"""

class DialogueLine(BaseModel):
    speaker: str = Field(description="The speaker of this line (Host or Guest)")
    text: str = Field(description="The spoken dialogue text")

class PodcastScript(BaseModel):
    lines: list[DialogueLine] = Field(description="The lines of dialogue in the podcast script")

def generate_podcast_script(topic: str) -> list[dict]:
    """Generates a podcast script using Gemini."""
    
    prompt = f'Please generate a podcast script about the following topic: "{topic}"'
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=PodcastScript,
            ),
        )
        
        script_data = json.loads(response.text)
        return script_data.get("lines", [])
        
    except Exception as e:
        print(f"Error generating script: {e}")
        return []

if __name__ == "__main__":
    # Test the script generator
    test_topic = "Why Python is the best language for AI"
    print(f"Generating script for topic: '{test_topic}'...")
    script = generate_podcast_script(test_topic)
    
    print("\nGenerated Script:")
    for line in script:
         print(f"{line.get('speaker', 'Unknown')}: {line.get('text', '')}")

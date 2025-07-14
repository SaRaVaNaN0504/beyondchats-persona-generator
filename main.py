import praw
import google.generativeai as genai
import argparse
import configparser
import re
from urllib.parse import urlparse
import sys

# --- CONFIGURATION & INITIALIZATION ---

def load_config():
    """Loads API credentials from config.ini"""
    try:
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        if 'reddit' not in config or 'google' not in config:
            print("Error: Config file 'config.ini' is missing or malformed.")
            sys.exit(1)
        return config
    except Exception as e:
        print(f"Error reading config file: {e}")
        sys.exit(1)

def initialize_reddit(config):
    """Initializes and returns a PRAW Reddit instance."""
    return praw.Reddit(
        client_id=config['reddit']['client_id'],
        client_secret=config['reddit']['client_secret'],
        user_agent=config['reddit']['user_agent'],
        read_only=True
    )

# --- DATA SCRAPING ---

def extract_username_from_url(url):
    """Extracts the Reddit username from a profile URL."""
    try:
        path = urlparse(url).path
        # Expected path format: /user/username/
        parts = path.strip('/').split('/')
        
        # CORRECTED LOGIC:
        # Check if the path starts with 'user' and has a username part after it.
        if len(parts) >= 2 and parts[0] == 'user':
            return parts[1]  # Return the username, which is the second part
            
        return None # Return None if the URL format isn't what we expect
    except Exception:
        # In case of any other parsing errors, return None
        return None

def scrape_redditor_data(reddit, username, limit=100):
    """Scrapes a Redditor's recent comments and submissions."""
    print(f"Accessing Reddit API for user: {username}...")
    try:
        redditor = reddit.redditor(username)
        _ = redditor.id
    except Exception as e:
        print(f"Error: Could not find Reddit user '{username}' or user is suspended. Details: {e}")
        return None, None

    activity_data = []
    
    print("Scraping comments...")
    for comment in redditor.comments.new(limit=limit):
        activity_data.append(
            f"COMMENT (permalink: https://www.reddit.com{comment.permalink}):\n{comment.body}\n---"
        )
        
    print("Scraping posts...")
    for submission in redditor.submissions.new(limit=limit):
        activity_data.append(
            f"POST (permalink: {submission.permalink}):\nTitle: {submission.title}\nBody: {submission.selftext}\n---"
        )
        
    if not activity_data:
        return None, username

    return "\n".join(activity_data), username

# --- PERSONA GENERATION WITH LLM ---

def generate_persona(api_key, user_activity, username):
    """Uses the Google Gemini API to generate a user persona."""
    print("Sending data to the LLM for analysis...")
    genai.configure(api_key=api_key)
    # NEW, CORRECTED LINE
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = f"""
    You are a highly skilled user profiler. Your task is to create a detailed user persona based on the following Reddit activity from the user '{username}'.

    **Instructions:**
    1.  Analyze the provided text ONLY. Do not invent information.
    2.  For every characteristic you identify (interest, personality trait, etc.), you MUST cite the source by including the permalink to the post or comment that supports your finding. Format citations as: [citation: permalink_url]
    3.  If you cannot determine a piece of information, explicitly state: "Could not be determined from the provided data."
    4.  Structure the output exactly as follows:

    **Persona for User: {username}**

    **1. Executive Summary:**
    A brief, one-paragraph overview of the user.

    **2. Inferred Demographics:**
    -   **Age Range:**
    -   **Profession/Field of Study:**
    -   **Location:**

    **3. Key Interests & Hobbies:**
    -   (Bulleted list of interests)

    **4. Personality & Communication Style:**
    -   (Bulleted list of traits)

    **5. Notable Quotes:**
    -   (List 2-3 direct quotes that are highly representative)
    ---
    **Reddit Activity Data to Analyze:**
    {user_activity}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred with the AI model: {e}"

# --- MAIN SCRIPT EXECUTION ---

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description="Generate a Reddit user persona from their profile URL.")
    parser.add_argument('--url', required=True, help="The full URL of the Reddit user's profile.")
    args = parser.parse_args()

    username = extract_username_from_url(args.url)
    if not username:
        print(f"Error: Invalid Reddit user URL provided: {args.url}")
        return

    print(f"--- Starting Analysis for Reddit User: {username} ---")

    try:
        config = load_config()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return

    # 1. Scrape Data from Reddit
    print("Scraping user activity from Reddit...")
    reddit_instance = initialize_reddit(config)
    activity_data, username = scrape_redditor_data(reddit_instance, username)

    if not activity_data:
        print(f"No activity data found for user '{username}'. Cannot generate a persona.")
        return

    # 2. Generate Persona using LLM
    print("Generating persona using the LLM. This may take a moment...")
    persona_text = generate_persona(config['google']['api_key'], activity_data, username)

    # 3. Save the Output to a Text File
    output_filename = f"{username}_persona.txt"
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(persona_text)
        print(f"\n--- Success! ---")
        print(f"Persona has been saved to '{output_filename}'")
    except Exception as e:
        print(f"\nError: Could not write to file. Details: {e}")


if __name__ == '__main__':
    main()  
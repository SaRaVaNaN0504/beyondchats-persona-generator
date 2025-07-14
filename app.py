import streamlit as st
import praw
import google.generativeai as genai
import configparser
from urllib.parse import urlparse
import sys

# --- UI Styling Function ---
def set_page_style():
    """Injects custom CSS for a beautiful UI."""
    st.markdown(
        """
        <style>
        .stApp {
            background-image: linear-gradient(to right top, #d16ba5, #c777b9, #ba83ca, #aa8fd8, #9a9ae1, #8aa7ec, #79b3f4, #69bff8, #52cffe, #41dfff, #46eefa, #5ffbf1);
            background-attachment: fixed;
            background-size: cover;
        }
        [data-testid="main"] > div {
            background-color: rgba(255, 255, 255, 0.8);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Page Config & Style Application ---
st.set_page_config(
    page_title="AI Reddit Persona Generator",
    page_icon="🤖",
    layout="wide"
)
set_page_style()

# --- BACKEND FUNCTIONS ---

def load_config():
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        if 'reddit' not in config or 'google' not in config:
            st.error("Config file 'config.ini' is missing or malformed.")
            st.stop()
        return config
    except Exception as e:
        st.error(f"Error reading config file: {e}")
        st.stop()

def initialize_reddit(config):
    return praw.Reddit(
        client_id=config['reddit']['client_id'],
        client_secret=config['reddit']['client_secret'],
        user_agent=config['reddit']['user_agent'],
        read_only=True
    )

def extract_username_from_url(url):
    try:
        path = urlparse(url).path
        parts = path.strip('/').split('/')
        if len(parts) >= 2 and parts[0] == 'user':
            return parts[1]
        return None
    except Exception:
        return None

def scrape_redditor_data(reddit, username, limit=50):
    try:
        redditor = reddit.redditor(username)
        _ = redditor.id
    except Exception:
        return None, f"Error: Could not find Reddit user '{username}' or user is suspended."
    activity_data = []
    try:
        comments = list(redditor.comments.new(limit=limit))
        if not comments:
            comments = list(redditor.comments.top('all', limit=limit))
        for comment in comments:
            activity_data.append(f"COMMENT (permalink: https://www.reddit.com{comment.permalink}):\n{comment.body}\n---")
    except Exception as e:
        st.warning(f"Could not fetch comments: {e}")
    try:
        submissions = list(redditor.submissions.new(limit=25))
        if not submissions:
            submissions = list(redditor.submissions.top('all', limit=25))
        for submission in submissions:
            activity_data.append(f"POST (permalink: {submission.permalink}):\nTitle: {submission.title}\nBody: {submission.selftext}\n---")
    except Exception as e:
        st.warning(f"Could not fetch posts: {e}")
    if not activity_data:
        return None, f"No public activity could be retrieved for user '{username}'. The user may have no posts/comments, or their activity may be restricted from the API."
    return "\n".join(activity_data), None

# --- THIS IS THE CORRECTED FUNCTION ---
def generate_persona(api_key, user_activity, username):
    """Uses the Google Gemini API to generate a user persona."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # THE FULL, COMPLETE PROMPT IS RESTORED HERE
    prompt = f"""
    You are a highly skilled user profiler. Your task is to create a detailed user persona based on the following collection of Reddit posts and comments from the user '{username}'.
    Analyze the text provided and construct a persona that includes the sections outlined below.

    **CRITICAL INSTRUCTIONS:**
    1.  Base your entire analysis *only* on the text provided below. Do not invent information.
    2.  For every single point you make (each interest, personality trait, etc.), you MUST provide a "citation" by including the permalink to the exact comment or post that supports your conclusion.
    3.  Format the citation like this at the end of the sentence: [citation: permalink_url]
    4.  If you cannot reasonably infer a piece of information, you must state: "Could not be determined from the provided data."
    5.  The entire output must be in Markdown format.

    **PERSONA STRUCTURE:**

    ### 1. Executive Summary
    A brief, one-paragraph overview of the user, their main interests, and their typical online behavior.

    ### 2. Inferred Demographics
    -   **Age Range:** (e.g., 20-25, 30-40, etc.)
    -   **Profession/Field of Study:** (e.g., Software Development, Student, Healthcare)
    -   **Location:** (e.g., India, USA, etc. Be as specific as the data allows)

    ### 3. Key Interests & Hobbies
    A bulleted list of their primary interests, such as technology, specific games, TV shows, etc.

    ### 4. Personality & Communication Style
    A bulleted list describing their personality traits and how they communicate.

    ---
    **Reddit Activity Data for '{username}' to Analyze:**

    {user_activity}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred with the AI model: {e}"

# --- STREAMLIT UI ---

col1, col2 = st.columns([1, 10])
with col1:
    st.image('reddit_logo.png', width=80)
with col2:
    st.title("AI Reddit Persona Generator")
    st.subheader("Generate an AI-powered persona from a Reddit user's profile")

st.divider()

st.write("Simply paste a Reddit user's full profile URL below and click 'Generate'.")

with st.expander("Click here to see example URLs"):
    st.code("https://www.reddit.com/user/kojied/")
    st.code("https://www.reddit.com/user/Hungry-Move-6603/")
    st.code("https://www.reddit.com/user/thisisbillgates/")

url = st.text_input("Enter Reddit Profile URL", placeholder="https://www.reddit.com/user/...", label_visibility="collapsed")

if st.button("✨ Generate Persona", type="primary"):
    if url:
        username = extract_username_from_url(url)
        if not username:
            st.error("Invalid Reddit URL. Please use the full profile URL format.", icon="🚨")
        else:
            with st.spinner(f"🔍 Accessing Reddit API for '{username}'..."):
                config = load_config()
                reddit_instance = initialize_reddit(config)
                google_api_key = config['google']['api_key']
                activity, error_msg = scrape_redditor_data(reddit_instance, username)

            if error_msg:
                st.error(error_msg, icon="🔥")
            else:
                with st.spinner(f"🤖 AI is building the persona for '{username}'..."):
                    persona_text = generate_persona(google_api_key, activity, username)
                
                st.success("Persona Generated!", icon="✅")
                
                with st.container(border=True):
                    st.markdown(persona_text)
                
                st.download_button(
                    label="Download Persona as Text File",
                    data=persona_text,
                    file_name=f"{username}_persona.txt",
                    mime="text/plain"
                )
    else:
        st.warning("Please enter a URL to get started.", icon="👋")
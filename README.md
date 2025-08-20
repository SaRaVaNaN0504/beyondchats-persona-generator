# AI Reddit Persona Generator

This project, is a web application that generates a detailed user persona from a Reddit profile URL using AI.

**Live Demo:** [https://beyondchats-persona-generator-5aivb7xzapefyredk4wwdh.streamlit.app/]

## Features

-   Scrapes recent user activity (posts & comments) using the Reddit API.
-   Handles difficult-to-scrape profiles by trying multiple methods.
-   Uses Google's Gemini LLM to analyze text and infer characteristics.
-   Cites every piece of information with a permalink to the source.
-   Features two interfaces: a command-line script and a user-friendly web app.

## Project Structure

-   `main.py`: The original command-line script.
-   `app.py`: The Streamlit web application.
-   `requirements.txt`: Project dependencies.
-   `config.ini`: (Local only) For storing API keys.
-   `*.txt`: Sample output files as required by the assignment.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd reddit-persona-generator
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Create `config.ini`:** Create this file in the root directory and add your API keys:
    ```ini
    [reddit]
    client_id = YOUR_REDDIT_CLIENT_ID
    client_secret = YOUR_REDDIT_CLIENT_SECRET
    user_agent = persona_script by u/your_username

    [google]
    api_key = YOUR_GOOGLE_API_KEY
    ```

## How to Run

### 1. Web Application (Recommended)

To run the user-friendly web interface, use the following command:

```bash
streamlit run app.py
```

### 2. Command-Line Script

To use the original script, run `main.py` with the `--url` argument:

```bash
python main.py --url https://www.reddit.com/user/kojied/
```
This will generate a `SaRaVaNaN0504_persona.txt` file in the project directory.

### OUTPUT

<img width="100%" alt="image" src="https://github.com/user-attachments/assets/299a5aeb-83ac-4075-bebb-547225f155a6" />

```

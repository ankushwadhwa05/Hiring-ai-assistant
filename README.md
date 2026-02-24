
# AI Hiring Assistant

## Project Overview
The AI Hiring Assistant is an intelligent, conversational AI chatbot designed for a fictional recruitment agency specializing in technology placements. Built to handle the initial screening of candidates, the bot dynamically gathers essential biographical data before seamlessly pivoting to conduct a customized technical assessment based strictly on the candidate's declared tech stack. 

## Features
* **Dynamic Conversation Flow:** Transitions intelligently from data collection to technical screening.
* **Real-Time Sentiment Analysis:** Analyzes candidate responses using TextBlob to display their emotional tone (Positive, Negative, Neutral) on a recruiter dashboard.
* **Multilingual Support:** Capable of conducting the interview in multiple languages (English, Spanish, French, German, Hindi, Mandarin) while retaining context.
* **Simulated Database Integration:** Automatically saves the completed interview transcript and sentiment score to a local JSON file (`simulated_backend_db.json`) upon completion.
* **Graceful Exit Mechanisms:** Recognizes conversation-ending keywords and exits the process securely.

## Installation Instructions

1. **Clone the repository:**
   ```bash
   git clone <https://github.com/ankushwadhwa05/Hiring-ai-assistant>

    ```

2. **Create a virtual environment (optional but recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```


3. **Install the required dependencies:**
```bash
pip install -r requirements.txt

```


4. **Environment Variables:**
Create a `.env` file in the root directory and add your Google Gemini API key:
```bash
GEMINI_API_KEY="your_actual_api_key_here"

```


*(Ensure this file is saved with UTF-8 encoding).*

## Usage Guide

To launch the application locally, run the following command in your terminal:

```bash
streamlit run app2.py

```

This will open the application in your default web browser. Use the sidebar to configure the language, and interact with the chatbot in the main window. Type "exit" or "quit" at any time to terminate the interview and save the session data.

## Technical Details

* **Frontend/UI:** Streamlit (Python)
* **LLM Engine:** Google Gemini 2.5 Flash via `google-genai` SDK
* **Sentiment Analysis:** TextBlob
* **State Management:** Streamlit Session State (`st.session_state`) is heavily utilized to maintain conversation history, track the current phase of the interview (greeting, gathering, tech_questions, ended), and retain extracted user data across Streamlit's reruns.
* **Data Storage:** A custom Python function serializes the chat history and final sentiment into a simulated JSON backend.

## Prompt Design

The core intelligence of the app relies on a dynamic System Prompt that updates based on the state of the conversation.

1. **Information Gathering Phase:** The prompt instructs the LLM to adopt a professional recruiter persona and sequentially collect 7 specific data points (Name, Email, Phone, Experience, Position, Location, Tech Stack). It is strictly instructed to append a specific flag (`TRANSITION_TO_TECH`) only when all fields are populated.
2. **Technical Assessment Phase:** Once triggered by the flag, the prompt dynamically updates to instruct the LLM to generate 3-5 technical questions based *only* on the previously declared tech stack, acting as a technical interviewer.

## Challenges & Solutions

* **Challenge:** Maintaining conversation context while utilizing Streamlit's top-down execution model, which resets variables on every user input.
* **Solution:** Leveraged `st.session_state` to store the entire array of message dictionaries. This array is passed to the Gemini API on every call, ensuring the LLM always has the full context of the candidate's answers.


* **Challenge:** Preventing the LLM from answering technical questions *for* the user if prompted.
* **Solution:** Implemented strict guardrails within the System Prompt, explicitly commanding the model to refuse to answer coding queries and to forcefully redirect off-topic users back to the interview flow.



---

*Developed by Ankush Wadhwa*

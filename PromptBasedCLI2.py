import subprocess
import logging
import re
import streamlit 

# Setup logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ollama_chat.log"),
        logging.StreamHandler()
    ]
)

# Regex to remove ANSI escape codes
ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')



def ask_ollama(prompt, model="llama3"):
    try:
        logging.info(f"Running ollama with model '{model}' and prompt: {prompt}")
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            response = result.stdout.strip()
            logging.info(f"Response: {response}")
            return response
        else:
            error_msg = result.stderr.strip()
            logging.error(f"Ollama error: {error_msg}")
            return f"Error running Ollama:\n{error_msg}"
    except FileNotFoundError:
        return "Ollama is not installed or not in PATH."
    except subprocess.CalledProcessError as e:
        return f"A system error occurred:\n{e}"
        
def list_ollama_models():
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            print("Available Ollama models:\n" + output + "\n")

            lines = [ansi_escape.sub('', line) for line in output.splitlines()]
            models = [line.strip().split()[0].lower() for line in lines[1:] if line.strip()]
            print("DEBUG: Cleaned model names:", models)
            return models
        else:
            streamlit.error("Error listing models:\n" + result.stderr.strip())
            return []
    except FileNotFoundError:
        streamlit.error("Ollama is not installed or not in PATH.")
        return []




#Streamlit UI
streamlit.title("Ollama Chatbot with CLI interface")

models = list_ollama_models()
if not models:
    models = ["llama3"] #fallback if listing fails

user_input = streamlit.text_area("Type your message here:", height=100)
model = streamlit.selectbox("Choose a model:", models)

if "response" not in streamlit.session_state:
    streamlit.session_state.response = ""

if streamlit.button("Ask"):
    if user_input.strip():
        with streamlit.spinner("Thinking..."):
            streamlit.session_state.response = ask_ollama(user_input, model=model)
    else:
        streamlit.warning("Please type a prompt before clicking Ask.")

if streamlit.session_state.response:
    streamlit.markdown("Response")
    streamlit.write(streamlit.session_state.response)


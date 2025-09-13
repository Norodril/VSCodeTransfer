import streamlit as st
import subprocess

personalities = {
    "nice": "You're a helpful and friendly, be nice.",
    "professional": "You're a concise and highly professional assistant.",
    "funny": "You're a witty and sarcastic assistant. Make sure to be funny.",
}

def run_ollama(prompt, system_msg):
    full_prompt = f"<|system|>\n{system_msg}\n<|user|>\n{prompt}\n<|assistant|>\n"
    ##Json format (system and user prompt)
    result = subprocess.run(
        ["ollama", "run", "llama3", full_prompt],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

st.set_page_config(page_title="Ollama Chatbot", layout="centered")
st.title("Custom Chatbot")

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    selected_personality = st.selectbox("Choose a personality", list(personalities.keys()))
    st.markdown("Chatbot will reply based on the selected style.")

user_input = st.text_input("Ask a question:", key="input")

if st.button("Send"):
    if user_input.strip() != "":
        # Show thinking spinner
        with st.spinner("Thinking..."):
            system_msg = personalities[selected_personality]
            reply = run_ollama(user_input, system_msg)

            # Save chat history
            st.session_state.history.append(("You", user_input))
            st.session_state.history.append((selected_personality + " Bot", reply))

st.markdown("Chat History")
for sender, msg in st.session_state.history:
    st.markdown(f"**{sender}:** {msg}")
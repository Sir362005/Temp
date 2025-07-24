import streamlit as st
import requests

# Set Streamlit page config
st.set_page_config(page_title="Hugging Face Chatbot", page_icon="🤖")

st.title("🤖 Hugging Face Chatbot")
st.markdown("Chat with various LLMs hosted on Hugging Face")

# Model options
MODEL_OPTIONS = {
    "LLaMA 2 (Meta)": "meta-llama/Llama-2-7b-chat-hf",
    "Mistral 7B": "mistralai/Mistral-7B-Instruct-v0.1",
    "Mixtral 8x7B": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "Zephyr 7B": "HuggingFaceH4/zephyr-7b-alpha",
    "Phi-2": "microsoft/phi-2",
    "Command-R": "CohereForAI/c4ai-command-r-v01"
}

# Hugging Face API token (via Streamlit Secrets)
API_URL_BASE = "https://api-inference.huggingface.co/models/"
headers = {
    "Authorization": f"Bearer {st.secrets['hf_token']}"
}

# Sidebar - Model Selection
selected_model = st.sidebar.selectbox("Select a model:", list(MODEL_OPTIONS.keys()))

# Session State for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.text_input("You:", key="input")

# Display chat history
for msg in st.session_state.chat_history:
    st.markdown(f"**{msg['role'].capitalize()}:** {msg['text']}")

# On Send
if st.button("Send"):
    if user_input:
        # Append user message
        st.session_state.chat_history.append({"role": "user", "text": user_input})

        with st.spinner("Thinking..."):
            # Construct payload for Hugging Face Inference API
            payload = {
                "inputs": f"{user_input}",
                "parameters": {"max_new_tokens": 100, "temperature": 0.7},
            }

            model_id = MODEL_OPTIONS[selected_model]
            response = requests.post(API_URL_BASE + model_id, headers=headers, json=payload)

            if response.status_code == 200:
                try:
                    result = response.json()
                    # Handle both formats: string or list of generated_text
                    bot_output = result[0]["generated_text"] if isinstance(result, list) else result.get("generated_text", "")
                except Exception:
                    bot_output = "⚠️ Could not parse model response."
            else:
                bot_output = f"⚠️ Error: {response.status_code} — {response.text}"

        # Append bot response
        st.session_state.chat_history.append({"role": "bot", "text": bot_output})
        st.experimental_rerun()

import streamlit as st
import requests

# Set Streamlit page config
st.set_page_config(page_title="🤖 Hugging Face Chatbot", page_icon="🤖")

st.title("🤖 Hugging Face Chatbot")
st.markdown("Chat with various LLMs hosted on Hugging Face")

# Supported models
MODEL_OPTIONS = {
    "Mistral 7B": "mistralai/Mistral-7B-Instruct-v0.1",
    "Mixtral 8x7B": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "Zephyr 7B": "HuggingFaceH4/zephyr-7b-alpha",
    "Phi-2": "microsoft/phi-2",
    "Command-R": "CohereForAI/c4ai-command-r-v01",
    "Falcon 7B": "tiiuae/falcon-7b-instruct"
}

# Sidebar: model selection
selected_model = st.sidebar.selectbox("Choose a model:", list(MODEL_OPTIONS.keys()))

# Hugging Face API setup
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_OPTIONS[selected_model]}"
HEADERS = {"Authorization": f"Bearer {st.secrets['hf_token']}"}

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["text"])

# Get user input
user_input = st.chat_input("Ask something...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "text": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            payload = {
                "inputs": user_input,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7
                }
            }

            response = requests.post(API_URL, headers=HEADERS, json=payload)

            if response.status_code == 200:
                try:
                    result = response.json()
                    if isinstance(result, list) and "generated_text" in result[0]:
                        reply = result[0]["generated_text"]
                    elif "generated_text" in result:
                        reply = result["generated_text"]
                    elif "outputs" in result:
                        reply = result["outputs"]
                    else:
                        reply = str(result)
                except Exception:
                    reply = "⚠️ Could not parse model response."
            else:
                reply = f"⚠️ Error: {response.status_code} — {response.text}"

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "text": reply})

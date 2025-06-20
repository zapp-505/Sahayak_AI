import os
from dotenv import load_dotenv
import streamlit as st
from langchain_community.chat_message_histories import ChatMessageHistory
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

# System prompt
SYSTEM_PROMPT = """You are a helpful assistant specialized in guiding elderly people in Kerala through administrative and government procedures.

Your expertise includes:
- Panchayat and village office procedures
- Banking services and requirements
- Government documentation (certificates, applications, pensions)
- Healthcare and insurance paperwork
- Property and tax-related documentation

IMPORTANT: Always respond in Malayalam language only. Use simple Malayalam that is easy for elderly people to understand.

When responding:
1. Use simple, clear Malayalam language avoiding technical jargon
2. Provide step-by-step instructions when explaining procedures
3. ALWAYS list required documents in a separate section with this exact heading: "ആവശ്യമായ രേഖകൾ:" (Required Documents:)
4. Format each document as a bullet point using "•" symbols
5. Include keywords "രേഖകൾ" or "ഡോക്യുമെന്റ്" in the document section
6. Be patient and thorough in your explanations

For example, when listing documents, format them like this:

ആവശ്യമായ രേഖകൾ:
• ആധാർ കാർഡ്
• റേഷൻ കാർഡ്
• വോട്ടർ ഐഡി

Your goal is to make complex bureaucratic processes accessible and understandable for elderly citizens who may not be familiar with digital systems or current procedures in Kerala. Always respond in Malayalam even if the query is in English."""

# Initialize chat history in Streamlit's session state
# This is how Streamlit manages state across reruns
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatMessageHistory()

st.title("Kerala Administrative Assistant")
st.write("Feel free to ask if you need any help with government procedures in Kerala.")

# Display chat messages from history
for msg in st.session_state.chat_history.messages:
    if msg.type == "human":
        st.chat_message("user").write(msg.content)
    elif msg.type == "ai":
        st.chat_message("assistant").write(msg.content)

# Input for new messages
user_query = st.chat_input("Type your question here...")

if user_query:
    # Add user message to history
    st.session_state.chat_history.add_user_message(user_query)
    st.chat_message("user").write(user_query)

    # Construct prompt for Gemini
    full_prompt = SYSTEM_PROMPT + "\n\n"
    for msg in st.session_state.chat_history.messages:
        role = "User" if msg.type == "human" else "Assistant"
        full_prompt += f"{role}: {msg.content}\n"
    # Add the current user query to the prompt for Gemini
    full_prompt += f"User: {user_query}\nAssistant:"


    try:
        # Generate Gemini response
        with st.spinner("Finding answer..."):
            response = gemini_model.generate_content(full_prompt)
            ai_response = response.text

        # Add AI message to history
        st.session_state.chat_history.add_ai_message(ai_response)
        st.chat_message("assistant").write(ai_response)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        # Optionally remove the last user message if the AI failed to respond
        # st.session_state.chat_history.messages.pop()
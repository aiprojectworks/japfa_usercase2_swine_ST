import streamlit as st
from openai import OpenAI
import os




# Initialize OpenAI client with API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Replace with your actual assistant ID
assistant_id = st.secrets["ASSISTANT_ID"]

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to create a thread and run the assistant
def run_assistant(user_input):
    # Create a new thread for each conversation
    thread = client.beta.threads.create()

    # Add the user's message to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )

    # Run the assistant on the thread
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )
    
    # Wait for the run to complete
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Retrieve assistant's messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    assistant_messages = [msg for msg in messages.data if msg.role == "assistant"]

    # Return the assistant's latest response
    return assistant_messages[0].content[0].text.value

# Streamlit UI
st.title("Japfa Swine Info Query")

# Initialize input value in session state if not exists
if "input_value" not in st.session_state:
    st.session_state.input_value = ""

# User input
user_input = st.text_input("You:", value=st.session_state.input_value, key="user_input")

# Handle user input and display chat history
if st.button("Send"):
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get assistant's response
        assistant_response = run_assistant(user_input)
        
        # Add assistant message to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
        
        # Clear input by updating session state
        st.session_state.input_value = ""
        st.rerun()

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])
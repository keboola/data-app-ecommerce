import streamlit as st
import openai
import json
import time
from typing import List
from tempfile import gettempdir
from PIL import Image
from io import BytesIO
import os
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock
import pandas as pd

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

session_defaults = {
    "messages": [],
}
for key, value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

def get_file_ids_from_csv(file_path: str) -> List[str]:
    """Read file IDs from a CSV file."""
    df = pd.read_csv(file_path)
    return df['file_id'].tolist()

st.markdown(
    """
    <div style="display: flex; align-items: center;">
        <img src="https://assets-global.website-files.com/5e21dc6f4c5acf29c35bb32c/5e21e66410e34945f7f25add_Keboola_logo.svg" alt="Keboola Logo" style="height: 55px; margin-right: 15px;">
        <h1 style="margin: 0;">E-commerce Chatbot</h1>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("""---""")
col1, col2, col3, col4, col5,col6 = st.columns(6)

if st.sidebar.button("Clear Chat", type="tertiary"):
    st.session_state.messages = []
    if "thread_id" in st.session_state:
        del st.session_state.thread_id
    st.rerun()

st.markdown("""
<style>
.chat-message {
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
}

.chat-message.user {
    background-color: #f0f2f6;
}

.chat-message .message-content {
    display: flex;
    margin-bottom: 0.5rem;
}

.chat-message .avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin-right: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

.chat-message.user .avatar {
    background-color: #f0f2f6;
    color: white;
}

.chat-message .content {
    flex-grow: 1;
}
</style>
""", unsafe_allow_html=True)

def initialize_assistant() -> str:
    """Initialize or retrieve the assistant ID."""
    if "assistant_id" not in st.session_state:
        st.session_state.assistant_id = st.secrets["ASSISTANT_ID"]
    return st.session_state.assistant_id

def create_thread(file_ids: List[str]) -> str:
    """Create a new thread or retrieve existing thread ID."""
    if "thread_id" not in st.session_state:
        attachments = [{"file_id": file_id, "tools": [{"type": "code_interpreter"}]} for file_id in file_ids]
        
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": ("""
                        To help you navigate the CSV files you're working with, find the description of tables and columns in the DatabaseSchema.txt file.
                        """             
                    ),
                    "attachments": attachments
                }
            ]
        )
        st.session_state.thread_id = thread.id
    return st.session_state.thread_id
assistant_id = initialize_assistant()
file_ids = get_file_ids_from_csv('/data/in/tables/file_upload_data_app.csv')
thread_id = create_thread(file_ids)

for message in st.session_state.messages:
        if message["role"] == "user":
            avatar = '🧑‍💻'
        else:
            avatar = 'https://components.keboola.com/images/default-app-icon.png'
        
        with st.chat_message(message["role"], avatar=avatar):
            if "[Image:" in message["content"]:
                start_index = message["content"].find("[Image:") + len("[Image: ")
                end_index = message["content"].find("]", start_index)
                image_path = message["content"][start_index:end_index]
                st.image(image_path)
                
                text_content = message["content"][:start_index - len("[Image: ")] + message["content"][end_index + 1:]
                st.markdown(text_content)
            else:
                st.markdown(message["content"])

if prompt := st.chat_input("How can I help you?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar='🧑‍💻'):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar='https://components.keboola.com/images/default-app-icon.png'):
        # Create a placeholder for the assistant's response
        message_placeholder = st.empty()
        assistant_reply = ""

        # Create the message in the thread
        thread_message = client.beta.threads.messages.create(
            st.session_state.thread_id,
            role="user",
            content=prompt,
        )

        # Create a streaming run
        stream = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            stream=True
        )

        # Process the streaming response
        for event in stream:
            if isinstance(event, ThreadMessageDelta):
                if isinstance(event.data.delta.content[0], TextDeltaBlock):
                    # Clear the placeholder
                    message_placeholder.empty()
                    
                    # Add the new text
                    assistant_reply += event.data.delta.content[0].text.value
                    
                    # Display the updated text
                    message_placeholder.markdown(assistant_reply)

        # After streaming is complete, process any images
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )
        newest_message = messages.data[0]
        complete_message_content = assistant_reply

        for message_content in newest_message.content:
            if hasattr(message_content, "image_file"):
                file_id = message_content.image_file.file_id
                resp = client.files.with_raw_response.retrieve_content(file_id)
                
                if resp.status_code == 200:
                    image_data = BytesIO(resp.content)
                    img = Image.open(image_data)
                    
                    temp_dir = gettempdir()
                    image_path = os.path.join(temp_dir, f"{file_id}.png")
                    img.save(image_path)
                    
                    st.image(img)
                    complete_message_content += f"[Image: {image_path}]\n"

        # Store the complete message in session state
        st.session_state.messages.append({"role": "assistant", "content": complete_message_content})
import streamlit as st
import openai
import json
import time
from typing import List
from tempfile import gettempdir
from PIL import Image
from io import BytesIO
import os
# Initialize the OpenAI client
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

session_defaults = {
    "messages": [],
}
for key, value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Custom styling
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
# Add a clear chat button
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

# Initialize the assistant and thread
assistant_id = initialize_assistant()
file_ids = ["file-EYg1ZpzZZvyYXs6dX7adYP", 
            "file-R9YjDKAD55HiaFyHD6sFCM", 
            "file-36UWTpzuCNaRT7HJrE3rLD",
            "file-M37FK1HCDppQH1pjMiE1XS",
            "file-B7cV47tcEC8zwMKESSgXdt",
            "file-6erWmfWa1ccRvqmSBKLAkU",
            "file-9f6PGtnnuU8DY5JKFqbGKn",
            "file-Edv5kNxWWU3jLZ3XrsVmhx",
            "file-JZhgddcDk1RsGHn2enNxSg",
           # "file-BSHtSKigyhUJWXswtN9z7o",
           # "file-5v8aJnkvypyxXb5EBQ81xk",
           # "file-6TiB1V1E2mBaYrFXp1toNm",
           # "file-Ngre85rrQfkfvTdTRxjEkX",
           # "file-B7CphxcmSqohmtvzvqhxry",
           # "file-4ufkyD1E8tQrTJ28bk7hTn",
           # "file-NAbxmN279paKeecAQNBDdR",
           # "file-SW4zyVrngnf8EEdznAUHbR",
           # "file-M2GPPDpTxWnTfpfoNLXqzQ",
           # "file-2UoffjUnDL48jJXG3K1rw6",
           # "file-5cW7o4HRU9BSfbNURfRXzP",
          #  "file-CJdDErXGWruvQLdQCvhWTo",
          #  "file-XRD7nm7vC8hhxirx7nXYcB",
          #  "file-XP5cMEeKbBbf4Xopediwda"
            ]  # Replace with your actual file IDs
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

    with st.spinner('🤖 Analyzing, please wait...'):  
        thread_message = client.beta.threads.messages.create(
            st.session_state.thread_id,
            role="user",
            content=prompt,
        )
        run = client.beta.threads.runs.create_and_poll(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
        )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )
        newest_message = messages.data[0]
        complete_message_content = ""
        with st.chat_message("assistant", avatar='🤖'):
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

                elif hasattr(message_content, "text"):
                    text = message_content.text.value
                    st.markdown(text)
                    complete_message_content += text + "\n"

        st.session_state.messages.append({"role": "assistant", "content": complete_message_content})

    else:
        st.write(f"Run status: {run.status}")
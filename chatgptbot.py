import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
  SystemMessage,
  HumanMessage,
  AIMessage
)
from PyPDF2 import PdfReader
from streamlit_lottie import st_lottie
from streamlit_pills import pills

OPENAI_API_KEY = "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"
def init():
    load_dotenv()

    if os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "":
        print("OPEN AI KEY is not set")
        exit(1)
    else:
        print("OPEN AI KEY is set")

    st.set_page_config(
        page_title="Your own Chatgpt",
        page_icon=""
    )

def main():
    init()


    chat = ChatOpenAI(openai_api_key=OPENAI_API_KEY,temperature=0.7)

    messages = [
        SystemMessage(content="You are a helpful assistant")
    ]

    st.header(":violet[*Meet*] :orange[*Robocop*] :violet[*, Your Chat Buddy!*] :robot_face:")

    # message("Hello, how are you?")
    # message("I am good", is_user=True)

    with st.sidebar:
        st_lottie("https://lottie.host/10971ba6-d563-462f-92a7-de6b74dbb32e/LQDYRX5RvC.json")
        user_input = st.text_input("Your message: ", key="user_input")
        file_type = st.radio(
            "Choose a document to upload:",
            ["PDF", "Email"])
        file = st.file_uploader("Upload a File and start asking questions", type=None)
        if file:
            options = ["Summarize PDF", "Categorize Email", "Show Data"]
            selection = pills("Directions", options)
            # st.markdown(f"Your selected options: {selection}.")

    if user_input:
        message(user_input, is_user=True)
        messages.append(HumanMessage(content=user_input))
        chat(messages)
        response = chat(messages)
        message(response.content,is_user=False)

if __name__ == "__main__":
    main()




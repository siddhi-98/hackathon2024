import streamlit as st
from streamlit_chat import message
# from dotenv import load_dotenv
import os
# from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import (
  SystemMessage,
  HumanMessage,
  AIMessage
)
from PyPDF2 import PdfReader
from streamlit_lottie import st_lottie
from streamlit_pills import pills
import openai



# OPENAI_API_KEY = "3e0d2321a0624ff4934c66ee7210ca56"
openai.api_type = "azure"
openai.api_base = "https://genai-openai-datawarriors.openai.azure.com/"
openai.api_key = "3e0d2321a0624ff4934c66ee7210ca56"


def init(self,data=None):

    st.set_page_config(
        page_title="Your own Chatgpt",
        page_icon=""
    )

def main(self):
    init(self)


    # chat = ChatOpenAI(openai_api_key=OPENAI_API_KEY,temperature=0.7)
    message_text = [{"role":"system", "content":"You are a helpful AI assistant."}]

    messages = [
        SystemMessage(content="You are a helpful assistant")
    ]

    completion = openai.ChatCompletion.create(
        engine="gpt-35-turbo",
        messages=message_text,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
    )

    print(completion)
    # st.header(":violet[*Meet*] :orange[*Robocop*] :violet[*, Your Chat Buddy!*] :robot_face:")

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
        # chat(messages)
        # response = chat(messages)
        # message(response.content,is_user=False)

if __name__ == "__main__":
    main(self=main)

import streamlit as st
from streamlit_chat import message
import tempfile
import os
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
import PyPDF2
from PyPDF2 import PdfReader
from streamlit_lottie import st_lottie
from streamlit_pills import pills
import openai
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import json
import base64

from test_payload import payload

# Set your Azure OpenAI API key and endpoint
openai.api_type = "azure"
openai.api_base = "https://genai-openai-datawarriors.openai.azure.com/"
openai.api_key = "3e0d2321a0624ff4934c66ee7210ca56"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False


def login():
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "Harshit" and password == "harshit@321":  # Replace with your authentication logic
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")


def init():
    st.set_page_config(
        page_title="PLUTO",
        page_icon=""
    )


def display_messages():
    for message in st.session_state.messages:
        if "```json" in message['content']:
            message['content'] = str.replace(message['content'], "```json", "")
        # json_data = json.loads(message['content'])
        # message['content'] = json.dumps(message['content'],indent=4)
        st.markdown(f"**{message['role']}**: {message['content']}")


def display_json_messages():
    for message in st.session_state.messages:
        st.markdown(f"**{message['role']}**: {json.loads(message['content'])}")


def download_pdf_from_blob(container_name, blob_name, download_path):
    container_client = BlobServiceClient.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    with open(download_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())


def extract_text_from_pdf(pdf_path):
    pdf_text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            pdf_text += page.extract_text()
    print(pdf_text)
    return pdf_text


def process_input_file(text, ops_selection):
    # user_input = st.session_state.user_input
    if ops_selection == "CLM OPS":
        user_content =f"With reference to use case 3 this is the content:\n\n{text}"
    else:
        user_content = f"Extract the relevant fields from this text:\n\n{text}"
    payload = {
        "messages": [

            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        #"text": "You are a GenAI Super Assistant for a bank's operations team helping them with a number of use cases, specifically focusing on the following:\n\nInstructions:\n\nUse Case 1: Credit Operations email categorization, assignment and response generation.\nCategorize Emails:\nAnalyze the content of incoming emails.\nCategorize each email into one of the predefined categories (e.g., Billing, Projects, Support).\nFurther subcategorize the email for more detailed classification (e.g., Overdue Invoice, New Proposal).\nAssign Emails:\nUse a skill matrix to determine the best team member to handle each email.\nAssign the email to the appropriate person based on their skills and availability.\nGenerate Actions and Responses:\nIdentify the actions required to address the email’s content.\nGenerate a response email\nAlso generate the final response email informing the requestor about the completion of the request\n\nUse Case 2: Information extraction from onboarding form\nExtract the following fields: Full Name, Date of Birth, Nationality, Address, City, State/Province, Postal Code, Country, Phone Number, Email Address, Proof of Identity, Proof of Address, Annual Income, Net Worth, Source of Funds\nValidate that the information in the fields is functionally relevant and display a message if successful else a failure\nReturn the output in a json format\n\nContext:\n\nFor Use Case 1:\nCategories and Subcategories:\nBilling: Overdue Invoice, Payment Confirmation, Billing Inquiry\nProjects: New Proposal, Project Update, Project Inquiry\nSupport: Technical Issue, Account Issue, General Inquiry\nSkill Matrix:\nAlice: Billing (Overdue Invoice, Payment Confirmation)\nBob: Projects (New Proposal, Project Update)\nCharles: Support (Technical Issue, Account Issue)\nExample Prompts and Completions:\nPrompt: “Categorize the following email: ‘Subject: Invoice overdue\\nBody: Please pay the overdue invoice.’”\nCompletion: “Category: Billing\\nSubcategory: Overdue Invoice”\nPrompt: “Assign the following email: ‘Category: Billing\\nSubcategory: Overdue Invoice’”\nCompletion: “Assigned to: Alice”\nPrompt: “Generate a response for the following email: ‘Subject: Invoice overdue\\nBody: Please pay the overdue invoice.’ Actions: Review invoice, Send payment reminder”\nCompletion: “Dear [Requestor],\\n\\nWe have reviewed your invoice and sent a payment reminder. Your request has been completed.\\n\\nBest regards,\\n[Your Company\n\nUse Case 2:Please ensure that you refer to the latest data for information retrieval. The fields extracted should reflect the data from the user and nothing should be assumed.Please don't infer any information and treat the text as it is.]”"
                        #"test": "You are a GenAI Super Assistant for a bank's operations team helping them with a number of use cases, specifically focusing on the following:\n \nInstructions:\n\nUse Case 1: Credit Operations email categorization, assignment and response generation. \nCategorize Emails:\nAnalyze the content of incoming emails.\nCategorize each email into one of the predefined categories (e.g., Billing, Projects, Support).\nFurther subcategorize the email for more detailed classification (e.g., Overdue Invoice, New Proposal).\nAssign Emails:\nUse a skill matrix to determine the best team member to handle each email.\nAssign the email to the appropriate person based on their skills and availability.\nGenerate Actions and Responses:\nIdentify the actions required to address the email’s content.\nGenerate a response email\nAlso generate the final response email informing the requestor about the completion of the request\n\nUse Case 2: Information extraction from onboarding form given the content of the form is provided.\nExtract the following fields: Full Name, Date of Birth, Nationality, Address, City, State/Province, Postal Code, Country, Phone Number, Email Address, Proof of Identity, Proof of Address, Annual Income, Net Worth, Source of Funds\nValidate that the information in the fields is functionally relevant and display a message if successful else a failure.\nAlways return the fields output in a json format. The information should be inferred as it is present in the input, and nothing should be assumed. \n\nUse Case 3:\nAnalyze the content of incoming data and documents and if you find any of the following listed restricted country related information.\nRestricted country list is ( North Korea, Iran, Syria, Cuba, Venezuela, Crimea Region (Ukraine), Sudan (North and South), Myanmar (Burma), Afghanistan, Belarus, Burundi, Central African Republic, Democratic Republic of the Congo, Mali, Nicaragua, Russia, Somalia, South Sudan, Egypt, Guinea, Guinea-Bissau, Iraq, Lebanon, Libya, Tunisia, Ukraine, Yemen, Zimbabwe).\nIf you find any of the above listed restricted country related information highlight either in bold or red color.\n \nContext:\n \nFor Use Case 1:\nCategories and Subcategories:\nBilling: Overdue Invoice, Payment Confirmation, Billing Inquiry\nProjects: New Proposal, Project Update, Project Inquiry\nSupport: Technical Issue, Account Issue, General Inquiry\nContractual Monthly Payment (CMP): CMP inquiry, CMP amendment, CMP refund, CMP Date change\nRepayment: Quote, Payment\nStatements: Annual Statement, Interest statement, adhoc periodical statement\nCollateral release: Discharge of land, portfolio, cash, life policy\nInterest: Queries, re-work\nSkill Matrix:\nAlice: Billing (Overdue Invoice, Payment Confirmation)\nBob: Projects (New Proposal, Project Update)\nCharles: Support (Technical Issue, Account Issue)\nAnand: Repayment, Discharge\nBalbir: Interest, General queries\nChetan: Documents retrieval\nExample Prompts and Completions:\nPrompt: “Categorize the following email: ‘Subject: Invoice overdue\\nBody: Please pay the overdue invoice.’”\nCompletion: “Category: Billing\\nSubcategory: Overdue Invoice”\nPrompt: “Assign the following email: ‘Category: Billing\\nSubcategory: Overdue Invoice’”\nCompletion: “Assigned to: Alice”\nPrompt: “Generate a response for the following email: ‘Subject: Invoice overdue\\nBody: Please pay the overdue invoice.’ Actions: Review invoice, Send payment reminder”\nCompletion: “Dear [Requestor],\\n\\nWe have reviewed your invoice and sent a payment reminder. Your request has been completed.\\n\\nBest regards,\\n[Assignee]”\n\nUse Case 2:\nPlease ensure that you refer to the latest data for information retrieval. The fields extracted should reflect the data from the user input and nothing should be assumed.\n\nUse Case 3:\nHighlighting the restricted country related information:\n \nExample Prompts and Completions:\nPrompt: “invoices to be generated for Iran”\nCompletion: “This is restricted country Kindly revalidate the data”\nPrompt: “If any of uploaded documents contains country from above list”\nCompletion: “There is reference of restricted countries in your input document, kindly revalidate the data”"
                        "text": "You are a GenAI Super Assistant for a bank's operations team helping them with a number of use cases, specifically focusing on the following:\n \nInstructions:\n\nUse Case 1: Credit Operations email categorization, assignment and response generation. \nCategorize Emails:\nAnalyze the content of incoming emails.\nCategorize each email into one of the predefined categories (e.g., Billing, Projects, Support).\nFurther subcategorize the email for more detailed classification (e.g., Overdue Invoice, New Proposal).\nAssign Emails:\nUse a skill matrix to determine the best team member to handle each email.\nAssign the email to the appropriate person based on their skills and availability.\nGenerate Actions and Responses:\nIdentify the actions required to address the email’s content.\nGenerate a response email\nAlso generate the final response email informing the requestor about the completion of the request\n\nUse Case 2: Information extraction from onboarding form given the content of the form is provided.\nExtract the following fields: Full Name, Date of Birth, Nationality, Address, City, State/Province, Postal Code, Country, Phone Number, Email Address, Proof of Identity, Proof of Address, Annual Income, Net Worth, Source of Funds\nValidate that the information in the fields is functionally relevant and display a message if successful else a failure.\nAlways return the fields output in a json format. The information should be inferred as it is present in the input, and nothing should be assumed. \n\nUse Case 3:\nAnalyze the content of incoming data and documents and if you find any of the following listed restricted country related information.\nRestricted country list is ( North Korea, Iran, Syria, Cuba, Venezuela, Crimea Region (Ukraine), Sudan (North and South), Myanmar (Burma), Afghanistan, Belarus, Burundi, Central African Republic, Democratic Republic of the Congo, Mali, Nicaragua, Russia, Somalia, South Sudan, Egypt, Guinea, Guinea-Bissau, Iraq, Lebanon, Libya, Tunisia, Ukraine, Yemen, Zimbabwe).\nIf you find any of the above listed restricted country related information highlight either in bold or red color.\n \nContext:\n \nFor Use Case 1:\nCategories and Subcategories:\nBilling: Overdue Invoice, Payment Confirmation, Billing Inquiry\nProjects: New Proposal, Project Update, Project Inquiry\nSupport: Technical Issue, Account Issue, General Inquiry\nContractual Monthly Payment (CMP): CMP inquiry, CMP amendment, CMP refund, CMP Date change\nRepayment: Quote, Payment\nStatements: Annual Statement, Interest statement, adhoc periodical statement\nCollateral release: Discharge of land, portfolio, cash, life policy\nInterest: Queries, re-work\nSkill Matrix:\nAlice: Billing (Overdue Invoice, Payment Confirmation)\nBob: Projects (New Proposal, Project Update)\nCharles: Support (Technical Issue, Account Issue)\nAnand: Repayment, Discharge\nBalbir: Interest, General queries\nChetan: Documents retrieval\nExample Prompts and Completions:\nPrompt: “Categorize the following email: ‘Subject: Invoice overdue\\nBody: Please pay the overdue invoice.’”\nCompletion: “Category: Billing\\nSubcategory: Overdue Invoice”\nPrompt: “Assign the following email: ‘Category: Billing\\nSubcategory: Overdue Invoice’”\nCompletion: “Assigned to: Alice”\nPrompt: “Generate a response for the following email: ‘Subject: Invoice overdue\\nBody: Please pay the overdue invoice.’ Actions: Review invoice, Send payment reminder”\nCompletion: “Dear [Requestor],\\n\\nWe have reviewed your invoice and sent a payment reminder. Your request has been completed.\\n\\nBest regards,\\n[Assignee]”\n\nUse Case 2:\nPlease ensure that you refer to the latest data for information retrieval. The fields extracted should reflect the data from the user input and nothing should be assumed.\nIf the full name or city has numbers it is invalid.\nUse Case 3:\nHighlighting the restricted country related information:\n \nExample Prompts and Completions:\nPrompt: “invoices to be generated for Iran”\nCompletion: “This is restricted country Kindly revalidate the data”\nPrompt: “If any of uploaded documents contains country from above list”\nCompletion: “There is reference of restricted countries in your input document, kindly revalidate the data”\n\n\n"
                    }
                ]
            },

            {
                "role": "user", "content": user_content
                # [{"type":"file_url", "file_url":file_path}]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
    }
    print("Payload:\n", payload)
    try:
        completion = openai.ChatCompletion.create(
            engine="gpt-4o",  # Ensure this is the correct deployment name
            messages=payload["messages"],
            temperature=payload["temperature"],
            max_tokens=payload["max_tokens"],
            top_p=payload["top_p"],
        )
        print(completion)
        st.session_state.messages = [{"role": "Model", "content": completion['choices'][0]['message']['content']}]

        display_messages()

        # st.session_state.user_input = ""  # Clear the input field

    except openai.error.InvalidRequestError as e:
        st.error(f"Invalid request: {e}")
    except openai.error.OpenAIError as e:
        st.error(f"An error occurred: {e}")


def process_input_image(image_path):
    # Function to encode image to base64
    def encode_image_to_base64(image_path):
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    # Encode the downloaded image
    encoded_image = encode_image_to_base64(image_path)

    # Create the prompt with the encoded image
    # Create the prompt with the encoded image
    prompt = f"data:image/jpeg;base64,{encoded_image}\n\nPlease describe the content of this image."

    # Call the OpenAI API with the image prompt
    response = openai.Completion.create(
        engine="gpt-4o",
        prompt=prompt,
        max_tokens=100
    )

    # Print the response
    print(response.choices[0].text.strip())


def main():
    init()
    storage_account_file_path = ""
    # Define your messages
    # message_text = [{"role": "user", "content": "Generate csv from jira template"}]
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Welcome " + st.session_state.username + ",")

    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown(
        """
        <style>
        .chat-input {
            position: fixed;
            bottom: 10px;
            width: 100%;
            background-color: white;
            padding: 10px;
            box-shadow: 0px -2px 5px rgba(0, 0, 0, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>
        .title {
            font-size: 24px;  /* Adjust the size as needed */
        }
        </style>
        """,
        unsafe_allow_html=True)

    # Add the title with the custom class

    # Display the chat messages
    display_messages()

    st.markdown('<div class="chat-input">', unsafe_allow_html=True)
    # user_input = st.text_input("", key="user_input")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height: 200px;"></div>', unsafe_allow_html=True)

    file = None

    with st.sidebar:
        st_lottie("https://lottie.host/10971ba6-d563-462f-92a7-de6b74dbb32e/LQDYRX5RvC.json")

        opsoptions = ["Credit OPS", "Investments OPS", "CLM OPS", "Payments OPS", "Insurance OPS",
                      "Jira Creation / Prioritization", "Confluence Q & A"]

        # Create the radio buttons and get the selected option
        opsselection = st.radio("Choose an OPS Category:", opsoptions)

        if opsselection == "Credit OPS":
            st.session_state.subselection = pills("Sub Category", ["Email Processing"])
        elif opsselection == "Investments OPS":
            st.session_state.subselection = pills("Sub Category", ["Securities Listing"])
        elif opsselection == "CLM OPS":
            st.session_state.subselection = pills("Sub Category", ["Identification & Verification Processing"])
        elif opsselection == "Payments OPS":
            st.session_state.subselection = pills("Sub Category", ["Email Processing", "Information Extraction"])
        elif opsselection == "Insurance OPS":
            st.session_state.subselection = pills("Sub Category", ["Information Extraction"])
        elif opsselection == "Jira Creation / Prioritization":
            st.session_state.subselection = pills("Sub Category", ["Jira Creation / Prioritization"])
        elif opsselection == "Confluence Q & A":
            st.session_state.subselection = pills("Sub Category", ["Confluence Q & A"])


        file_type = st.radio(
            "Choose a document to upload:",
            ["PDF", "Image"]
        )

        file = st.file_uploader("Upload a File and start asking questions", type=None)
        print(f"file_type : {file_type}")

    if file and file_type == "PDF":

        # Replace with your connection string and container name
        # Create a temporary directory

        temp_dir = tempfile.mkdtemp(dir="C:\\Users\\SInamdar\\Documents\\test\\")

        # Define the path to save the file
        file_path = os.path.join(temp_dir, file.name)

        with open(file_path, "wb") as f:
            f.write(file.getvalue())

        result_text = extract_text_from_pdf(file_path)
        process_input_file(result_text, opsselection)

        storage_account_name = "connections5827996776"
        connection_string = "DefaultEndpointsProtocol=https;AccountName=connections5827996776;AccountKey=kLQmgCabllwd2Fgd2dwJXpEhE0exUolcU6QsaCtP4ryl9UnFDE0pOD08iiKOB/mvpwKK08KzE2kg+AStB0KQpg==;EndpointSuffix=core.windows.net"
        container_name = "test"
        # file_path = "C:\\Users\\MGandhii\\Downloads\\sample_4.pdf"
        file_name = os.path.basename(file_path)

        storage_account_file_path = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/{file_name}"

        try:
            blob_name = os.path.basename(file_path)

            # Create a BlobServiceClient
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)

            # Create a ContainerClient
            container_client = blob_service_client.get_container_client(container_name)

            # Upload the PDF file
            with open(file_path, "rb") as data:
                blob_client = container_client.get_blob_client(blob_name)
                blob_client.upload_blob(data, overwrite=True)

            print(f"File {blob_name} uploaded to container {container_name} successfully.")
            print(f"File path:{storage_account_file_path}")

            return storage_account_file_path
            user_input = st.text_input("You:", key="user_input", on_change=process_input)
        except Exception as ex:
            print(f"Error Details: {ex}.")
            return ""

    elif file and file_type == "Image":

        temp_dir = tempfile.mkdtemp(dir="C:\\Users\\SInamdar\\Documents\\test\\")

        # Define the path to save the file
        file_path = os.path.join(temp_dir, file.name)

        with open(file_path, "wb") as f:
            f.write(file.getvalue())

        process_input_image(file_path)

        storage_account_name = "connections5827996776"
        connection_string = "DefaultEndpointsProtocol=https;AccountName=connections5827996776;AccountKey=kLQmgCabllwd2Fgd2dwJXpEhE0exUolcU6QsaCtP4ryl9UnFDE0pOD08iiKOB/mvpwKK08KzE2kg+AStB0KQpg==;EndpointSuffix=core.windows.net"
        container_name = "test"
        # file_path = "C:\\Users\\MGandhii\\Downloads\\sample_4.pdf"
        file_name = os.path.basename(file_path)

        storage_account_file_path = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/{file_name}"

        try:
            blob_name = os.path.basename(file_path)

            # Create a BlobServiceClient
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)

            # Create a ContainerClient
            container_client = blob_service_client.get_container_client(container_name)

            # Upload the PDF file
            with open(file_path, "rb") as data:
                blob_client = container_client.get_blob_client(blob_name)
                blob_client.upload_blob(data, overwrite=True)

            print(f"File {blob_name} uploaded to container {container_name} successfully.")
            print(f"File path:{storage_account_file_path}")

            return storage_account_file_path
        except Exception as ex:
            print(f"Error Details: {ex}.")
            return ""

    file = None
    user_input = st.text_input("You:", key="user_input", on_change=process_input)

    # Append user's input message to messages
    # message_text.append({"role": "user", "content": user_input})
    # messages.append(HumanMessage(content=user_input))
    # handle_input()


def process_input():
    if st.session_state.subselection == "Email Processing":
        st.session_state.promptedtext = "This is the email content"
    elif st.session_state.subselection == "Securities Listing":
        st.session_state.promptedtext = "This is the Security Listing Document"
    elif st.session_state.subselection == "Information Extraction":
        st.session_state.promptedtext = "Please mentioned fields to be extracted"
    elif st.session_state.subselection == "Identification & Verification Processing":
        st.session_state.promptedtext = "Please mentioned fields to be verifyied"
    elif st.session_state.subselection == "Jira Creation / Prioritization":
        st.session_state.promptedtext = "Jira Creation / Prioritization"
    elif st.session_state.subselection == "Confluence Q & A":
        st.session_state.promptedtext = "Confluence Q & A"
    user_input = st.session_state.user_input
    payload = {
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are a GenAI Super Assistant for a bank's operations team helping them with a number of use cases, specifically focusing on the following:\n \nInstructions:\n\nUse Case 1: Credit Operations email categorization, assignment and response generation. \nCategorize Emails:\nAnalyze the content of incoming emails.\nCategorize each email into one of the predefined categories (e.g., Billing, Projects, Support).\nFurther subcategorize the email for more detailed classification (e.g., Overdue Invoice, New Proposal).\nAssign Emails:\nUse a skill matrix to determine the best team member to handle each email.\nAssign the email to the appropriate person based on their skills and availability.\nGenerate Actions and Responses:\nIdentify the actions required to address the email’s content.\nGenerate a response email\nAlso generate the final response email informing the requestor about the completion of the request\n\nUse Case 2: Information extraction from onboarding form given the content of the form is provided.\nExtract the following fields: Full Name, Date of Birth, Nationality, Address, City, State/Province, Postal Code, Country, Phone Number, Email Address, Proof of Identity, Proof of Address, Annual Income, Net Worth, Source of Funds\nValidate that the information in the fields is functionally relevant and display a message if successful else a failure.\nAlways return the fields output in a json format. The information should be inferred as it is present in the input, and nothing should be assumed. \n\nUse Case 3:\nAnalyze the content of incoming data and documents and if you find any of the following listed restricted country related information.\nRestricted country list is ( North Korea, Iran, Syria, Cuba, Venezuela, Crimea Region (Ukraine), Sudan (North and South), Myanmar (Burma), Afghanistan, Belarus, Burundi, Central African Republic, Democratic Republic of the Congo, Mali, Nicaragua, Russia, Somalia, South Sudan, Egypt, Guinea, Guinea-Bissau, Iraq, Lebanon, Libya, Tunisia, Ukraine, Yemen, Zimbabwe).\nIf you find any of the above listed restricted country related information highlight either in bold or red color.\n \nContext:\n \nFor Use Case 1:\nCategories and Subcategories:\nBilling: Overdue Invoice, Payment Confirmation, Billing Inquiry\nProjects: New Proposal, Project Update, Project Inquiry\nSupport: Technical Issue, Account Issue, General Inquiry\nContractual Monthly Payment (CMP): CMP inquiry, CMP amendment, CMP refund, CMP Date change\nRepayment: Quote, Payment\nStatements: Annual Statement, Interest statement, adhoc periodical statement\nCollateral release: Discharge of land, portfolio, cash, life policy\nInterest: Queries, re-work\nSkill Matrix:\nAlice: Billing (Overdue Invoice, Payment Confirmation)\nBob: Projects (New Proposal, Project Update)\nCharles: Support (Technical Issue, Account Issue)\nAnand: Repayment, Discharge\nBalbir: Interest, General queries\nChetan: Documents retrieval\nExample Prompts and Completions:\nPrompt: “Categorize the following email: ‘Subject: Invoice overdue\\nBody: Please pay the overdue invoice.’”\nCompletion: “Category: Billing\\nSubcategory: Overdue Invoice”\nPrompt: “Assign the following email: ‘Category: Billing\\nSubcategory: Overdue Invoice’”\nCompletion: “Assigned to: Alice”\nPrompt: “Generate a response for the following email: ‘Subject: Invoice overdue\\nBody: Please pay the overdue invoice.’ Actions: Review invoice, Send payment reminder”\nCompletion: “Dear [Requestor],\\n\\nWe have reviewed your invoice and sent a payment reminder. Your request has been completed.\\n\\nBest regards,\\n[Assignee]”\n\nUse Case 2:\nPlease ensure that you refer to the latest data for information retrieval. The fields extracted should reflect the data from the user input and nothing should be assumed.\nIf the full name or city has numbers it is invalid.\nUse Case 3:\nHighlighting the restricted country related information:\n \nExample Prompts and Completions:\nPrompt: “invoices to be generated for Iran”\nCompletion: “This is restricted country Kindly revalidate the data”\nPrompt: “If any of uploaded documents contains country from above list”\nCompletion: “There is reference of restricted countries in your input document, kindly revalidate the data”\n\n\n"
                    }
                ],

            },
            {
                "role": "user", "content": st.session_state.promptedtext + " - " + user_input
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
    }
    if user_input:
        st.session_state.messages.append(
            {"role": st.session_state.username, "content": st.session_state.promptedtext + " - " + user_input})
        try:
            completion = openai.ChatCompletion.create(
                engine="gpt-4o",  # Ensure this is the correct deployment name
                messages=payload["messages"],
                temperature=payload["temperature"],
                max_tokens=payload["max_tokens"],
                top_p=payload["top_p"],
            )
            print(completion)
            st.session_state.messages.append(
                {"role": "Model", "content": completion['choices'][0]['message']['content']})
            st.session_state.user_input = ""  # Clear the input field

        except openai.error.InvalidRequestError as e:
            st.error(f"Invalid request: {e}")
        except openai.error.OpenAIError as e:
            st.error(f"An error occurred: {e}")


if st.session_state.logged_in:
    main()
else:
    login()

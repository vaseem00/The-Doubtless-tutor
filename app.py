import streamlit as st
import os
import requests
import json
from operator import itemgetter
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
import langchain
from langchain.schema.output_parser import StrOutputParser

from langchain import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

os.environ["OPENAI_API_KEY"] =""

model = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0
    )

#langchain.debug = True

# Function to process the text and images
def process_input_image(image):
    template1="You are a helpful assistant that answers the students question step by step with upmost accuracy."
    system_message_prompt1 = SystemMessagePromptTemplate.from_template(template1)
    human_template1 ="{question}"
    human_message_prompt1 = HumanMessagePromptTemplate.from_template(human_template1)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt1, human_message_prompt1])

    template2="You are a helpful assistant that looks at answers and finds what is wrong with them based on the original question given."
    system_message_prompt2 = SystemMessagePromptTemplate.from_template(template2)
    human_template2="### Question:\n\n{question}\n\n ###Answer Given:{initial_answer}\n\n Review your previous answer and find problems with your answer"
    human_message_prompt2 = HumanMessagePromptTemplate.from_template(human_template2)

    rc_prompt = ChatPromptTemplate.from_messages([system_message_prompt2, human_message_prompt2])

    template3="You are a helpful assistant that reviews generated answers and solves the question once more for verification."
    system_message_prompt3 = SystemMessagePromptTemplate.from_template(template3)
    human_template3="### Question:\n\n{question}\n\n ###Answer Given:{initial_answer}\n\n Review your previous answer and solve the question independently"
    human_message_prompt3 = HumanMessagePromptTemplate.from_template(human_template3)

    verf_prompt = ChatPromptTemplate.from_messages([system_message_prompt3, human_message_prompt3])

    template4="You are a helpful assistant that reviews answers and critiques based on the original question given and write a new improved final answer in step by step manner, only if the initial answer and verified answer is same."
    system_message_prompt4 = SystemMessagePromptTemplate.from_template(template4)
    human_template4="### Question:\n\n{question}\n\n ###Answer Given:{initial_answer}\n\n \
    ###Constructive Criticism:{constructive_criticism}\n\n ###verified answer:{verify_answer}\n\n Based on the problems you found, improve your answer. Also note: if initial answer and verified answer are not same, return I cannot solve the question.\n\n### Final Answer:"
    human_message_prompt4 = HumanMessagePromptTemplate.from_template(human_template4)

    improvement_prompt = ChatPromptTemplate.from_messages([system_message_prompt4, human_message_prompt4])


    chain1 = chat_prompt | model | StrOutputParser()

    critque_chain = {"question": itemgetter("question"),
                    "initial_answer": chain1 } | rc_prompt | model | StrOutputParser()

    chain_ver = {"question": itemgetter("question"),
                    "initial_answer": chain1,
                        "constructive_criticism": critque_chain} | verf_prompt | model | StrOutputParser()

    chain2 = {"question": itemgetter("question"),
            "initial_answer": chain1,
            "verify_answer": chain_ver,
            "constructive_criticism": critque_chain} | improvement_prompt | model | StrOutputParser()

    if image is not None:
        image_content = image.read()
        photo_file_path = 'file_0.jpg'
        with open(photo_file_path, 'wb') as f:
            f.write(image_content)
        payload = { 'isOverlayRequired': True,
                        'apikey': 'K89461687888957',
                        'language': 'eng',
                        }
        with open(image, 'rb') as f:
            r = requests.post('https://api.ocr.space/parse/image',
                                files={photo_file_path: f},
                                data=payload,
                                )
                
            #print(r.content.decode())
                
        data = json.loads(r.content.decode())
        lens = data["ParsedResults"][0]["ParsedText"]
        final_answer = chain2.invoke({"question":lens})
        return final_answer
    else:
        return None

def process_input_text(text):
    template1="You are a helpful assistant that answers the students question step by step with upmost accuracy."
    system_message_prompt1 = SystemMessagePromptTemplate.from_template(template1)
    human_template1 ="{question}"
    human_message_prompt1 = HumanMessagePromptTemplate.from_template(human_template1)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt1, human_message_prompt1])

    template2="You are a helpful assistant that looks at answers and finds what is wrong with them based on the original question given."
    system_message_prompt2 = SystemMessagePromptTemplate.from_template(template2)
    human_template2="### Question:\n\n{question}\n\n ###Answer Given:{initial_answer}\n\n Review your previous answer and find problems with your answer"
    human_message_prompt2 = HumanMessagePromptTemplate.from_template(human_template2)

    rc_prompt = ChatPromptTemplate.from_messages([system_message_prompt2, human_message_prompt2])

    template3="You are a helpful assistant that reviews generated answers and solves the question once more for verification."
    system_message_prompt3 = SystemMessagePromptTemplate.from_template(template3)
    human_template3="### Question:\n\n{question}\n\n ###Answer Given:{initial_answer}\n\n Review your previous answer and solve the question independently"
    human_message_prompt3 = HumanMessagePromptTemplate.from_template(human_template3)

    verf_prompt = ChatPromptTemplate.from_messages([system_message_prompt3, human_message_prompt3])

    template4="You are a helpful assistant that reviews answers and critiques based on the original question given and write a new improved final answer in step by step manner, only if the initial answer and verified answer is same."
    system_message_prompt4 = SystemMessagePromptTemplate.from_template(template4)
    human_template4="### Question:\n\n{question}\n\n ###Answer Given:{initial_answer}\n\n \
    ###Constructive Criticism:{constructive_criticism}\n\n ###verified answer:{verify_answer}\n\n Based on the problems you found, improve your answer. Also note: if initial answer and verified answer are not same, return I cannot solve the question.\n\n### Final Answer:"
    human_message_prompt4 = HumanMessagePromptTemplate.from_template(human_template4)

    improvement_prompt = ChatPromptTemplate.from_messages([system_message_prompt4, human_message_prompt4])


    chain1 = chat_prompt | model | StrOutputParser()

    critque_chain = {"question": itemgetter("question"),
                    "initial_answer": chain1 } | rc_prompt | model | StrOutputParser()

    chain_ver = {"question": itemgetter("question"),
                    "initial_answer": chain1,
                        "constructive_criticism": critque_chain} | verf_prompt | model | StrOutputParser()

    chain2 = {"question": itemgetter("question"),
            "initial_answer": chain1,
            "verify_answer": chain_ver,
            "constructive_criticism": critque_chain} | improvement_prompt | model | StrOutputParser()

    if text is not None:
        final_answer = chain2.invoke({"question":text})
        return final_answer
    else:
        return None




# Title of the app
st.title('The doubtless Tutor')

# Text input
user_text = st.text_input("Enter your question:")

# Image input
uploaded_image = st.file_uploader("Upload your question as image...", type=["jpg", "png", "jpeg"])

text_output = None
image_output = None

# Check if user_text is not empty before processing
if user_text:
    text_output = process_input_text(user_text)

# Check if an image has been uploaded before processing
if uploaded_image:
    image_output = process_input_image(uploaded_image)
    
text_output = process_input_text(user_text)
image_output = process_input_image(uploaded_image)

if text_output:
    st.write(text_output)

if image_output:
    st.write(image_output)

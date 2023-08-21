import os
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

os.environ["OPENAI_API_KEY"] = ""

model = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0
    )

template1="You are a helpful assistant that answers the students question step by step with upmost accuracy."
system_message_prompt1 = SystemMessagePromptTemplate.from_template(template1)
human_template1="{question}"
human_message_prompt1 = HumanMessagePromptTemplate.from_template(human_template)
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

langchain.debug = True

chain2.invoke({"question":"Consider 2 forces acting on a mass of 2.63 kg. F1 = 9.6 N @ 18.3 degrees and F2 = 8.81 N @ 77.8 degrees where the angles are measured relative to the +x direction. What is the magnitude of the acceleration produced considering only these 2 forces acting?"})

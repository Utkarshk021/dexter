import openai
import streamlit as st
import time

assistant_id = st.secrets["ASSISTANT_KEY_DEXTER"]
valid_passcode = st.secrets["PASSCODE"]

client = openai

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "buttons_shown" not in st.session_state:
    st.session_state.buttons_shown = False
if "prompt" not in st.session_state:
    st.session_state.prompt = ""
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.set_page_config(page_title="Dexter", page_icon=":briefcase:")

openai.api_key = st.secrets["OPENAI_API_KEY"]

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Sidebar for user input
st.sidebar.title("Tell us about yourself")

passcode = st.sidebar.text_input("Enter passcode", type="password")
year = st.sidebar.selectbox("What year are you in?", ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"])
major = st.sidebar.selectbox("What is your major?", ["Computer Science", "Business", "Engineering", "Arts", "Other"])
career_interest = st.sidebar.selectbox("What are your career interests?", ["Software Engineering", "Product Management", "Marketing", "Product Design"])

if st.sidebar.button("Start Chat"):
    if passcode == valid_passcode:
        st.session_state.authenticated = True
        st.session_state.start_chat = True
        st.session_state.year = year
        st.session_state.major = major
        st.session_state.career_interest = career_interest
        st.session_state.buttons_shown = False  # Reset buttons_shown when starting a new chat
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
        st.session_state.query_count = 0  # Reset query count for a new chat
    else:
        st.sidebar.error("Invalid passcode. Please try again.")

# Share information about the MVP
st.sidebar.markdown("---")
st.sidebar.markdown("MVP built with ❤️ [Utkarsh Khandelwal](mailto:ukhandelwal21@gmail.com)")

st.title("Dexter! Your Handshake Assistant")
st.write("Welcome! My name is Dexter - I'm here to help you navigate your career journey and make the most of Handshake.")

if st.button("Exit Chat"):
    st.session_state.messages = []  # Clear the chat history
    st.session_state.start_chat = False  # Reset the chat state
    st.session_state.thread_id = None
    st.session_state.buttons_shown = False  # Reset buttons_shown on exiting chat
    st.session_state.authenticated = False  # Reset authentication on exiting chat

def typing_effect(text):
    for char in text:
        yield char
        time.sleep(0.008)

if st.session_state.authenticated and st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-3.5-turbo"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Initial assistant message
    if not st.session_state.messages:
        initial_message = f"Thanks for sharing your information as a :red[{st.session_state.year}] majoring in :red[{st.session_state.major}] with career interests in :red[{st.session_state.career_interest}] " \
                          f". I'm here to assist you with your career journey and help you make the most of Handshake."

        st.session_state.messages.append({"role": "assistant", "content": initial_message})
        with st.chat_message("assistant"):
            st.write_stream(typing_effect(initial_message))

        summary_message = "Feel free to ask me about career tips, handshake tips, reaching out to recruiters, and more."
        st.session_state.messages.append({"role": "assistant", "content": summary_message})
        with st.chat_message("assistant"):
            st.write_stream(typing_effect(summary_message))

    # Add predefined buttons only at the start
    if not st.session_state.buttons_shown:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("How to Optimize Handshake profile"):
                st.session_state.prompt = "How to optimize my Handshake profile to attract more employers?"
                st.session_state.buttons_shown = True
            if st.button("How to Tailor resume for job posting"):
                st.session_state.prompt = "How do I tailor my resume for a specific job posting on Handshake?"
                st.session_state.buttons_shown = True
            if st.button("How to Stand out in virtual career fairs"):
                st.session_state.prompt = "What strategies can I use to stand out in virtual career fairs?"
                st.session_state.buttons_shown = True
            if st.button("How often to Update Handshake profile"):
                st.session_state.prompt = "How often should I update my Handshake profile?"
                st.session_state.buttons_shown = True
        with col2:
            if st.button("How to Network with alumni"):
                st.session_state.prompt = "What are some effective ways to network with alumni?"
                st.session_state.buttons_shown = True
            if st.button("How to use Handshake messaging"):
                st.session_state.prompt = "How can I use Handshake's messaging feature to connect with recruiters professionally?"
                st.session_state.buttons_shown = True
            if st.button("How to find mentorship opportunities"):
                st.session_state.prompt = "How can I use Handshake to find mentorship opportunities in my industry?"
                st.session_state.buttons_shown = True
            if st.button("Handshake to research potential employers"):
                st.session_state.prompt = "How can I use Handshake to research potential employers before applying?"
                st.session_state.buttons_shown = True

    if st.session_state.prompt:
        st.session_state.query_count += 1
        if st.session_state.query_count > 10:
            st.write("You have reached the maximum number of queries for this session.")
        else:
            st.session_state.messages.append({"role": "user", "content": st.session_state.prompt})
            with st.chat_message("user"):
                st.markdown(st.session_state.prompt)

            client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=st.session_state.prompt
            )

            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant_id,
            )

            while run.status != 'completed':
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            # Process and display assistant messages
            assistant_messages_for_run = [
                message for message in messages
                if message.run_id == run.id and message.role == "assistant"
            ]
            for message in assistant_messages_for_run:
                st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
                with st.chat_message("assistant"):
                    st.write_stream(typing_effect(message.content[0].text.value))
            
            st.session_state.prompt = ""

    # User input
    if user_input := st.chat_input("How can I assist you with your career journey?"):
        st.session_state.query_count += 1
        if st.session_state.query_count > 10:
            st.write("You have reached the maximum number of queries for this session.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=user_input
            )

            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant_id,
            )

            while run.status != 'completed':
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            # Process and display assistant messages
            assistant_messages_for_run = [
                message for message in messages
                if message.run_id == run.id and message.role == "assistant"
            ]
            for message in assistant_messages_for_run:
                st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
                with st.chat_message("assistant"):
                    st.write_stream(typing_effect(message.content[0].text.value))

else:
    if not st.session_state.authenticated:
        st.write("Please enter the passcode in the sidebar to begin.")
    else:
        st.write("Please provide your information in the sidebar and click 'Start Chat' to begin.")

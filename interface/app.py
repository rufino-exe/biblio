import streamlit as st
import requests
import uuid

RASA_URL = 'http://localhost:5005/webhooks/rest/webhook'

st.set_page_config(page_title='Nexus Library', layout='centered')

# DARK CORPORATE STYLE
st.markdown("""
<style>
body, .stApp {
    background-color: #0d0d0d !important;
    color: #e5e5e5 !important;
}

/* Header */
header[data-testid="stHeader"] {
    background-color: #0d0d0d !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    background: #161616 !important;
    border: 1px solid #2a2a2a !important;
}
[data-testid="stChatInput"] textarea {
    color: #e5e5e5 !important;
    background: transparent !important;
}
[data-testid="stChatInputSubmitButton"] button {
    background: #2a2a2a !important;
    color: #e5e5e5 !important;
}

/* Messages */
[data-testid="stChatMessage"] {
    background: #161616 !important;
    border: 1px solid #2a2a2a !important;
    color: #e5e5e5 !important;
}

/* Button */
.stButton > button {
    background: #161616 !important;
    color: #e5e5e5 !important;
    border: 1px solid #2a2a2a !important;
}
.stButton > button:hover {
    background: #1f1f1f !important;
}

/* Title */
h1 {
    border-bottom: 1px solid #2a2a2a;
    color: #e5e5e5 !important;
}

/* Remove menu */
#MainMenu, [data-testid="stDecoration"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

st.title('Nexus Library')
st.caption('Sistema de consulta de acervo digital')

# Session
if 'sender_id' not in st.session_state:
    st.session_state.sender_id = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = []

# History
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# Input
if prompt := st.chat_input('Digite sua consulta...'):
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    try:
        response = requests.post(
            RASA_URL,
            json={'sender': st.session_state.sender_id, 'message': prompt},
            timeout=30
        )
        bot_msgs = response.json()

        if bot_msgs:
            for bot_msg in bot_msgs:
                text = bot_msg.get('text', '')
                if text:
                    st.session_state.messages.append({'role': 'assistant', 'content': text})
                    with st.chat_message('assistant'):
                        st.markdown(text)
        else:
            st.session_state.messages.append({'role': 'assistant', 'content': '(Sem resposta do sistema)'})
            with st.chat_message('assistant'):
                st.markdown('(Sem resposta do sistema)')

    except requests.exceptions.ConnectionError:
        st.error('Erro de conexão com o servidor Rasa.')
    except requests.exceptions.Timeout:
        st.error('Tempo de resposta excedido.')

# Clear
if st.button('Limpar sessão'):
    st.session_state.messages = []
    st.session_state.sender_id = str(uuid.uuid4())
    st.rerun()
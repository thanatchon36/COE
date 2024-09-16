import streamlit as st
from streamlit_feedback import streamlit_feedback
import time
import datetime
import pandas as pd
from PIL import Image
import os
import csv
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import requests

def get_response(prompt, context = []):
    start_time = time.time()
    port = 9101
    api_route = 'coe_query'
    post_params = {'query': prompt,
                }
    res = requests.post(f'http://127.0.0.1:{port}/{api_route}', json = post_params)
    execution_time = time.time() - start_time
    execution_time = round(execution_time, 2)
    return {'response': res.json()['response'], 'raw_input': "", 'raw_output': "", 'engine': "coe", 'frontend_query_time': execution_time, 'backend_query_time': res.json()['query_time_sec']}

def get_response_dev(prompt, context = []):
    start_time = time.time()
    time.sleep(3)
    execution_time = time.time() - start_time
    execution_time = round(execution_time, 2)
    return {'response': 'response', 'raw_input': 'raw_input', 'raw_output': 'raw_output', 'engine': 'engine', 'frontend_query_time': execution_time, 'backend_query_time': execution_time}

def reset(df):
    cols = df.columns
    return df.reset_index()[cols]

show_chat_history_no = 5
admin_list = ['thanatcc', 'da', 'chinnawd']
da_username_list = ['thanatcc','chinnawd','anaky','bodinc','kawinwil','palakorb','peranutn','pitiyatp','senangma','skunpojt','supachas','wasakory','kriangks','nontawic','bodinc','chalisak','wanpracc','suwatchc','bovonvij']

st.set_page_config(page_title = 'COE', page_icon = 'fav.png', layout="wide")

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

authenticator.login('BotGPT Login', 'main')

if st.session_state["authentication_status"]:
    
    if "chat_id" not in st.session_state:
        now = str(datetime.datetime.now())
        st.session_state.chat_id  = now

    bot_image = Image.open('fav.png')
    bot_image_2 = Image.open('fav_3.png')
    user_image = Image.open('fav_2.png')

    with st.sidebar:
        
        clear_session_click = st.button("New Chat")
        if clear_session_click:
            st.session_state.messages = []
            st.session_state.context = []
            now = str(datetime.datetime.now())
            st.session_state.chat_id  = now

        context_radio = st.radio(
            "Context:",
            ["COE",],
        )
                
        csv_file = f"data/{st.session_state.username}.csv"
        file_exists = os.path.isfile(csv_file)
        if file_exists:
            if len(pd.read_csv(csv_file, sep = ',')) > 0:
                # Init State Sessioin
                if 'page' not in st.session_state:
                    st.session_state['page'] = 1
                    
                with st.expander("Chat History"):
                    hist_df = pd.read_csv(f'data/{st.session_state.username}.csv', sep = ',')
                    full_hist_df = hist_df.copy()
                    hist_df = reset(hist_df.sort_values(by = 'turn_id', ascending = False))
                    hist_df = hist_df.groupby('chat_id').first().reset_index()
                    hist_df = reset(hist_df.sort_values(by = 'turn_id', ascending = False))

                    hist_df['page'] = hist_df.index
                    hist_df['page'] = hist_df['page'] / show_chat_history_no
                    hist_df['page'] = hist_df['page'].astype(int)
                    hist_df['page'] = hist_df['page'] + 1

                    st.session_state['max_page'] = hist_df['page'].max()

                    filter_hist_df_2 = reset(hist_df[hist_df['page'] == st.session_state['page']])

                    for index, row in filter_hist_df_2.iterrows():
                        if st.session_state.chat_id != row['chat_id']:
                            chat_button_click = st.button(f"{row['user_text'][:30]}" + '...', key = row['chat_id'])
                            if chat_button_click:
                                st.session_state.messages = []
                                st.session_state.context = []
                                st.session_state.chat_id = row['chat_id']
                                st.session_state.turn_id = row['turn_id']
                                fil_hist_df = full_hist_df.copy()
                                fil_hist_df = reset(fil_hist_df[fil_hist_df['chat_id'] == row['chat_id']])
                                for index_2, row_2 in fil_hist_df.iterrows(): 
                                    st.session_state.messages.append({"role": "user", "content": row_2['user_text'], "raw_content": row_2['raw_input']})
                                    st.session_state.messages.append({"role": "assistant", "content": row_2['generative_text'], "chat_id": row_2['chat_id'], "turn_id":  row_2['turn_id'],
                                                                      "raw_content": row_2['raw_output'],
                                                                      })

                                    st.session_state.context.append({"role": "user", "content": row_2['raw_input']})
                                    st.session_state.context.append({"role": "system", "content": row_2['raw_output']})

                    if 'max_page' not in st.session_state:
                        st.session_state['max_page'] = 10
                    if int(st.session_state['max_page']) > 1:
                        page = st.slider('Page No:', 1, int(st.session_state['max_page']), key = 'page')

        with st.expander("Change Password"):
            try:
                if authenticator.reset_password(st.session_state["username"], 'Reset password'):
                    with open('config.yaml', 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
                    st.success('Password modified successfully')
            except Exception as e:
                st.error(e)

        if st.session_state.username in admin_list:
            with st.expander("Register User"):
                try:
                    if authenticator.register_user('Register user', preauthorization=False):
                        with open('config.yaml', 'w') as file:
                            yaml.dump(config, file, default_flow_style=False)
                        st.success('User registered successfully')
                except Exception as e:
                    st.error(e)

        authenticator.logout(f"Logout ({st.session_state['username']})", 'main', key='unique_key')

    with st.chat_message("assistant", avatar = bot_image_2):
        # Create an empty message placeholder
        mp = st.empty()
        # Create a container for the message
        sl = mp.container()
        # Add a Markdown message describing the app
        sl.markdown(f"""
            Hi {st.session_state.name}! I am BotGPT, ready to provide assistance.
        """)

        existing_df = pd.DataFrame()

    mp = st.empty()

    # Initialize chat history if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "context" not in st.session_state:
        st.session_state.context = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message(message["role"], avatar = bot_image_2):
                st.markdown(message["content"])
                col1, col2, col3 = st.columns(3)
                with col1:
                    feedback_options = ["...",
                                        "😄", 
                                        "🙂",
                                        "😐",
                                        "🙁",
                                        ]
                    feedback_radio_1 = st.radio(
                                        "ความพึงพอใจในการใช้งาน:",
                                        feedback_options,
                                        key='radio_1_' + message['turn_id'],
                                    )
                    if feedback_radio_1 != '...':
                        csv_file = f"data/feedback.csv"
                        file_exists = os.path.isfile(csv_file)
                        if not file_exists:
                            with open(csv_file, mode='a', newline='') as file:
                                writer = csv.writer(file)
                                writer.writerow(['username','chat_id','turn_id','feedback_text'])
                        with open(csv_file, mode='a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([st.session_state.username, st.session_state.chat_id, message['turn_id'], feedback_radio_1,])
                        st.success("Thanks! Your valuable feedback is updated in the database.")
                with col2:
                    if context_radio == 'COE':
                        feedback_options = ["...",
                                            "คำตอบถูกต้องครบถ้วน",
                                            "คำตอบถูกต้องบางส่วน",
                                            "คำตอบไม่ถูกต้อง",
                                            "คำตอบไม่เกี่ยวข้องกับคำถาม"]
                    feedback_radio_2 = st.radio(
                                        "ความถูกต้องของคำตอบ:",
                                        feedback_options,
                                        key='radio_2_' + message['turn_id'],
                                    )
                    if feedback_radio_2 != '...':
                        csv_file = f"data/feedback.csv"
                        file_exists = os.path.isfile(csv_file)
                        if not file_exists:
                            with open(csv_file, mode='a', newline='') as file:
                                writer = csv.writer(file)
                                writer.writerow(['username','chat_id','turn_id','feedback_text'])
                        with open(csv_file, mode='a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([st.session_state.username, st.session_state.chat_id, message['turn_id'], feedback_radio_2,])
                        st.success("Thanks! Your valuable feedback is updated in the database.")                                
        else:
            with st.chat_message(message["role"], avatar = user_image):
                st.markdown(message["content"])


    if prompt := st.chat_input(placeholder="Kindly input your query or command for prompt assistance..."):
        # Display user input in the chat
        st.chat_message("user", avatar = user_image).write(prompt)

        # Create a chat message for the assistant
        with st.chat_message("assistant", avatar = bot_image_2):
            full_response = ""  # Initialize an empty string to store the full response
            message_placeholder = st.empty()  # Create an empty placeholder for displaying messages

            with st.spinner('Thinking...'):
                if context_radio == 'COE':
                    response_dict = get_response(prompt, context = st.session_state.context)
                    response = response_dict['response']
                    raw_input = response_dict['raw_input']
                    raw_output = response_dict['raw_output']
                    engine = response_dict['engine']
                    frontend_query_time = response_dict['frontend_query_time']
                    backend_query_time = response_dict['backend_query_time']
                                        
                full_response = ""
                # Simulate streaming the response with a slight delay
                for chunk in response.split("\n"):
                    # Add a small delay to simulate typing
                    time.sleep(0.05)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                    full_response += chunk + "  \n"  # Add double space escape sequence for line break
                    message_placeholder.markdown(full_response)

            # csv_file = f"data/{st.session_state['username']}.csv"
            csv_file = f"data/{st.session_state.username}.csv"
            file_exists = os.path.isfile(csv_file)
            if not file_exists:
                with open(csv_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['username','chat_id','turn_id','user_text','generative_text','raw_input','raw_output','engine','frontend_query_time','backend_query_time'])
            with open(csv_file, mode='a', newline='', encoding = 'utf-8') as file:
                writer = csv.writer(file)
                current_time = str(datetime.datetime.now())
                st.session_state.turn_id = current_time
                writer.writerow([st.session_state.username, st.session_state.chat_id, st.session_state.turn_id, prompt, full_response, raw_input, raw_output, engine, frontend_query_time, backend_query_time])

            # Add the assistant's response to the chat history
            st.session_state.messages.append({"role": "user", "content": prompt, "raw_content": raw_input})
            st.session_state.messages.append({"role": "assistant", "content": full_response, "chat_id": st.session_state.chat_id, "turn_id":  st.session_state.turn_id,
                                                "raw_content": raw_output,
                                                })
            
            st.session_state.context.append({"role": "user", "content": raw_input})
            st.session_state.context.append({"role": "system", "content": raw_output})

            st.rerun()

elif st.session_state["authentication_status"] == False:
    st.error("Username/password is incorrect. If you encounter any issues related to user login, please contact Thanatchon Chongmankhong at thanatcc@bot.or.th.")
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password. If you encounter any issues related to user login, please contact Thanatchon Chongmankhong at thanatcc@bot.or.th.')
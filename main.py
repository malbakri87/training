from openai import OpenAI
import streamlit as st
import base64

st.set_page_config(layout = "wide")

st.title("File Analyzer")

model_name = "gpt-4.1"

# display the password text input 
api_key = st.sidebar.text_input("API Key", type="password")

if api_key:
    try:
        client = OpenAI(api_key = api_key)

        # initialize the session state if not exists
        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.display_content = []
              
        # display all history contents based on the role 
        for message in st.session_state.display_content:
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)
        
        # display the chat input with placeholder, and the types of files accepted
        if prompt := st.chat_input("Enter your prompt", accept_file=True,file_type=["pdf", "png", "jpeg", "jpg"]):
            content = []
            display_content = ""

            if prompt.files:
                file = prompt.files[0]

                display_content += f"Uploaded {file.name}"

                # create pdf
                if file.type == "application/pdf":
                    file = client.files.create(
                        file=file,
                        purpose="user_data"
                    )

                    content.append({"type": "file", "file": {"file_id" : file.id}})

                # create images
                else:
                    base64_image = base64.b64encode(file.read()).decode("utf-8")
                    image_url = f"data:image/jpeg;base64,{base64_image}"

                    content.append({"type": "image_url", "image_url": {"url": image_url}})  

            if prompt.text and prompt.files: display_content += "<br>"
            
            if prompt.text:
                text = prompt.text
                display_content += text
                content.append({"type": "text", "text": text})

            # store all history user content in session state

            st.session_state.messages.append({"role": "user", "content": content})
            st.session_state.display_content.append({"role": "user", "content": display_content})

            # display the user content 

            with st.chat_message("user"):
                st.markdown(display_content, unsafe_allow_html=True)

            # display the assistant content 

            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True
                )
                response = st.write_stream(stream)
            
            # store all history assistant content in session state

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.display_content.append({"role": "assistant", "content": response})

    except Exception as e:
        st.info(e)
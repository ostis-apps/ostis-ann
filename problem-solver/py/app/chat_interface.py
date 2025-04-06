import streamlit as st
from api_utils import get_api_response
from response_parser import display_llm_response

def display_chat_interface():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if isinstance(message.get("content"), str):
                display_llm_response(message["content"])
            else:
                st.markdown(message.get("content", ""))

    if prompt := st.chat_input("Query:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Generating response..."):
            response = get_api_response(prompt, st.session_state.session_id, st.session_state.model)

            if response:
                st.session_state.session_id = response.get('session_id')
                answer = response['answer']

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                with st.chat_message("assistant"):
                    display_llm_response(answer)

                    with st.expander("Details"):
                        st.subheader("Generated Answer")
                        st.code(answer)
                        st.subheader("Model Used")
                        st.code(response['model'])
                        st.subheader("Session ID")
                        st.code(response['session_id'])
            else:
                st.error("Failed to get a response from the API. Please try again.")

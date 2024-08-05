import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="🦙💬 Toucan AI Financial Chatbot")
st.markdown('Welcome to Toucan AI! Your assistant for summarizing and analyzing financial data from filings.')

# Replicate Credentials
os.environ['REPLICATE_API_TOKEN'] = 'r8_WU7WeG93u6FmXN6qR4vnE53F5ejFzCW2dPD51'
replicate_api = os.environ['REPLICATE_API_TOKEN']

with st.sidebar:
    st.title('🦙💬 Toucan AI Chatbot')
    st.success('API key already provided!', icon='✅')
    
    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
    if selected_model == 'Llama2-7B':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'Llama2-13B':
        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8)
    st.markdown('📖 Thank you for testing Toucan AI!')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Mock function to summarize financial data
def get_company_summary(company_name):
    summaries = {
        "apple": "Apple Inc. recently reported a strong financial performance with revenue growth driven by iPhone sales and services. The company posted a quarterly revenue of $90 billion, up 8% year-over-year. Apple's services segment, including App Store, Apple Music, and iCloud, saw significant growth, contributing $18 billion to the revenue. The company's net income for the quarter was $20 billion, reflecting a profit margin of 22%. Apple's stock price has been performing well, with a year-to-date increase of 15%.",
        "microsoft": "Microsoft Corporation's latest earnings report highlights robust performance in its cloud computing and software segments. The company achieved a quarterly revenue of $45 billion, a 12% increase compared to the previous year. Azure, Microsoft's cloud platform, experienced a 30% revenue growth, significantly contributing to the overall financial performance. The net income for the quarter was $15 billion, resulting in a profit margin of 33%. Microsoft's stock has seen a steady rise, with a 10% increase year-to-date.",
        "google": "Alphabet Inc., the parent company of Google, reported strong financial results driven by growth in advertising and cloud services. The company's quarterly revenue was $65 billion, up 10% year-over-year. Google Cloud's revenue grew by 35%, contributing $5 billion to the overall revenue. Alphabet's net income for the quarter was $18 billion, with a profit margin of 28%. The stock price has increased by 12% year-to-date, reflecting investor confidence in the company's growth prospects."
    }
    return summaries.get(company_name.lower(), "Sorry, I don't have a summary for that company at the moment.")

# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(prompt_input):
    string_dialogue = "You are a helpful assistant specialized in summarizing and analyzing financial data from SEC filings. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run(llm, 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
    return output

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if "apple" in prompt.lower() or "microsoft" in prompt.lower() or "google" in prompt.lower():
                # Extract company name from the prompt
                company_name = prompt.split()[-1]
                filing_summary = get_company_summary(company_name)
                response = generate_llama2_response(filing_summary)
            else:
                response = generate_llama2_response(prompt)
                
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)

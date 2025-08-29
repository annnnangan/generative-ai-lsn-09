import streamlit as st
import time
import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
import asyncio

# Page configuration
st.set_page_config(
    page_title="Streamlit AI Chat Application",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #f0f0f0;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    .main-header .caption {
        font-size: 0.9rem;
    }
    .section-margin {
        margin: 1.5rem 0;
    }
    .input-section {
        margin-bottom: 2rem;
    }
    .status-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-top: 1px solid #dee2e6;
        text-align: center;
        z-index: 1000;
    }
    .chat-message {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .ai-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .send-button {
        width: 100%;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Initialize OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'current_response' not in st.session_state:
    st.session_state.current_response = ""

if 'is_streaming' not in st.session_state:
    st.session_state.is_streaming = False

if 'openrouter_agent' not in st.session_state:
    st.session_state.openrouter_agent = None

# Function to initialize OpenRouter agent
def initialize_openrouter_agent(model_name):
    """Initialize OpenRouter agent with selected model"""
    try:
        if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
            st.error("⚠️ Please set your OpenRouter API key in the .env file")
            return None
        
        model = OpenAIModel(
            model_name,
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY
        )
        return Agent(model)
    except Exception as e:
        st.error(f"❌ Failed to initialize OpenRouter agent: {str(e)}")
        return None

# Header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown('<h1>🤖 Streamlit AI Chat Application</h1>', unsafe_allow_html=True)
st.markdown('<p class="caption">Interactive AI chat with OpenRouter models and real-time streaming</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Main layout - Two columns
col1, col2 = st.columns([3, 2])  # 60% - 40% split

with col1:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.subheader("Configuration & Input")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # API Key Status
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        st.warning("🔑 Please set your OpenRouter API key in the .env file")
    else:
        st.success("🔑 OpenRouter API key configured")
    
    # Model Selection
    st.markdown('<div class="section-margin">', unsafe_allow_html=True)
    model_options = [
        "openai/gpt-4o-mini",
        "openai/gpt-4o",
        "anthropic/claude-3-haiku",
        "anthropic/claude-3.1-sonnet",
        "meta-llama/llama-3.1-8b",
        "google/gemini-pro"
    ]
    selected_model = st.selectbox(
        "Model Selection",
        options=model_options,
        index=0,
        help="Choose the AI model from OpenRouter"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System Prompt
    st.markdown('<div class="section-margin">', unsafe_allow_html=True)
    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful AI assistant that provides clear, concise answers...",
        height=100,
        help="Define the AI's behavior and personality"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Context
    st.markdown('<div class="section-margin">', unsafe_allow_html=True)
    context = st.text_area(
        "Context",
        placeholder="Provide relevant background information here...",
        height=100,
        help="Add any background information relevant to your question"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Question
    st.markdown('<div class="section-margin">', unsafe_allow_html=True)
    question = st.text_input(
        "Question",
        placeholder="Ask your question here...",
        help="Enter your question or prompt"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Send Button
    st.markdown('<div class="section-margin">', unsafe_allow_html=True)
    if st.button("Send Message", type="primary", use_container_width=True):
        if question.strip():
            if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
                st.error("❌ Please configure your OpenRouter API key first")
            else:
                # Initialize OpenRouter agent
                agent = initialize_openrouter_agent(selected_model)
                if agent:
                    try:
                        # Prepare the prompt
                        full_prompt = f"System: {system_prompt}\n\nContext: {context}\n\nQuestion: {question}"
                        
                        # Add user message to history
                        st.session_state.chat_history.append({
                            "role": "user", 
                            "content": question
                        })
                        
                        # Get AI response from OpenRouter
                        with st.spinner("🤖 Getting response from AI..."):
                            response = asyncio.run(agent.run(full_prompt))
                            ai_response = str(response)
                        
                        # Add AI response to history
                        st.session_state.chat_history.append({
                            "role": "ai",
                            "content": ai_response
                        })
                        
                        st.session_state.current_response = ai_response
                        st.success("✅ Response received from OpenRouter!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error getting response: {str(e)}")
                        st.session_state.current_response = f"Error: {str(e)}"
                        st.rerun()

with col2:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.subheader("Response & History")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Current Response Area
    st.markdown('<div class="section-margin">', unsafe_allow_html=True)
    st.markdown("**Current Response**")
    response_container = st.container()
    st.markdown('</div>', unsafe_allow_html=True)
    
    with response_container:
        if st.session_state.current_response:
            if st.session_state.current_response.startswith("Error:"):
                st.error(f"💭 {st.session_state.current_response}")
            else:
                st.markdown(f"💭 {st.session_state.current_response}")
        else:
            st.info("💭 AI response will appear here after you send a message...")
    
    st.markdown("---")
    
    # Chat History
    st.markdown('<div class="section-margin">', unsafe_allow_html=True)
    with st.expander("📚 Previous Conversations", expanded=True):
        if st.session_state.chat_history:
            for i, message in enumerate(reversed(st.session_state.chat_history[-6:])):  # Show last 6 messages
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 User:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message ai-message">
                        <strong>🤖 AI:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No previous conversations yet.")

# Status Bar
st.markdown("---")
col_status1, col_status2, col_status3 = st.columns(3)

with col_status1:
    st.success("🔗 Connected to OpenRouter")

with col_status2:
    st.info("📊 Langfuse Analytics Active")

with col_status3:
    st.success("⚡ Ready")

# Footer information
st.markdown("---")
st.caption("This is a UI mockup. No real API integrations are implemented.")
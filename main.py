import streamlit as st
import time
import os
import json
from datetime import datetime
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
        
        # Set environment variables for OpenRouter
        os.environ["OPENAI_API_KEY"] = OPENROUTER_API_KEY
        os.environ["OPENAI_BASE_URL"] = OPENROUTER_BASE_URL
        
        model = OpenAIModel(model_name)
        return Agent(model)
    except Exception as e:
        st.error(f"❌ Failed to initialize OpenRouter agent: {str(e)}")
        return None

def export_conversation():
    """Export conversation history to JSON file"""
    if not st.session_state.chat_history:
        return None
    
    conversation_data = {
        "export_date": datetime.now().isoformat(),
        "model_used": st.session_state.get("last_model", "Unknown"),
        "conversation": st.session_state.chat_history
    }
    
    return json.dumps(conversation_data, indent=2)

def clear_conversation():
    """Clear conversation history"""
    st.session_state.chat_history = []
    st.session_state.current_response = ""
    st.success("🗑️ Conversation history cleared!")

def handle_api_error(error, model_name):
    """Handle different types of API errors with user-friendly messages"""
    error_msg = str(error).lower()
    
    if "rate limit" in error_msg or "quota" in error_msg:
        return f"⚠️ Rate limit exceeded for {model_name}. Please try again later or switch to a different model."
    elif "authentication" in error_msg or "unauthorized" in error_msg:
        return "🔑 Authentication failed. Please check your OpenRouter API key."
    elif "model not found" in error_msg:
        return f"❌ Model {model_name} is not available. Please select a different model."
    elif "timeout" in error_msg:
        return "⏰ Request timed out. Please try again."
    else:
        return f"❌ Error with {model_name}: {str(error)}"

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
        "gpt-4o-mini",
        "gpt-4o",
        "claude-3-haiku",
        "claude-3.1-sonnet",
        "llama-3.1-8b",
        "gemini-pro"
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
                        
                        # Track the model used
                        st.session_state.last_model = selected_model
                        
                        # Get AI response from OpenRouter
                        with st.spinner("🤖 Getting response from AI..."):
                            st.info(f"🔧 Using model: {selected_model}")
                            st.info(f"🔧 API Base URL: {OPENROUTER_BASE_URL}")
                            
                            response = asyncio.run(agent.run(full_prompt))
                            # Extract the actual content from AgentRunResult
                            ai_response = response.output if hasattr(response, 'output') else str(response)
                            
                            # Add AI response to history
                            st.session_state.chat_history.append({
                                "role": "ai",
                                "content": ai_response
                            })
                            
                            st.session_state.current_response = ai_response
                            st.success("✅ Response received from OpenRouter!")
                            st.rerun()
                            
                    except Exception as e:
                        # Use improved error handling
                        error_message = handle_api_error(e, selected_model)
                        st.error(error_message)
                        st.session_state.current_response = f"Error: {error_message}"
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
                # Display AI response with proper formatting
                st.markdown("💭 **AI Response:**")
                st.markdown(st.session_state.current_response)
        else:
            st.info("💭 AI response will appear here after you send a message...")
    
    st.markdown("---")
    
    # Conversation Management Controls
    st.markdown('<div class="section-margin">', unsafe_allow_html=True)
    col_export, col_clear = st.columns(2)
    
    with col_export:
        if st.button("📥 Export Chat", use_container_width=True):
            conversation_json = export_conversation()
            if conversation_json:
                st.download_button(
                    label="💾 Download JSON",
                    data=conversation_json,
                    file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            else:
                st.warning("No conversation to export")
    
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            clear_conversation()
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
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
                        <strong>🤖 AI:</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    # Display AI response with proper markdown formatting
                    st.markdown(message["content"])
        else:
            st.info("No previous conversations yet.")

# Performance & Status Section
st.markdown("---")
st.subheader("📊 Performance & Status")

col_status1, col_status2, col_status3 = st.columns(3)

with col_status1:
    if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_openrouter_api_key_here":
        st.success("🔗 Connected to OpenRouter")
    else:
        st.error("❌ OpenRouter not configured")

with col_status2:
    if st.session_state.chat_history:
        st.info(f"💬 {len(st.session_state.chat_history)} messages")
    else:
        st.info("💬 No messages yet")

with col_status3:
    if st.session_state.get("last_model"):
        st.success(f"🤖 Last model: {st.session_state.last_model}")
    else:
        st.success("⚡ Ready")

# Footer information
st.markdown("---")
st.caption("This is a UI mockup. No real API integrations are implemented.")
import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import hashlib
from dotenv import load_dotenv
import re

from components.ui import UIComponents
from components.rag import RAGComponents
from components.web_crawler import WebCrawler
from utils import FileUtils, TextProcessor, QuestionGenerator

load_dotenv()

class BitcoinL2RAG:
    def __init__(self):
        self.setup_page_config()
        self.csv_file_path = "data.csv"
        self.ui = UIComponents()
        self.rag = RAGComponents()
        self.web_crawler = WebCrawler()
        self.file_utils = FileUtils()
        self.text_processor = TextProcessor()
        self.question_generator = QuestionGenerator()
        
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Bitcoin L2 Research Assistant",
            page_icon="₿",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
    def check_csv_updates(self):
        """Check if CSV has been updated and refresh data if needed"""
        try:
            if os.path.exists(self.csv_file_path):
                current_hash = self.file_utils.get_file_hash(self.csv_file_path)
                
                if "csv_hash" not in st.session_state:
                    st.session_state.csv_hash = current_hash
                    return True
                
                if st.session_state.csv_hash != current_hash:
                    st.session_state.csv_hash = current_hash
                    # Clear existing vectors to force reload
                    if "vectors" in st.session_state:
                        del st.session_state.vectors
                    if "csv_data" in st.session_state:
                        del st.session_state.csv_data
                    if "web_documents" in st.session_state:
                        del st.session_state.web_documents
                    
                    st.markdown("""
                    <div class="update-status">
                        🔄 <strong>CSV Updated!</strong> Refreshing knowledge base with latest data...
                    </div>
                    """, unsafe_allow_html=True)
                    return True
            return False
        except Exception as e:
            st.error(f"Error checking CSV updates: {str(e)}")
            return False

    def initialize_components(self):
        """Initialize the RAG components"""
        # Check for CSV updates
        self.check_csv_updates()
        
        if "vectors" not in st.session_state:
            with st.spinner("🔄 Initializing Bitcoin L2 knowledge base..."):
                try:
                    # Initialize embeddings
                    success = self.rag.initialize_embeddings()
                    if not success:
                        return False
                    
                    # Load saved chat history if it exists
                    if "chat_history" in st.session_state and "session_id" in st.session_state:
                        try:
                            saved_messages = self.file_utils.load_chat_history(st.session_state.session_id)
                            if saved_messages:
                                # Add saved messages to the chat history
                                for msg in saved_messages:
                                    st.session_state.chat_history.add_message(msg)
                                st.info(f"📝 Loaded previous conversation with {len(saved_messages)//2} exchanges")
                        except Exception as e:
                            st.warning(f"Could not load chat history: {str(e)}")
                        
                    if not os.path.exists(self.csv_file_path):
                        st.error(f"❌ CSV file not found: {self.csv_file_path}")
                        st.info("📁 Please ensure the Bitcoin L2 CSV file is in the same directory as this script.")
                        return False
                    
                    # Load CSV data
                    self.rag.load_csv_data(self.csv_file_path)
                    
                    # No web crawling, just use empty list for web documents
                    st.session_state.web_documents = []
                    
                    # Create a placeholder for the success message
                    load_message = st.empty()
                    with load_message.container():
                        st.markdown("""
                        <div class="crawler-message">
                            <p>✅ Knowledge base initialized successfully!</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Create vector store
                    self.rag.create_vector_store()
                    
                    # Clear the success message after 3 seconds
                    time.sleep(3)
                    load_message.empty()
                    
                    return True
                    
                except Exception as e:
                    st.error(f"❌ Error initializing components: {str(e)}")
                    return False
        return True

    def display_sidebar_stats(self):
        """Display statistics in the sidebar"""
        st.sidebar.markdown("### 🔧 Settings")
        
        # API Key selection
        st.sidebar.markdown("#### 🔑 API Key Settings")
        api_key_option = st.sidebar.selectbox(
            "Choose API Key Source",
            options=["Default API Key", "Custom API Key"],
            key="api_key_option"
        )
        
        if api_key_option == "Custom API Key":
            custom_api_key = st.sidebar.text_input(
                "OpenRouter API Key", 
                type="password",
                key="custom_api_key",
                help="Enter your OpenRouter API Key. It will not be stored after the session ends."
            )
            if custom_api_key:
                # Store in session state to be used by RAG components
                st.session_state.openrouter_api_key = custom_api_key
            else:
                st.sidebar.warning("Please enter your API key")
                # Default to the environment variable if no custom key is provided
                st.session_state.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        else:
            # Use the default environment variable
            st.session_state.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
            
        # Model information
        st.sidebar.markdown(f"**Model:** Deepseek R1 0528 Qwen3 8B (free)")
        
        # Search parameters
        search_depth = st.sidebar.slider("Search Depth", 3, 15, 8)
        st.session_state.search_depth = search_depth
        
        # Display chat history in sidebar
        st.sidebar.markdown("### 💬 Chat History")
        if "chat_history" in st.session_state and st.session_state.chat_history.messages:
            messages = st.session_state.chat_history.messages
            history_items = []
            
            # Extract and format user questions
            for i, msg in enumerate(messages):
                if msg.type == "human":
                    # Create a unique key for this history item
                    key = f"hist_{i}_{hash(msg.content)}"[:20]
                    question = msg.content
                    display_text = question
                    if len(display_text) > 50:
                        display_text = display_text[:50] + "..."
                    
                    # Add to history items
                    history_items.append((key, question, display_text))
            
            # Show the number of questions
            if history_items:
                question_count = len(history_items)
                st.sidebar.markdown(f"**{question_count} question{'' if question_count == 1 else 's'} in this session**")
                st.sidebar.markdown("<small>Click on a question to reuse it</small>", unsafe_allow_html=True)
            
            # Display each history item with a button using the custom CSS class
            for key, full_question, display_text in history_items:
                # Manually create a styled button using HTML
                clicked = st.sidebar.button(
                    display_text, 
                    key=key, 
                    use_container_width=True
                )
                
                if clicked:
                    # When clicked, set it as the selected question
                    st.session_state["sample_question_selected"] = full_question
                    st.rerun()
        else:
            st.sidebar.markdown("No questions asked yet.")
        
        # Add a chat history clear button to sidebar
        if st.sidebar.button("🧹 Clear Chat"):
            if "chat_history" in st.session_state:
                st.session_state.chat_history.clear()
                
                # Also clear response data and any stored thinking processes
                if "response_data" in st.session_state:
                    del st.session_state.response_data
                
                # Clear all thinking and context keys
                keys_to_delete = []
                for key in st.session_state.keys():
                    if key.startswith("thinking_") or key.startswith("context_"):
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    del st.session_state[key]
                    
                st.rerun()

    def display_related_questions(self, previous_query):
        """Display AI-generated related questions based on previous query"""
        st.markdown("<div class='full-width-container'><h4>Related Questions</h4></div>", unsafe_allow_html=True)
        
        # Check if we have already generated questions for this query
        cache_key = f"related_questions_{hash(previous_query)}"
        if cache_key not in st.session_state:
            # Generate new related questions
            with st.spinner("Generating related questions..."):
                related_questions = self.question_generator.generate_related_questions(previous_query, max_questions=3)
                # Clean and truncate questions for uniform display
                cleaned_questions = []
                for q in related_questions:
                    # Remove explanatory text after periods or question marks if any
                    q_parts = re.split(r'(?<=[.?!])\s+', q, 1)
                    cleaned_questions.append(q_parts[0].strip())
                st.session_state[cache_key] = cleaned_questions
        else:
            # Use cached questions
            related_questions = st.session_state[cache_key]
        
        if not related_questions:
            st.info("No related questions available at the moment.")
            return
        
        # Create custom HTML buttons for related questions
        st.markdown('<div class="sample-questions-container">', unsafe_allow_html=True)
        cols = st.columns(3)
        
        # Create a unique key for tracking selection
        if "related_question_key" not in st.session_state:
            st.session_state.related_question_key = str(int(time.time()))
            
        for i, question in enumerate(related_questions):
            col_idx = i % 3
            with cols[col_idx]:
                # Show only the question in the button
                if st.button(question, key=f"related_{i}_{st.session_state.related_question_key}"):
                    # Store the selection in session state
                    st.session_state["sample_question_selected"] = question
                    # Rerun to apply the question to the input field
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    def main(self):
        """Main application function"""
        self.ui.load_custom_css()
        
        # Add additional CSS for sidebar chat history and professional header
        st.markdown("""
        <style>
        /* Bitcoin-themed professional header styling */
        .app-header {
            background: linear-gradient(135deg, #F7931A 0%, #FFD700 50%, #F7931A 100%);
            color: #0f1221;
            padding: 2.5rem 2rem;
            border-radius: var(--border-radius);
            margin: 0 auto 2.5rem auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: 0 10px 30px rgba(247, 147, 26, 0.3), 
                        0 0 0 1px rgba(247, 147, 26, 0.5),
                        inset 0 0 30px rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 215, 0, 0.5);
            position: relative;
            overflow: hidden;
            text-align: center;
            max-width: 90%;
        }
        
        /* Top darker bar */
        .app-header::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #d97301, #9c5900, #d97301);
            z-index: 5;
        }
        
        .app-header .header-content {
            position: relative;
            z-index: 2;
        }
        
        .app-header h1 {
            margin: 0;
            font-size: 3rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            justify-content: center;
            letter-spacing: 1px;
            color: #000000;
            text-shadow: 0px 1px 2px rgba(255,255,255,0.3);
        }
        
        .app-header h1 span.bitcoin-icon {
            font-size: 3.2rem;
            margin-right: 0.8rem;
            display: inline-block;
            color: #0f1221;
            -webkit-background-clip: text;
            background-image: linear-gradient(45deg, #0f1221, #1d2744);
            filter: drop-shadow(0px 1px 2px rgba(255,255,255,0.3));
            transform: translateY(-2px);
        }
        
        .app-header .subtitle {
            font-size: 1.3rem;
            margin-top: 0.6rem;
            font-weight: 600;
            color: #0f1221;
            opacity: 0.9;
            letter-spacing: 0.6px;
            text-shadow: 0px 1px 1px rgba(255,255,255,0.2);
        }
        
        /* Query header styling */
        .query-header {
            background: rgba(255, 255, 255, 0.05);
            border-left: 4px solid var(--primary);
            padding: 1rem 1.5rem;
            border-radius: var(--border-radius);
            margin-bottom: 1.5rem;
        }
        
        .query-header h3 {
            margin: 0;
            font-weight: 500;
        }
        
        /* Input container styling */
        .input-container {
            margin-bottom: 1.5rem;
        }
        
        /* Style the input field to look more professional */
        .stTextInput > div > div > input {
            border: 2px solid var(--primary);
            border-radius: var(--border-radius);
            padding: 1rem 1rem 1rem 2.5rem;
            font-size: 1.1rem;
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="%23F7931A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>');
            background-repeat: no-repeat;
            background-position: 12px center;
            box-shadow: 0 4px 8px rgba(247, 147, 26, 0.1);
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--primary-hover);
            box-shadow: 0 4px 16px rgba(247, 147, 26, 0.15);
            outline: none;
        }
        
        /* Enhanced input label styling */
        .stTextInput label {
            font-weight: 600;
            color: var(--primary);
            font-size: 1.25rem !important;
            margin-bottom: 8px !important;
            display: flex !important;
            align-items: center !important;
        }
        
        .stTextInput label .emoji-icon {
            font-size: 1.4rem;
            margin-right: 8px;
            display: inline-block;
        }
        
        /* Sidebar chat history styling for buttons */
        section[data-testid="stSidebar"] button.history-btn {
            background: rgba(255, 255, 255, 0.1);
            padding: 8px 10px;
            margin-bottom: 8px;
            border-radius: 5px;
            font-size: 0.9rem;
            border-left: 3px solid var(--primary);
            word-wrap: break-word;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: left;
            width: 100%;
            white-space: normal;
            height: auto;
            line-height: 1.2;
            color: white;
        }
        
        section[data-testid="stSidebar"] button.history-btn:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateX(2px);
        }
        
        /* Bitcoin pattern background */
        .bitcoin-pattern {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20"><rect width="20" height="20" fill="none"/><path d="M10.5,8.5l1.979,1.25l-1.959,1.25" fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.2)" stroke-width="0.5" /></svg>');
            background-size: 20px 20px;
            opacity: 0.5;
            z-index: 0;
        }
        
        /* Shine effect */
        .shine-effect {
            position: absolute;
            top: 0;
            left: -150%;
            width: 150%;
            height: 100%;
            background: linear-gradient(
                to right,
                rgba(255, 255, 255, 0) 0%,
                rgba(255, 255, 255, 0.3) 77%,
                rgba(255, 255, 255, 0.5) 92%,
                rgba(255, 255, 255, 0) 100%
            );
            transform: rotate(25deg);
            animation: shine 6s infinite;
            z-index: 1;
        }
        
        @keyframes shine {
            0% {
                left: -150%;
            }
            20% {
                left: 100%;
            }
            100% {
                left: 100%;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Generate a unique session id if not present
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(int(time.time()))
        
        # Professional header
        st.markdown("""
        <div class="app-header">
            <div class="bitcoin-pattern"></div>
            <div class="shine-effect"></div>
            <div class="header-content">
                <h1><span class="bitcoin-icon">₿</span> L2GPT</h1>
                <div class="subtitle">Bitcoin Layer 2 Research Assistant</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize components
        initialized = self.initialize_components()
        if not initialized:
            return
        
        # Sidebar
        self.display_sidebar_stats()
        
        # Main interface - updated to display current query instead of fixed header
        current_query = ""
        if "chat_history" in st.session_state and st.session_state.chat_history.messages:
            # Get the most recent user query if available
            for msg in reversed(st.session_state.chat_history.messages):
                if msg.type == "human":
                    current_query = msg.content
                    break
        
        # Display chat history if available
        if "chat_history" in st.session_state and st.session_state.chat_history.messages:
            # Get pairs of messages (user + AI response)
            messages = st.session_state.chat_history.messages
            i = 0
            while i < len(messages):
                if i + 1 < len(messages) and messages[i].type == "human" and messages[i+1].type == "ai":
                    # User message
                    user_content = messages[i].content
                    ai_content = messages[i+1].content
                    message_index = i // 2
                    
                    # Display user message with enhanced styling
                    st.markdown(f"""
                    <div class="chat-message user">
                        <div class="chat-icon">💬</div>
                        <div class="chat-content">{user_content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Check if this is the LATEST response in the chat history
                    is_latest_response = (i + 1 == len(messages) - 1)
                    
                    # Only show thinking process for previous responses (not the latest one)
                    # Latest one will be shown separately below the chat history
                    thinking_key = f"thinking_{message_index}"
                    if not is_latest_response and thinking_key in st.session_state and st.session_state[thinking_key]:
                        with st.expander("🧠 Reasoning", expanded=False):
                            st.markdown(f"""
                            <div class="thinking-process-container">
                                <div class="thinking-box">
                                    {st.session_state[thinking_key]}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # AI message
                    processed_content = self.text_processor.process_markdown(ai_content)
                    st.markdown(f"""
                    <div class="chat-message ai">
                        <div class="chat-icon">₿</div>
                        <div class="chat-content">{processed_content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show citations for this response if available, but not for the latest response
                    context_key = f"context_{message_index}"
                    if not is_latest_response and context_key in st.session_state and st.session_state[context_key]:
                        self.ui.display_citations({"context": st.session_state[context_key]})
                    
                    i += 2
                else:
                    # Handle odd messages (should be rare)
                    if messages[i].type == "human":
                        st.markdown(f"""
                        <div class="chat-message user">
                            <div class="chat-icon">👤</div>
                            <div class="chat-content">{messages[i].content}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        processed_content = self.text_processor.process_markdown(messages[i].content)
                        st.markdown(f"""
                        <div class="chat-message ai">
                            <div class="chat-icon">₿</div>
                            <div class="chat-content">{processed_content}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    i += 1
                    
            st.markdown("<hr style='margin: 20px 0; opacity: 0.2;'>", unsafe_allow_html=True)

        # Display additional information about the latest response if available
        if hasattr(st.session_state, 'response_data') and st.session_state.response_data:
            data = st.session_state.response_data
            
            # ALWAYS show thinking process for the current response
            if data['thinking']:
                with st.expander("🧠 Reasoning", expanded=False):
                    st.markdown(f"""
                    <div class="thinking-process-container">
                        <div class="thinking-box">
                            {data['thinking']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Display citations directly without the container box
            self.ui.display_citations(data)
            
            # Store thinking and context in session state for history
            if "chat_history" in st.session_state and hasattr(st.session_state.chat_history, "messages"):
                if len(st.session_state.chat_history.messages) > 0:
                    message_index = (len(st.session_state.chat_history.messages) // 2) - 1
                    if message_index >= 0:  # Safety check
                        thinking_key = f"thinking_{message_index}"
                        context_key = f"context_{message_index}"
                        st.session_state[thinking_key] = data['thinking']
                        st.session_state[context_key] = data['context']
        
        # After displaying data sources, show the input box for new questions
        
        # Store a fixed tab id to avoid input regeneration
        if "tab_id" not in st.session_state:
            st.session_state.tab_id = f"tab_{int(time.time())}"
            
        # Check for stored sample question
        if "sample_question_selected" in st.session_state:
            query = st.session_state["sample_question_selected"]
            # Clear it from session state so it doesn't persist across refreshes
            del st.session_state["sample_question_selected"]
        else:
            query = ""
            
        # Persistent input box with enhanced styling and emoji
        st.markdown("<div class='input-container'>", unsafe_allow_html=True)
        
        # Add custom CSS for the input label
        st.markdown("""
        <style>
        .question-label-container {
            padding: 5px 0;
            margin-bottom: 10px;
        }
        .question-label {
            font-size: 2rem;
            font-weight: 600;
            color: var(--primary);
            display: flex;
            align-items: center;
        }
        .question-label .emoji {
            font-size: 1.5rem;
            margin-right: 10px;
        }
        </style>
        <div class="question-label-container">
            <h2 class="question-label"><span class="emoji">💬</span> Enter your question</h2>
        </div>
        """, unsafe_allow_html=True)
        
        query = st.text_input(
            "",  # Empty label since we're using custom label
            value=query,
            key=f"user_query_{st.session_state.tab_id}",
            placeholder="e.g., Compare the security models of Lightning Network vs Liquid Network",
            help="Ask about Bitcoin L2 technologies, comparisons, metrics, or specific projects",
            label_visibility="collapsed"  # Hide the default label
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Check if there are any previous user queries
        has_previous_query = False
        most_recent_query = ""
        if "chat_history" in st.session_state and st.session_state.chat_history.messages:
            for msg in reversed(st.session_state.chat_history.messages):
                if msg.type == "human":
                    has_previous_query = True
                    most_recent_query = msg.content
                    break
        
        # Display appropriate questions based on user history
        if has_previous_query:
            # Show AI-generated related questions if user has asked before
            self.display_related_questions(most_recent_query)
        else:
            # Show sample questions for new users
            self.ui.display_sample_questions()
        
        # Create a clean separation before results
        st.markdown("<hr style='margin: 30px 0; opacity: 0.2;'>", unsafe_allow_html=True)
        
        # Create placeholder for results 
        results_placeholder = st.empty()
        
        # Track query processing with a fingerprint to avoid duplicates
        if "query_fingerprint" not in st.session_state:
            st.session_state.query_fingerprint = ""
        
        # Process query if it's new
        # Check if we need to regenerate a response
        regenerate_query = st.session_state.get("regenerate_query", "")
        if regenerate_query:
            query = regenerate_query
            # Clear the regenerate flag
            del st.session_state.regenerate_query
        
        current_fingerprint = f"{query}_{st.session_state.tab_id}"
        is_new_query = current_fingerprint != st.session_state.query_fingerprint
        
        if query and (is_new_query or regenerate_query):
            with st.spinner("🔍 Analyzing Bitcoin L2 data..."):
                try:
                    # Update fingerprint
                    st.session_state.query_fingerprint = current_fingerprint
                    
                    start_time = time.process_time()
                    
                    # Create retrieval chain and get response
                    response = self.rag.process_query(query)
                    
                    # Store data for display
                    st.session_state.response_data = {
                        'query': query,
                        'answer': response['answer'],
                        'thinking': response['thinking'],
                        'context': response['context'],
                        'processing_time': time.process_time() - start_time,
                        'response_id': f"response_{int(time.time())}"
                    }
                    
                    # Save chat history after each response
                    if "chat_history" in st.session_state and st.session_state.chat_history.messages:
                        self.file_utils.save_chat_history(
                            st.session_state.chat_history.messages, 
                            st.session_state.session_id
                        )
                    
                    # Trigger a rerun to display updated chat history
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
                    st.session_state.response_data = None
                
        # Add feedback buttons at the bottom if there's a response
        if hasattr(st.session_state, 'response_data') and st.session_state.response_data:
            data = st.session_state.response_data
                
            # Add feedback buttons
            st.markdown("### Was this response helpful?")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("👍 Yes", key=f"yes_{data['response_id']}"):
                    self.file_utils.save_feedback("positive", query=data['query'])
                    st.success("Thanks for your feedback!")
            
            with col2:
                if st.button("👎 No", key=f"no_{data['response_id']}"):
                    st.session_state.show_feedback = True
                    
            with col3:
                if st.button("🔄 Regenerate", key=f"regenerate_{data['response_id']}"):
                    # Clear fingerprint to allow regeneration
                    st.session_state.query_fingerprint = ""
                    # Remove the last AI message from chat history to allow regeneration
                    if "chat_history" in st.session_state and st.session_state.chat_history.messages:
                        # Get the last message and check if it's an AI message
                        if len(st.session_state.chat_history.messages) > 0 and st.session_state.chat_history.messages[-1].type == "ai":
                            # Pop the last message (AI's response)
                            st.session_state.chat_history.messages.pop()
                    # Store the last query for reprocessing
                    st.session_state.regenerate_query = data['query']
                    # Rerun with the same query
                    st.rerun()
            
            # Handle detailed feedback
            if st.session_state.get('show_feedback', False):
                with st.expander("Tell us what could be improved", expanded=True):
                    feedback = st.text_area("Your feedback:", key="feedback_text", max_chars=500)
                    if st.button("Submit Feedback"):
                        if feedback:
                            self.file_utils.save_feedback("negative", feedback, data['query'])
                            st.success("Thank you for your feedback! We'll use it to improve our assistant.")
                            st.session_state.show_feedback = False
                            # Clear the text area
                            st.session_state.feedback_text = ""
                        else:
                            st.warning("Please provide some feedback before submitting.") 
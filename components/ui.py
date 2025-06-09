import streamlit as st
import time
from datetime import datetime
from urllib.parse import urlparse
import re

class UIComponents:
    def __init__(self):
        pass
        
    def load_custom_css(self):
        """Load custom CSS for professional styling"""
        st.markdown("""
        <style>
        /* Modern color palette */
        :root {
            --primary: #F7931A;
            --primary-hover: #E77D00;
            --secondary: #1E3A8A;
            --light-bg: #F3F4F6;
            --dark-bg: #0F172A;
            --dark-accent: #1E293B;
            --light-text: #F9FAFB;
            --dark-text: #111827;
            --border-radius: 10px;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --code-bg: #1a1e29;
            --code-accent: #252a3a;
            --code-text: #e9ecef;
        }
        
        /* Global styles */
        body {
            background-color: var(--light-bg);
            color: var(--dark-text);
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        /* Main header styles */
        .main-header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
            color: var(--light-text);
            padding: 2rem;
            border-radius: var(--border-radius);
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: var(--shadow);
        }
        
        .main-header h1 {
            font-size: 2.2rem;
            margin-bottom: 0.5rem;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
        }
        
        .main-header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        /* Chat message styling with improved design */
        .chat-message {
            display: flex;
            margin: 1.2rem 0;
            padding: 1rem;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .chat-message.user {
            background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
            margin-right: 4rem;
            border-left: 4px solid #2563EB;
            border-top-left-radius: 0;
            box-shadow: 0 4px 10px rgba(30, 58, 138, 0.15);
        }
        
        .chat-message.user .chat-content {
            color: #1E3A8A;
            font-weight: 600;
            font-size: 1.05rem;
        }
        
        .chat-message.ai {
            background: linear-gradient(135deg, var(--dark-bg) 0%, var(--dark-accent) 100%);
            color: var(--light-text);
            margin-left: 4rem;
            border-right: 4px solid var(--primary);
            border-top-right-radius: 0;
        }
        
        .chat-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 2.5rem;
            height: 2.5rem;
            border-radius: 50%;
            margin-right: 1rem;
            font-size: 1.2rem;
        }
        
        .chat-message.user .chat-icon {
            background-color: var(--secondary);
            color: black;
        }
        
        .chat-message.ai .chat-icon {
            background-color: var(--primary);
            color: white;
        }
        
        .chat-content {
            flex-grow: 1;
            padding: 0.3rem;
            overflow-wrap: break-word;
            word-break: break-word;
            line-height: 1.5;
        }
        
        /* Enhanced Markdown Styling */
        .markdown-content {
            font-size: 1.05rem;
            line-height: 1.6;
            color: inherit;
        }
        
        .markdown-content p {
            margin-bottom: 1rem;
        }
        
        .markdown-content strong {
            font-weight: 700;
            color: #FFF;
        }
        
        .markdown-content em {
            font-style: italic;
            opacity: 0.85;
        }
        
        .markdown-content .markdown-h1,
        .markdown-content .markdown-h2,
        .markdown-content .markdown-h3,
        .markdown-content .markdown-h4,
        .markdown-content .markdown-h5,
        .markdown-content .markdown-h6 {
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            font-weight: 700;
            line-height: 1.2;
        }
        
        .markdown-content .markdown-h1 {
            font-size: 2rem;
            border-bottom: 2px solid var(--primary);
            padding-bottom: 0.3rem;
        }
        
        .markdown-content .markdown-h2 {
            font-size: 1.8rem;
            border-bottom: 1px solid rgba(247, 147, 26, 0.5);
            padding-bottom: 0.2rem;
        }
        
        .markdown-content .markdown-h3 {
            font-size: 1.5rem;
            color: var(--primary);
        }
        
        .markdown-content .markdown-h4 {
            font-size: 1.3rem;
        }
        
        .markdown-content .markdown-h5 {
            font-size: 1.1rem;
        }
        
        .markdown-content .markdown-h6 {
            font-size: 1rem;
            color: rgba(255, 255, 255, 0.7);
        }
        
        /* Lists styling */
        .markdown-content ul,
        .markdown-content ol {
            padding-left: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .markdown-content li {
            margin-bottom: 0.5rem;
        }
        
        .markdown-content ul li {
            list-style-type: disc;
        }
        
        .markdown-content ol li {
            list-style-type: decimal;
        }
        
        /* Code blocks styling */
        .code-block-wrapper {
            margin: 1rem 0;
            border-radius: var(--border-radius);
            overflow: hidden;
            background: var(--code-bg);
            box-shadow: 0 3px 6px rgba(0,0,0,0.2);
        }
        
        .code-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--code-accent);
            padding: 0.5rem 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .code-language {
            font-family: monospace;
            font-size: 0.9rem;
            color: var(--primary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .code-block {
            margin: 0;
            padding: 1rem;
            background: var(--code-bg);
            overflow-x: auto;
        }
        
        .markdown-content code {
            font-family: 'Consolas', 'Monaco', 'Andale Mono', monospace;
            color: var(--code-text);
        }
        
        .inline-code {
            background: rgba(247, 147, 26, 0.2);
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 0.9em !important;
            border: 1px solid rgba(247, 147, 26, 0.3);
            color: #ffcc80 !important;
            font-family: 'Consolas', 'Monaco', 'Andale Mono', monospace;
        }
        
        /* Blockquote styling */
        .markdown-content blockquote {
            border-left: 4px solid var(--primary);
            padding: 0.8rem 1.2rem;
            margin: 1rem 0;
            background: rgba(255,255,255,0.05);
            border-radius: 0 var(--border-radius) var(--border-radius) 0;
            font-style: italic;
        }
        
        /* Horizontal rule styling */
        .markdown-hr {
            border: 0;
            height: 1px;
            background: linear-gradient(to right, transparent, var(--primary), transparent);
            margin: 2rem 0;
        }
        
        /* Table styling */
        .markdown-table {
            width: 100%;
            margin: 1.5rem 0;
            border-collapse: separate;
            border-spacing: 0;
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        
        .markdown-table thead {
            background: var(--primary);
            color: var(--dark-bg);
        }
        
        .markdown-table th {
            font-weight: 700;
            text-align: left;
            padding: 0.75rem 1rem;
        }
        
        .markdown-table tbody tr {
            background: rgba(255,255,255,0.05);
            transition: background 0.2s ease;
        }
        
        .markdown-table tbody tr:nth-child(odd) {
            background: rgba(255,255,255,0.02);
        }
        
        .markdown-table tbody tr:hover {
            background: rgba(247, 147, 26, 0.1);
        }
        
        .markdown-table td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        /* Links styling */
        .markdown-link {
            color: var(--primary);
            text-decoration: none;
            border-bottom: 1px dashed var(--primary);
            transition: all 0.2s ease;
        }
        
        .markdown-link:hover {
            color: var(--primary-hover);
            border-bottom-style: solid;
        }
        
        .chat-message.ai .chat-content code {
            background: rgba(247, 147, 26, 0.2);
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 0.9em;
            border: 1px solid rgba(247, 147, 26, 0.3);
            color: #ffcc80;
        }
        
        .chat-message.ai .chat-content a {
            color: var(--primary);
            text-decoration: none;
        }
        
        .chat-message.ai .chat-content a:hover {
            text-decoration: underline;
        }
        
        /* Citation box with improved design */
        .citation-box {
            background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
            border: 2px solid var(--secondary);
            border-radius: var(--border-radius);
            padding: 1.5rem;
            margin: 1.5rem 0;
            box-shadow: var(--shadow);
        }
        
        .citation-box h4 {
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--secondary);
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .citation-box h4::before {
            content: "🔍";
            font-size: 1.2em;
            margin-right: 0.5rem;
        }
        
        /* Button styling */
        .stButton > button {
            background-color: var(--primary);
            color: var(--light-text);
            border: none;
            border-radius: calc(var(--border-radius) / 2);
            padding: 0.8rem 1rem;
            font-weight: 600;
            white-space: normal;
            height: auto;
            text-align: center;
            line-height: 1.4;
            min-height: 60px !important;
            transition: all 0.2s ease;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            display: -webkit-box !important;
            -webkit-line-clamp: 2 !important;
            -webkit-box-orient: vertical !important;
            margin-bottom: 0 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stButton > button:hover {
            background-color: var(--primary-hover);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            cursor: pointer;
        }
        
        /* Enhanced input styling */
        .stTextInput > div > div > input {
            border: 2px solid var(--primary);
            border-radius: var(--border-radius);
            padding: 1rem;
            font-size: 1.1rem;
            box-shadow: 0 4px 8px rgba(247, 147, 26, 0.1);
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--primary-hover);
            box-shadow: 0 4px 16px rgba(247, 147, 26, 0.15);
        }
        
        /* Sample questions styling */
        .sample-questions-container {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            width: 100%;
            margin: 1rem 0;
        }
        
        .sample-question-button {
            flex: 1 1 calc(33.33% - 12px);
            min-width: 250px;
            background: linear-gradient(135deg, var(--dark-bg) 0%, var(--dark-accent) 100%);
            color: var(--light-text);
            border: 1px solid var(--primary);
            border-radius: var(--border-radius);
            padding: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: left;
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
            margin-bottom: 0.5rem;
        }
        
        .sample-question-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            border-color: var(--primary-hover);
        }
        
        /* Source code and thinking box */
        .thinking-box {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(252, 211, 77, 0.3);
            border-radius: var(--border-radius);
            padding: 1rem;
            font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
            font-size: 0.9rem;
            color: #E5E7EB;
            overflow-x: auto;
            line-height: 1.5;
        }
        
        /* Expanders styling */
        .streamlit-expanderHeader {
            background-color: #F8FAFC;
            border-radius: var(--border-radius);
            padding: 0.5rem 1rem;
            font-weight: 600;
            color: var(--secondary);
            transition: all 0.2s ease;
        }
        
        .streamlit-expanderHeader:hover {
            background-color: #F1F5F9;
        }
        
        /* Other styles */
        a {
            color: var(--primary);
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        .stMarkdown a {
            color: var(--primary);
            text-decoration: none;
        }
        
        .full-width-container {
            width: 100%;
            max-width: 100%;
            padding: 0;
            margin-bottom: 1.5rem;
        }
        
        hr {
            border: 0;
            height: 1px;
            background: #E5E7EB;
            margin: 1.5rem 0;
        }
        
        /* Info boxes */
        .info-box, .update-status {
            background-color: #EFF6FF;
            border-left: 4px solid var(--secondary);
            color: var(--secondary);
            padding: 1rem;
            border-radius: calc(var(--border-radius) / 2);
            margin: 1rem 0;
            box-shadow: var(--shadow);
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            border-right: none;
            padding: 1.5rem 1rem;
            color: var(--light-text);
        }
        
        section[data-testid="stSidebar"] h3 {
            color: var(--primary);
            font-size: 1.3rem;
            margin-top: 1.5rem;
            font-weight: 600;
            border-bottom: 1px solid rgba(247, 147, 26, 0.3);
            padding-bottom: 0.5rem;
        }
        
        section[data-testid="stSidebar"] .stSlider label {
            color: var(--light-text);
        }
        
        section[data-testid="stSidebar"] button {
            width: 100%;
            margin-bottom: 0.5rem;
            background: rgba(247, 147, 26, 0.8);
            border: none;
            color: white;
            transition: all 0.2s ease;
        }
        
        section[data-testid="stSidebar"] button:hover {
            background: rgba(247, 147, 26, 1);
            transform: translateY(-2px);
        }
        
        section[data-testid="stSidebar"] .stMetric {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 0.5rem;
            border-radius: var(--border-radius);
            margin-bottom: 0.5rem;
        }
        
        section[data-testid="stSidebar"] .stMetric label {
            color: var(--primary) !important;
        }
        
        section[data-testid="stSidebar"] .stMetric div {
            color: white !important;
        }
        
        /* Data sources box styling */
        .data-sources-container {
            background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
            border: 2px solid #3B82F6;
            border-radius: var(--border-radius);
            padding: 1.5rem;
            margin: 1.5rem 0;
            box-shadow: var(--shadow);
        }
        
        .data-sources-container h3 {
            color: #3B82F6;
            font-size: 1.3rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
        }
        
        .data-sources-container h3:before {
            content: "🔍";
            margin-right: 0.5rem;
            font-size: 1.2rem;
        }
        
        /* Thinking box improvement */
        .thinking-process-container {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            border-left: 4px solid #FCD34D;
            border-radius: var(--border-radius);
            padding: 1.5rem;
            margin: 1rem 0;
            color: white;
            box-shadow: var(--shadow);
        }
        
        /* Style for expanders with thinking process */
        .streamlit-expanderHeader {
            font-weight: 600;
            color: #FCD34D;
            background-color: #0F172A;
            border-radius: var(--border-radius);
            padding: 0.75rem 1rem;
            margin-bottom: 0.5rem;
            transition: all 0.2s ease;
        }
        
        .streamlit-expanderHeader:hover {
            background-color: #1E293B;
        }
        
        /* Streamlit expander content needs padding fix */
        .streamlit-expanderContent {
            padding-left: 0 !important;
            padding-right: 0 !important;
        }
        
        .thinking-box {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(252, 211, 77, 0.3);
            border-radius: var(--border-radius);
            padding: 1rem;
            font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
            font-size: 0.9rem;
            color: #E5E7EB;
            overflow-x: auto;
            line-height: 1.5;
            white-space: pre-wrap;
        }
                                                                                                                                                                                                                                                                                                                                                                                    
        /* Metadata table styling */
        .metadata-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 1rem 0;
            background: rgba(15, 23, 42, 0.95);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            border: 1px solid rgba(247, 147, 26, 0.2);
        }
        .metadata-table th {
            background: rgba(247, 147, 26, 0.2);
            color: #F7931A;
            text-align: left;
            padding: 14px 18px;
            font-weight: 600;
            letter-spacing: 0.5px;
            font-size: 1.05rem;
            text-transform: uppercase;
            border-bottom: 2px solid rgba(247, 147, 26, 0.3);
        }
        .metadata-table td {
            padding: 12px 18px;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            color: #F9FAFB;
            font-size: 1.02rem;
        }
        .metadata-table tr:last-child td {
            border-bottom: none;
        }
        .metadata-table .icon {
            margin-right: 10px;
            opacity: 1;
            font-size: 1.1rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 24px;
            height: 24px;
        }
        .metadata-badge {
            display: inline-block;
            background: rgba(247, 147, 26, 0.15);
            color: #F7931A;
            padding: 5px 10px;
            border-radius: 6px;
            margin: 3px;
            font-size: 0.95rem;
            font-weight: 500;
            border: 1px solid rgba(247, 147, 26, 0.2);
            transition: all 0.2s ease;
        }
        .metadata-badge:hover {
            background: rgba(247, 147, 26, 0.25);
            transform: translateY(-1px);
        }
        .metadata-table tr:nth-child(odd) {
            background: rgba(255, 255, 255, 0.03);
        }
        .metadata-table a {
            text-decoration: none;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .metadata-table a:hover {
            text-decoration: underline;
            opacity: 0.9;
        }
        .metadata-header {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            color: #F7931A;
        }
        .metadata-header .icon {
            margin-right: 10px;
            font-size: 1.6rem;
        }
        </style>
        """, unsafe_allow_html=True)

    def display_sample_questions(self):
        """Display sample question buttons"""
        # Sample questions
        st.markdown("<div class='full-width-container'><h4>Sample Questions</h4></div>", unsafe_allow_html=True)
        
        sample_questions = [
            "Compare trust assumptions of Tachi vs Lightning Network",
            "What consensus mechanisms are used by Bitcoin L2s?",
            "Which Bitcoin L2 solutions support smart contracts?",
            "How do fee structures differ across Bitcoin L2 networks?",
            "What's the maturity status of Bitcoin scaling solutions?", 
            "How does Ark's onboarding compare to Liquid Network?"
        ]
        
        # Create custom HTML buttons for sample questions
        st.markdown('<div class="sample-questions-container">', unsafe_allow_html=True)
        cols = st.columns(3)
        
        # Create a unique key for tracking selection
        if "sample_question_key" not in st.session_state:
            st.session_state.sample_question_key = str(int(time.time()))
            
        for i, question in enumerate(sample_questions):
            col_idx = i % 3
            with cols[col_idx]:
                # Show only the question in button
                if st.button(question, key=f"sample_{i}_{st.session_state.sample_question_key}"):
                    # Store the selection in session state
                    st.session_state["sample_question_selected"] = question
                    # Rerun to apply the question to the input field
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    def create_copy_button(self, text_to_copy, key):
        """Create a simple, reliable copy solution for Streamlit"""
        # Simple container for the copy section
        copy_container = st.container()
        
        with copy_container:
            # Add a clear separator
            st.markdown("<hr style='margin: 15px 0 20px 0; opacity: 0.2;'>", unsafe_allow_html=True)
            
            # Create columns for layout
            col1, col2 = st.columns([4, 1])
            
            # Title in the first column
            with col1:
                st.markdown("### 📋 Copy Response")
            
            # Put the copy button in the second column
            with col2:
                st.download_button(
                    label="Download",
                    data=text_to_copy,
                    file_name="bitcoin_l2_response.txt",
                    mime="text/plain",
                    key=f"dl_{key}"
                )
            
            # Put the selectable text in a code block
            st.code(text_to_copy, language=None)
            
            # Instructions
            st.caption("Select the text above and press Ctrl+C (or ⌘+C on Mac) to copy, or use the Download button.")
        
        return ""

    def display_results(self, data, results_placeholder, text_processor):
        """Display query results in a formatted manner"""
        with results_placeholder.container():
            # Results header
            st.markdown("### 🎯 Analysis Results")
            
            # Show thinking process in collapsible section
            if data.get('thinking'):
                with st.expander("🧠 Reasoning", expanded=False):
                    html_thinking = data['thinking'].replace("\n", "<br>")
                    st.markdown(f"""
                    <div class="thinking-process-container">
                        <h4>DeepSeek R1 Thinking Process</h4>
                        {html_thinking}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Format and display the main response
            response_text = data['answer'] 
            
            # Check for a title header pattern at the beginning
            title_match = re.match(r"^\*\*(.+?)\*\*[\s\\n]*", response_text)
            if title_match:
                header = title_match.group(1)
                rest = response_text[title_match.end():].lstrip()
                
                # Process the rest of the content with enhanced markdown processing
                processed_content = text_processor.process_markdown(rest)
                
                # Combine with header
                response_html = f'<div class="response-header">{header}</div>{processed_content}'
            else:
                # No header, process everything
                response_html = text_processor.process_markdown(response_text)
            
            # Generate a unique response ID for this instance
            response_id = f"response_{int(time.time())}_{hash(data['answer'])}"[:20]
            
            # Display the response box
            st.markdown(f"""
            <div class="response-box">
                {response_html}
            </div>
            """, unsafe_allow_html=True)
            
            # Generation info 
            st.markdown(f"""
            <div class="generation-info">
                ⏱️ <strong>Processing Time:</strong> {data['processing_time']:.2f}s | 
                🤖 <strong>Model:</strong> DeepSeek R1 Distill 70B | 
                📚 <strong>Sources:</strong> {len(data['context'])} documents
            </div>
            """, unsafe_allow_html=True)
            
            # Like/Dislike buttons
            st.markdown("""
            <div style="display: flex; gap: 10px; margin: 15px 0;">
                <div style="flex: 1; text-align: center;">
                    <button onclick="alert('Thanks for your feedback!')" style="background: none; border: none; font-size: 24px; cursor: pointer;">
                        👍
                    </button>
                </div>
                <div style="flex: 1; text-align: center;">
                    <button onclick="alert('Thanks for your feedback!')" style="background: none; border: none; font-size: 24px; cursor: pointer;">
                        👎
                    </button>
                </div>
                <div style="flex: 6;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Citations and sources
            self.display_citations(data)

    def display_citations(self, data):
        """Display citations and sources for the response"""
        # Define Bitcoin L2 project names to look for
        l2_projects = {
            'Lightning', 'Liquid', 'Rootstock', 'RSK', 'Stacks', 'Ark', 'Tachi', 
            'Bitlayer', 'BitcoinOS', 'Babylon', 'Merlin', 'CoreDAO', 'Arch'
        }
        
        # Extract citations
        citations = {
            'sources': [],
            'links': [],
            'projects_mentioned': set()
        }
        
        for doc in data['context']:
            content = doc.page_content.lower()
            
            # Extract links
            links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', doc.page_content)
            citations['links'].extend(links)
            
            # Extract project mentions
            for project in l2_projects:
                if project.lower() in content:
                    citations['projects_mentioned'].add(project)
            
            # Add source info
            if hasattr(doc, 'metadata'):
                if 'source' in doc.metadata:
                    citations['sources'].append(doc.metadata['source'])
                if 'url' in doc.metadata:
                    citations['links'].append(doc.metadata['url'])
        
        # Remove duplicates
        citations['links'] = list(set(citations['links']))
        
        # Create metadata table with all information
        st.markdown('<div class="metadata-header"><span class="icon">👁️</span>Response Metadata</div>', unsafe_allow_html=True)
        
        # Prepare projects list as badges
        projects_html = ""
        for project in sorted(citations['projects_mentioned']):
            projects_html += f'<span class="metadata-badge">{project}</span> '
        
        if not projects_html:
            projects_html = "<em>None referenced</em>"
        
        # Prepare links list (limit to 3)
        links_html = ""
        for i, link in enumerate(citations['links'][:3]):
            domain = urlparse(link).netloc
            links_html += f'<a href="{link}" target="_blank" style="color:#F7931A;">{domain}</a>'
            if i < min(len(citations['links'][:3])-1, 2):
                links_html += ", "
        
        if not links_html:
            links_html = "<em>None found</em>"
        elif len(citations['links']) > 3:
            links_html += f" <em>and {len(citations['links'])-3} more</em>"
        
        # Get processing time and source count from the data
        processing_time = data.get('processing_time', 0)
        sources_count = len(data['context'])
        
        # Build table HTML
        table_html = f"""
        <table class="metadata-table">
            <tr>
                <th width="25%">Metric</th>
                <th>Details</th>
            </tr>
            <tr>
                <td><span class="icon">⏱️</span> Processing Time</td>
                <td>{processing_time:.2f}s</td>
            </tr>
            <tr>
                <td><span class="icon">🔍</span> Sources Analyzed</td>
                <td>{sources_count}</td>
            </tr>
            <tr>
                <td><span class="icon">₿</span> L2 Projects Referenced</td>
                <td>{projects_html}</td>
            </tr>
            <tr>
                <td><span class="icon">🔗</span> Reference Links</td>
                <td>{links_html}</td>
            </tr>
        </table>
        """
        
        st.markdown(table_html, unsafe_allow_html=True) 
import hashlib
import re
import os
import json
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
import traceback
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class FileUtils:
    """Utility class for file operations"""
    
    def __init__(self):
        self.chat_history_dir = "chat_history"
        self.feedback_dir = os.path.join(self.chat_history_dir, "feedback")
        
        # Create directories if they don't exist
        os.makedirs(self.chat_history_dir, exist_ok=True)
        os.makedirs(self.feedback_dir, exist_ok=True)
        
    def get_file_hash(self, file_path):
        """Get a hash of the file contents"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def save_chat_history(self, messages, session_id):
        """Save chat history to a JSON file"""
        try:
            file_path = os.path.join(self.chat_history_dir, f"{session_id}.json")
            with open(file_path, "w") as f:
                json.dump(messages, f, default=lambda x: x.__dict__)
            return True
        except Exception as e:
            print(f"Error saving chat history: {str(e)}")
            return False
    
    def load_chat_history(self, session_id):
        """Load chat history from a JSON file"""
        try:
            file_path = os.path.join(self.chat_history_dir, f"{session_id}.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading chat history: {str(e)}")
            return []
    
    def save_feedback(self, feedback_type, feedback_text="", query=""):
        """Save user feedback to a file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_path = os.path.join(self.feedback_dir, f"{feedback_type}_{timestamp}.json")
            
            feedback_data = {
                "timestamp": timestamp,
                "type": feedback_type,
                "feedback": feedback_text,
                "query": query
            }
            
            with open(file_path, "w") as f:
                json.dump(feedback_data, f)
            return True
        except Exception as e:
            print(f"Error saving feedback: {str(e)}")
            return False

class TextProcessor:
    """Utility class for text processing"""
    
    def __init__(self):
        pass
        
    def clean_csv_content(self, text):
        """Clean CSV content for better display"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove URL prefixes to shorten display
        text = re.sub(r'https?://(?:www\.)?', '', text)
        
        return text
    
    def process_markdown(self, text):
        """Process markdown for better display in Streamlit"""
        if not text:
            return ""
        
        # Handle headings (h1-h6)
        for i in range(6, 0, -1):
            pattern = r'^{} (.*?)$'.format('#' * i)
            replacement = r'<h{0} class="markdown-h{0}">\1</h{0}>'.format(i)
            text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
        
        # Replace double asterisks with proper HTML bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # Replace single asterisks with proper HTML italic
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # Process code blocks with proper syntax highlighting
        text = re.sub(r'```(\w*)\n(.*?)\n```', self._process_code_block, text, flags=re.DOTALL)
        
        # Process inline code
        text = re.sub(r'`(.*?)`', r'<code class="inline-code">\1</code>', text)
        
        # Convert markdown links to HTML links with styling
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank" class="markdown-link">\1</a>', text)
        
        # Process numbered lists
        numbered_list_pattern = re.compile(r'^(\d+)\.\s+(.*?)$', re.MULTILINE)
        if numbered_list_pattern.search(text):
            # Start an ordered list
            text = numbered_list_pattern.sub(r'<li>\2</li>', text)
            # Ensure proper list structure by adding <ol> and </ol> tags
            text = re.sub(r'(?<!<ol>)\s*<li>', r'<ol><li>', text, count=1)
            text = re.sub(r'</li>\s*(?!<li>|</ol>)', r'</li></ol>', text)
        
        # Process bullet points (unordered lists) with improved regex
        text = re.sub(r'^- (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        if '<li>' in text and '<ol>' not in text:  # Only add <ul> tags if not already part of an ordered list
            # Add proper list structure
            text = re.sub(r'(?<!<ul>)<li>', r'<ul><li>', text, count=1)
            text = re.sub(r'</li>\s*(?!<li>|</ul>)', r'</li></ul>', text)
        
        # Process horizontal rules
        text = re.sub(r'^---+$', r'<hr class="markdown-hr">', text, flags=re.MULTILINE)
        
        # Process blockquotes
        text = re.sub(r'^>\s+(.*?)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
        
        # Handle tables (basic implementation)
        if '|' in text and '-|-' in text:
            lines = text.split('\n')
            table_start = None
            table_end = None
            
            # Find table boundaries
            for i, line in enumerate(lines):
                if '|' in line:
                    if table_start is None:
                        table_start = i
                    table_end = i
                elif table_end is not None and table_start is not None and i > table_end + 1:
                    # Gap found after table
                    break
            
            if table_start is not None and table_end is not None:
                table_lines = lines[table_start:table_end+1]
                header_separator_idx = None
                
                # Find header separator line
                for i, line in enumerate(table_lines):
                    if '-|-' in line or '|-|' in line or '|-' in line or '-|' in line:
                        header_separator_idx = i
                        break
                
                if header_separator_idx is not None:
                    # Build HTML table
                    html_table = "<table class='markdown-table'>"
                    
                    # Process header
                    if header_separator_idx > 0:  # There is a header row
                        html_table += "<thead><tr>"
                        header_cells = table_lines[0].split('|')
                        for cell in header_cells:
                            if cell.strip():  # Skip empty cells (from starting/ending |)
                                html_table += f"<th>{cell.strip()}</th>"
                        html_table += "</tr></thead>"
                    
                    # Process body
                    html_table += "<tbody>"
                    for i, line in enumerate(table_lines):
                        if i != header_separator_idx and (header_separator_idx == 0 or i != 0):
                            html_table += "<tr>"
                            cells = line.split('|')
                            for cell in cells:
                                if cell.strip():  # Skip empty cells
                                    html_table += f"<td>{cell.strip()}</td>"
                            html_table += "</tr>"
                    html_table += "</tbody></table>"
                    
                    # Replace the table in the original text
                    table_text = '\n'.join(lines[table_start:table_end+1])
                    text = text.replace(table_text, html_table)
        
        # Add proper paragraph breaks
        text = re.sub(r'\n\n(?!<)', r'</p><p>', text)
        
        # If the text doesn't start with an HTML tag, wrap it in <p>
        if not text.startswith(('<h', '<ul', '<ol', '<pre', '<blockquote', '<table', '<p')):
            text = '<p>' + text
        
        # If the text doesn't end with an HTML closing tag, add </p>
        if not text.endswith(('</h1>', '</h2>', '</h3>', '</h4>', '</h5>', '</h6>', '</ul>', '</ol>', '</pre>', '</blockquote>', '</table>', '</p>')):
            text = text + '</p>'
        
        # Fix any double paragraph tags
        text = re.sub(r'<p><p>', '<p>', text)
        text = re.sub(r'</p></p>', '</p>', text)
        
        # Remove empty paragraphs
        text = re.sub(r'<p>\s*</p>', '', text)
        
        # Add responsive styling hooks
        text = f'<div class="markdown-content">{text}</div>'
        
        return text
        
    def _process_code_block(self, match):
        """Helper function to process code blocks with enhanced styling"""
        language = match.group(1) or "plaintext"
        code = match.group(2)
        
        # Ensure code is properly escaped for HTML
        code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Create a formatted code block with language label and copy button
        return f'''
        <div class="code-block-wrapper">
            <div class="code-header">
                <span class="code-language">{language}</span>
            </div>
            <pre class="code-block"><code class="language-{language}">{code}</code></pre>
        </div>
        '''

class QuestionGenerator:
    def __init__(self):
        """Initialize the question generator with OpenRouter API"""
        # Will initialize client on first invoke to ensure we get the latest API key from session state
        self.client = None
        
    def _get_client(self):
        """Get OpenRouter client with the most up-to-date API key"""
        import streamlit as st
        
        # Get API key from session state or environment variable
        openrouter_api_key = st.session_state.get('openrouter_api_key', os.environ.get('OPENROUTER_API_KEY'))
        
        # Create a new client with the current API key
        return ChatOpenAI(
            openai_api_key=openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model_name="deepseek-ai/deepseek-r1-0528-qwen3-8b",
            temperature=0.7,
            default_headers={
                "HTTP-Referer": os.environ.get("YOUR_SITE_URL", "localhost"),
                "X-Title": os.environ.get("YOUR_SITE_NAME", "Bitcoin L2 Research Assistant"),
                "User-Agent": os.environ.get("USER_AGENT", "BitcoinL2ResearchAssistant/1.0")
            }
        )
        
    def generate_related_questions(self, previous_query, max_questions=3):
        """Generate related questions based on the user's previous query"""
        try:
            # Get the client with current API key
            client = self._get_client()
            
            prompt = f"""
            Based on the following user query about Bitcoin Layer 2 technology:
            "{previous_query}"
            
            Generate {max_questions} highly relevant follow-up questions that the user might be interested in asking next.
            Each question should:
            - Be direct and concise, ending with a question mark
            - Contain only the question itself with no explanations
            - Focus on Bitcoin Layer 2 technologies
            - Be no more than one sentence
            
            Return ONLY a clean list of questions without any explanations:
            1. First question?
            2. Second question?
            3. Third question?
            """
            
            # Using LangChain's ChatOpenAI to generate questions
            from langchain_core.messages import HumanMessage
            response = client.invoke([HumanMessage(content=prompt)])
            response_text = response.content
            
            # Parse the numbered list into separate questions
            questions = []
            pattern = r'\d+\.\s*(.*?)(?=\d+\.|$)'
            matches = re.findall(pattern, response_text, re.DOTALL)
            
            # Clean up the questions
            for match in matches:
                question = match.strip()
                # Remove any explanations after the first sentence ending with ? or .
                q_parts = re.split(r'(?<=[.?!])\s+', question, 1)
                clean_question = q_parts[0].strip()
                if clean_question:
                    questions.append(clean_question)
            
            # If we couldn't parse the format, try an alternate approach
            if not questions:
                # Split by newlines and look for lines starting with a number
                lines = response_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if re.match(r'^\d+\.', line):
                        question = re.sub(r'^\d+\.\s*', '', line).strip()
                        # Remove any explanations after the first sentence
                        q_parts = re.split(r'(?<=[.?!])\s+', question, 1)
                        clean_question = q_parts[0].strip()
                        if clean_question:
                            questions.append(clean_question)
            
            # Limit to max_questions
            return questions[:max_questions]
            
        except Exception as e:
            print(f"Error generating related questions: {str(e)}")
            print(traceback.format_exc())
            return [] 
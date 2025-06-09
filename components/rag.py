import streamlit as st
import pandas as pd
import os
import re
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import CSVLoader
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage

class RAGComponents:
    def __init__(self):
        """Initialize the RAG components"""
        pass
        
    def initialize_embeddings(self):
        """Initialize embeddings model"""
        try:
            # Initialize embeddings
            st.session_state.embeddings = OllamaEmbeddings(model="nomic-embed-text")
            
            # Initialize chat history if it doesn't exist
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = StreamlitChatMessageHistory()
                
            # Initialize memory if it doesn't exist
            if "memory" not in st.session_state:
                st.session_state.memory = ConversationBufferMemory(
                    return_messages=True,
                    output_key="answer",
                    chat_memory=st.session_state.chat_history
                )
                
            return True
        except Exception as e:
            st.error(f"❌ Error initializing embeddings: {str(e)}")
            return False
            
    def load_csv_data(self, csv_file_path):
        """Load the CSV data"""
        try:
            # Load CSV data
            st.session_state.loader = CSVLoader(
                file_path=csv_file_path,
                encoding='utf-8',
                csv_args={'delimiter': ','}
            )
            
            st.session_state.docs = st.session_state.loader.load()
            
            # Load CSV for metadata and display
            st.session_state.csv_data = pd.read_csv(csv_file_path)
            return True
        except Exception as e:
            st.error(f"❌ Error loading CSV data: {str(e)}")
            return False
            
    def create_vector_store(self):
        """Create the vector store for retrieval"""
        try:
            # Use only CSV docs, no web documents
            all_documents = st.session_state.docs
            
            # Text splitting for better retrieval
            st.session_state.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ",", " "]
            )
            
            st.session_state.final_documents = st.session_state.text_splitter.split_documents(all_documents)
            
            # Create vector store
            st.session_state.vectors = FAISS.from_documents(
                st.session_state.final_documents, 
                st.session_state.embeddings
            )
            return True
        except Exception as e:
            st.error(f"❌ Error creating vector store: {str(e)}")
            return False
    
    def create_llm_chain(self):
        """Create the LLM and retrieval chain"""
        # Set up OpenRouter LLM with Deepseek R1 0528 Qwen3 8B
        openrouter_api_key = st.session_state.get('openrouter_api_key', os.environ.get('OPENROUTER_API_KEY'))
        if not openrouter_api_key:
            st.error("❌ OPENROUTER_API_KEY not found in environment variables or session state")
            return None
            
        llm = ChatOpenAI(
            openai_api_key=openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model_name="deepseek-ai/deepseek-r1-0528-qwen3-8b",
            temperature=0.1,
            default_headers={
                "HTTP-Referer": os.environ.get("YOUR_SITE_URL", "localhost"),
                "X-Title": os.environ.get("YOUR_SITE_NAME", "Bitcoin L2 Research Assistant"),
                "User-Agent": os.environ.get("USER_AGENT", "BitcoinL2ResearchAssistant/1.0")
            }
        )
        
        # Enhanced prompt template for Bitcoin L2 queries with conversation history
        prompt = ChatPromptTemplate.from_template("""
        You are an expert Bitcoin Layer 2 (L2) scaling solutions analyst. Answer questions based on the provided context about Bitcoin L2 solutions, including data from official websites and documentation.

        Context Information:
        {context}

        Chat History:
        {chat_history}

        Instructions:
        1. Provide comprehensive, accurate information about Bitcoin L2 solutions
        2. Include specific technical details, metrics, TVL data, and performance comparisons when available
        3. Mention official website links and resources when discussing specific L2 projects
        4. When comparing L2 solutions, highlight key differences in:
           - Technology approach (Lightning, Sidechains, Rollups, etc.)
           - Security model and trust assumptions
           - Transaction throughput and fees
           - Developer tooling and ecosystem
           - Maturity and adoption metrics
        5. Be objective and cite specific data points from the context
        6. If discussing risks or limitations, be balanced and factual
        7. Structure your response clearly with headers and bullet points when appropriate
        8. If the question relates to previous questions in the chat history, provide context-aware responses
        9. If clarification of a previous answer is needed, refer to your earlier responses

        Question: {input}

        Provide a detailed, well-structured answer:
        """)
        
        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = st.session_state.vectors.as_retriever(
            search_kwargs={"k": getattr(st.session_state, 'search_depth', 8)}
        )
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        return retrieval_chain
        
    def parse_thinking_and_response(self, raw_response):
        """Parse DeepSeek's thinking process and actual response"""
        try:
            # DeepSeek R1 format: <think>...</think> followed by actual response
            think_pattern = r'<think>(.*?)</think>'
            thinking_match = re.search(think_pattern, raw_response, re.DOTALL)
            
            if thinking_match:
                thinking_content = thinking_match.group(1).strip()
                # Remove the thinking part to get the actual response
                actual_response = re.sub(think_pattern, '', raw_response, flags=re.DOTALL).strip()
                return thinking_content, actual_response
            else:
                # No thinking tags found, return empty thinking and full response
                return "", raw_response
        except Exception as e:
            st.error(f"Error parsing response: {str(e)}")
            return "", raw_response
    
    def process_query(self, query):
        """Process a user query and return the response"""
        try:
            # Create retrieval chain
            retrieval_chain = self.create_llm_chain()
            if not retrieval_chain:
                raise Exception("Could not create retrieval chain")
            
            # Get response with memory
            response = retrieval_chain.invoke({
                "input": query, 
                "chat_history": st.session_state.memory.chat_memory.messages
            })
            
            # Parse thinking and actual response
            raw_answer = response['answer']
            thinking_content, actual_answer = self.parse_thinking_and_response(raw_answer)
            
            # Save to chat history
            st.session_state.chat_history.add_user_message(query)
            st.session_state.chat_history.add_ai_message(actual_answer)
            
            return {
                'answer': actual_answer,
                'thinking': thinking_content,
                'context': response['context']
            }
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")
            raise e 
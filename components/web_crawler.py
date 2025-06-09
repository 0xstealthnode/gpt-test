import streamlit as st
import pandas as pd
import re
import time
from datetime import datetime
from urllib.parse import urlparse
from langchain_community.document_loaders import WebBaseLoader

class WebCrawler:
    def __init__(self):
        """Initialize the web crawler"""
        pass
    
    def extract_links_from_csv(self, csv_file_path):
        """Extract all URLs from the CSV file"""
        try:
            df = pd.read_csv(csv_file_path)
            links = []
            
            # Search for URLs in all cells
            for column in df.columns:
                for cell in df[column].astype(str):
                    # Find URLs using regex
                    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', cell)
                    links.extend(urls)
            
            # Remove duplicates and filter valid URLs
            unique_links = list(set(links))
            valid_links = []
            
            for link in unique_links:
                try:
                    parsed = urlparse(link)
                    if parsed.scheme and parsed.netloc:
                        # Clean up common formatting issues
                        clean_link = link.rstrip(')')
                        valid_links.append(clean_link)
                except:
                    continue
                    
            return valid_links
        except Exception as e:
            st.error(f"Error extracting links from CSV: {str(e)}")
            return []

    def crawl_web_content(self, links):
        """Crawl web content from extracted links"""
        web_documents = []
        
        if not links:
            return web_documents
            
        # Create placeholders that will auto-disappear after 20 seconds
        # Using a container to group all crawling messages together
        with st.container():
            crawler_container = st.empty()
            progress_container = st.empty()
            status_container = st.empty()
            results_container = st.empty()
            
            with crawler_container.container():
                st.markdown("""
                <div class="crawler-message">
                    <h4>🌐 Crawling Web Resources</h4>
                </div>
                """, unsafe_allow_html=True)
            
            progress_bar = progress_container.progress(0)
            
            successful_crawls = 0
            
            for i, url in enumerate(links[:20]):  # Limit to first 20 URLs to avoid timeout
                try:
                    status_container.text(f"Crawling {i+1}/{min(len(links), 20)}: {url[:50]}...")
                    progress_bar.progress((i + 1) / min(len(links), 20))
                    
                    # Use WebBaseLoader to load content
                    loader = WebBaseLoader([url])
                    loader.requests_kwargs = {
                        'timeout': 10,
                        'headers': {
                            'User-Agent': 'BitcoinL2RAG/1.0 (Research Assistant)'
                        }
                    }
                    
                    docs = loader.load()
                    
                    for doc in docs:
                        # Add metadata
                        doc.metadata.update({
                            'source_type': 'web',
                            'url': url,
                            'crawled_at': datetime.now().isoformat()
                        })
                        web_documents.append(doc)
                    
                    successful_crawls += 1
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    with st.sidebar:  # Show warnings in sidebar instead
                        st.warning(f"⚠️ Could not crawl {url}: {str(e)[:100]}...")
                    continue
            
            with results_container.container():
                st.markdown(f"""
                <div class="crawler-message">
                    <p>✅ Successfully crawled {successful_crawls} out of {min(len(links), 20)} websites</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Force clear all placeholders after 3 seconds
            time.sleep(3)
            crawler_container.empty()
            progress_container.empty()
            status_container.empty()
            results_container.empty()
        
        return web_documents 
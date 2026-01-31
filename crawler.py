import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
from typing import List, Dict, Set
from config import BASE_URL, MAX_PAGES

class WebCrawler:
    def __init__(self, base_url: str, max_pages: int = 20):
        self.base_url = base_url
        self.max_pages = max_pages
        self.visited_urls: Set[str] = set()
        self.crawled_data: List[Dict] = []
        
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and within the same domain"""
        parsed_base = urlparse(self.base_url)
        parsed_url = urlparse(url)
        
        # Must be same domain
        if parsed_url.netloc != parsed_base.netloc:
            return False
            
        # Avoid non-HTML files
        excluded_extensions = ['.pdf', '.jpg', '.png', '.gif', '.css', '.js']
        if any(url.lower().endswith(ext) for ext in excluded_extensions):
            return False
            
        return True
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    def extract_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract meaningful content from page"""
        # Get title
        title = soup.find('title')
        title_text = title.get_text() if title else "No Title"
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get main content - adjust selectors based on your target website
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
        else:
            text = soup.get_text(separator=' ', strip=True)
        
        text = self.clean_text(text)
        
        return {
            'url': url,
            'title': self.clean_text(title_text),
            'content': text,
            'length': len(text)
        }
    
    def get_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract all valid links from page"""
        links = []
        for link in soup.find_all('a', href=True):
            absolute_url = urljoin(current_url, link['href'])
            # Remove fragments
            absolute_url = absolute_url.split('#')[0]
            
            if self.is_valid_url(absolute_url) and absolute_url not in self.visited_urls:
                links.append(absolute_url)
        
        return links
    
    def crawl_page(self, url: str) -> bool:
        """Crawl a single page"""
        try:
            print(f"Crawling: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Educational RAG Bot)'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content
            page_data = self.extract_content(soup, url)
            
            # Only save if content is substantial
            if page_data['length'] > 100:
                self.crawled_data.append(page_data)
                print(f"✓ Saved: {page_data['title'][:50]}... ({page_data['length']} chars)")
            
            # Get new links to crawl
            new_links = self.get_links(soup, url)
            
            # Add to queue
            for link in new_links:
                if len(self.visited_urls) < self.max_pages:
                    if link not in self.visited_urls:
                        self.visited_urls.add(link)
                        time.sleep(0.5)  # Be polite, don't hammer the server
                        self.crawl_page(link)
            
            return True
            
        except Exception as e:
            print(f"✗ Error crawling {url}: {str(e)}")
            return False
    
    def crawl(self) -> List[Dict]:
        """Start crawling from base URL"""
        print(f"\n🕷️  Starting crawl from: {self.base_url}")
        print(f"Max pages: {self.max_pages}\n")
        
        self.visited_urls.add(self.base_url)
        self.crawl_page(self.base_url)
        
        print(f"\n✅ Crawling complete!")
        print(f"Pages crawled: {len(self.crawled_data)}")
        print(f"Total content: {sum(d['length'] for d in self.crawled_data)} characters\n")
        
        return self.crawled_data
    
    def save_to_file(self, filename: str = "crawled_data.json"):
        """Save crawled data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.crawled_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Data saved to {filename}")


def main():
    """Test the crawler"""
    crawler = WebCrawler(BASE_URL, MAX_PAGES)
    data = crawler.crawl()
    crawler.save_to_file()
    
    # Print sample
    if data:
        print("\n📄 Sample page:")
        print(f"Title: {data[0]['title']}")
        print(f"Content preview: {data[0]['content'][:200]}...")


if __name__ == "__main__":
    main()
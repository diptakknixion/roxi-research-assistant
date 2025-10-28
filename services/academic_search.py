import requests
from ratelimit import limits, sleep_and_retry
import time

# Microsoft Academic API (using academic-accelerator as a proxy)
BASE_URL = "https://academic-accelerator.com/api/v1/paper/search"

class AcademicSearch:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    @sleep_and_retry
    @limits(calls=2, period=1)  # 2 requests per second
    def search(self, query, max_results=10):
        """Search Microsoft Academic for papers"""
        try:
            params = {
                'q': query,
                'size': max_results,
                'sort': 'relevance',
                'fields': 'title,authors,abstract,year,doi,url,citation_count,journal,fields_of_study,pdf_url'
            }
            
            response = self.session.get(BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            papers = []
            for item in data.get('data', [])[:max_results]:
                try:
                    paper = {
                        'title': item.get('title', 'No Title'),
                        'abstract': item.get('abstract', 'No abstract available'),
                        'authors': [f"{author.get('last_name', '')}, {author.get('first_name', '')}".strip() 
                                  for author in item.get('authors', []) if author],
                        'year': int(item.get('year', 0)) if item.get('year') else None,
                        'doi': item.get('doi'),
                        'url': item.get('url'),
                        'pdf_url': item.get('pdf_url'),
                        'journal': item.get('journal', {}).get('name', 'Unknown Journal'),
                        'citation_count': item.get('citation_count', 0),
                        'source': 'Microsoft Academic',
                        'publication_types': ['JournalArticle'],
                        'fields_of_study': item.get('fields_of_study', [])
                    }
                    papers.append(paper)
                except Exception as e:
                    print(f"Error processing Academic paper: {e}")
                    continue
                    
            return papers
            
        except Exception as e:
            print(f"Academic search error: {e}")
            return []

# Create a singleton instance
academic_searcher = AcademicSearch()

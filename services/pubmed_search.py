from pymed import PubMed
from ratelimit import limits, sleep_and_retry
import time

# Rate limiting: 3 requests per second
CALLS_PER_SECOND = 3
PERIOD = 1

class PubMedSearch:
    def __init__(self):
        self.pubmed = PubMed(tool="ROXI", email="your.email@example.com")  # Replace with your email
    
    @sleep_and_retry
    @limits(calls=CALLS_PER_SECOND, period=PERIOD)
    def search(self, query, max_results=10):
        """Search PubMed for articles"""
        try:
            results = self.pubmed.query(query, max_results=max_results)
            papers = []
            
            for article in results:
                try:
                    # Extract publication date
                    pub_date = article.publication_date
                    year = int(pub_date.year) if pub_date else None
                    
                    # Get PDF URL if available
                    pdf_url = None
                    for link in article.links:
                        if 'pdf' in link.lower():
                            pdf_url = link
                            break
                    
                    paper = {
                        'title': article.title,
                        'abstract': article.abstract if hasattr(article, 'abstract') else 'No abstract available',
                        'authors': [f"{author['lastname']}, {author['initials']}" 
                                  for author in article.authors] if hasattr(article, 'authors') else [],
                        'year': year,
                        'doi': article.doi,
                        'pmid': article.pubmed_id,
                        'url': f"https://pubmed.ncbi.nlm.nih.gov/{article.pubmed_id}",
                        'pdf_url': pdf_url,
                        'journal': article.journal if hasattr(article, 'journal') else 'Unknown Journal',
                        'citation_count': 0,  # PubMed doesn't provide citation counts
                        'source': 'PubMed',
                        'publication_types': ['JournalArticle'],
                        'fields_of_study': [keyword for keyword in article.keywords] if hasattr(article, 'keywords') else []
                    }
                    papers.append(paper)
                except Exception as e:
                    print(f"Error processing PubMed article: {e}")
                    continue
                    
            return papers
            
        except Exception as e:
            print(f"PubMed search error: {e}")
            return []

# Create a singleton instance
pubmed_searcher = PubMedSearch()

# services/scholar.py
import requests
import time
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# Rate limiting for Semantic Scholar
SEMANTIC_SCHOLAR_REQUESTS = []
MAX_REQUESTS_PER_MINUTE = 10
REQUEST_TIMEOUT_SECONDS = 60

def check_rate_limit():
    """Check and enforce rate limiting for Semantic Scholar"""
    global SEMANTIC_SCHOLAR_REQUESTS
    now = datetime.now()
    
    # Remove requests older than 60 seconds
    SEMANTIC_SCHOLAR_REQUESTS = [req_time for req_time in SEMANTIC_SCHOLAR_REQUESTS 
                                  if (now - req_time).total_seconds() < REQUEST_TIMEOUT_SECONDS]
    
    # If we've hit the limit, wait
    if len(SEMANTIC_SCHOLAR_REQUESTS) >= MAX_REQUESTS_PER_MINUTE:
        wait_time = REQUEST_TIMEOUT_SECONDS - (now - SEMANTIC_SCHOLAR_REQUESTS[0]).total_seconds()
        if wait_time > 0:
            print(f"Rate limit approaching. Waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time + 0.5)
            SEMANTIC_SCHOLAR_REQUESTS = []
    
    SEMANTIC_SCHOLAR_REQUESTS.append(now)

def search_papers(query, limit=10):
    """
    Search for research papers using multiple sources for comprehensive results
    """
    results = []
    
    # Search Semantic Scholar (primary source)
    semantic_results = search_semantic_scholar(query, limit)
    results.extend(semantic_results)
    time.sleep(1)  # Wait between API calls to avoid rate limiting
    
    # Search arXiv for preprints and recent research (with error handling)
    try:
        arxiv_results = search_arxiv(query, limit//3)
        results.extend(arxiv_results)
        time.sleep(1)
    except Exception as e:
        print(f"arXiv search failed: {e}")
        # Continue without arXiv results
    
    # Search CrossRef for additional papers (with error handling)
    try:
        crossref_results = search_crossref(query, limit//3)
        results.extend(crossref_results)
        time.sleep(1)
    except Exception as e:
        print(f"CrossRef search failed: {e}")
        # Continue without CrossRef results
    
    # Remove duplicates based on DOI and title
    unique_results = remove_duplicates(results)
    
    # Filter by relevance to query
    filtered_results = filter_by_relevance(unique_results, query)
    
    # Sort by relevance score, citation count, and recency
    def safe_sort_key(paper):
        # Get citation count, default to 0 if None
        try:
            cites = int(paper.get("citation_count", 0)) if paper.get("citation_count") is not None else 0
        except (ValueError, TypeError):
            cites = 0
            
        # Get year, default to 0 if None
        try:
            year = int(paper.get("year", 0)) if paper.get("year") is not None else 0
        except (ValueError, TypeError):
            year = 0
        
        # Get relevance score
        relevance = paper.get("relevance_score", 0)
            
        return (relevance, cites, year)
    
    filtered_results.sort(key=safe_sort_key, reverse=True)
    
    return filtered_results[:limit]

def search_semantic_scholar(query, limit=10):
    """Search papers using Semantic Scholar API with rate limiting"""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit * 2,  # Get more results to filter
        "fields": "title,authors,year,externalIds,url,abstract,venue,citationCount,publicationDate,openAccessPdf,publicationTypes,fieldsOfStudy",
        "publicationTypes": "JournalArticle,Conference,Review",  # Filter for research papers only
        "minCitationCount": 1,  # Lower requirement to get more open access papers
        "year": "2000-"  # Only papers from 2000 onwards
    }
    
    try:
        # Check rate limit before making request
        check_rate_limit()
        
        response = requests.get(url, params=params, timeout=10)
        
        # Handle rate limiting (429 error)
        if response.status_code == 429:
            print(f"Rate limited by Semantic Scholar. Waiting 60 seconds...")
            time.sleep(60)
            # Retry once after waiting
            response = requests.get(url, params=params, timeout=10)
        
        response.raise_for_status()
        data = response.json()
        results = []

        for paper in data.get("data", []):
            # Extract author information
            authors = []
            for author in paper.get("authors", []):
                authors.append(author.get("name", "Unknown Author"))
            
            # Get external IDs
            external_ids = paper.get("externalIds", {})
            
            # Get PDF URL if available
            pdf_url = None
            if paper.get("openAccessPdf"):
                pdf_url = paper.get("openAccessPdf", {}).get("url")
            
            # Filter out non-research content
            publication_types = paper.get("publicationTypes", [])
            fields_of_study = paper.get("fieldsOfStudy", [])
            
            # Skip if it's not a proper research paper
            if not publication_types or not any(pt in ["JournalArticle", "Conference", "Review"] for pt in publication_types):
                continue
                
            # Skip if it looks like encyclopedia/reference content
            title = paper.get("title", "").lower()
            if any(skip_word in title for skip_word in ["encyclopedia", "handbook", "dictionary", "manual", "guide", "introduction to"]):
                continue
            
            result = {
                "title": paper.get("title", "No Title"),
                "authors": authors,
                "year": paper.get("year"),
                "abstract": paper.get("abstract", "No abstract available"),
                "venue": paper.get("venue", "Unknown Venue"),
                "citation_count": paper.get("citationCount", 0),
                "doi": external_ids.get("DOI"),
                "pmid": external_ids.get("PubMed"),
                "arxiv": external_ids.get("ArXiv"),
                "url": paper.get("url"),
                "pdf_url": pdf_url,
                "publication_date": paper.get("publicationDate"),
                "publication_types": publication_types,
                "fields_of_study": fields_of_study,
                "source": "Semantic Scholar"
            }
            results.append(result)
        
        return results
    except Exception as e:
        print(f"Error searching Semantic Scholar: {e}")
        return []

def search_crossref(query, limit=5):
    """Search papers using CrossRef API"""
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": limit,
        "select": "title,author,published-print,DOI,abstract,container-title,URL,type,subject",
        "filter": "type:journal-article,type:proceedings-article"  # Filter for research papers only
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = []

        for item in data.get("message", {}).get("items", []):
            # Extract authors
            authors = []
            for author in item.get("author", []):
                given = author.get("given", "")
                family = author.get("family", "")
                full_name = f"{given} {family}".strip()
                if full_name:
                    authors.append(full_name)
            
            # Extract publication year
            year = None
            published = item.get("published-print", {}).get("date-parts")
            if published and len(published) > 0 and len(published[0]) > 0:
                year = published[0][0]
            
            # Filter out non-research content
            title = item.get("title", [""])[0].lower() if item.get("title") else ""
            if any(skip_word in title for skip_word in ["encyclopedia", "handbook", "dictionary", "manual", "guide", "introduction to"]):
                continue
                
            # Only include recent research (last 30 years)
            if year and year < 1994:
                continue
            
            result = {
                "title": item.get("title", ["No Title"])[0] if item.get("title") else "No Title",
                "authors": authors,
                "year": year,
                "abstract": "Abstract not available from CrossRef",
                "venue": item.get("container-title", ["Unknown Venue"])[0] if item.get("container-title") else "Unknown Venue",
                "citation_count": 0,  # CrossRef doesn't provide citation counts
                "doi": item.get("DOI"),
                "pmid": None,
                "arxiv": None,
                "url": item.get("URL"),
                "pdf_url": None,
                "publication_date": None,
                "publication_types": [item.get("type", "journal-article")],
                "fields_of_study": item.get("subject", []),
                "source": "CrossRef"
            }
            results.append(result)
        
        return results
    except Exception as e:
        print(f"Error searching CrossRef: {e}")
        return []

def search_arxiv(query, limit=5):
    """Search papers using arXiv API"""
    import xml.etree.ElementTree as ET
    
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": limit,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.content)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        
        results = []
        entries = root.findall('atom:entry', namespace)
        
        for entry in entries:
            # Extract title
            title_elem = entry.find('atom:title', namespace)
            title = title_elem.text.strip() if title_elem is not None else "No Title"
            
            # Extract authors
            authors = []
            author_elems = entry.findall('atom:author', namespace)
            for author_elem in author_elems:
                name_elem = author_elem.find('atom:name', namespace)
                if name_elem is not None:
                    authors.append(name_elem.text.strip())
            
            # Extract abstract
            summary_elem = entry.find('atom:summary', namespace)
            abstract = summary_elem.text.strip() if summary_elem is not None else "No abstract available"
            
            # Extract arXiv ID and create URLs
            id_elem = entry.find('atom:id', namespace)
            arxiv_url = id_elem.text if id_elem is not None else ""
            arxiv_id = arxiv_url.split('/')[-1] if arxiv_url else ""
            
            # Extract publication date
            published_elem = entry.find('atom:published', namespace)
            pub_date = published_elem.text if published_elem is not None else ""
            year = int(pub_date[:4]) if pub_date and len(pub_date) >= 4 else None
            
            # Extract categories (fields of study)
            categories = []
            category_elems = entry.findall('atom:category', namespace)
            for cat_elem in category_elems:
                term = cat_elem.get('term')
                if term:
                    categories.append(term)
            
            # Create PDF URL
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else None
            
            result = {
                "title": title,
                "authors": authors,
                "year": year,
                "abstract": abstract,
                "venue": "arXiv preprint",
                "citation_count": 0,  # arXiv doesn't provide citation counts
                "doi": None,
                "pmid": None,
                "arxiv": arxiv_id,
                "url": arxiv_url,
                "pdf_url": pdf_url,
                "publication_date": pub_date,
                "publication_types": ["preprint"],
                "fields_of_study": categories,
                "source": "arXiv"
            }
            results.append(result)
        
        return results
    except Exception as e:
        print(f"Error searching arXiv: {e}")
        return []

def filter_by_relevance(papers, query):
    """Filter papers by strict relevance to the search query"""
    query_lower = query.lower()
    query_keywords = set(query_lower.split())
    
    # Remove common words that don't add value
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'it', 'its', 'they', 'their', 'them', 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'about', 'also', 'more', 'other', 'some', 'any', 'all', 'each', 'every', 'both', 'neither', 'either', 'no', 'not', 'only', 'just', 'very', 'too', 'so', 'such', 'than', 'then', 'there', 'here', 'now', 'here', 'up', 'down', 'out', 'over', 'under', 'above', 'below', 'through', 'during', 'before', 'after', 'between', 'among', 'into', 'onto', 'off', 'against', 'along', 'around', 'across', 'behind', 'beyond', 'beside', 'near', 'toward', 'towards', 'within', 'without', 'via', 'via', 'per', 'per', 'via', 'using', 'used', 'use', 'uses', 'using', 'been', 'being', 'be', 'am', 'are', 'is', 'was', 'were', 'been', 'being'}
    query_keywords = {word for word in query_keywords if word not in stop_words and len(word) > 2}
    
    # If no meaningful keywords, return empty (no results)
    if not query_keywords:
        return []
    
    scored_papers = []
    
    for paper in papers:
        # Get paper fields
        title = (paper.get("title") or "").lower()
        abstract = (paper.get("abstract") or "").lower()
        venue = (paper.get("venue") or "").lower()
        
        # STRICT FILTERING: Paper must have keywords in title or abstract
        title_keywords_found = [kw for kw in query_keywords if kw in title]
        abstract_keywords_found = [kw for kw in query_keywords if kw in abstract]
        
        # Skip papers with no keyword matches in title or abstract
        if not title_keywords_found and not abstract_keywords_found:
            continue
        
        # Calculate relevance score
        relevance_score = 0
        
        # Title matches are most important (10 points each)
        relevance_score += len(title_keywords_found) * 10
        
        # Abstract matches (3 points each)
        relevance_score += len(abstract_keywords_found) * 3
        
        # Bonus for exact phrase match in title (highest priority)
        if query_lower in title:
            relevance_score += 50
        # Bonus for exact phrase match in abstract
        elif query_lower in abstract:
            relevance_score += 25
        
        # Bonus for having all keywords in title
        if len(title_keywords_found) == len(query_keywords):
            relevance_score += 20
        
        # Bonus for recent papers (within last 5 years)
        try:
            year = int(paper.get("year", 0))
            if year >= 2020:
                relevance_score += 5
        except:
            pass
        
        # Bonus for highly cited papers
        try:
            citations = int(paper.get("citation_count", 0))
            if citations >= 50:
                relevance_score += 10
            elif citations >= 20:
                relevance_score += 5
        except:
            pass
        
        paper["relevance_score"] = relevance_score
        scored_papers.append(paper)
    
    return scored_papers

def remove_duplicates(papers):
    """Remove duplicate papers based on DOI and title similarity"""
    unique_papers = []
    seen_dois = set()
    seen_titles = set()
    
    for paper in papers:
        # Check DOI first
        doi = paper.get("doi")
        if doi and doi in seen_dois:
            continue
        
        # Check title similarity
        title = paper.get("title", "").lower().strip()
        if title in seen_titles:
            continue
        
        # Add to unique list
        unique_papers.append(paper)
        if doi:
            seen_dois.add(doi)
        if title:
            seen_titles.add(title)
    
    return unique_papers

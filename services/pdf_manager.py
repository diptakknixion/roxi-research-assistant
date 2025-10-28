import requests
import os
import hashlib
import fitz  # PyMuPDF
from urllib.parse import urlparse, unquote
import time

def download_pdf(url, folder="data/library"):
    """
    Download PDF from URL with robust error handling and redirect following
    """
    if not url:
        return {"status": "error", "message": "No URL provided"}
    
    os.makedirs(folder, exist_ok=True)
    
    try:
        # Generate a safe filename
        parsed_url = urlparse(url)
        filename_from_url = os.path.basename(unquote(parsed_url.path))
        
        if not filename_from_url.endswith('.pdf'):
            # Generate filename from URL hash if no proper filename
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename_from_url = f"paper_{url_hash}.pdf"
        
        filepath = os.path.join(folder, filename_from_url)
        
        # Check if file already exists
        if os.path.exists(filepath):
            return {
                "status": "success", 
                "filepath": filepath,
                "message": "File already exists",
                "size": os.path.getsize(filepath)
            }
        
        # Enhanced headers for academic PDF access
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Use session to handle redirects properly
        session = requests.Session()
        session.headers.update(headers)
        
        # Configure maximum redirects in session
        session.max_redirects = 10
        
        # Follow redirects with a maximum limit
        response = session.get(url, stream=True, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        # Check content type more carefully
        content_type = response.headers.get('content-type', '').lower()
        print(f"Content-Type: {content_type}")
        
        # If it's HTML, try to find PDF link
        if 'text/html' in content_type:
            # Look for PDF links in the HTML
            try:
                html_content = response.text[:5000]  # Get first 5000 chars to search
                import re
                
                # Find PDF links
                pdf_patterns = [
                    r'href=["\']([^"\']*\.pdf)["\']',
                    r'url:\s*["\']([^"\']*\.pdf)["\']',
                    r'src=["\']([^"\']*\.pdf)["\']'
                ]
                
                for pattern in pdf_patterns:
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    if matches:
                        for pdf_url in matches:
                            if pdf_url.startswith('http'):
                                print(f"Found PDF link: {pdf_url}")
                                # Try downloading the found PDF
                                pdf_response = session.get(pdf_url, stream=True, timeout=30, allow_redirects=True)
                                if 'pdf' in pdf_response.headers.get('content-type', '').lower():
                                    response = pdf_response
                                    break
                else:
                    # Check if the page indicates access restrictions
                    if any(term in html_content.lower() for term in ['paywall', 'subscription', 'access denied', 'login required', 'purchase']):
                        return {"status": "error", "message": "PDF requires subscription or purchase. Try the 'View Paper' link to access it directly."}
                    
                    # If no PDF found in HTML, return error
                    return {"status": "error", "message": "Page is HTML, not PDF. This paper may require institutional access or purchase. Try clicking 'View Paper' to check availability."}
            except Exception as e:
                print(f"Failed to parse HTML for PDF link: {e}")
                return {"status": "error", "message": "Could not extract PDF from page - may require institutional access"}
        
        # Double check we got PDF content
        final_content_type = response.headers.get('content-type', '').lower()
        if 'pdf' not in final_content_type and not url.lower().endswith('.pdf'):
            return {"status": "error", "message": f"URL returned content type: {final_content_type} instead of PDF"}
        
        # Download the file
        total_size = 0
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    total_size += len(chunk)
                    # Check PDF header early
                    if total_size == len(chunk):
                        if not chunk.startswith(b'%PDF'):
                            f.close()
                            os.remove(filepath)
                            return {"status": "error", "message": "File does not have PDF header - it's likely HTML or another format"}
        
        # Verify the downloaded file is a valid PDF
        if not is_valid_pdf(filepath):
            os.remove(filepath)
            return {"status": "error", "message": "Downloaded file is not a valid PDF"}
        
        return {
            "status": "success",
            "filepath": filepath,
            "message": "PDF downloaded successfully",
            "size": total_size
        }
        
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Network error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Error downloading: {str(e)}"}

def is_valid_pdf(filepath):
    """Check if the downloaded file is a valid PDF"""
    try:
        doc = fitz.open(filepath)
        page_count = len(doc)
        doc.close()
        return page_count > 0
    except:
        return False

def extract_text_from_pdf(filepath):
    """Extract text from PDF with better error handling"""
    if not os.path.exists(filepath):
        return {"status": "error", "message": "PDF file not found"}
    
    try:
        doc = fitz.open(filepath)
        text = ""
        metadata = {
            "page_count": len(doc),
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "creator": doc.metadata.get("creator", "")
        }
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        
        doc.close()
        
        return {
            "status": "success",
            "text": text,
            "metadata": metadata,
            "word_count": len(text.split())
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Error extracting text: {str(e)}"}

def get_pdf_info(filepath):
    """Get basic information about a PDF file"""
    if not os.path.exists(filepath):
        return {"status": "error", "message": "PDF file not found"}
    
    try:
        doc = fitz.open(filepath)
        info = {
            "status": "success",
            "filename": os.path.basename(filepath),
            "size": os.path.getsize(filepath),
            "page_count": len(doc),
            "metadata": {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "modification_date": doc.metadata.get("modDate", "")
            }
        }
        doc.close()
        return info
        
    except Exception as e:
        return {"status": "error", "message": f"Error reading PDF info: {str(e)}"}

def list_downloaded_pdfs(folder="data/library"):
    """List all downloaded PDFs with their information"""
    if not os.path.exists(folder):
        return {"status": "error", "message": "Library folder not found"}
    
    try:
        pdf_files = []
        for filename in os.listdir(folder):
            if filename.lower().endswith('.pdf'):
                filepath = os.path.join(folder, filename)
                info = get_pdf_info(filepath)
                if info["status"] == "success":
                    pdf_files.append(info)
        
        return {
            "status": "success",
            "count": len(pdf_files),
            "files": pdf_files
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Error listing PDFs: {str(e)}"}

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Create data directory if it doesn't exist
try:
    os.makedirs("data/library", exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create data directory: {e}")

# Import services with error handling - AFTER app creation
search_papers = None
download_pdf = None
list_downloaded_pdfs = None
get_pdf_info = None
format_citation = None
generate_bibtex = None
summarize_paper = None
extract_key_information = None

try:
    from services.scholar import search_papers as _search_papers
    search_papers = _search_papers
except Exception as e:
    print(f"Warning: Failed to import search_papers: {e}")

try:
    from services.pdf_manager import download_pdf as _download_pdf, list_downloaded_pdfs as _list_pdfs, get_pdf_info as _get_pdf_info
    download_pdf = _download_pdf
    list_downloaded_pdfs = _list_pdfs
    get_pdf_info = _get_pdf_info
except Exception as e:
    print(f"Warning: Failed to import pdf_manager: {e}")

try:
    from services.citation import format_citation as _format_citation, generate_bibtex as _generate_bibtex
    format_citation = _format_citation
    generate_bibtex = _generate_bibtex
except Exception as e:
    print(f"Warning: Failed to import citation: {e}")

try:
    from services.summarizer import summarize_paper as _summarize_paper, extract_key_information as _extract_key_information
    summarize_paper = _summarize_paper
    extract_key_information = _extract_key_information
except Exception as e:
    print(f"Warning: Failed to import summarizer: {e}")
    import traceback
    traceback.print_exc()

# Vercel serverless handler
try:
    from serverless_wsgi import handle
    def handler(request):
        try:
            return handle(app, request)
        except Exception as e:
            print(f"Handler error: {e}")
            import traceback
            traceback.print_exc()
            raise
except ImportError as e:
    print(f"Warning: serverless_wsgi not available: {e}")
    handler = None

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    try:
        return jsonify({
            "status": "ok",
            "services": {
                "search_papers": search_papers is not None,
                "pdf_manager": download_pdf is not None,
                "citation": format_citation is not None,
                "summarizer": summarize_paper is not None
            }
        })
    except Exception as e:
        print(f"Health check error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    """Home page with ROXI interface"""
    try:
        return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROXI - Research Paper AI Assistant</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: rgba(255,255,255,0.95); color: #333; padding: 40px; border-radius: 15px; text-align: center; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header p { color: #666; font-size: 1.1em; margin: 5px 0; }
        .search-box { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin-bottom: 30px; }
        .search-box h2 { color: #333; margin-bottom: 20px; }
        .search-input { width: 100%; padding: 15px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; transition: border-color 0.3s; }
        .search-input:focus { outline: none; border-color: #667eea; }
        .search-btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; margin-top: 15px; transition: transform 0.2s; }
        .search-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        .search-btn:active { transform: translateY(0); }
        .results { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .results h2 { color: #333; margin-bottom: 20px; }
        .paper { border: 1px solid #e0e0e0; padding: 25px; margin: 15px 0; border-radius: 10px; background: #f9f9f9; transition: all 0.3s; border-left: 4px solid #667eea; }
        .paper:hover { box-shadow: 0 5px 15px rgba(0,0,0,0.1); background: white; }
        .paper-title { font-weight: bold; color: #333; font-size: 1.3em; margin-bottom: 10px; line-height: 1.4; }
        .paper-meta { display: flex; flex-wrap: wrap; gap: 15px; margin: 10px 0; font-size: 0.95em; color: #666; }
        .meta-item { display: flex; align-items: center; gap: 5px; }
        .paper-abstract { margin: 15px 0; padding: 15px; background: #f0f0f0; border-radius: 8px; color: #555; line-height: 1.6; }
        .paper-fields { margin: 10px 0; color: #888; font-size: 0.9em; }
        .field-tag { display: inline-block; background: #e8eaf6; color: #667eea; padding: 4px 10px; border-radius: 15px; margin: 3px; font-size: 0.85em; }
        .button-group { margin-top: 20px; display: flex; flex-wrap: wrap; gap: 10px; }
        .btn { padding: 10px 18px; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; transition: all 0.3s; font-size: 0.95em; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        .btn-secondary { background: #f0f0f0; color: #333; border: 1px solid #ddd; }
        .btn-secondary:hover { background: #e0e0e0; }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .citation-box { background: #f8f9fa; padding: 15px; border-left: 4px solid #667eea; margin: 15px 0; border-radius: 8px; font-family: 'Courier New', monospace; font-size: 0.9em; line-height: 1.5; color: #333; }
        .loading { text-align: center; padding: 40px; color: #666; font-size: 1.1em; }
        .spinner { display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 10px; vertical-align: middle; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .no-results { text-align: center; padding: 40px; color: #999; }
        .download-status { padding: 10px 15px; border-radius: 6px; margin-top: 10px; font-size: 0.9em; }
        .download-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .download-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 ROXI</h1>
            <p>Your AI Research Assistant for Academic Papers</p>
            <p style="font-size: 0.95em; margin-top: 10px;">Search • Download • Summarize • Cite</p>
        </div>
        
        <div class="search-box">
            <h2>🔍 Search Research Papers</h2>
            <input type="text" id="searchQuery" class="search-input" placeholder="Enter your research query (e.g., 'machine learning', 'quantum computing', 'climate change')">
            <button onclick="searchPapers()" class="search-btn">🔍 Search Papers</button>
        </div>
        
        <div id="results" class="results" style="display: none;">
            <h2>📚 Search Results</h2>
            <div id="resultsContent"></div>
        </div>
        
        <div id="library" class="results" style="display: none; margin-top: 30px;">
            <h2>📖 PDF Library & Summarization</h2>
            <div style="margin-bottom: 20px;">
                <button onclick="refreshLibrary()" class="btn btn-primary">🔄 Refresh Library</button>
                <p style="color: #666; font-size: 0.9em; margin-top: 10px;">Downloaded PDFs appear here. Click "Summarize" to generate AI-powered summaries.</p>
            </div>
            <div id="libraryContent"></div>
        </div>
        
        <div class="search-box" style="margin-top: 30px;">
            <h2>📥 View PDF Library</h2>
            <button onclick="toggleLibrary()" class="btn btn-secondary">📖 Show/Hide Library</button>
        </div>
    </div>

    <script>
        async function searchPapers() {
            const query = document.getElementById('searchQuery').value;
            if (!query.trim()) {
                alert('Please enter a search query');
                return;
            }
            
            const resultsDiv = document.getElementById('results');
            const resultsContent = document.getElementById('resultsContent');
            
            resultsDiv.style.display = 'block';
            resultsContent.innerHTML = '<div class="loading"><span class="spinner"></span>Searching for papers...</div>';
            
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=10`);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const papers = await response.json();
                
                if (!Array.isArray(papers)) {
                    throw new Error('Invalid response format');
                }
                
                if (papers.length === 0) {
                    resultsContent.innerHTML = '<div class="no-results">📭 No papers found for your query. Try a different search term.</div>';
                    return;
                }
                
                let html = '';
                papers.forEach((paper, index) => {
                    const authors = paper.authors && paper.authors.length > 0 ? paper.authors.join(', ') : 'Unknown Authors';
                    const year = paper.year || 'Year not specified';
                    const citations = paper.citation_count || 0;
                    const venue = paper.venue || 'Unknown Venue';
                    const source = paper.source || 'Unknown Source';
                    
                    html += `
                        <div class="paper">
                            <div class="paper-title">${paper.title}</div>
                            <div class="paper-meta">
                                <div class="meta-item">👥 ${authors}</div>
                                <div class="meta-item">📅 ${year}</div>
                                <div class="meta-item">📖 ${venue}</div>
                                <div class="meta-item">🏷️ ${source}</div>
                                <div class="meta-item">📊 ${citations} citations</div>
                            </div>
                            ${paper.fields_of_study && paper.fields_of_study.length > 0 ? `
                                <div class="paper-fields">
                                    🔬 Fields: ${paper.fields_of_study.slice(0, 5).map(f => '<span class="field-tag">' + f + '</span>').join('')}
                                </div>
                            ` : ''}
                            ${paper.abstract ? `<div class="paper-abstract"><strong>Abstract:</strong> ${paper.abstract.substring(0, 400)}${paper.abstract.length > 400 ? '...' : ''}</div>` : ''}
                            
                            <div class="button-group">
                                <button class="btn btn-primary" onclick="generateCitation(${index}, 'APA')">📝 APA Citation</button>
                                <button class="btn btn-primary" onclick="generateCitation(${index}, 'MLA')">📝 MLA Citation</button>
                                <button class="btn btn-primary" onclick="generateCitation(${index}, 'IEEE')">📝 IEEE Citation</button>
                                ${paper.pdf_url ? `<button class="btn btn-secondary" onclick="downloadPaper('${paper.pdf_url}', ${index})">📥 Download PDF</button>` : '<button class="btn btn-secondary" disabled>📥 No PDF Available</button>'}
                                ${paper.url ? `<a href="${paper.url}" target="_blank" class="btn btn-secondary">🔗 View Paper</a>` : ''}
                            </div>
                            
                            <div id="citation-${index}" style="display: none;"></div>
                            <div id="download-status-${index}" style="display: none;"></div>
                        </div>
                    `;
                });
                
                resultsContent.innerHTML = html;
                window.currentPapers = papers;
                
            } catch (error) {
                resultsContent.innerHTML = `<div class="no-results">❌ Error searching papers: ${error.message}. Please try again.</div>`;
                console.error('Search error:', error);
            }
        }
        
        async function generateCitation(paperIndex, style) {
            const paper = window.currentPapers[paperIndex];
            const citationDiv = document.getElementById(`citation-${paperIndex}`);
            
            try {
                const response = await fetch('/api/citation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ...paper, style: style })
                });
                
                const result = await response.json();
                citationDiv.innerHTML = `
                    <div class="citation-box">
                        <strong>${style} Citation:</strong><br>
                        ${result.citation}
                    </div>
                `;
                citationDiv.style.display = 'block';
                
            } catch (error) {
                console.error('Citation error:', error);
            }
        }
        
        async function downloadPaper(url, paperIndex) {
            const button = event.target;
            const originalText = button.textContent;
            button.textContent = '⏳ Downloading...';
            button.disabled = true;
            
            const statusDiv = document.getElementById(`download-status-${paperIndex}`);
            
            try {
                const response = await fetch('/api/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.message || 'Download failed');
                }
                
                // Get the filename from the Content-Disposition header
                const contentDisposition = response.headers.get('content-disposition');
                let filename = 'paper.pdf';
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
                    if (filenameMatch) filename = filenameMatch[1];
                }
                
                // Get the blob and trigger download
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(downloadUrl);
                document.body.removeChild(a);
                
                button.textContent = '✅ Downloaded';
                statusDiv.innerHTML = `<div class="download-status download-success">✅ PDF downloaded successfully to your Downloads folder!</div>`;
                statusDiv.style.display = 'block';
                
            } catch (error) {
                button.textContent = '❌ Failed';
                statusDiv.innerHTML = `<div class="download-status download-error">❌ Download failed: ${error.message}</div>`;
                statusDiv.style.display = 'block';
                console.error('Download error:', error);
            }
            
            setTimeout(() => {
                button.textContent = originalText;
                button.disabled = false;
            }, 4000);
        }
        
        // Library functions
        let libraryVisible = false;
        
        function toggleLibrary() {
            const libraryDiv = document.getElementById('library');
            libraryVisible = !libraryVisible;
            
            if (libraryVisible) {
                libraryDiv.style.display = 'block';
                refreshLibrary();
            } else {
                libraryDiv.style.display = 'none';
            }
        }
        
        async function refreshLibrary() {
            const libraryContent = document.getElementById('libraryContent');
            libraryContent.innerHTML = '<div class="loading"><span class="spinner"></span>Loading PDF library...</div>';
            
            try {
                const response = await fetch('/api/library');
                const data = await response.json();
                
                if (data.status !== 'success') {
                    libraryContent.innerHTML = '<div class="no-results">❌ Error loading library</div>';
                    return;
                }
                
                if (data.count === 0) {
                    libraryContent.innerHTML = '<div class="no-results">📭 No PDFs downloaded yet. Download some papers first!</div>';
                    return;
                }
                
                let html = '';
                data.files.forEach((pdf, index) => {
                    html += `
                        <div class="paper" style="border-left: 4px solid #28a745;">
                            <div class="paper-title">📄 ${pdf.filename}</div>
                            <div class="paper-meta">
                                <div class="meta-item">📊 Size: ${Math.round(pdf.size / 1024)} KB</div>
                                <div class="meta-item">📑 Pages: ${pdf.page_count}</div>
                                <div class="meta-item">👥 Author: ${pdf.metadata.author || 'Unknown'}</div>
                            </div>
                            <div class="button-group">
                                <button class="btn btn-primary" onclick="summarizePDF('${pdf.filename}', ${index})">🤖 Summarize</button>
                                <button class="btn btn-secondary" onclick="extractInfo('${pdf.filename}', ${index})">📋 Extract Info</button>
                                <button class="btn btn-secondary" onclick="downloadFromLibrary('${pdf.filename}')">💾 Save to PC</button>
                            </div>
                            <div id="summary-${index}" style="display: none; margin-top: 15px;"></div>
                            <div id="extracted-${index}" style="display: none; margin-top: 15px;"></div>
                        </div>
                    `;
                });
                
                libraryContent.innerHTML = html;
                
            } catch (error) {
                libraryContent.innerHTML = '<div class="no-results">❌ Error loading library</div>';
                console.error('Library error:', error);
            }
        }
        
        async function summarizePDF(filename, pdfIndex) {
            const summaryDiv = document.getElementById(`summary-${pdfIndex}`);
            
            // Show summary type selector
            summaryDiv.innerHTML = `
                <div class="citation-box">
                    <strong>🤖 Choose Summary Type:</strong><br><br>
                    <button class="btn btn-primary" onclick="generateSummary('${filename}', ${pdfIndex}, 'bullet_points')">📝 Bullet Points</button>
                    <button class="btn btn-primary" onclick="generateSummary('${filename}', ${pdfIndex}, 'abstract')">📄 Abstract</button>
                    <button class="btn btn-primary" onclick="generateSummary('${filename}', ${pdfIndex}, 'detailed')">📖 Detailed</button>
                    <button class="btn btn-primary" onclick="generateSummary('${filename}', ${pdfIndex}, 'key_findings')">🔬 Key Findings</button>
                </div>
            `;
            summaryDiv.style.display = 'block';
        }
        
        async function generateSummary(filename, pdfIndex, summaryType) {
            const summaryDiv = document.getElementById(`summary-${pdfIndex}`);
            summaryDiv.innerHTML = '<div class="loading"><span class="spinner"></span>Generating summary...</div>';
            
            try {
                const response = await fetch('/api/summarize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        filepath: `data/library/${filename}`,
                        summary_type: summaryType
                    })
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    summaryDiv.innerHTML = `
                        <div class="citation-box">
                            <strong>🤖 ${summaryType.replace('_', ' ').toUpperCase()} SUMMARY:</strong><br><br>
                            <div style="white-space: pre-line; line-height: 1.6;">${result.summary}</div>
                            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e0e0e0; font-size: 0.85em; color: #666;">
                                📊 Original: ${result.original_word_count} words | 📅 Generated: ${new Date().toLocaleString()}
                            </div>
                        </div>
                    `;
                } else {
                    summaryDiv.innerHTML = `<div class="citation-box" style="border-left-color: #dc3545;">❌ Summary failed: ${result.message}</div>`;
                }
                
            } catch (error) {
                summaryDiv.innerHTML = `<div class="citation-box" style="border-left-color: #dc3545;">❌ Error: ${error.message}</div>`;
                console.error('Summary error:', error);
            }
        }
        
        async function extractInfo(filename, pdfIndex) {
            const infoDiv = document.getElementById(`extracted-${pdfIndex}`);
            infoDiv.innerHTML = '<div class="loading"><span class="spinner"></span>Extracting information...</div>';
            infoDiv.style.display = 'block';
            
            try {
                const response = await fetch('/api/extract-info', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        filepath: `data/library/${filename}`
                    })
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    const info = result.extracted_info;
                    infoDiv.innerHTML = `
                        <div class="citation-box">
                            <strong>📋 Extracted Information:</strong><br><br>
                            <div style="display: grid; grid-template-columns: auto 1fr; gap: 10px; font-size: 0.9em;">
                                <strong>Title:</strong> <div>${info.title}</div>
                                <strong>Authors:</strong> <div>${info.authors.join(', ')}</div>
                                <strong>Research Area:</strong> <div>${info.research_area}</div>
                                <strong>Keywords:</strong> <div>${info.keywords.join(', ')}</div>
                                <strong>Methodology:</strong> <div>${info.methodology}</div>
                                <strong>Main Contribution:</strong> <div>${info.main_contribution}</div>
                                <strong>Limitations:</strong> <div>${info.limitations}</div>
                                <strong>Future Work:</strong> <div>${info.future_work}</div>
                            </div>
                        </div>
                    `;
                } else {
                    infoDiv.innerHTML = `<div class="citation-box" style="border-left-color: #dc3545;">❌ Extraction failed: ${result.message}</div>`;
                }
                
            } catch (error) {
                infoDiv.innerHTML = `<div class="citation-box" style="border-left-color: #dc3545;">❌ Error: ${error.message}</div>`;
                console.error('Extract error:', error);
            }
        }
        
        async function downloadFromLibrary(filename) {
            try {
                const response = await fetch('/api/download-from-library', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: filename })
                });
                
                if (!response.ok) {
                    throw new Error('Download failed');
                }
                
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(downloadUrl);
                document.body.removeChild(a);
                
            } catch (error) {
                alert('Failed to download file: ' + error.message);
                console.error('Download error:', error);
            }
        }
        
        // Allow Enter key to search
        document.getElementById('searchQuery').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchPapers();
            }
        });
    </script>
</body>
</html>
    """)
    except Exception as e:
        print(f"Home route error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/search", methods=["GET"])
def api_search():
    """Search for research papers"""
    query = request.args.get("q")
    limit = request.args.get("limit", 10, type=int)
    
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    if limit > 50:
        limit = 50  # Cap the limit
    
    try:
        if search_papers is None:
            return jsonify({"error": "Search service not available"}), 500
        
        print(f"Searching for: {query} (limit: {limit})")
        results = search_papers(query, limit)
        print(f"Found {len(results)} results")
        return jsonify(results)
    except Exception as e:
        print(f"Search error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

@app.route("/api/download", methods=["POST"])
def api_download():
    """Download PDF from URL and return it for browser download"""
    from flask import send_file
    data = request.get_json()
    url = data.get("url") if data else None
    
    if not url:
        return jsonify({"status": "error", "message": "URL is required"}), 400
    
    try:
        if download_pdf is None:
            return jsonify({"status": "error", "message": "PDF download not available"}), 500
        
        # Download the PDF to a temporary location
        result = download_pdf(url)
        
        if result["status"] != "success":
            return jsonify(result), 400
        
        filepath = result["filepath"]
        
        # Generate a proper filename for download
        import hashlib
        from urllib.parse import urlparse, unquote
        parsed_url = urlparse(url)
        filename = os.path.basename(unquote(parsed_url.path))
        
        if not filename or not filename.endswith('.pdf'):
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"paper_{url_hash}.pdf"
        
        # Send the file to the browser for download
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Download failed: {str(e)}"}), 500

@app.route("/api/summarize", methods=["POST"])
def api_summarize():
    """Summarize a downloaded PDF"""
    data = request.get_json()
    filepath = data.get("filepath") if data else None
    summary_type = data.get("summary_type", "bullet_points") if data else "bullet_points"
    
    if not filepath:
        return jsonify({"status": "error", "message": "Filepath is required"}), 400
    
    if summarize_paper is None:
        return jsonify({"status": "error", "message": "Summarization not available"}), 500
    
    result = summarize_paper(filepath, summary_type)
    return jsonify(result)

@app.route("/api/extract-info", methods=["POST"])
def api_extract_info():
    """Extract structured information from a PDF"""
    data = request.get_json()
    filepath = data.get("filepath") if data else None
    
    if not filepath:
        return jsonify({"status": "error", "message": "Filepath is required"}), 400
    
    if extract_key_information is None:
        return jsonify({"status": "error", "message": "Information extraction not available"}), 500
    
    result = extract_key_information(filepath)
    return jsonify(result)

@app.route("/api/library", methods=["GET"])
def api_library():
    """List all PDFs in the library"""
    if list_downloaded_pdfs is None:
        return jsonify({"status": "error", "message": "Library access not available"}), 500
    
    result = list_downloaded_pdfs()
    return jsonify(result)

@app.route("/api/check-api-key", methods=["GET"])
def api_check_api_key():
    """Check if OpenAI API key is configured"""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your-api-key-here":
        return jsonify({
            "status": "success", 
            "message": "OpenAI API key is configured",
            "key_preview": api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
        })
    else:
        return jsonify({
            "status": "error", 
            "message": "OpenAI API key not configured"
        }), 400

@app.route("/api/download-from-library", methods=["POST"])
def api_download_from_library():
    """Download a PDF from the library to user's PC"""
    from flask import send_file
    data = request.get_json()
    filename = data.get("filename") if data else None
    
    if not filename:
        return jsonify({"status": "error", "message": "Filename is required"}), 400
    
    filepath = os.path.join("data/library", filename)
    
    if not os.path.exists(filepath):
        return jsonify({"status": "error", "message": "File not found in library"}), 404
    
    try:
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Download failed: {str(e)}"}), 500

@app.route("/api/citation", methods=["POST"])
def api_citation():
    """Generate citation in specified format"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON data is required"}), 400
    
    if format_citation is None or generate_bibtex is None:
        return jsonify({"error": "Citation service not available"}), 500
    
    style = data.get("style", "APA")
    
    try:
        citation = format_citation(data, style)
        bibtex = generate_bibtex(data)
        
        return jsonify({
            "citation": citation,
            "bibtex": bibtex,
            "style": style
        })
    except Exception as e:
        return jsonify({"error": f"Citation generation failed: {str(e)}"}), 500


@app.route("/api/pdf-info/<path:filename>", methods=["GET"])
def api_pdf_info(filename):
    """Get information about a specific PDF"""
    filepath = os.path.join("data/library", filename)
    result = get_pdf_info(filepath)
    return jsonify(result)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    print("🤖 Starting ROXI - Research Paper AI Assistant")
    print("📍 Access the web interface at: http://localhost:5000")
    print("📚 API endpoints available at: http://localhost:5000/api/")
    app.run(debug=True, host="0.0.0.0", port=5000)

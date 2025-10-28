# 🤖 ROXI - Research Paper AI Assistant

ROXI is an intelligent research assistant that helps you search for academic papers, download PDFs, generate proper citations, and summarize research content using mock AI demonstrations.

## ✨ Features

- **🔍 Smart Paper Search**: Search across multiple academic databases (Semantic Scholar, CrossRef)
- **📥 PDF Download**: Automatically download research papers when available
- **📝 Citation Generation**: Generate citations in multiple formats (APA, MLA, IEEE, Chicago, Harvard)
- **🤖 AI Summarization**: Get AI-powered summaries of research papers (mock demonstrations ready for real API integration)
- **📚 Library Management**: Organize and manage your downloaded papers
- **🌐 Web Interface**: User-friendly web interface for easy interaction
- **🔌 REST API**: Complete API for programmatic access

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the ROXI directory
cd ROXI

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

**Note**: ROXI currently uses mock AI demonstrations. For real AI summarization, you'll need to configure an API key:

Create a `.env` file:
```env
OPENAI_API_KEY=your_api_key_here
```

The mock AI features work immediately without any API key setup.

### 3. Run ROXI

```bash
python app.py
```

Access ROXI at: `http://localhost:5000`

## 🎯 Usage

### Web Interface

1. **Search Papers**: Enter your research query in the search box
2. **View Results**: Browse through search results with abstracts and metadata
3. **Generate Citations**: Click citation buttons to get properly formatted citations
4. **Download PDFs**: Download available papers directly to your library
5. **Manage Library**: View and organize your downloaded papers

### API Endpoints

#### Search Papers
```bash
GET /api/search?q=machine learning&limit=10
```

#### Download PDF
```bash
POST /api/download
Content-Type: application/json

{
    "url": "https://example.com/paper.pdf"
}
```

#### Generate Citation
```bash
POST /api/citation
Content-Type: application/json

{
    "title": "Paper Title",
    "authors": ["Author 1", "Author 2"],
    "year": 2023,
    "venue": "Journal Name",
    "doi": "10.1000/example",
    "style": "APA"
}
```

#### Summarize Paper
```bash
POST /api/summarize
Content-Type: application/json

{
    "filepath": "data/library/paper.pdf",
    "summary_type": "bullet_points"
}
```

## 📋 Citation Formats

ROXI supports multiple citation formats:

- **APA**: American Psychological Association
- **MLA**: Modern Language Association  
- **IEEE**: Institute of Electrical and Electronics Engineers
- **Chicago**: Chicago Manual of Style
- **Harvard**: Harvard Referencing System
- **BibTeX**: For LaTeX documents

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your API key for AI features (optional - mock AI works without it)
- `FLASK_ENV`: Set to `development` for debug mode

### Directory Structure

```
ROXI/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── data/
│   └── library/          # Downloaded PDFs storage
└── services/
    ├── __init__.py
    ├── scholar.py        # Paper search functionality
    ├── pdf_manager.py    # PDF download and processing
    ├── citation.py       # Citation formatting
    └── summarizer.py     # AI summarization
```

## 🛠️ API Reference

### Search Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search` | GET | Search for research papers |
| `/api/download` | POST | Download PDF from URL |
| `/api/citation` | POST | Generate formatted citation |
| `/api/summarize` | POST | AI summarize PDF content |
| `/api/extract-info` | POST | Extract structured info from PDF |
| `/api/library` | GET | List downloaded PDFs |
| `/api/pdf-info/<filename>` | GET | Get PDF metadata |

### Response Formats

All API responses follow this structure:

```json
{
    "status": "success|error",
    "data": {},
    "message": "Optional message"
}
```

## 🔍 Search Sources

ROXI searches multiple academic databases:

1. **Semantic Scholar**: Comprehensive academic search with abstracts and citations
2. **CrossRef**: DOI-based academic publication database
3. **Automatic Deduplication**: Removes duplicate results across sources

## 🤖 AI Features (Mock Demonstrations)

### Summarization Types

**Note**: Currently uses mock demonstrations. Real AI integration ready with proper API setup.

- **bullet_points**: 5-point summary covering key aspects
- **abstract**: Concise abstract-style summary (150-200 words)
- **detailed**: Comprehensive summary with sections
- **key_findings**: Focus on main discoveries and results

### Information Extraction

ROXI can extract structured information from papers (mock demonstrations):
- Title and authors
- Research area and keywords
- Methodology description
- Main contributions
- Datasets and tools used
- Limitations and future work

### Real AI Integration

The code is structured for easy AI API integration. Simply replace the mock functions with real API calls to enable:
- Actual OpenAI GPT summaries
- Real PDF content analysis
- Dynamic information extraction

## 🔒 Privacy & Security

- No paper content is stored permanently (only metadata)
- OpenAI API calls are made securely
- Downloaded PDFs are stored locally
- No user data is transmitted to third parties

## 🐛 Troubleshooting

### Common Issues

1. **Search returns no results**
   - Try different keywords or broader terms
   - Check internet connection

2. **PDF download fails**
   - Ensure the URL points to a valid PDF
   - Some papers may require institutional access

3. **AI summarization not working**
   - Currently uses mock demonstrations - no API key needed
   - For real AI: configure API key in `.env` file
   - Mock summaries should work immediately

4. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

### Error Codes

- `400`: Bad request (missing parameters)
- `404`: Endpoint not found
- `500`: Internal server error

## 📈 Performance Tips

- Use specific search terms for better results
- Limit search results (default: 10) for faster responses
- AI summarization works best with papers under 50 pages
- Download PDFs locally for faster repeated access

## 🤝 Contributing

To contribute to ROXI:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Please check the license file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section above
- Review API documentation
- Ensure all dependencies are properly installed

---

**Happy Researching with ROXI! 🚀📚**

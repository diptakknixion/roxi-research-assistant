def format_citation(meta, style="APA"):
    """
    Format citation in various academic styles
    """
    authors = meta.get("authors", [])
    title = meta.get("title", "No Title")
    year = meta.get("year", "n.d.")
    venue = meta.get("venue", "")
    doi = meta.get("doi")
    url = meta.get("url")
    
    # Format authors based on style
    if style.upper() == "APA":
        return format_apa_citation(authors, title, year, venue, doi, url)
    elif style.upper() == "MLA":
        return format_mla_citation(authors, title, year, venue, doi, url)
    elif style.upper() == "IEEE":
        return format_ieee_citation(authors, title, year, venue, doi, url)
    elif style.upper() == "CHICAGO":
        return format_chicago_citation(authors, title, year, venue, doi, url)
    elif style.upper() == "HARVARD":
        return format_harvard_citation(authors, title, year, venue, doi, url)
    else:
        return "Unsupported citation style. Available styles: APA, MLA, IEEE, Chicago, Harvard"

def format_author_name_apa(name):
    """Format a single author name for APA (Last, F. M.)"""
    parts = name.strip().split()
    if len(parts) == 0:
        return "Unknown"
    elif len(parts) == 1:
        return parts[0]
    else:
        # Last name is typically the last part
        last_name = parts[-1]
        # Get initials from first and middle names
        initials = " ".join([p[0] + "." for p in parts[:-1] if p])
        return f"{last_name}, {initials}"

def format_authors_apa(authors):
    """Format authors for APA style"""
    if not authors:
        return "Unknown Author"
    
    formatted_authors = [format_author_name_apa(author) for author in authors]
    
    if len(formatted_authors) == 1:
        return formatted_authors[0]
    elif len(formatted_authors) == 2:
        return f"{formatted_authors[0]}, & {formatted_authors[1]}"
    elif len(formatted_authors) <= 20:
        return ", ".join(formatted_authors[:-1]) + f", & {formatted_authors[-1]}"
    else:
        return ", ".join(formatted_authors[:19]) + ", ... " + formatted_authors[-1]

def format_author_name_mla(name, is_first=True):
    """Format a single author name for MLA (Last, First for first author; First Last for others)"""
    parts = name.strip().split()
    if len(parts) == 0:
        return "Unknown"
    elif len(parts) == 1:
        return parts[0]
    else:
        if is_first:
            # First author: Last, First Middle
            last_name = parts[-1]
            first_names = " ".join(parts[:-1])
            return f"{last_name}, {first_names}"
        else:
            # Other authors: First Middle Last
            return " ".join(parts)

def format_authors_mla(authors):
    """Format authors for MLA style"""
    if not authors:
        return "Unknown Author"
    
    if len(authors) == 1:
        return format_author_name_mla(authors[0], is_first=True)
    elif len(authors) == 2:
        first = format_author_name_mla(authors[0], is_first=True)
        second = format_author_name_mla(authors[1], is_first=False)
        return f"{first}, and {second}"
    else:
        first = format_author_name_mla(authors[0], is_first=True)
        return f"{first}, et al."

def format_authors_ieee(authors):
    """Format authors for IEEE style"""
    if not authors:
        return "Unknown Author"
    
    if len(authors) <= 6:
        return ", ".join(authors)
    else:
        return f"{authors[0]} et al."

def format_apa_citation(authors, title, year, venue, doi, url):
    """Format citation in APA 7th edition style"""
    author_str = format_authors_apa(authors)
    
    # Handle year
    year_str = str(year) if year and year != "n.d." else "n.d."
    
    # Build citation
    citation = f"{author_str} ({year_str}). {title}"
    
    # Add venue/journal in italics (represented with underscores)
    if venue:
        citation += f". _{venue}_"
    
    # Add DOI (preferred) or URL
    if doi:
        citation += f". https://doi.org/{doi}"
    elif url:
        citation += f". {url}"
    
    return citation

def format_mla_citation(authors, title, year, venue, doi, url):
    """Format citation in MLA 9th edition style"""
    author_str = format_authors_mla(authors)
    
    # Build citation
    citation = f"{author_str}. \"{title}.\""
    
    # Add venue/journal in italics
    if venue:
        citation += f" _{venue}_,"
    
    # Add year
    year_str = str(year) if year and year != "n.d." else "n.d."
    citation += f" {year_str}"
    
    # Add DOI or URL
    if doi:
        citation += f", https://doi.org/{doi}"
    elif url:
        citation += f", {url}"
    
    citation += "."
    return citation

def format_ieee_citation(authors, title, year, venue, doi, url):
    """Format citation in IEEE style"""
    author_str = format_authors_ieee(authors)
    
    # Build citation
    citation = f"{author_str}, \"{title},\""
    
    # Add venue in italics
    if venue:
        citation += f" _{venue}_,"
    
    # Add year
    year_str = str(year) if year and year != "n.d." else "n.d."
    citation += f" {year_str}"
    
    # Add DOI or URL
    if doi:
        citation += f", doi: {doi}"
    elif url:
        citation += f". [Online]. Available: {url}"
    
    citation += "."
    return citation

def format_chicago_citation(authors, title, year, venue, doi, url):
    """Format citation in Chicago 17th edition style (Author-Date)"""
    if not authors:
        author_str = "Unknown Author"
    else:
        # Format first author: Last, First
        first_author = format_author_name_mla(authors[0], is_first=True)
        if len(authors) == 1:
            author_str = first_author
        else:
            author_str = f"{first_author}, et al."
    
    # Build citation
    year_str = str(year) if year and year != "n.d." else "n.d."
    citation = f"{author_str}. {year_str}. \"{title}.\""
    
    # Add venue in italics
    if venue:
        citation += f" _{venue}_"
    
    # Add DOI or URL
    if doi:
        citation += f". https://doi.org/{doi}"
    elif url:
        citation += f". {url}"
    
    citation += "."
    return citation

def format_harvard_citation(authors, title, year, venue, doi, url):
    """Format citation in Harvard style"""
    if not authors:
        author_str = "Unknown Author"
    else:
        # Get last name of first author
        first_author_parts = authors[0].strip().split()
        first_author_last = first_author_parts[-1] if first_author_parts else "Unknown"
        
        if len(authors) == 1:
            author_str = first_author_last
        elif len(authors) == 2:
            second_author_parts = authors[1].strip().split()
            second_author_last = second_author_parts[-1] if second_author_parts else "Unknown"
            author_str = f"{first_author_last} and {second_author_last}"
        else:
            author_str = f"{first_author_last} et al."
    
    # Build citation
    year_str = str(year) if year and year != "n.d." else "n.d."
    citation = f"{author_str} ({year_str}) '{title}'"
    
    # Add venue in italics
    if venue:
        citation += f", _{venue}_"
    
    # Add DOI or URL
    if doi:
        citation += f". doi: {doi}"
    elif url:
        citation += f". Available at: {url}"
    
    citation += "."
    return citation

def generate_bibtex(meta):
    """Generate BibTeX citation"""
    authors = " and ".join(meta.get("authors", ["Unknown Author"]))
    title = meta.get("title", "No Title")
    year = meta.get("year", "")
    venue = meta.get("venue", "")
    doi = meta.get("doi", "")
    url = meta.get("url", "")
    
    # Generate a citation key
    first_author = meta.get("authors", ["Unknown"])[0].split()[-1] if meta.get("authors") else "Unknown"
    key = f"{first_author.lower()}{year}"
    
    bibtex = f"@article{{{key},\n"
    bibtex += f"  author = {{{authors}}},\n"
    bibtex += f"  title = {{{title}}},\n"
    
    if venue:
        bibtex += f"  journal = {{{venue}}},\n"
    
    if year:
        bibtex += f"  year = {{{year}}},\n"
    
    if doi:
        bibtex += f"  doi = {{{doi}}},\n"
    
    if url:
        bibtex += f"  url = {{{url}}},\n"
    
    bibtex += "}"
    return bibtex

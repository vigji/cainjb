from pathlib import Path
import PyPDF2
import shutil

def extract_pdf_text(pdf_path):
    """Extract text from PDF file, excluding the page number header"""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = reader.pages[0].extract_text()
    # Remove the page number header (format: [XX])
    lines = text.split('\n')
    filtered_lines = [
        line for line in lines 
        if (not line.strip().startswith('[') or not line.strip().endswith(']'))
        and not line.strip().endswith('NOTES')
    ]
    # Remove non-ascii characters
    clean_lines = [''.join(c for c in line if ord(c) < 128) for line in filtered_lines[:-1]]
    return '\n'.join(clean_lines)

def update_markdown_file(md_path, pdf_text):
    """Update specific sections in markdown file with extracted PDF text"""
    content = md_path.read_text()
    
    # Split content at the markers
    sections = content.split('**Annotated text**:')
    if len(sections) != 2:
        return False
        
    before_annotated = sections[0]
    rest = sections[1].split('Original page:')
    if len(rest) != 2:
        return False
        
    page_section = rest[1].split('**Original text**:')
    if len(page_section) != 2:
        return False
        
    after_original = page_section[1]
    
    # Extract page number from md_path name
    page_num = md_path.stem.split()[-1]
    
    # Reconstruct the content with new text
    new_content = (
        f"{before_annotated}"
        f"**Annotated text**:\n```\n{pdf_text}\n```\n\n"
        f"Original page:\n[page_{page_num}.pdf]"
        f"(https://github.com/vigji/cainjb/blob/main/source_material/pages/page_{page_num}.pdf)\n\n"
        f"**Original text**:\n```\n{pdf_text}\n```\n"
        f"{after_original}"
    )
    
    md_path.write_text(new_content)
    return True

def main():
    source_dir = Path("/Users/vigji/code/cainjb/source_material/pages")
    wiki_dir = Path("/Users/vigji/code/cainjb.wiki/pages")
    template_path = wiki_dir / "template.md"
    
    for page_num in range(30, 33):
        pdf_path = source_dir / f"page_{page_num}.pdf"
        md_path = wiki_dir / f"page {page_num}.md"
        
        if not pdf_path.exists():
            print(f"Warning: PDF file not found: {pdf_path}")
            continue
            
        if not md_path.exists():
            shutil.copy(template_path, md_path)
            print(f"Created new markdown file from template: {md_path}")
            
        try:
            pdf_text = extract_pdf_text(pdf_path)
            if update_markdown_file(md_path, pdf_text):
                print(f"Successfully processed page {page_num}")
            else:
                print(f"Failed to update markdown for page {page_num}: Invalid format")
        except Exception as e:
            print(f"Error processing page {page_num}: {str(e)}")

if __name__ == "__main__":
    main()
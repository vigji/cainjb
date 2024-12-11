from pathlib import Path
import PyPDF2
import shutil
import re


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

    # Define markers
    annotated_marker = '**Annotated text**:'
    original_page_marker = 'Original page:'
    original_text_marker = '**Original text**:'

    # Split content at the annotated text marker
    sections = content.split(annotated_marker)
    if len(sections) != 2:
        return False

    before_annotated, remaining = sections

    # Split remaining content at the original page marker
    rest = remaining.split(original_page_marker)
    if len(rest) != 2:
        return False

    annotated_section, after_original_page = rest

    # Split after original page at the original text marker
    page_section = after_original_page.split(original_text_marker)
    if len(page_section) != 2:
        return False

    original_page, after_original_text = page_section

    # Extract page number from md_path name
    page_num = md_path.stem.split()[-1]

    # Reconstruct the content with new text
    new_content = (
        f"{before_annotated}"
        f"{annotated_marker}\n```\n{pdf_text}\n```\n\n"
        f"{original_page_marker}\n[page_{page_num}.pdf]"
        f"(https://github.com/vigji/cainjb/blob/main/source_material/pages/page_{page_num}.pdf)\n\n"
        f"{original_text_marker}\n```\n{pdf_text}\n```\n"
        f"{after_original_text}"
    )

    md_path.write_text(new_content)
    return True


def fix_pdf_links(wiki_dir: Path) -> None:
    """Fix PDF links in markdown files to the format [page_X.pdf](https://github.com/vigji/cainjb/blob/main/source_material/pages/page_X.pdf)."""
    pattern = re.compile(
        r'\[pag(\d+)\.pdf\]\(https://github\.com/vigji/cainjb/blob/main/source_material/pages/pag\1\.pdf\)'
    )
    replacement = r'[page_\1.pdf](https://github.com/vigji/cainjb/blob/main/source_material/pages/page_\1.pdf)'

    for md_file in wiki_dir.glob('*.md'):
        content = md_file.read_text()
        new_content, count = pattern.subn(replacement, content)
        if count > 0:
            md_file.write_text(new_content)
            print(f"Updated links in {md_file}")


def main():
    source_dir = Path("/Users/vigji/code/cainjb/source_material/pages")
    wiki_dir = Path("/Users/vigji/code/cainjb.wiki/pages")
    template_path = wiki_dir / "template.md"

    for page_num in range(24, 101):
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

    # Fix PDF links after processing all files
    fix_pdf_links(wiki_dir)


if __name__ == "__main__":
    main()
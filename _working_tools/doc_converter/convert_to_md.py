import os
import mammoth
import re
from datetime import datetime

class DocumentConverter:
    def __init__(self):
        self.current_section = None
        
    def process_line(self, line):
        """Process each line according to its type"""
        line = line.strip()
        if not line:
            return ""
            
        # Handle section markers
        if line.startswith("Section:"):
            section_name = line.replace("Section:", "").strip()
            return f"\n\n# Section: {section_name}\n"
            
        # Handle numbered sections (e.g., "1. Brand Overview")
        if re.match(r'^\d+\.\s+', line):
            return f"\n## {line}\n"
            
        # Handle definitions
        if line.startswith("Definition:"):
            return f"\n**Definition:** {line.replace('Definition:', '').strip()}\n"
            
        # Handle statements
        for statement_type in ["Mission Statement:", "Vision Statement:", "Brand Voice:", "Brand Personality:"]:
            if line.startswith(statement_type):
                return f"\n### {statement_type}\n"
                
        # Handle bullet points
        if line.strip().startswith("•"):
            return f"* {line.strip()[1:].strip()}"
            
        # Handle terms with dash definitions
        if " – " in line:
            term, definition = line.split(" – ", 1)
            return f"* **{term.strip()}** – {definition.strip()}"
            
        return line

    def convert_docx_to_md(self):
        print("Starting DOCX to MD conversion...")
        
        docx_files = [f for f in os.listdir('.') if f.endswith('.docx')]
        if not docx_files:
            print("No .docx files found!")
            return False
        
        docx_path = docx_files[0]
        print(f"Processing: {docx_path}")

        try:
            # Convert DOCX to HTML
            with open(docx_path, "rb") as docx_file:
                result = mammoth.convert_to_html(docx_file)
                html_content = result.value

            # Clean up HTML
            content = html_content.replace('<p>', '\n').replace('</p>', '\n')
            content = content.replace('<ul>', '').replace('</ul>', '')
            content = content.replace('<li>', '• ').replace('</li>', '\n')
            
            # Process line by line
            processed_lines = []
            for line in content.split('\n'):
                processed_line = self.process_line(line)
                if processed_line:
                    processed_lines.append(processed_line)

            # Combine processed content
            md_content = "\n".join(processed_lines)
            
            # Clean up multiple newlines
            md_content = re.sub(r'\n{3,}', '\n\n', md_content)

            # Add document header
            final_content = f"""---
title: {docx_path.replace('.docx', '')}
date: {datetime.now().strftime("%B %d, %Y")}
---

{md_content}
"""

            # Write to file
            output_file = f"{docx_path.replace('.docx', '.md')}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            print(f"Created Markdown file: {output_file}")
            return True

        except Exception as e:
            print(f"Error during conversion: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    try:
        import mammoth
    except ImportError:
        print("Installing required packages...")
        os.system("pip install mammoth")
        print("Packages installed!")
    
    converter = DocumentConverter()
    converter.convert_docx_to_md() 
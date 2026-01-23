import os
import mammoth
import pdfkit
import re
from datetime import datetime
from docx import Document
from PIL import Image
import io
import shutil
import base64

class DocumentStyler:
    def __init__(self):
        # Brand colors from the document
        self.primary_deep_purple = "#59315F"
        self.bright_purple = "#833177"
        self.dark_green = "#949778"
        self.light_green = "#AFB59D"
        self.beige = "#E5E5DF"
        self.text_color = "#333333"

    def get_css(self):
        return f"""
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 30px;
                color: {self.text_color};
                background: white;
                line-height: 1.6;
                font-size: 14pt;
            }}
            
            .header {{
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 2px solid {self.primary_deep_purple};
            }}
            
            .content-section {{
                margin-bottom: 30px;
                page-break-inside: avoid;
            }}
            
            h1, .section-header {{
                color: {self.primary_deep_purple};
                font-size: 24pt;
                margin-top: 40px;
                margin-bottom: 20px;
                page-break-after: avoid;
                font-weight: bold;
            }}
            
            h2, .numbered-section {{
                color: {self.bright_purple};
                font-size: 18pt;
                margin: 30px 0 15px 0;
                page-break-after: avoid;
                font-weight: bold;
            }}
            
            h3 {{
                color: {self.dark_green};
                font-size: 16pt;
                margin: 25px 0 15px 0;
                font-weight: bold;
            }}
            
            p {{
                font-size: 14pt;
                margin: 15px 0;
                line-height: 1.6;
            }}
            
            ul {{
                margin: 20px 0;
                padding-left: 30px;
            }}
            
            li {{
                font-size: 14pt;
                margin: 12px 0;
                line-height: 1.6;
                page-break-inside: avoid;
            }}
            
            .page-break {{
                page-break-before: always;
                height: 1px;
            }}
            
            img {{
                max-width: 90%;
                height: auto;
                margin: 30px auto;
                display: block;
                page-break-inside: avoid;
            }}
            
            .brand-section {{
                background: {self.beige}22;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid {self.primary_deep_purple};
            }}
            
            .brand-value {{
                color: {self.bright_purple};
                font-weight: bold;
            }}
            
            .definition {{
                font-style: italic;
                color: {self.dark_green};
            }}
        """

def convert_docx_to_pdf():
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    
    docx_files = [f for f in os.listdir('.') if f.endswith('.docx')]
    if not docx_files:
        print("No .docx files found!")
        return
    
    docx_path = docx_files[0]
    print(f"Processing: {docx_path}")

    # Simple conversion with default settings
    with open(docx_path, "rb") as docx_file:
        print("Converting DOCX to HTML...")
        custom_styles = """
            p[style-name='Section Title'] => h1:fresh
            p[style-name='Heading 1'] => h1:fresh
            p[style-name='Heading 2'] => h2:fresh
        """
        result = mammoth.convert_to_html(
            docx_file,
            style_map=custom_styles
        )
        html_content = result.value
        print("Initial conversion complete.")

    # Process sections and add page breaks
    print("Processing sections...")
    html_content = re.sub(
        r'\{([^}]+)\}',
        lambda m: f'<div class="page-break"></div><h1 id="section-{re.sub(r"[^a-zA-Z0-9]", "-", m.group(1).lower())}" class="section-header">{m.group(1)}</h1>',
        html_content
    )

    # Process numbered sections
    print("Processing numbered sections...")
    def number_replacement(match):
        number = int(match.group(1))
        section_text = match.group(2)
        section_id = f"section-{number:02d}-{re.sub(r'[^a-zA-Z0-9]', '-', section_text.lower())}"
        return f'<div class="page-break"></div><h2 id="{section_id}" class="numbered-section">{number}. {section_text}</h2>'
    
    html_content = re.sub(r'(\d+)\.\s+((?:(?!\d+\.).)*?)(?=\s*\d+\.|$)', number_replacement, html_content, flags=re.DOTALL)

    html_doc = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    line-height: 1.4;
                    font-size: 11pt;
                }}
                .section-header {{
                    font-size: 14pt;
                    font-weight: bold;
                    margin-bottom: 15px;
                    padding-bottom: 5px;
                }}
                .numbered-section {{
                    white-space: nowrap;
                    font-size: 12pt;
                    margin-top: 15px;
                    margin-bottom: 10px;
                }}
                .page-break {{
                    page-break-before: always;
                    height: 1px;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    margin: 20px auto;
                    display: block;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{docx_path.replace('.docx', '')}</h1>
                <p>Generated on {datetime.now().strftime("%B %d, %Y")}</p>
            </div>
            <div class="content-section">
                {html_content}
            </div>
        </body>
    </html>
    """

    print("Writing temporary HTML file...")
    with open('temp.html', 'w', encoding='utf-8') as f:
        f.write(html_doc)

    print("\nConverting to PDF...")
    output_file = f"{docx_path.replace('.docx', '.pdf')}"
    try:
        options = {
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': "UTF-8",
            'enable-local-file-access': True,
            'footer-right': '[page]',
            'footer-font-size': '9',
            'footer-line': True,
            'header-line': True,
            'quiet': ''
        }
        
        pdfkit.from_file('temp.html', output_file, configuration=config, options=options)
        print(f"\nCreated PDF: {output_file}")
    except Exception as e:
        print(f"\nError creating PDF: {str(e)}")

    # Cleanup
    if os.path.exists('temp.html'):
        os.remove('temp.html')

if __name__ == "__main__":
    try:
        import mammoth
        import pdfkit
    except ImportError:
        print("Installing required packages...")
        os.system("pip install mammoth pdfkit")
        print("Packages installed!")
    
    convert_docx_to_pdf()
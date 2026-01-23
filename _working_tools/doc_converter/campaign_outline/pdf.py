import os
import markdown
import pdfkit
import re
from datetime import datetime

class BrandStyler:
    def __init__(self):
        self.primary_color = "#34C759"
        self.secondary_color = "#007AFF"
        self.accent_color = "#FF9500"
        self.text_color = "#2c3e50"
        
    def get_css(self):
        return f"""
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                color: {self.text_color};
                background: white;
                line-height: 1.6;
            }}
            
            .header {{
                background: {self.primary_color};
                color: white;
                padding: 40px;
                margin-bottom: 40px;
                text-align: center;
                page-break-after: avoid;
            }}
            
            .header h1 {{
                font-size: 32px;
                margin: 0;
                padding: 0;
            }}
            
            /* Table of Contents */
            .toc {{
                background: #f8f9fa;
                padding: 30px;
                margin: 20px 0 40px 0;
                border-radius: 4px;
                page-break-after: always;
            }}
            
            .toc h2 {{
                color: {self.primary_color};
                margin-top: 0;
                padding-top: 0;
                border: none;
            }}
            
            .toc ul {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            
            .toc li {{
                margin: 10px 0;
                padding: 0;
            }}
            
            .toc a {{
                color: {self.secondary_color};
                text-decoration: none;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }}
            
            .toc a:hover {{
                color: {self.primary_color};
            }}
            
            .toc .page-ref {{
                color: {self.accent_color};
                font-size: 0.9em;
                margin-left: 10px;
            }}
            
            .toc-line {{
                border-bottom: 1px dotted #ddd;
                flex: 1;
                margin: 0 10px;
            }}
            
            .section-group {{
                background: white;
                padding: 30px;
                margin-bottom: 40px;
                border: 1px solid #eee;
                border-radius: 4px;
                page-break-inside: avoid;
            }}
            
            .content-section {{
                page-break-inside: avoid;
                margin-bottom: 30px;
            }}
            
            .section-title {{
                color: {self.primary_color};
                font-size: 24px;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid {self.primary_color};
            }}
            
            .document {{
                background: white;
                padding: 20px;
                margin-bottom: 20px;
            }}
            
            h1, h2, h3 {{
                page-break-after: avoid;
            }}
            
            h1 + *, h2 + *, h3 + * {{
                page-break-before: avoid;
            }}
            
            h1 {{
                color: {self.primary_color};
                font-size: 28px;
                margin-top: 0;
            }}
            
            h2 {{
                color: {self.secondary_color};
                font-size: 22px;
                margin: 25px 0 15px 0;
                padding-top: 15px;
                border-top: 1px solid #eee;
            }}
            
            h3 {{
                color: {self.text_color};
                font-size: 18px;
                margin: 20px 0 10px 0;
            }}
            
            ul {{
                list-style: none;
                padding-left: 20px;
                margin: 15px 0;
            }}
            
            ul li {{
                padding: 8px 0;
                position: relative;
                page-break-inside: avoid;
            }}
            
            ul li:before {{
                content: "•";
                color: {self.accent_color};
                position: absolute;
                left: -15px;
            }}
            
            .placeholder {{
                background: #f8f9fa;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
                color: {self.secondary_color};
            }}
            
            .definition-group {{
                page-break-inside: avoid;
                margin-bottom: 20px;
            }}
            
            .footer {{
                text-align: center;
                padding: 20px;
                color: {self.text_color};
                font-size: 14px;
                margin-top: 40px;
                border-top: 1px solid #eee;
                page-break-before: avoid;
            }}
            
            .toc-page {{
                margin: 40px 0;
                page-break-after: always;
            }}
            
            .toc-header {{
                color: {self.primary_color};
                font-size: 24px;
                margin-bottom: 30px;
                padding-bottom: 10px;
                border-bottom: 2px solid {self.primary_color};
            }}
            
            .toc-entry {{
                display: flex;
                align-items: center;
                margin: 15px 0;
            }}
            
            .toc-entry a {{
                display: flex;
                align-items: center;
                width: 100%;
                color: {self.text_color};
                text-decoration: none;
            }}
            
            .toc-number {{
                color: {self.primary_color};
                font-weight: bold;
                margin-right: 10px;
                min-width: 30px;
            }}
            
            .toc-title {{
                flex: 1;
            }}
            
            .toc-dots {{
                border-bottom: 1px dotted {self.text_color}44;
                flex: 1;
                margin: 0 10px;
            }}
            
            .toc-page-num {{
                color: {self.secondary_color};
            }}
            
            .section-anchor {{
                visibility: hidden;
                position: relative;
                top: -50px;
            }}
        """

def create_toc_page(files):
    toc_entries = []
    for i, file in enumerate(files, 1):
        # Create sanitized ID for the anchor
        section_id = f"section-{i:02d}-{re.sub(r'[^a-zA-Z0-9]', '-', file.lower())}"
        toc_entries.append(f"""
            <div class="toc-entry">
                <a href="#{section_id}">
                    <span class="toc-number">{i:02d}</span>
                    <span class="toc-title">{file}</span>
                    <span class="toc-dots"></span>
                    <span class="toc-page-num">{i + 1}</span>
                </a>
            </div>
        """)
    
    return f"""
        <div class="toc-page">
            <h1 class="toc-header">Table of Contents</h1>
            {''.join(toc_entries)}
        </div>
    """

def convert_markdown_to_pdf():
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    styler = BrandStyler()
    
    markdown_files = [f for f in os.listdir('.') if f.endswith('.md')]
    markdown_files.sort()
    
    if not markdown_files:
        print("No markdown files found!")
        return
    
    combined_content = []
    
    # Add header
    combined_content.append(f"""
        <div class="header">
            <h1>Marketing Campaign Templates</h1>
            <p>Generated on {datetime.now().strftime("%B %d, %Y")}</p>
        </div>
    """)
    
    # Add table of contents page
    combined_content.append(create_toc_page(markdown_files))
    
    # Process each file
    for i, file in enumerate(markdown_files, 1):
        print(f"\nProcessing: {file}")
        # Create sanitized ID for the anchor
        section_id = f"section-{i:02d}-{re.sub(r'[^a-zA-Z0-9]', '-', file.lower())}"
        
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Remove emoji characters
            content = re.sub(r'[^\x00-\x7F]+', '', content)
            # Style placeholders
            content = re.sub(r'\[([^\]]+)\]', r'<span class="placeholder">[\1]</span>', content)
            
            html_content = markdown.markdown(content, extensions=['tables'])
            combined_content.append(f"""
                <div id="{section_id}" class="section-anchor"></div>
                <div class="content-section">
                    <h1 class="bookmark-heading" data-level="1">
                        <span class="section-number">{i:02d}</span> {file}
                    </h1>
                    {html_content}
                </div>
                <div class="page-break"></div>
            """)
    
    # Add footer
    combined_content.append("""
        <div class="footer">
            <p>Generated using Marketing Campaign Template System</p>
        </div>
    """)
    
    html_doc = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="UTF-8">
            <style>
                {styler.get_css()}
            </style>
        </head>
        <body>
            {''.join(combined_content)}
        </body>
    </html>
    """
    
    with open('temp.html', 'w', encoding='utf-8') as f:
        f.write(html_doc)
    
    print("\nConverting to PDF...")
    output_file = 'combined_templates.pdf'
    try:
        options = {
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': "UTF-8",
            'outline': '',
            'outline-depth': 1,
            'enable-local-file-access': '',
            'enable-internal-links': '',
            'footer-right': '[page]',
            'footer-font-size': '9',
            'footer-line': True,
            'header-line': True
        }
        
        pdfkit.from_file('temp.html', output_file, configuration=config, options=options)
        print(f"\nCreated PDF: {output_file}")
    except Exception as e:
        print(f"\nError creating PDF: {str(e)}")
    
    if os.path.exists('temp.html'):
        os.remove('temp.html')

if __name__ == "__main__":
    try:
        import markdown
        import pdfkit
    except ImportError:
        print("Installing required packages...")
        os.system("pip install markdown pdfkit")
        print("Packages installed!")
    
    convert_markdown_to_pdf()
import os
import markdown
import pdfkit
from datetime import datetime

def check_wkhtmltopdf():
    """Check if wkhtmltopdf is installed and accessible"""
    paths = [
        r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
        r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
        'wkhtmltopdf'  # Check if it's in PATH
    ]
    
    for path in paths:
        if os.path.exists(path):
            return path
            
    print("wkhtmltopdf not found! Please install it from: https://wkhtmltopdf.org/downloads.html")
    return None

def convert_md_to_pdf():
    print("Starting MD to PDF conversion...")
    
    # Check wkhtmltopdf installation
    wkhtmltopdf_path = check_wkhtmltopdf()
    if not wkhtmltopdf_path:
        return False
    
    # Find markdown files
    md_files = [f for f in os.listdir('.') if f.endswith('.md')]
    if not md_files:
        print("No markdown files found!")
        return False
    
    md_file = md_files[0]
    print(f"Found markdown file: {md_file}")
    
    try:
        # Read markdown content
        print("Reading markdown content...")
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert to HTML
        print("Converting to HTML...")
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'toc']
        )
        
        # Create HTML document with styling
        html_doc = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    margin: 1in;
                    size: letter;
                }}
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 11pt;
                    line-height: 1.4;
                }}
                h1 {{
                    font-size: 16pt;
                    color: #333;
                    border-bottom: 1px solid #ccc;
                    padding-bottom: 5px;
                }}
                h2 {{
                    font-size: 14pt;
                    color: #444;
                    margin-top: 20px;
                }}
                h3 {{
                    font-size: 12pt;
                    color: #555;
                }}
                ul {{
                    margin: 10px 0;
                    padding-left: 20px;
                }}
                li {{
                    margin: 5px 0;
                }}
                strong {{
                    color: #333;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Write temporary HTML file
        temp_html = 'temp_output.html'
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(html_doc)
        
        # Configure PDF options
        print("Converting to PDF...")
        output_file = f"{md_file.replace('.md', '.pdf')}"
        
        options = {
            'page-size': 'Letter',
            'margin-top': '1.0in',
            'margin-right': '1.0in',
            'margin-bottom': '1.0in',
            'margin-left': '1.0in',
            'encoding': "UTF-8",
            'no-outline': None,
            'quiet': ''
        }
        
        # Convert to PDF
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        pdfkit.from_file(temp_html, output_file, options=options, configuration=config)
        
        # Clean up temporary file
        os.remove(temp_html)
        
        if os.path.exists(output_file):
            print(f"Successfully created PDF: {output_file}")
            return True
        else:
            print("Error: PDF file was not created")
            return False
            
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        import markdown
        import pdfkit
    except ImportError:
        print("Installing required packages...")
        os.system("pip install markdown pdfkit")
        print("Packages installed!")
    
    convert_md_to_pdf() 
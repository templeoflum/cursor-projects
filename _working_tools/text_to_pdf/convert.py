import re
from fpdf import FPDF

def is_section_marker(text):
    """Return True if text is enclosed in curly braces."""
    stripped = text.strip()
    return stripped.startswith("{") and stripped.endswith("}")

def is_numbered_section(text):
    """
    Return True if text starts with a number and a period and the number is greater than 1.
    For example: "2. Campaign Details" should trigger a page break.
    """
    match = re.match(r'^\s*(\d+)\.', text)
    if match:
        try:
            number = int(match.group(1))
            return number > 1
        except ValueError:
            return False
    return False

def is_bullet_item(text):
    """
    Return True if text starts with a hyphen.
    (Assumes bullet items begin with "-" followed by a space.)
    """
    return text.strip().startswith("-")

def add_bullet_group(pdf, bullet_items, line_height=8):
    """
    Write a group of bullet list items to the PDF.
    If the group won't fit on the current page, start a new page.
    """
    required_space = line_height * len(bullet_items)
    available_space = pdf.h - pdf.b_margin - pdf.get_y()
    if required_space > available_space:
        pdf.add_page()
    for item in bullet_items:
        pdf.multi_cell(0, line_height, item)
    pdf.ln(2)

def convert_txt_to_pdf(input_file, output_file):
    # Read all lines from the text file
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file '{input_file}': {e}")
        return

    if not lines:
        print("No lines found in the file.")
        return
    else:
        print(f"Found {len(lines)} lines in the file.")

    # Initialize the PDF
    pdf = FPDF()
    pdf.add_page()  # Create the first page
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    bullet_buffer = []  # buffer to hold bullet items

    # Process each line
    for idx, line in enumerate(lines):
        text = line.strip()
        if not text:
            continue  # skip blank lines

        print(f"Processing line {idx}: '{text}'")  # Debug print

        # If line is a section marker, flush bullet buffer and add a new page
        if is_section_marker(text):
            if bullet_buffer:
                add_bullet_group(pdf, bullet_buffer)
                bullet_buffer = []
            pdf.add_page()
            pdf.multi_cell(0, 8, text)
            pdf.ln(4)
            continue

        # If line is a numbered section (with number > 1), flush and add a new page
        if is_numbered_section(text):
            if bullet_buffer:
                add_bullet_group(pdf, bullet_buffer)
                bullet_buffer = []
            pdf.add_page()
            pdf.multi_cell(0, 8, text)
            pdf.ln(4)
            continue

        # If line is a bullet item, buffer it
        if is_bullet_item(text):
            bullet_buffer.append(text)
        else:
            # Flush bullet buffer if it has items
            if bullet_buffer:
                add_bullet_group(pdf, bullet_buffer)
                bullet_buffer = []
            pdf.multi_cell(0, 8, text)
            pdf.ln(4)

    # Flush any remaining bullet items at the end
    if bullet_buffer:
        add_bullet_group(pdf, bullet_buffer)

    try:
        pdf.output(output_file)
        print(f"PDF generated and saved as: {output_file}")
    except Exception as e:
        print(f"Error writing PDF file: {e}")

if __name__ == '__main__':
    input_file = "NAD_outline.txt"   # Make sure this file exists and is not empty
    output_file = "output.pdf"
    convert_txt_to_pdf(input_file, output_file)

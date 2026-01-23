import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
import tkinter as tk
from tkinter import scrolledtext

load_dotenv() # Load variables from .env file

# Configure the API key
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Load Model Data
def load_model_from_file(file_path):
    """Loads the model name from the .res file or returns error message"""
    try:
        with open(file_path, "r", encoding='utf-8') as file:
          for line in file:
            match = re.search(r"concept:(.*)", line) #simplified regex
            if match:
               print("found match!:", line)
               model_name = match.group(1).strip()
               print ("concept line:", model_name)
               return model_name
        return "error loading, no model found" # returns this if there are no matches
    except FileNotFoundError:
        return "error loading, file not found"


model_file_path = 'model_registry.reso'
model_name = load_model_from_file(model_file_path)
print("Model name from:", model_file_path, "is: ", model_name)

# Set the model
model = genai.GenerativeModel(model_name)


def parse_markdown(markdown_text):
    """Parses a Markdown string and returns a dictionary of sections."""
    sections = {}
    current_header = None
    lines = markdown_text.splitlines()

    for line in lines:
        header_match = re.match(r"(#+) (.*)",
                               line)  # regex to get headers and header content, removed ^ and $
        if header_match:
            level = len(header_match.group(1))  # get header level 1, 2 or 3
            header_text = header_match.group(2).strip()
            current_header = f"{'#' * level} {header_text}"  # store header as string to use as key
            sections[current_header] = ""  # set empty string for value
        elif current_header is not None:  # append content if the line is not a header
            sections[current_header] += line + "\n"

    return sections


# Example usage with file
def parse_markdown_file(file_path):
    with open(file_path, "r", encoding='utf-8') as file:
        markdown_text = file.read()
    return parse_markdown(markdown_text)

def expand_section(header, content, feedback = None):
  """Expands a section using the Gemini API."""
  if feedback:
    prompt = f"Expand on the following section, taking into account the following feedback: {feedback}\n\nHeader: {header}\nContent: {content}\n\nExpanded content:"
  else:
      prompt = f"Expand on the following section:\n\nHeader: {header}\nContent: {content}\n\nExpanded content:"
  response = model.generate_content(prompt)
  return response.text

def assemble_markdown(expanded_sections):
    """Assembles the expanded sections into a single Markdown document string."""
    markdown_output = ""
    for header, content in expanded_sections.items():
        markdown_output += f"{header}\n\n{content}\n\n"
    return markdown_output


def expand_framework():
    """Expands the framework text using all the functions"""
    markdown_text = input_text_area.get("1.0", tk.END)
    parsed_sections = parse_markdown(markdown_text)

    expanded_sections = {}
    for header, content in parsed_sections.items():
      expanded_content = expand_section(header, content)
      expanded_sections[header] = expanded_content
    
    assembled_document = assemble_markdown(expanded_sections)
    output_text_area.delete("1.0", tk.END)
    output_text_area.insert(tk.END, assembled_document)


if __name__ == '__main__':
    # Create the main window
    window = tk.Tk()
    window.title("AI Framework Expander")
    window.geometry("800x600")

    # Input Text Area
    input_label = tk.Label(window, text="Input Framework (Markdown):")
    input_label.pack(pady=10)
    input_text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=10)
    input_text_area.pack(pady=10)

    # Expand Button
    expand_button = tk.Button(window, text="Expand Framework", command=expand_framework)
    expand_button.pack(pady=20)

    # Output Text Area
    output_label = tk.Label(window, text="Expanded Framework:")
    output_label.pack(pady=10)
    output_text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=10)
    output_text_area.pack(pady=10)


    # Start the main loop
    window.mainloop()
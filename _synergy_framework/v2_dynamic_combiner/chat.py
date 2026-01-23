import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
import tkinter as tk
from tkinter import scrolledtext

load_dotenv()  # Load variables from .env file

# Configure the API key
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Load Model Data
def load_model_from_file(file_path):
    """Loads the model name from the .reso file or returns error message"""
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


def generate_text(text):
  """Generates text using the Gemini API."""
  prompt = f"Respond to the following text: {text}"
  response = model.generate_content(prompt)
  return response.text

def generate_text_ui():
  """Gets text from input and displays response from AI"""
  text = input_text_area.get("1.0", tk.END)
  output = generate_text(text)
  output_text_area.delete("1.0", tk.END)
  output_text_area.insert(tk.END, output)

if __name__ == '__main__':
    # Create the main window
    window = tk.Tk()
    window.title("AI Chat Module")
    window.geometry("800x600")

    # Model Info - This shows the default model selected
    model_label = tk.Label(window, text=f"Using Model: {model_name}")
    model_label.pack(pady=10)

    # Input Text Area
    input_label = tk.Label(window, text="Input Text:")
    input_label.pack(pady=10)
    input_text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=10)
    input_text_area.pack(pady=10)

    # Generate Button
    generate_button = tk.Button(window, text="Generate Text", command=generate_text_ui)
    generate_button.pack(pady=20)

    # Output Text Area
    output_label = tk.Label(window, text="Output:")
    output_label.pack(pady=10)
    output_text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=10)
    output_text_area.pack(pady=10)


    # Start the main loop
    window.mainloop()
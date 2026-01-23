import sys

def get_user_input(prompt):
    """Reads characters from stdin until a number or enter is detected."""
    print(prompt, end="", flush=True)  # Keep prompt on the same line and show now
    input_buffer = ""
    while True:
        char = sys.stdin.read(1) #read input character by character
        if char == '\n': #check for endline
            return input_buffer.strip()
        if char.isdigit(): #if digit is entered add to buffer
           input_buffer += char
        elif char != '' and char !='\r': # if any other character is entered let user know it must be a number and reset buffer
            print (f"\nInput must be a digit. Please try again:")
            input_buffer = ""
        if len(input_buffer) > 3:
            print(f"\nInput limited to 3 digits. Please try again:")
            input_buffer = "" # limit input to 3 char to stop extreme number errors
        continue # continue if not enter, or digit


def test_input():
    """Tests the input method with a single prompt."""
    user_input = get_user_input("Enter a number (or press enter to continue): ")
    print(f"\nInput received: {user_input}")


if __name__ == "__main__":
    test_input()
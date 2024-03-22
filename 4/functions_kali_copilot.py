import openai
from openai import OpenAI
import os
import subprocess

client = OpenAI() # Create a new OpenAI client
conversation_history = [{"role": "system", "content": "You are a Kali Linux expert. When I give you a prompt, provide me with the Kali Linux command necessary to complete the request. Use all conversation history as reference as needed. (Assume I have all necessary apps, tools, and commands necessary to complete the request. Provide me with ONLY THE COMMAND and DO NOT generate anything before or further beyond the command. DO NOT provide back ticks around the command. DO NOT provide any explanation. Provide the simplest form of the command possible unless I ask for special options, considerations, output, etc. If the request does require a compound command, provide all necessary operators, options, pipes, etc. as a single one-line command. Do not provide me more than one variation or more than one line. DO NOT provide markdown. Just provie the command as plain text.)"}]

def open_file(filepath): #Open and read a file
    with open(filepath, 'r', encoding='UTF-8') as infile:
        return infile.read()
        
def save_file(filepath, content): #Create a new file or overwrite an existing one.
    with open(filepath, 'w', encoding='UTF-8') as outfile:
        outfile.write(content)

def append_file(filepath, content): #Create a new file or append an existing one.
    with open(filepath, 'a', encoding='UTF-8') as outfile:
        outfile.write(content)

def load_functions_list():
    # Load functions list from a text file
    try:
        with open('functions.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Functions list file not found: {file}")
        return ""

def send_question_to_openai(request):
    functions_list = load_functions_list()

    prompt = f"Based on the following question and and a list of functions, look through the functions and contents and tell me which one can best provide me what I need based on my question. Reply with the name of the function and nothing else. Do not include the parentheis. Here is my question: {request} \n\nWhich of the following functions will most likely give me what I need?\n\n {functions_list} \n\nReply with the name of the function and nothing else. Do not include the parentheis."

    # Send the request to OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
    except Exception as e:
        print("An error occurred while connecting to the OpenAI API:", e)
        return f"An error occurred while connecting to the OpenAI API: {e}"

    # Extract the answer
    answer = response.choices[0].message.content.strip()
    print(f"Function: {answer}")
    return answer

openai.api_key = os.getenv("OPENAI_API_KEY") #Use this if you prefer to use the key in an environment variable.        
#openai.api_key = open_file('openai-key.txt') #Grabs your OpenAI key from a file

def general_message(request): #Generates a general message
        # Send the request to OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": request}],
            temperature=0.5,
        )
    except Exception as e:
        print("An error occurred while connecting to the OpenAI API:", e)
        return f"An error occurred while connecting to the OpenAI API: {e}"

    # Extract the answer
    answer = response.choices[0].message.content.strip()
    print(f"Function: {answer}")
    return answer
        
def get_command(): #Sets up and runs the request to the OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=conversation_history,
            temperature=0.1,
        )
        response_text = response.choices[0].message.content.strip()
        return response_text
    except openai.APIConnectionError as e: #Returns and error and retries if there is an issue communicating with the API
        print(f"\nError communicating with the API.")
        print(f"\nError: {e}") #More detailed error output
        print("\nRetrying...")
        return get_command(conversation_history)
    
def command_request(initial_request):
    # Generate the response from GPT
    command_to_execute = get_command(conversation_history)  # This should ideally return only the command to execute
    print(f"Executing Command: {command_to_execute}\n")  # Debugging print

    if command_to_execute.strip():  # Check if the command is not empty
        process = subprocess.Popen(command_to_execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output, error = process.communicate()

        if error:
            print(f"Error executing command: {error}")

        print(output)

        assistant_response = {"role": "assistant", "content": f"{command_to_execute}\n\n{output}"}
        conversation_history.append(assistant_response)
    else:
        print("No command to execute.")

    # Debug the the conversation history
    # print("Current conversation history:", json.dumps(conversation_history, indent=2))
    
    append_file("command-log.txt", "Request: " + initial_request + "\nCommand: " + command_to_execute + "\nOutput: " + output + "\nError: " + error + "\n\n")

while True:
    initial_request = input("\nEnter request: ")

    if initial_request.lower() == "quit":
        break
    else:
        user_prompt = {"role": "user", "content": initial_request}
        conversation_history.append(user_prompt)
        
        # Load functions list from functions.txt
    functions_list = load_functions_list()

    function_mapping = {
        "get_command": get_command,
        "general_message": general_message,
        # Add other functions here
    }

    # Check if functions list is empty
    if not functions_list:
        print("Functions list is empty. Please ensure functions.txt is populated.")

    function_name_str = send_question_to_openai(initial_request)
    function_to_call = function_mapping.get(function_name_str)

    if function_to_call:
        if function_to_call == command_request:
            result = command_request()
        if function_to_call == general_message:
            result = general_message()
    else:
        print("Function not found in the function mapping.")
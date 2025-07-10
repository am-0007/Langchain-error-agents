import os

def read_latest_error(log_file):
    if not os.path.exists(log_file):
        return "Error: Log file not found."
    with open(log_file, 'r') as f:
        lines = f.readlines()
        if not lines:
            return "No errors found in log."
        return lines[-1].strip()

def main():
    log_file = "errors.log"
    latest_error = read_latest_error(log_file)
    print(f"Latest error: {latest_error}")

    user_input = input("What do you think caused this error? ")

    prompt = f"The user suspects the cause of the error \"{latest_error}\" is: {user_input}. Please provide a solution."
    print(f"Generated Prompt: {prompt}")

if __name__ == "__main__":
    main()

import time
import subprocess
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

MAX_RETRIES = os.getenv("MAX_RETRIES")
RETRY_DELAY = os.getenv("RETRY_DELAY")
PYTHON_BIN = os.getenv("PYTHON_BIN")
AEOLUS_URL = os.getenv("AEOLUS_URL")
USER_ID = os.getenv("USER_ID")
READER_TOKEN = os.getenv("READER_TOKEN")

if MAX_RETRIES is None or RETRY_DELAY is None or PYTHON_BIN is None or AEOLUS_URL is None or USER_ID is None or USER_ID is None:
    raise RuntimeError("config incomplete/missing")

MAX_RETRIES = int(MAX_RETRIES)
RETRY_DELAY = int(RETRY_DELAY)

retries = 0
success = False

errors = []

def sendErrorsAsMessage(errors: str):
    data = {
        "message": errors.replace('"', "'")
    }
    json_data = json.dumps(data)
    headers = {
        "Content-Type": "application/json",
        "Hades-Login-Token": READER_TOKEN
    }
    response = requests.post(str(AEOLUS_URL) + "/rest/messages/send/" + str(USER_ID), data=json_data, headers=headers)

    if response.status_code != 204:
        print(response.reason)
        raise RuntimeError("Could not upload reading")
    pass

while retries < MAX_RETRIES and not success:
    print("try " + str(retries) + "...")
    try:
        # Run the reader.py script
        completed_process = subprocess.run(
            [PYTHON_BIN, "reader.py"],
            check=True,
            text=True,
            capture_output=True
        )
        # Print the output of the reader.py script
        print("Output:", completed_process.stdout)
        # If the script runs successfully, break out of the loop
        success = True
    except subprocess.CalledProcessError as e:
        # Handle errors thrown by the reader.py script
        print(f"Attempt {retries} failed with an error.")
        errors.append(e)
    except Exception as e:
        # Handle any other exceptions
        print(f"Attempt {retries} encountered an unexpected error.")
        errors.append(e)

    time.sleep(RETRY_DELAY)
    retries += 1
    pass

if success:
    exit(0)

print("Error reading temperature value")
cummError = ""
for e in errors:
    print(e.stderr)
    cummError = cummError + "\n" + e.stderr
    pass

sendErrorsAsMessage(cummError)

exit(1)

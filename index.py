import time
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

MAX_RETRIES = os.getenv("MAX_RETRIES")
RETRY_DELAY = os.getenv("RETRY_DELAY")
PYTHON_BIN = os.getenv("PYTHON_BIN")

if MAX_RETRIES is None or RETRY_DELAY is None or PYTHON_BIN is None:
    raise RuntimeError("config incomplete/missing")

MAX_RETRIES = int(MAX_RETRIES)
RETRY_DELAY = int(RETRY_DELAY)

retries = 0
success = False

errors = []

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
for e in errors:
    print(e.stderr)
    pass

exit(1)

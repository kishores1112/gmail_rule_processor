import json
import os

import requests

print("running scripts")

run_id = os.environ.get("GITHUB_RUN_ID", "unknown")
diff_file = os.environ.get("DIFF_FILE", f"tmp/diff_{run_id}.txt")
print(f"GitHub Run ID: {run_id}")
print(f"Diff file: {diff_file}")

CONVERSATION_API_URL = (
    "https://devgai-conversation-api.annalect.com/v2/api/conversations"
)
ACTION_REQUIRED = f"ACTION_RECOMMENDED_RUN_ID_{run_id}"

# Input
with open(diff_file, "r") as f:
    diff_content = f.read()

# Output
response_json_file = f"tmp/scan_response_{run_id}.json"
message_file = f"tmp/scan_message_{run_id}.txt"
status_file = f"tmp/scan_status_{run_id}.txt"


payload = {
    "model_name": "gpt-4o",
    "metadata": {"run_id": run_id},
    "client_id": "default",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "text": (
                        # f"Analyze the following code diff for security vulnerabilities:\n\n{diff_content}\n\n""
                        f"Analyze the following code diff for hard coded or leaked security credentials:\n\n{diff_content}\n\n"
                        f"If you find any likely hard coded or leaked security credentials, you MUST prepend your response with the exact string '{ACTION_REQUIRED}'. "
                        f"If there are no likely vulnerabilities, DO NOT include '{ACTION_REQUIRED}' in your response. "
                        f"After the string (if present), provide an explanation."
                    )
                }
            ],
        }
    ],
    "system_prompt": [
        {
            "text": "Help identify hard coded or leaked security credentials in the codebase."
        }
    ],
    "additional_model_request_fields": {},
    "user_id": "default",
}

headers = {"x-api-key": "dev-1356134h1fh134fhg134hg4h134hg134hg"}
conversation_api_key = os.environ.get("CONVERSATION_API_KEY", "Unknown")
headers = {"x-api-key": "dev-6de44a2f86e5c7b8ff97e6f1ead92a9cdeb4cbc4fb64c1f2a39514551ff0c9af"}

print("Response from the API:")
response = requests.post(url=CONVERSATION_API_URL, json=payload, headers=headers)
print(response.status_code)
response_json = response.json()

# Write full response JSON to file
with open(response_json_file, "w") as f:
    json.dump(response_json, f, indent=2)

message_text = response_json["data"]["output"]["message"]["content"][0]["text"]
print(message_text)

# Write message text to file
with open(message_file, "w") as f:
    f.write(message_text)

# Write status to file
if ACTION_REQUIRED in message_text:
    with open(status_file, "w") as f:
        f.write("ACTION_REQUIRED")
else:
    with open(status_file, "w") as f:
        f.write("OK")

print("Script completed successfully.")

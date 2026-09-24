import os
from dotenv import load_dotenv
from huggingface_hub import HfApi

# Load environment variables
load_dotenv("backend/.env")

# Get token
token = os.getenv("HF_TOKEN")
if not token:
    print("ERROR: HF_TOKEN not found! Please save your backend/.env file.")
    exit(1)

api = HfApi(token=token)
repo_id = "mohanvannemreddy7/genvideoai"

print(f"Uploading all files to: https://huggingface.co/spaces/{repo_id}...")

# Upload the current folder, replacing remote files but ignoring git, venv, and cache
api.upload_folder(
    folder_path=".",
    repo_id=repo_id,
    repo_type="space",
    delete_patterns="*",  # This ensures any remote files not present locally are deleted
    ignore_patterns=[
        ".git/*",
        "backend/venv/*",
        "backend/__pycache__/*",
        "backend/outputs/*",
        "backend/uploads/*",
        "upload_to_hf.py", # Exclude this script itself
        "backend/cookies.txt", # Don't push private cookies
        "backend/.env" # SECRETS: Exclude environment variables
    ]
)

print("Upload complete!")

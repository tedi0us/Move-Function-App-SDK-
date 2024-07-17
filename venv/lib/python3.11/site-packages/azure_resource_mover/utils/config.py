# azure_resource_mover/utils/config.py

import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://wapp-azurenamingtool-wus.azurewebsites.net/api"
TENANT_ID = "cbca83b8-a971-43a8-9ab3-ce2599ff12ea"
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
RESOURCE_ID = "41aee129-4726-4cc1-b8de-374db5917da1"
API_KEY = os.getenv('AZURE_NAMING_TOOL_API_KEY')

DEBUG = False
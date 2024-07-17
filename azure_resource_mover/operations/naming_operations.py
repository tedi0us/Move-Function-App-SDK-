# azure_resource_mover/naming_api.py

import os
import json
from dotenv import load_dotenv
import msal
import requests

load_dotenv()

BASE_URL = "https://wapp-azurenamingtool-wus.azurewebsites.net/api"
TENANT_ID = "cbca83b8-a971-43a8-9ab3-ce2599ff12ea"
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
RESOURCE_ID = "41aee129-4726-4cc1-b8de-374db5917da1"
API_KEY = os.getenv('AZURE_NAMING_TOOL_API_KEY')

DEBUG = False  # Set this to True when you need detailed logs

def get_access_token():
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=authority, client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=[f"{RESOURCE_ID}/.default"])
    if "access_token" in result:
        return result["access_token"]
    else:
        print(f"Error getting token: {result.get('error')}")
        print(f"Error description: {result.get('error_description')}")
        return None

def make_api_call(endpoint, method="GET", params=None, data=None):
    token = get_access_token()
    if not token:
        print("Failed to get access token")
        return None

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
        "APIKey": API_KEY,
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/{endpoint}"
    
    if DEBUG:
        print(f"Making {method} request to: {url}")
        print(f"Headers: {headers}")
        print(f"Params: {params}")
        print(f"Data: {json.dumps(data, indent=2) if data else None}")

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        
        if DEBUG:
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                if DEBUG:
                    print(f"Response JSON: {json.dumps(json_response, indent=2)}")
                return json_response
            except json.JSONDecodeError:
                if DEBUG:
                    print("Received non-JSON response:")
                    print(response.text[:500])  # Print first 500 characters of response
                return None
        else:
            if DEBUG:
                print(f"API returned status code {response.status_code}")
                print(response.text[:500])
            return None

    except requests.RequestException as e:
        if DEBUG:
            print(f"API call failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response headers: {dict(e.response.headers)}")
                print(f"Response content: {e.response.text[:500]}")
        return None

def get_resource_types():
    """Get all resource types."""
    return make_api_call("ResourceTypes")

def get_resource_name_components(resource_type_short):
    """Get the components for a specific resource type."""
    all_types = get_resource_types()
    if not all_types:
        print("Failed to retrieve resource types.")
        return None

    resource_type = next((rt for rt in all_types if rt.get('ShortName', '').lower() == resource_type_short.lower()), None)
    if not resource_type:
        print(f"Resource type with short name '{resource_type_short}' not found.")
        return None

    # Parse the optional and exclude fields
    optional_components = resource_type.get('optional', '').split(',') if resource_type.get('optional') else []
    excluded_components = resource_type.get('exclude', '').split(',') if resource_type.get('exclude') else []

    # We don't have explicit required components, so we'll consider all non-excluded as required
    all_possible_components = ['ResourceEnvironment', 'ResourceLocation', 'ResourceInstance', 'ResourceName', 'ResourceOrg', 'ResourceProjAppSvc', 'ResourceUnitDept', 'ResourceFunction']
    required_components = [comp for comp in all_possible_components if comp not in excluded_components and comp not in optional_components]

    return required_components, optional_components, resource_type

def get_component_options(component_name):
    """Retrieve options for a specific naming component."""
    response = make_api_call(f"{component_name}s")
    if response:
        if isinstance(response, list):
            return [{"name": option.get("name", "N/A"), "shortName": option.get("shortName", "N/A")} for option in response]
        elif isinstance(response, dict):
            if DEBUG:
                print(f"Unexpected response format for {component_name}:")
                print(json.dumps(response, indent=2))
        else:
            if DEBUG:
                print(f"Unexpected response type for {component_name}: {type(response)}")
                print(response[:500])  # Print first 500 characters of response
    else:
        if DEBUG:
            print(f"Failed to retrieve options for {component_name}")
    return []

def create_proj_app_svc(name, short_name):
    """Create a new project/app/service."""
    data = {
        "name": name,
        "shortName": short_name
    }
    response = make_api_call("ResourceProjAppSvcs", method="POST", data=data)
    if response:
        print(f"Successfully created new project/app/service: {name} ({short_name})")
        return True
    else:
        print(f"Failed to create new project/app/service: {name} ({short_name})")
        return False

def generate_resource_name(resource_type, **components):
    """Generate a resource name based on the provided resource type and components."""
    # Map the component names to the format expected by the API
    component_map = {
        "ResourceEnvironment": "resourceEnvironment",
        "ResourceLocation": "resourceLocation",
        "ResourceInstance": "resourceInstance",
        "ResourceName": "resourceName",
        "ResourceOrg": "resourceOrg",
        "ResourceProjAppSvc": "resourceProjAppSvc",
        "ResourceUnitDept": "resourceUnitDept",
        "ResourceFunction": "resourceFunction"
    }

    data = {
        "resourceType": resource_type,
        **{component_map.get(k, k): v for k, v in components.items() if v},
        "customComponents": {},
        "resourceId": 0,
        "createdBy": "ARMover"
    }
    
    if DEBUG:
        print(f"Sending data to API: {json.dumps(data, indent=2)}")
    
    response = make_api_call("ResourceNamingRequests/RequestName", method="POST", data=data)
    
    if response is None:
        if DEBUG:
            print("API call returned None. Check the make_api_call function for errors.")
        return None

    if DEBUG:
        print(f"API Response: {json.dumps(response, indent=2)}")

    if isinstance(response, dict):
        if 'resourceName' in response and response['resourceName']:
            return {"generatedName": response['resourceName']}
        elif 'message' in response:
            if "already exists" in response['message']:
                return {"error": "name_exists"}
            else:
                if DEBUG:
                    print(f"API Error: {response['message']}")
                return None
    else:
        if DEBUG:
            print("Unexpected API response format:")
            print(json.dumps(response, indent=2))
        return None

def get_naming_component_options():
    """
    Generator function to yield naming component options one at a time.
    """
    components = [
        ("Resource Type", get_resource_types),
        ("Resource Environment", lambda: get_component_options("ResourceEnvironment")),
        ("Resource Location", lambda: get_component_options("ResourceLocation")),
        ("Resource Project/Application/Service", lambda: get_component_options("ResourceProjAppSvc")),
        ("Resource Function", lambda: get_component_options("ResourceFunction")),
        ("Resource Instance", lambda: get_component_options("ResourceInstance")),
        ("Resource Organization", lambda: get_component_options("ResourceOrg")),
        ("Resource Unit/Department", lambda: get_component_options("ResourceUnitDept"))
    ]

    for component_name, get_options_func in components:
        options = get_options_func()
        if options:
            yield component_name, options
        else:
            yield component_name, []

def list_all_components():
    """List all available naming components."""
     
    components = [
        "ResourceEnvironment",
        "ResourceLocation",
        "ResourceOrg",
        "ResourceProjAppSvc",
        "ResourceType",
        "ResourceUnitDept",
        "ResourceFunction"
    ]
    return {component: get_component_options(component) for component in components}

if __name__ == "__main__":
    print("Retrieving naming component options sequentially:")
    for component_name, options in get_naming_component_options():
        print(f"\n{component_name}:")
        if options:
            for option in options:
                if isinstance(option, dict):
                    print(f"- {option.get('name', 'N/A')} (Short Name: {option.get('shortName', 'N/A')})")
                else:
                    print(f"- {option}")
        else:
            print("No options available")
        input("Press Enter to continue to the next component...")
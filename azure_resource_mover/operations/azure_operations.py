# azure_resource_mover/azure_operations.py

import json
import subprocess

def run_az_command(command):
    """Run an Azure CLI command and return the result as a dictionary."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout.strip():
            return json.loads(result.stdout)
        else:
            return None  # Return None for commands with no output
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Azure CLI command: {e}")
        print(f"Error output: {e.stderr}")
        return None
    except json.JSONDecodeError:
        print(f"Command output is not in JSON format: {result.stdout}")
        return None

def get_subscriptions():
    """Get a list of available subscriptions."""
    return run_az_command("az account list")

def move_function_app(source_subscription_id, target_subscription_id, resource_group_name, function_app_name):
    """
    Move a function app between subscriptions.
    Note: This is a complex operation and may require additional steps depending on your specific setup.
    """
    # Set the source subscription
    run_az_command(f"az account set --subscription {source_subscription_id}")

    # Get function app details
    function_app = run_az_command(f"az functionapp show --name {function_app_name} --resource-group {resource_group_name}")
    if not function_app:
        print(f"Function app {function_app_name} not found in source subscription")
        return None

    # Set the target subscription
    run_az_command(f"az account set --subscription {target_subscription_id}")

    # Create or ensure resource group exists in target subscription
    run_az_command(f"az group create --name {resource_group_name} --location {function_app['location']}")

    # Create function app in target subscription
    new_function_app = run_az_command(
        f"az functionapp create --name {function_app_name} --resource-group {resource_group_name} "
        f"--consumption-plan-location {function_app['location']} --runtime python --os-type Linux"
    )

    if new_function_app:
        print(f"Function app {function_app_name} created in target subscription")
        
        # TODO: Copy app settings, connection strings, and other configurations
        
        # Delete the original function app
        run_az_command(f"az account set --subscription {source_subscription_id}")
        run_az_command(f"az functionapp delete --name {function_app_name} --resource-group {resource_group_name}")
        print(f"Original function app {function_app_name} deleted from source subscription")

        return new_function_app
    else:
        print(f"Failed to create function app {function_app_name} in target subscription")
        return None

def create_function_app(subscription_id, resource_group_name, function_app_name, location):
    """Create a new function app."""
    run_az_command(f"az account set --subscription {subscription_id}")
    return run_az_command(
        f"az functionapp create --name {function_app_name} --resource-group {resource_group_name} "
        f"--consumption-plan-location {location} --runtime python --os-type Linux"
    )

def list_function_apps(subscription_id, resource_group_name=None):
    """List all function apps in a subscription or resource group."""
    run_az_command(f"az account set --subscription {subscription_id}")
    if resource_group_name:
        return run_az_command(f"az functionapp list --resource-group {resource_group_name}")
    else:
        return run_az_command("az functionapp list")

def list_resource_groups(subscription_id):
    """List all resource groups in a subscription."""
    run_az_command(f"az account set --subscription {subscription_id}")
    return run_az_command("az group list")

def delete_function_app(subscription_id, resource_group_name, function_app_name):
    """Delete a function app."""
    run_az_command(f"az account set --subscription {subscription_id}")
    return run_az_command(f"az functionapp delete --name {function_app_name} --resource-group {resource_group_name}")

if __name__ == "__main__":
    # This allows you to test the Azure operations directly
    print("Listing Subscriptions:")
    subscriptions = get_subscriptions()
    for sub in subscriptions:
        print(f"- {sub['name']} (ID: {sub['id']})")

    # Uncomment and modify to test other operations
    # subscription_id = "your_subscription_id"
    # resource_group = "your_resource_group"
    # location = "your_location"
    # 
    # print("\nListing Function Apps:")
    # apps = list_function_apps(subscription_id, resource_group)
    # for app in apps:
    #     print(f"- {app['name']}")
    # 
    # new_app_name = "testfunctionapp12345"
    # print(f"\nCreating new Function App: {new_app_name}")
    # new_app = create_function_app(subscription_id, resource_group, new_app_name, location)
    # if new_app:
    #     print(f"Created: {new_app['name']}")
    # 
    #     print(f"\nDeleting Function App: {new_app_name}")
    #     if delete_function_app(subscription_id, resource_group, new_app_name):
    #         print("Function App deleted successfully")
    #     else:
    #         print("Failed to delete Function App")
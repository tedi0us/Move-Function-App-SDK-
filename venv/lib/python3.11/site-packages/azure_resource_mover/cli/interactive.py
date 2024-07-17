# azure_resource_mover/cli/interactive.py

import re
from azure_resource_mover.operations.azure_operations import (
    get_subscriptions,
    move_function_app,
    list_function_apps,
    list_resource_groups
)
from azure_resource_mover.operations.naming_operations import (
    generate_resource_name,
    get_resource_name_components,
    get_component_options,
    create_proj_app_svc
)
from azure_resource_mover.utils.helpers import clear_screen, print_header_and_clear

def select_from_options(options, prompt):
    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option['name']} (Short Name: {option['shortName']})")
    while True:
        try:
            choice = int(input("Enter the number of your choice: ")) - 1
            if 0 <= choice < len(options):
                return options[choice]['shortName']
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")

def get_us_locations():
    all_locations = get_component_options("ResourceLocation")
    us_locations = [loc for loc in all_locations if loc['name'].startswith(('Central US', 'East US', 'North Central US', 'South Central US', 'West Central US', 'West US'))]
    return us_locations

def select_location():
    us_locations = get_us_locations()
    all_locations = get_component_options("ResourceLocation")

    while True:
        print("\nSelect Resource Location:")
        print("US Locations:")
        for i, loc in enumerate(us_locations, 1):
            print(f"{i}. {loc['name']} (Short Name: {loc['shortName']})")
        print(f"{len(us_locations) + 1}. View all locations")
        print(f"{len(us_locations) + 2}. Back")

        choice = input("Enter your choice: ")

        try:
            choice = int(choice)
            if 1 <= choice <= len(us_locations):
                return us_locations[choice - 1]['shortName']
            elif choice == len(us_locations) + 1:
                print("\nAll Locations:")
                for i, loc in enumerate(all_locations, 1):
                    print(f"{i}. {loc['name']} (Short Name: {loc['shortName']})")
                all_choice = input("Enter your choice (or 'b' to go back to US locations): ")
                if all_choice.lower() == 'b':
                    continue
                all_choice = int(all_choice)
                if 1 <= all_choice <= len(all_locations):
                    return all_locations[all_choice - 1]['shortName']
            elif choice == len(us_locations) + 2:
                return None
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")

def generate_resource_name_interactive(resource_type_short):
    print_header_and_clear()
    print(f"\nGenerating {resource_type_short.upper()} Name")
    print("-----------------------------")

    components_info = get_resource_name_components(resource_type_short)
    if not components_info:
        print(f"Failed to retrieve component information for {resource_type_short.upper()}.")
        return None

    required_components, optional_components, resource_type_details = components_info

    component_data = {}

    for component in required_components + optional_components:
        if component == "ResourceInstance":
            continue  # Skip this as we'll handle it separately

        if component in optional_components:
            include = input(f"\nDo you want to include {component}? (y/n): ").lower() == 'y'
            if not include:
                continue

        if component == "ResourceLocation":
            selected = select_location()
            if selected:
                component_data[component] = selected
            else:
                print("Location selection cancelled.")
                return None
        elif component == "ResourceProjAppSvc":
            options = get_component_options(component)
            print("\nCurrent Project/App/Service options:")
            for i, option in enumerate(options, 1):
                print(f"{i}. {option['name']} (Short Name: {option['shortName']})")

            create_new = input("\nDo you want to create a new project/app/service? (y/n): ").lower() == 'y'
            if create_new:
                name = input("Enter the name for the new project/app/service (e.g., 'HR PTO App'): ")
                words = name.split()
                suggested_short_name = ''.join(word[0] for word in words).lower()[:3]
                
                print(f"Suggested short name: {suggested_short_name}")
                confirm = input("Do you want to use this suggested short name? (y/n): ").lower() == 'y'
                
                if not confirm:
                    short_name = input("Enter a custom short name (1-3 characters): ")
                    if len(short_name) < 1 or len(short_name) > 3:
                        print("Short name must be between 1 and 3 characters. Please try again.")
                        continue
                else:
                    short_name = suggested_short_name

                if create_proj_app_svc(name, short_name):
                    component_data[component] = short_name
                    print(f"Successfully created new project/app/service: {name} ({short_name})")
                else:
                    print("Failed to create new project/app/service. Please select from existing options.")
                    selected = select_from_options(options, f"\nSelect {component}:")
                    component_data[component] = selected
            else:
                selected = select_from_options(options, f"\nSelect {component}:")
                component_data[component] = selected
        else:
            options = get_component_options(component)
            if options:
                selected = select_from_options(options, f"\nSelect {component}:")
                component_data[component] = selected
            else:
                print(f"No options available for {component}")
                value = input(f"Please enter a value for {component} manually: ")
                if value:
                    component_data[component] = value

    for attempt in range(1, 6):  # Try up to 5 times
        component_data['ResourceInstance'] = str(attempt)
        result = generate_resource_name(resource_type_short, **component_data)
        
        if result and 'generatedName' in result:
            generated_name = result['generatedName']
            print(f"\nGenerated {resource_type_short.upper()} name: {generated_name}")
            
            if 'regx' in resource_type_details and re.match(resource_type_details['regx'], generated_name):
                print("The generated name is valid according to the resource type rules.")
                return generated_name  # Return the generated name
            else:
                print("Warning: The generated name does not match the resource type rules.")
                if 'regx' in resource_type_details:
                    print(f"Validation regex: {resource_type_details['regx']}")
                print(f"Valid text: {resource_type_details.get('validText', 'N/A')}")
                print(f"Invalid text: {resource_type_details.get('invalidText', 'N/A')}")
                return generated_name  # Return the generated name even if it doesn't match rules
        elif result and 'error' in result and result['error'] == 'name_exists':
            print(f"\nAttempt {attempt}: The generated name already exists. Trying again with incremented instance.")
        else:
            print(f"\nAttempt {attempt}: Failed to generate a {resource_type_short.upper()} name. Trying again with incremented instance.")

    print(f"\nFailed to generate a unique {resource_type_short.upper()} name after 5 attempts.")
    return None  # Return None if failed to generate a name

def generate_function_app_name_interactive():
    return generate_resource_name_interactive("func")

def generate_resource_group_name_interactive():
    return generate_resource_name_interactive("rg")

def move_function_app_interactive():
    print_header_and_clear()
    print("\nMoving Function App")
    print("-------------------")

    # Get and select source subscription
    subscriptions = get_subscriptions()
    print("\nSelect source subscription:")
    for i, sub in enumerate(subscriptions, 1):
        print(f"{i}. {sub['name']} (ID: {sub['id']})")
    
    while True:
        try:
            choice = int(input("Enter the number of your choice: ")) - 1
            if 0 <= choice < len(subscriptions):
                source_sub = subscriptions[choice]['id']
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")

    # Get and select target subscription
    print("\nSelect target subscription:")
    for i, sub in enumerate(subscriptions, 1):
        print(f"{i}. {sub['name']} (ID: {sub['id']})")
    
    while True:
        try:
            choice = int(input("Enter the number of your choice: ")) - 1
            if 0 <= choice < len(subscriptions):
                target_sub = subscriptions[choice]['id']
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")

    # Get resource groups in the target subscription
    target_resource_groups = list_resource_groups(target_sub)
    if not target_resource_groups:
        print("No resource groups found in the target subscription or an error occurred.")
        input("Press Enter to continue...")
        return

    print("\nSelect target resource group:")
    for i, group in enumerate(target_resource_groups, 1):
        print(f"{i}. {group['name']} (Location: {group['location']})")
    
    while True:
        try:
            choice = int(input("Enter the number of your choice: ")) - 1
            if 0 <= choice < len(target_resource_groups):
                resource_group = target_resource_groups[choice]['name']
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")

    function_app = input("Enter function app name: ")

    # Generate new function app name
    print("\nDo you want to generate a new name for the moved function app?")
    generate_new_name = input("Enter 'y' for yes, or any other key to keep the current name: ").lower() == 'y'

    if generate_new_name:
        new_name = generate_function_app_name_interactive()
        if new_name:
            function_app = new_name
        else:
            print("Failed to generate a new name. Using the original name.")

    # Confirm move operation
    print(f"\nMoving function app '{function_app}' from subscription '{source_sub}' to '{target_sub}'")
    print(f"Target resource group: {resource_group}")
    confirm = input("Do you want to proceed? (y/n): ").lower()

    if confirm == 'y':
        result = move_function_app(source_sub, target_sub, resource_group, function_app)
        if result:
            print(f"Function app {function_app} moved successfully")
        else:
            print(f"Failed to move function app {function_app}")
    else:
        print("Move operation cancelled.")

    input("Press Enter to continue...")

def list_function_apps_interactive():
    print_header_and_clear()
    print("\nListing Function Apps")
    print("---------------------")
    
    # Get and select subscription
    subscriptions = get_subscriptions()
    print("\nSelect subscription:")
    for i, sub in enumerate(subscriptions, 1):
        print(f"{i}. {sub['name']} (ID: {sub['id']})")
    
    while True:
        try:
            choice = int(input("Enter the number of your choice: ")) - 1
            if 0 <= choice < len(subscriptions):
                subscription = subscriptions[choice]['id']
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")

    resource_group = input("Enter resource group name (or press Enter to list all): ")

    apps = list_function_apps(subscription, resource_group if resource_group else None)
    if apps:
        print("\nFunction Apps:")
        for app in apps:
            print(f"- {app['name']}")
    else:
        print("No Function Apps found or an error occurred.")

    input("Press Enter to continue...")

def list_resource_groups_interactive():
    print_header_and_clear()
    print("\nListing Resource Groups")
    print("------------------------")
    
    # Get and select subscription
    subscriptions = get_subscriptions()
    print("\nSelect subscription:")
    for i, sub in enumerate(subscriptions, 1):
        print(f"{i}. {sub['name']} (ID: {sub['id']})")
    
    while True:
        try:
            choice = int(input("Enter the number of your choice: ")) - 1
            if 0 <= choice < len(subscriptions):
                subscription = subscriptions[choice]['id']
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")

    groups = list_resource_groups(subscription)
    if groups:
        print("\nResource Groups:")
        for group in groups:
            print(f"- {group['name']} (Location: {group['location']})")
    else:
        print("No Resource Groups found or an error occurred.")

    input("Press Enter to continue...")
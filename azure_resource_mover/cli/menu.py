# azure_resource_mover/cli/menu.py

from azure_resource_mover.cli.interactive import (
    generate_function_app_name_interactive,
    generate_resource_group_name_interactive,
    move_function_app_interactive,
    list_function_apps_interactive,
    list_resource_groups_interactive
)
from azure_resource_mover.utils.helpers import clear_screen, print_header_and_clear

def generate_resource_menu():
    while True:
        print_header_and_clear()
        print("\nGenerate Resource Menu:")
        print("1. Generate Function App Name")
        print("2. Generate Resource Group Name")
        print("3. Back to Main Menu")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            generate_function_app_name_interactive()
            input("Press Enter to continue...")
        elif choice == '2':
            generate_resource_group_name_interactive()
            input("Press Enter to continue...")
        elif choice == '3':
            return
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

def move_resources_menu():
    while True:
        print_header_and_clear()
        print("\nMove Resources Menu:")
        print("1. Move Function App")
        print("2. Back to Main Menu")
        
        choice = input("Enter your choice (1-2): ")
        
        if choice == '1':
            move_function_app_interactive()
        elif choice == '2':
            return
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

def list_resources_menu():
    while True:
        print_header_and_clear()
        print("\nList Resources Menu:")
        print("1. List Function Apps")
        print("2. List Resource Groups")
        print("3. Back to Main Menu")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            list_function_apps_interactive()
        elif choice == '2':
            list_resource_groups_interactive()
        elif choice == '3':
            return
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

def main_menu():
    while True:
        print_header_and_clear()
        print("\nMain Menu:")
        print("1. Generate Resource")
        print("2. Move Resources")
        print("3. List Resources in Subscription")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            generate_resource_menu()
        elif choice == '2':
            move_resources_menu()
        elif choice == '3':
            list_resources_menu()
        elif choice == '4':
            print("Exiting AR MOVER. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main_menu()
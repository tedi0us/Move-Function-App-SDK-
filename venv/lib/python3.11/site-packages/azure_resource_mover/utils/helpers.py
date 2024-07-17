# azure_resource_mover/utils/helpers.py

import os
import platform
from azure_resource_mover.cli.header import print_header

def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def print_header_and_clear():
    clear_screen()
    print_header()
    print("AR MOVER - Azure Resource Mover")
    print("--------------------------------")

def select_from_list(options, prompt):
    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    
    while True:
        try:
            choice = int(input("Enter the number of your choice: ")) - 1
            if 0 <= choice < len(options):
                return options[choice]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")

def confirm_action(prompt):
    while True:
        response = input(f"{prompt} (y/n): ").lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Invalid input. Please enter 'y' for yes or 'n' for no.")

def input_with_default(prompt, default):
    user_input = input(f"{prompt} [{default}]: ")
    return user_input if user_input else default
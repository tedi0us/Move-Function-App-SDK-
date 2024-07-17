# azure_resource_mover/main.py

from azure_resource_mover.cli.menu import main_menu
from azure_resource_mover.utils.helpers import print_header_and_clear

def run():
    print_header_and_clear()
    main_menu()

if __name__ == "__main__":
    run()
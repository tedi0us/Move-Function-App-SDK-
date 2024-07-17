# azure_resource_mover/header.py

BANNER = """
 _______  _______  _______  _______           _______  _______ 
(  ___  )(  ____ )(       )(  ___  )|\     /|(  ____ \(  ____ )
| (   ) || (    )|| () () || (   ) || )   ( || (    \/| (    )|
| (___) || (____)|| || || || |   | || |   | || (__    | (____)|
|  ___  ||     __)| |(_)| || |   | |( (   ) )|  __)   |     __)
| (   ) || (\ (   | |   | || |   | | \ \_/ / | (      | (\ (   
| )   ( || ) \ \__| )   ( || (___) |  \   /  | (____/\| ) \ \__
|/     \||/   \__/|/     \|(_______)   \_/   (_______/|/   \__/
               Azure Resource Mover CLI Tool
"""

def print_header():
    print(BANNER)
    print("Welcome to AR MOVER - Azure Resource Mover CLI tool")
    print("Use --help for more information on commands.")
    print()
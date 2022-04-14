from chesslib import MatchManager
from sys import exit

def main():

    manager = MatchManager()
    if manager.inProgress:
        print("There are IN-PROGRESS matches.  Would you like to select one to resume? y/n")
        if input("> ") == 'y':
            manager.resume_match()
        else:
            print("Create a new match?  y/n")
            if input("> ") == "y":
                manager.create_match()
            else:
                print("Goodbye")
                exit(0)

    else:
        print("Create a new match?  y/n")
        if input("> ") == "y":
            manager.create_match()         
        else:
            print("Goodbye")
            exit(0)
    
    manager.play()
        
    
if __name__ == "__main__":
    main()
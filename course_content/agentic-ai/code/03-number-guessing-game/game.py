
import random

MODES = {
    "easy": {
        "start": 1,
        "end": 20,
        "attempts": 10
    },
    "medium": {
        "start": 1,
        "end": 50,
        "attempts": 7
    },
    "hard": {
        "start": 1,
        "end": 100,
        "attempts": 6
    }
}

def show_greeting():
    print("Welcome to Number Guessing Game !!!")

def show_options():
    print("1. Easy - [1 - 20] with 10 attempts")
    print("2. Medium - [1 - 50] with 7 attempts")
    print("3. Hard - [1 - 100] with 6 attempts")

def get_user_option():
    option = input("Enter the options (1/2/3) : ")
    return option

def get_start_end_attempts(user_selected_mode: str):
    value = {}
    if user_selected_mode == "1":
        value = MODES["easy"]
    elif user_selected_mode == "2":
        value = MODES["medium"]
    elif user_selected_mode == "3":
        value = MODES["hard"]
    return value.get("start"), value.get("end"), value.get("attempts")

def generate_secret_number(start: int, end: int):
    return random.randint(start, end)

def play(secret_number, attempts):
    while attempts > 0:
        user_guess = int(input("Enter your Guess : "))
        if user_guess == secret_number:
            print("Hurraaayyyy !! Congratulations You Won")
            return True
        elif user_guess > secret_number:
            print("Your guess is higher")
        else:
            print("Your guess is lower")
        attempts = attempts - 1

    print("Dont Worry !!! You have lost the game. Better luck next time.")
    print("The Secret Number is ", secret_number)
    return False

def play_again():
    play_again = input("Do you want to play again ? (Y/N) ")
    if play_again.upper() == "Y":
        main()
    return None

def collect_details_for_leaderboard():
    with open("leaderboard.txt", "a") as f:
        name = input("Enter the name : ")
        f.write(name + "\n")

def main():
    show_greeting()
    show_options()
    user_selected_mode = get_user_option()
    start, end, attempts = get_start_end_attempts(user_selected_mode)
    secret_number = generate_secret_number(start, end)
    print(secret_number)
    won = play(secret_number, attempts)
    if won:
        collect_details_for_leaderboard()
    play_again()

main()

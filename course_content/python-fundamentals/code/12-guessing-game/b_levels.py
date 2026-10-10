import random

def print_menu():
    """
    Function to print menu"""
    print("Welcome to the Enhanced Number Guessing Game!")

    # Select difficulty level
    print("Select difficulty level:")
    print("1. Easy (Range: 1-50, 10 attempts)")
    print("2. Medium (Range: 1-100, 7 attempts)")
    print("3. Hard (Range: 1-1000, 5 attempts)")

def get_min_max_total_attempts(difficulty):
    # Set parameters based on difficulty level
    if difficulty == 1:
        min_value, max_value, max_attempts = 1, 50, 10
    elif difficulty == 2:
        min_value, max_value, max_attempts = 1, 100, 7
    else:
        min_value, max_value, max_attempts = 1, 1000, 5
    return min_value, max_value, max_attempts

def play(secret_number, min_value, max_value, max_attempts):
    attempts = 0
    hints_given = False

    print(f"\nI'm thinking of a number between {min_value} and {max_value}.")
    print(f"You have {max_attempts} attempts to guess it.\n")

    while attempts < max_attempts:
        guess = get_valid_number(f"Attempt {attempts + 1}: Enter your guess: ", min_value, max_value)
        attempts += 1

        if guess < secret_number:
            print("Too low! Try again.")
        elif guess > secret_number:
            print("Too high! Try again.")
        else:
            print(f"Congratulations! You guessed the number in {attempts} attempts.")
            break

        # Provide a hint after half the attempts if the user hasn't guessed correctly
        if attempts == max_attempts // 2 and not hints_given:
            hint = "even" if secret_number % 2 == 0 else "odd"
            print(f"Hint: The number is {hint}.")
            hints_given = True

    if attempts == max_attempts and guess != secret_number:
        print(f"\nSorry, you've used all {max_attempts} attempts. The correct number was {secret_number}.")

def get_valid_number(prompt, min_value, max_value):
    """Helper function to get a valid number within a specified range."""
    while True:
        try:
            num = int(input(prompt))
            if min_value <= num <= max_value:
                return num
            else:
                print(f"Please enter a number between {min_value} and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def play_again():
    # Ask the user if they want to play again
    play_again = input("\nDo you want to play again? (yes/no): ").strip().lower()
    if play_again == 'yes':
        number_guessing_game()
    else:
        print("Thank you for playing! Goodbye.")

def number_guessing_game():
    """
    An enhanced number guessing game where the user selects a difficulty level
    and attempts to guess a randomly generated number within a range.
    """

    print_menu()
    difficulty = get_valid_number("Choose a difficulty level (1, 2, or 3): ", 1, 3)
    min_value, max_value, max_attempts = get_min_max_total_attempts(difficulty)
    secret_number = random.randint(min_value, max_value)
    play(secret_number, min_value, max_value, max_attempts)
    play_again()
    

if __name__ == "__main__":
    number_guessing_game()

import random

def get_user_guess():
    # Keep asking until the input is a whole number
    while True:
        try:
            return int(input("Enter your guess: "))
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def get_random_number():
    secret_number = random.randint(1, 100)
    return secret_number

def number_guessing_game():
    """
    A simple number guessing game where the user tries to guess a randomly
    generated number between 1 and 100.
    """

    # Generate a random number between 1 and 100
    secret_number = get_random_number()
    attempts = 0

    print("Welcome to the Number Guessing Game!")
    print("I'm thinking of a number between 1 and 100.")

    while True:
        attempts += 1
        guess = get_user_guess()

        # Check if the guess is correct
        if guess < secret_number:
            print("Too low! Try again.")
        elif guess > secret_number:
            print("Too high! Try again.")
        else:
            print(f"Congratulations! You guessed the number in {attempts} attempts.")
            break

if __name__ == "__main__":
    number_guessing_game()

import os
import re
import random
import string
import textwrap
import wikipediaapi
from colorama import Fore, Style

from dotenv import load_dotenv
import openai

# Define global variable Colours List from Colorama colours
COLOURS_LIST = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]

# Difficulty levels
EASY = (7, 5)
MEDIUM = (10, 7)
HARD = (15, 10)

# 1) Load environment variables
load_dotenv()

# 2) Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Optional: Raise an error if key is missing
if not openai.api_key:
    raise ValueError("API key not found. Ensure OPENAI_API_KEY is set in your .env file.")


def get_links_from_wiki():
    """
    Returns a list of titles of links from a specified Wikipedia page.
    """
    wiki_api = wikipediaapi.Wikipedia(language="en", user_agent="word-o-pedia/v1")
    page = wiki_api.page("Nelson Mandela")

    links_list = page.links.keys()
    return links_list


def get_game_words(links, difficulty):
    """
    Take every nth word to distribute evenly across the alphabet.
    """
    grid_size, num_words = difficulty

    # Only use links that are purely alphabetical and of length <= grid_size
    alphabetic_links = [
        link for link in links
        if re.match(r"^[A-Za-z]+$", link) and len(link) <= grid_size
    ]

    # Step size
    step = len(alphabetic_links) // num_words if len(alphabetic_links) > num_words else 1

    # Take every nth word, limited by num_words
    game_words = alphabetic_links[::step][:num_words]
    return game_words


def initialise_grid(game_words, difficulty):
    """
    Initializes the word search grid with the game words.
    """
    grid = fill_grid_with_placeholders(difficulty)

    # Insert words
    for word in game_words:
        place_word(grid, word, difficulty)

    # If you want to fill remaining '*' with random letters, do:
    # grid = fill_remaining_placeholders_with_random_letters(grid, difficulty)
    return grid


def fill_grid_with_placeholders(difficulty):
    """
    Creates a grid with '*' placeholders.
    """
    grid_size = difficulty[0]
    return [["*" for _ in range(grid_size)] for _ in range(grid_size)]


def place_word(grid, word, difficulty):
    """
    Place a single word horizontally in the grid.
    """
    grid_size = difficulty[0]
    word = word.upper()
    word_length = len(word)
    placed = False

    while not placed:
        # Randomly choose direction: 0 = horizontal, 1 = vertical, 2 = diagonal
        # direction = random.choice([0, 1, 2])
        direction = 0
        if direction == 0:  # Horizontal
            row = random.randint(0, grid_size - 1)
            col = random.randint(0, grid_size - word_length)
            #     if all(grid[row + i][col] in ('*', word[i]) for i in range(word_length)):
            can_place = True
            for i in range(word_length):
                if grid[row][col + i] not in ("*", word[i]):
                    can_place = False
                    break

            if can_place:
                for i in range(word_length):
                    grid[row][col + i] = word[i]
                placed = True

            # elif direction == 1:  # Vertical
            #     row = random.randint(0, grid_size - word_length)
            #     col = random.randint(0, grid_size - 1)
            #     if all(grid[row + i][col] in ('*', word[i]) for i in range(word_length)):
            #         for i in range(word_length):
            #             grid[row + i][col] = word[i]
            #         placed = True
            # elif direction == 2:  # Diagonal
            #     row = random.randint(0, grid_size - word_length)
            #     col = random.randint(0, grid_size - word_length)
            #     if all(grid[row + i][col + i] in ('*', word[i]) for i in range(word_length)):
            #         for i in range(word_length):
            #             grid[row + i][col + i] = word[i]
            #         placed = True


def fill_remaining_placeholders_with_random_letters(grid, difficulty):
    """ Fill remaining empty spaces with random letters """
    grid_size = difficulty[0]
    for i in range(grid_size):
        for j in range(grid_size):
            if grid[i][j] == '*':
                grid[i][j] = random.choice(string.ascii_uppercase)
    return grid


def print_game_grid(word_search_grid):
    """
    Print the grid row by row.
    """
    for row in word_search_grid:
        print("\t".join(row))


def get_hint_about_word(word):
    """
    Generate a hint (brief summary) using OpenAI's new chat interface,
    and hide the first word in the summary.
    """
    wiki_api = wikipediaapi.Wikipedia(language="en", user_agent="word-o-pedia/v1")
    page = wiki_api.page(word)

    if not page.exists():
        return f"Sorry, no information found for the word: {word}"

    input_string = page.summary

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that summarizes text very briefly."
                },
                {
                    "role": "user",
                    "content": f"Summarize this text in one sentence: {input_string}"
                }
            ],
        )

        summary = response.choices[0].message.content.strip()

        # Hide the first word
        words = summary.split(" ", 1)
        if len(words) == 1:
            # If there's only one word, star it
            blanked_first_word = "*" * len(words[0])
            summary_with_blanked_word = blanked_first_word
        else:
            first_word, rest = words
            blanked_first_word = "*" * len(first_word)
            summary_with_blanked_word = blanked_first_word + " " + rest

        wrapped_output = textwrap.fill(summary_with_blanked_word, width=50)

        wrapped_input_string = textwrap.fill(input_string, width=50)

        return wrapped_input_string, wrapped_output  # !!!!!REMOVE input_string AFTER DEMOING HOW THIS WORKS!!!!!

    except Exception as e:
        return f"An error occurred while generating the hint: {e}"


def update_game_grid(word_search_grid, word, colours_counter):
    """
    Search the grid for the given word horizontally and color the matching
    characters in-place. This assumes the word is placed in uppercase.
    """
    word = word.upper()
    word_length = len(word)
    grid_size = len(word_search_grid)

    for r in range(grid_size):
        # Convert the row (list of characters) into a string
        row_str = "".join(word_search_grid[r])

        # Find the start index of the word in the row string
        start_index = row_str.find(word)

        # If found, color each character of the word
        if start_index != -1:
            for i in range(word_length):
                # Wrap each character with the desired color
                word_search_grid[r][start_index + i] = (
                        COLOURS_LIST[colours_counter] + word_search_grid[r][start_index + i] + Style.RESET_ALL
                )

    return word_search_grid


def main():
    difficulty = MEDIUM
    colours_counter = 0
    found_words_counter = 0

    print("Welcome to WORD-O-PEDIA!\n")

    # PRINT OUT THE GAME GUIDE HERE

    links_list = get_links_from_wiki()
    game_words = get_game_words(links_list, difficulty)
    word_search_grid = initialise_grid(game_words, difficulty)

    while found_words_counter < len(game_words):
        print_game_grid(word_search_grid)  # Prints out the word search grid

        want_hint = input("\nWould you like a hint? (Y / N): ").strip().lower()
        if want_hint in {"y", "yes", "yeah"}:
            # print(f"\n{get_hint_about_word(game_words[0])}") UNCOMMENT THIS AFTER DEMO!!!!!
            long_summary, short_summary = get_hint_about_word(game_words[0])
            print(long_summary, "\n")  # DELETE THESE AFTER DEMO
            print(short_summary, "\n")  # DELETE THESE AFTER DEMO
        # print(game_words)
        user_guess = input("\nEnter a found word: ").strip().capitalize()
        if user_guess in game_words:
            print("\nWHOOOOOOOOO! You found " + COLOURS_LIST[colours_counter] + user_guess + Style.RESET_ALL + "\n")
            word_search_grid = update_game_grid(word_search_grid, user_guess, colours_counter)
            colours_counter += 1  # Update colour counter so next guessed word gets a different colour
            found_words_counter += 1  # Update the found words counter
        else:
            print(f"\n{user_guess} isn't one of the words we are looking for!\n")

    print(f"You found all {len(game_words)} words in ***** mins:secs")


if __name__ == "__main__":
    main()

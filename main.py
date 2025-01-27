import os
import re
import random
import string
import textwrap
import wikipediaapi

from dotenv import load_dotenv
import openai

# 1) Load environment variables
load_dotenv()

# 2) Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Optional: Raise an error if key is missing
# if not openai.api_key:
#     raise ValueError("API key not found. Ensure OPENAI_API_KEY is set in your .env file.")

# Difficulty levels
EASY = (7, 5)
MEDIUM = (10, 7)
HARD = (15, 10)

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
        # For now, only horizontal
        row = random.randint(0, grid_size - 1)
        col = random.randint(0, grid_size - word_length)

        can_place = True
        for i in range(word_length):
            if grid[row][col + i] not in ("*", word[i]):
                can_place = False
                break

        if can_place:
            for i in range(word_length):
                grid[row][col + i] = word[i]
            placed = True

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

def main():
    difficulty = MEDIUM

    print("Welcome to WORD-O-PEDIA!\n")
    links_list = get_links_from_wiki()
    game_words = get_game_words(links_list, difficulty)
    word_search_grid = initialise_grid(game_words, difficulty)

    print_game_grid(word_search_grid)

    want_hint = input("\nWould you like a hint? (Y / N): ").strip().lower()
    if want_hint in {"y", "yes", "yeah"}:
        # print(f"\n{get_hint_about_word(game_words[0])}") UNCOMMENT THIS AFTER DEMO!!!!!
        long_summary, short_summary = get_hint_about_word(game_words[0])
        print(long_summary, "\n") # DELETE THESE AFTER DEMO
        print(short_summary, "\n") # DELETE THESE AFTER DEMO

if __name__ == "__main__":
    main()

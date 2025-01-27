import wikipediaapi
import re
import random
import string


"""
Additional Functionality Options
    - Let the player choose if they want just horizontal words / horizontal and vertical / horizontal, vertical and diagonal

"""


# 3 different difficulty levels: easy, medium, hard
# each level a tuple consisting of grid_size and number of words
EASY = (7, 5)
MEDIUM = (10, 7)
HARD = (15, 10)


def get_links_from_wiki():
    """ returns list of titles of links from a specified wikipedia page"""
    wiki_api = wikipediaapi.Wikipedia(language="en", user_agent="word-o-pedia/v1")
    page_py = wiki_api.page("Nelson Mandela")
    # print(page_py.summary[:100])

    links_list = page_py.links.keys()
    return links_list


def get_game_words(links, difficulty):
    """ Take every nth word to distribute evenly across A-Z """
    grid_size, num_words = difficulty

    alphabetic_links = [link for link in links if re.match(r"^[A-Za-z]+$", link) and len(link) <= grid_size]

    step = len(alphabetic_links) // num_words  # Step size to take nth word
    game_words = alphabetic_links[::step][:num_words]  # Take every nth word, limited by num_words
    return game_words


def initialise_grid(game_words, difficulty):
    """ Initialises the word search grid with the game words and random characters """
    grid = fill_grid_with_placeholders(difficulty)
    # Insert words into the grid
    for word in game_words:
        place_word(grid, word, difficulty)
    # word_search_grid = fill_remaining_placeholders_with_random_letters(grid, difficulty)
    word_search_grid = grid # COMMENT THIS OUT AFTER UNCOMMENTING ABOVE
    return word_search_grid


def fill_grid_with_placeholders(difficulty):
    """ this functions creates a grid with placeholders """
    grid_size = difficulty[0]
    return [["*" for _ in range(grid_size)] for _ in range(grid_size)]


def place_word(grid, word, difficulty):
    """ Function to place a word in the grid """
    grid_size = difficulty[0]
    word = word.upper()  # Convert to uppercase and remove underscores
    word_length = len(word)
    placed = False

    while not placed:
        # Randomly choose direction: 0 = horizontal, 1 = vertical, 2 = diagonal
        direction = random.choice([0, 1, 2])
        if direction == 0:  # Horizontal
            row = random.randint(0, grid_size - 1)
            col = random.randint(0, grid_size - word_length)
            # Check for '*' as placeholders
            # if all(grid[row][col + i] in ('*', word[i]) for i in range(word_length)): # SHORTHAND VERSION OF THE CODE BELOW
            # Explicit check for placement
            can_place = True  # Assume the word can be placed initially
            for i in range(word_length):
                current_cell = grid[row][col + i]  # Get the current cell in the grid
                current_letter = word[i]          # Get the current letter of the word

                # Check if the cell is not a placeholder ('*') and does not match the letter
                if current_cell != '*' and current_cell != current_letter:
                    can_place = False  # Mark as not placeable
                    break  # Exit the loop as soon as a conflict is found

            # If the word can be placed, insert it
            if can_place:
                for i in range(word_length):
                    grid[row][col + i] = word[i]
                placed = True
            # ========================================
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


# def fill_remaining_placeholders_with_random_letters(grid, difficulty):
#     """ Fill remaining empty spaces with random letters """
#     grid_size = difficulty[0]
#     for i in range(grid_size):
#         for j in range(grid_size):
#             if grid[i][j] == '*':
#                 grid[i][j] = random.choice(string.ascii_uppercase)
#     return grid


def print_game_grid(word_search_grid):
    """ Print the grid """
    for row in word_search_grid:
        print('\t'.join(row))


def main():
    difficulty = MEDIUM

    print("Welcome to WORD-O-PEDIA!\n")
    links_list = get_links_from_wiki()
    game_words = get_game_words(links_list, difficulty)

    word_search_grid = initialise_grid(game_words, difficulty)
    print_game_grid(word_search_grid)


if __name__ == "__main__":
    main()

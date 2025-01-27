# Wikipedia Game Challenge - programming plan example

## Game goal and description:

### Basic Game MVP :

- Player is presented with a matrix of letters from a wikipedia article
- To win you have to find all the words

#### Fun / complications:

1. Add a timer with leaderboard -> player username
2. Let the player choose the matrix size (& number of words?)
3. HARDER games -> Limit information - player must guess wiki article

## Walkthrough - step-by-step of game progress:

1. Display welcome to Word - O - Pedia
2. Display an explanation of the game and the choices available including an example matrix
3. Setup : player is presented with a choice between a random topic or a search to create the matrix
4. After the choice the game begins and the chosen matrix is displayed to the player, with the information of how many words need to be found and the topic of the article.
5. The player is asked to type in words that they guess are hidden in the matrix
6. Correct words are highlighted
7. Otherwise Player is told the guess is incorrect (DO BETTER!)
8 .Player continues with steps 5, 6, 7 until all words are found

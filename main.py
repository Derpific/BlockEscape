import pygame, math, random

#Pygame Global Variables
WIDTH, HEIGHT = (1280, 720) #size of the screen
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT)) #the surface that everything is drawn on
FPS = 60 #frames per second of the game

# Main initialization function
# Calls all helper functions and initialize the basic game variables or objects
def init():
    initStates()
    initFonts()
    loadAssets()
    initSounds()
    initLevel()
    initCookies()
    initMenu()
    initGrid()
    initTimer()

# Initializes game states that the player will have
def initStates():
    global gameState, MENU, PLAY, WIN, LOSE, QUIT, isAlive
    MENU = 0
    PLAY = 1
    WIN = 2
    LOSE = 3
    QUIT = 4

    gameState = MENU

# Initialize and sets up different types of fonts needed
def initFonts():
    global font, titleFont, subTitleFont
    font = pygame.font.SysFont(None, 70)
    titleFont = pygame.font.SysFont(None, 60)
    subTitleFont = pygame.font.SysFont(None, 35)

#  initialize and sets up all images including backgrounds, and blocks
def loadAssets():
    global menu, bg, blocks, PLAYER_BLOCK, WALL_BLOCK, COOKIE, ENEMY_BLOCK, DEATH_BLOCK, JAIL_BLOCK, GOAL_BLOCK, WARP_BLOCK
    blocks = []
    menu = pygame.image.load("menu.png")
    bg = pygame.image.load("bg.png")

    block = pygame.image.load("playerblock.png")
    blocks.append(block)
    block = pygame.image.load("wallblock.png")
    blocks.append(block)
    block = pygame.image.load("cookie.png")
    blocks.append(block)
    block = pygame.image.load("enemyblock.png")
    blocks.append(block)
    block = pygame.image.load("deathblock.png")
    blocks.append(block)
    block = pygame.image.load("jailblock.png")
    blocks.append(block)
    block = pygame.image.load("checkeredblock.png")
    blocks.append(block)
    block = pygame.image.load("warpblock.png")
    blocks.append(block)
    PLAYER_BLOCK, WALL_BLOCK, COOKIE, ENEMY_BLOCK, DEATH_BLOCK, JAIL_BLOCK, GOAL_BLOCK, WARP_BLOCK = (0, 1, 2, 3, 4, 5, 6, 7)

# Initialize and setups all sounds
def initSounds():
    global countdownSound, deathSound, enemyEatSound, goalReachedSound, goalUnlockedSound, playerEatSound, playerWalkSound
    global isCountdownSoundPlaying
    isCountdownSoundPlaying = False

    countdownSound = pygame.mixer.Sound("countdown_sound.wav")
    deathSound = pygame.mixer.Sound("death_sound.wav")
    enemyEatSound = pygame.mixer.Sound("enemy_eat_sound.wav")
    goalReachedSound = pygame.mixer.Sound("goal_reached_sound.wav")
    goalUnlockedSound = pygame.mixer.Sound("goal_unlocked_sound.wav")
    playerEatSound = pygame.mixer.Sound("player_eat_sound.wav")
    playerWalkSound = pygame.mixer.Sound("player_walk_sound.wav")
    playerWalkSound.set_volume(0.8)

# Initializes level variable and default level
def initLevel():
    global level
    level = 1

# Initializes cookies variable and default amount
def initCookies():
    global cookies
    cookies = 0

# Initializes and sets up variables needed for the menu
def initMenu():
    global menuOption, PLAY_OPTION, QUIT_OPTION
    PLAY_OPTION = 0
    QUIT_OPTION = 1

    menuOption = PLAY_OPTION

# Function that loads level based on the level set and sets a cookie location
def initGrid():
    global SPACING

    loadLevel(level)
    setCookie()
    SPACING = 32

# Important function in order to set the grid into a 2D list. Opens the file based
# on level given and also stores player, enemy(ies) and goal location into variables
def loadLevel(level = 1):
    global grid, gridPos, playerX, playerY, horizontalEnemyPos, verticalEnemyPos, enemyPos, goalX, goalY, direction, SPACING
    grid = []
    playerX = -1
    playerY = -1
    direction = 1

    horizontalEnemyPos = []
    verticalEnemyPos = []

    goalX = -1
    goalY = -1

    with open("level" + str(level) + ".txt", 'r') as fh:
        y = 0

        for line in fh:
            row = []
            x = 0

            for char in line.strip():
                if char == "p":
                    playerX = x
                    playerY = y
                elif char == "1":
                    horizontalEnemyPos.append([x, y, 1])
                elif char == "2":
                    verticalEnemyPos.append([x, y, 1])
                elif char == "e":
                    goalX = x
                    goalY = y
                row.append(char)
                x += 1
            grid.append(row)
            y += 1
    gridPos = (50 + HEIGHT / 2 - len(grid) / 2 * 32, WIDTH / 2 - len(grid[0]) / 2 * 32)

# Set the cookie onto a random spot on the grid based on dimensions.
# Runs itself until an empty spot is found
def setCookie():
    global cookieX, cookieY

    cookieX = random.randint(0, len(grid[1])-1)
    cookieY = random.randint(0, len(grid)-1)

    if grid[cookieY][cookieX] == "_":
        grid[cookieY][cookieX] = "c"
    else:
        setCookie()

# initializes the main timer for the game based on 15% of the area of the grid
def initTimer():
    global timer

    timer = math.ceil(len(grid) * len(grid[1]) * 0.15 * 60)

# Main update function that runs helper functions if game state is PLAY
def update():
    if gameState == PLAY:
        updateTimer()
        updateEnemies()

# Function that updates the timer. Once hit 0 the player has lost, else continue decreasing
# On 3 seconds, a 3 second countdown sound is run and colour for the timer on screen changes
def updateTimer():
    global timer, timerColour, isCountdownSoundPlaying

    if timer <= 0:
        lostGame()
    else:
        timer -= 1

        if timer <= 3 * 60:
            isCountdownSoundPlaying = True
            timerColour = (255, 0, 0)
            countdownSound.play()
        else:
            timerColour = (255, 255, 255)

# Function that moves the enemy. Runs through the list of enemies initialized previously, and moves
# based on the timer if empty block while checking enemy interactions (cookies + handleEnemyMovementChecks())
def updateEnemies():
    global horizontalEnemyPos, verticalEnemyPos
    handleEnemyMovementChecks()

    if timer % 30 == 0:
        for i in range(len(horizontalEnemyPos)):
            enemyY = horizontalEnemyPos[i][1]
            enemyX = horizontalEnemyPos[i][0]
            direction = horizontalEnemyPos[i][2]
            nextPos = enemyX + direction

            if grid[enemyY][nextPos] != "x" and not grid[enemyY][nextPos].isnumeric() and grid[enemyY][nextPos] != "e" and grid[enemyY][nextPos] != "e*":
                grid[enemyY][enemyX] = "_"
                grid[enemyY][nextPos] = "1"
                horizontalEnemyPos[i][0] = nextPos

                if (enemyX, enemyY) == (cookieX, cookieY):
                    enemyEatSound.play()
                    setCookie()
            elif grid[enemyY][nextPos] == "x" or grid[enemyY][nextPos] == "e" or grid[enemyY][nextPos] == "e*":
                horizontalEnemyPos[i][2] = -direction
    if timer % 20 == 0:
        for i in range(len(verticalEnemyPos)):
            enemyY = verticalEnemyPos[i][1]
            enemyX = verticalEnemyPos[i][0]
            direction = verticalEnemyPos[i][2]

            nextPos = enemyY + direction

            if grid[nextPos][enemyX] != "x" and not grid[nextPos][enemyX].isnumeric() and grid[nextPos][enemyX] != "e" and grid[nextPos][enemyX] != "e*":
                grid[enemyY][enemyX] = "_"
                grid[nextPos][enemyX] = "2"
                verticalEnemyPos[i][1] = nextPos

                if (enemyX, enemyY) == (cookieX, cookieY):
                    enemyEatSound.play()
                    setCookie()
            elif grid[nextPos][enemyX] == "x" or grid[nextPos][enemyX] == "e" or grid[nextPos][enemyX] == "e*":
                verticalEnemyPos[i][2] = -direction

# Main draw function. Draws a default rectangle and runs helper functions depending on the game state
def draw():
    pygame.draw.rect(SCREEN, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
    if gameState == MENU:
        drawMenu()
    elif gameState != QUIT:
        drawGrid()
        drawNavBar()

        if gameState == LOSE:
            drawLostMessage()
        if gameState == WIN:
            drawWinMessage()
    pygame.display.flip()

# Draw function for when the player is in the menu
# Outputs the menu background, and the cookie beside the supposed option
def drawMenu():
    SCREEN.blit(menu, (0, 0))

    if menuOption == PLAY_OPTION:
        SCREEN.blit(blocks[COOKIE], (WIDTH / 3 + 80, HEIGHT / 2 - 75))
    else:
        SCREEN.blit(blocks[COOKIE], (WIDTH / 3 + 80, HEIGHT / 2))

# Runs setBlocks() from the grid previously initialized in order to output correct blocks, rows, and columns
# with proper spacing
def drawGrid():
    SCREEN.blit(bg, (0, 0))
    totalRows = len(grid)
    totalCols = len(grid[0])

    for i in range(totalRows):
        for j in range(totalCols):
            block = grid[i][j]
            row = gridPos[0] + SPACING * i
            col = gridPos[1] + SPACING * j
            setBlocks(block, col, row)

# Output the blocks onto the screen depending on the letter
def setBlocks(block, col, row):
    if block == "p":
        SCREEN.blit(blocks[PLAYER_BLOCK], (col, row))
    elif block == "x":
        SCREEN.blit(blocks[WALL_BLOCK], (col, row))
    elif block.isdigit():
        SCREEN.blit(blocks[ENEMY_BLOCK], (col, row))
    elif block == "e":
        SCREEN.blit(blocks[JAIL_BLOCK], (col, row))
    elif block == "e*":
        SCREEN.blit(blocks[GOAL_BLOCK], (col, row))
    elif block == "d":
        SCREEN.blit(blocks[DEATH_BLOCK], (col, row))
    elif block == "c":
        SCREEN.blit(blocks[COOKIE], (col, row))

# Draws the timer, cookies, and level beside the text
# Changes timer colour depending on time left
def drawNavBar():
    numColour = (255, 255, 255)

    timerAcc = font.render(str(round(timer / 60)), True, timerColour)
    SCREEN.blit(timerAcc, (WIDTH / 3 - 20, 20))

    levelAcc = font.render(str(level), True, numColour)
    SCREEN.blit(levelAcc, (WIDTH / 2 + 70, 20))

    cookiesAcc = font.render(str(cookies), True, numColour)
    SCREEN.blit(cookiesAcc, (WIDTH - WIDTH / 3 + 230, 20))

# Draws a message when a player has lost on the screen
def drawLostMessage():
    lossMessage = titleFont.render("You lost!", True, (200, 0, 0))
    SCREEN.blit(lossMessage, (WIDTH / 2 - WIDTH / 12, HEIGHT / 7))
    lossSubtitle = subTitleFont.render("Press ENTER to start again at LEVEL 1 or Q to quit!", True, (200, 150, 0))
    SCREEN.blit(lossSubtitle, (WIDTH / 4, HEIGHT - HEIGHT / 7))

# Draws a message when a player has won depending on the level factor onto the screen
def drawWinMessage():
    if level == 3:
        winMessage = titleFont.render("Congrats! You finished the game!", True, (125, 200, 0))
        SCREEN.blit(winMessage, (WIDTH / 3 - 50, HEIGHT - HEIGHT / 2 - HEIGHT / 4))
        winSubTitle = subTitleFont.render("Press ENTER to play again or Q to quit!", True, (200, 150, 50))
        SCREEN.blit(winSubTitle, (WIDTH / 3, HEIGHT - HEIGHT / 7))
    else:
        winMessage = titleFont.render("Congrats! You passed the level!", True, (100, 155, 0))
        SCREEN.blit(winMessage, (WIDTH / 3 - WIDTH / 12, HEIGHT - HEIGHT / 2 - HEIGHT / 3))
        winSubTitle = subTitleFont.render("Press ENTER to advance to LEVEL " + str(level+1), True, (200, 150, 0))
        SCREEN.blit(winSubTitle, (WIDTH / 3, HEIGHT - HEIGHT / 7))
        win2SubTitle = subTitleFont.render("Press Q to quit", True, (200, 150, 0))
        SCREEN.blit(win2SubTitle, (WIDTH / 3, HEIGHT - HEIGHT / 10))

# Keyboard function to handle player movement. Moves player on grid only if block is not a wall
# Options depend on the button pressed, runs helper function handleMovementChecks()
def handlePlayerMovement():
    global grid, playerX, playerY
    keyPressed = pygame.key.get_pressed()

    if keyPressed[pygame.K_UP]:
        nextPos = playerY - 1

        if grid[nextPos][playerX] != "x" and grid[nextPos][playerX] != "e":
            grid[playerY][playerX] = "_"
            grid[nextPos][playerX] = "p"
            playerY -= 1
            handleMovementChecks()
    elif keyPressed[pygame.K_DOWN]:
        nextPos = playerY + 1

        if grid[nextPos][playerX] != "x" and grid[nextPos][playerX] != "e":
            grid[playerY][playerX] = "_"
            grid[nextPos][playerX] = "p"
            playerY += 1
            handleMovementChecks()
    elif keyPressed[pygame.K_RIGHT]:
        nextPos = playerX + 1

        if grid[playerY][nextPos] != "x" and grid[playerY][nextPos] != "e":
            grid[playerY][playerX] = "_"
            grid[playerY][nextPos] = "p"
            playerX += 1
            handleMovementChecks()
    elif keyPressed[pygame.K_LEFT]:
        nextPos = playerX - 1

        if grid[playerY][nextPos] != "x" and grid[playerY][nextPos] != "e":
            grid[playerY][playerX] = "_"
            grid[playerY][nextPos] = "p"
            playerX -= 1
            handleMovementChecks()

# Keyboard function to handle in MENU state to either quit game or start game
# Options depend on the button pressed
def handleMenu():
    global gameState, menuOption
    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        if menuOption == PLAY_OPTION:
            menuOption = QUIT_OPTION
        else:
            menuOption = PLAY_OPTION
    if keys[pygame.K_DOWN]:
        if menuOption == QUIT_OPTION:
            menuOption = PLAY_OPTION
        else:
            menuOption = QUIT_OPTION
    elif keys[pygame.K_RETURN]:
        if menuOption == PLAY_OPTION:
            gameState = PLAY
        else:
            gameState = QUIT

# Keyboard function to handle in WIN state to either quit game or advance to next level
# Options depend on the button pressed. Helper function resetGame() included
def handleWin():
    global gameState, level

    keys = pygame.key.get_pressed()

    if keys[pygame.K_q]:
        gameState = QUIT
    elif keys[pygame.K_RETURN]:
        if level == 3:
            level = 1
            resetGame()
        else:
            level += 1
            resetGame()

# Keyboard function to handle in LOSE state to either reset to level 1 or quit game
# Options depend on the button pressed. Helper function 4resetGame() included
def handleLoss():
    global gameState, level
    keys = pygame.key.get_pressed()

    if keys[pygame.K_RETURN]:
        level = 1
        resetGame()
    elif keys[pygame.K_q]:
        gameState = QUIT

# Ran to check if the player has come into interaction with a cookie or goal block
# If come into interaction, do the things required. Helper function setCookie() and wonGame() included
def handleMovementChecks():
    global cookies

    if (playerX, playerY) == (cookieX, cookieY):
        grid[playerY][playerX] = "p"
        cookies += 1

        if cookies == 5:
            grid[goalY][goalX] = "e*"
            goalUnlockedSound.play()
            setCookie()
        else:
            setCookie()
        playerEatSound.play()
    elif (playerX, playerY) == (goalX, goalY) and cookies >= 5:
        wonGame()
    playerWalkSound.play()

# Ran to check if the enemy has come into contact with the player so they lose
def handleEnemyMovementChecks():
    for i in range(len(horizontalEnemyPos)):
        enemyY = horizontalEnemyPos[i][1]
        enemyX = horizontalEnemyPos[i][0]

        if (playerX, playerY) == (enemyX, enemyY):
            grid[enemyY][enemyX] = "_"
            lostGame()
    for i in range(len(verticalEnemyPos)):
        enemyY = verticalEnemyPos[i][1]
        enemyX = verticalEnemyPos[i][0]

        if (playerX, playerY) == (enemyX, enemyY):
            grid[enemyY][enemyX] = "_"
            lostGame()

# Ran when the game has lost. Sets up the state of LOSE, sound effects, and
# turns the player block into a death block
def lostGame():
    global gameState, isCountdownSoundPlaying
    gameState = LOSE
    grid[playerY][playerX] = "d"

    if isCountdownSoundPlaying:
        countdownSound.stop()
        isCountdownSoundPlaying = False
    deathSound.play()

# Ran when the player has won. Sets up the state of WIN and sound effects
def wonGame():
    global gameState, isCountdownSoundPlaying
    gameState = WIN

    if isCountdownSoundPlaying:
        countdownSound.stop()
        isCountdownSoundPlaying = False
    goalReachedSound.play()

# Ran to reset the game once a player has finished a level, all levels, or lost
# Resets cookies, re-initializes the grid for the level and the timer
def resetGame():
    global cookies, gameState
    cookies = 0
    gameState = PLAY
    initGrid()
    initTimer()

# The main function that handles everything. Includes keyboard
# pressing events in different game states that lead into helper functions
def main():
    global gameState
    pygame.init()
    init()
    clock = pygame.time.Clock()

    while gameState != QUIT:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameState = QUIT
            if event.type == pygame.KEYDOWN and gameState == PLAY:
                handlePlayerMovement()
            if event.type == pygame.KEYDOWN and gameState == MENU:
                handleMenu()
            if event.type == pygame.KEYDOWN and gameState == LOSE:
                handleLoss()
            if event.type == pygame.KEYDOWN and gameState == WIN:
                handleWin()
        update()
        draw()
    pygame.quit()

if __name__ == "__main__":
    main()
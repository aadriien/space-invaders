# Difficulty modes:
#   Easy -> only spaceship shoots (unlimited bullets), alien y axis consistent
#   Medium -> only spaceship shoots (unlimited), aliens descend when hit wall
#   Hard -> spaceship (unlimited) AND bottom aliens shoot, aliens descend at wall
#   Expert -> spaceship (limited bullets) AND aliens shoot, aliens descend at wall

# With each successful level (all aliens destroyed), new level begins 
# ... meaning there's 1 extra row & 1 extra column of aliens
# ... maybe they also move faster with level up?

# If an alien reaches spaceship (collide/contact), then game over
# If an alien successfully shoots spaceship, then game over

# TODO:


# DONE:
#   - implement Hard mode (bottom row of aliens can shoot)
#       -> implement game over when spaceship is hit by alien bullet
#   - implement Expert mode (spaceship's bullets are limited)
#       -> implement bullet counter metric on screen
#       -> implement game over when alien touches / collides with spaceship
#   - implement additional row & column of aliens on level up


import pygame
import random


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GREEN = (170, 208, 188) 
DEEP_GREEN = (71, 175, 121)
LIGHT_BLUE = (141, 214, 236)
DEEP_BLUE = (46, 147, 177)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BUTTON_WIDTH, BUTTON_HEIGHT = 250, 125
BUTTON_SPACING = 20

ALIEN_ROWS = 3
ALIEN_COLS = 5

BULLET_WIDTH, BULLET_HEIGHT = 8, 8
BULLET_SPEED = 4

SHOOT_COOLDOWN = 500 # 500 millisec == 0.5 sec
BULLET_LIMIT = 3 * ALIEN_ROWS * ALIEN_COLS 

SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 60, 100
SPACESHIP_SPEED = 5

ALIEN_WIDTH, ALIEN_HEIGHT = 50, 50
ALIEN_SPEED = 3

# 1 out of 500, or 0.2% chance of some alien shooting
ALIEN_SHOOT_PROBABILITY = 1 
ALIEN_SHOOT_PROB_DENOM = 500


# Difficulty selection on welcome page
class Button:
    def __init__(self, text, x_pos, y_pos):
        self.rect = pygame.Rect(x_pos, y_pos, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.text = text
        self.selected = False

    def draw_to_screen(self, screen):
        button_color = DEEP_BLUE if self.selected else LIGHT_BLUE
        border_color = BLACK
        border_thickness = 3 

        # Draw border first (slightly larger than button)
        pygame.draw.rect(
            screen, 
            border_color, 
            self.rect.inflate(border_thickness * 2, border_thickness * 2),  
            border_thickness
        )

        pygame.draw.rect(screen, button_color, self.rect, border_radius = 5)
        text_surface = FONT_LARGE.render(self.text, True, BLACK)
        screen.blit(text_surface, text_surface.get_rect(center = self.rect.center))


# Basic functionality for moving pieces (spaceship, aliens, etc)
class GameObject:
    def __init__(self, x_pos, y_pos, width, height, color):
        self.image = pygame.Surface((width, height))
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.center = (x_pos, y_pos)
    
    def draw_to_screen(self, screen):
        screen.blit(self.image, self.rect)


class Bullet(GameObject):
    def __init__(self, x_pos, y_pos):
        GameObject.__init__(
            self, 
            x_pos, y_pos, 
            BULLET_WIDTH, BULLET_HEIGHT, 
            BLACK
        )
        self.speed = BULLET_SPEED

    def move(self, direction):
        self.rect.y -= direction * self.speed

    def off_screen(self):
        return self.rect.y < 0


class Spaceship(GameObject):
    def __init__(self, x_pos, y_pos):
        GameObject.__init__(
            self, 
            x_pos, y_pos, 
            SPACESHIP_WIDTH, SPACESHIP_HEIGHT, 
            BLACK
        )
        self.image = pygame.image.load("images/spaceship.png") 
        self.image = pygame.transform.scale(self.image, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))

        self.speed = SPACESHIP_SPEED
        
        self.bullets = []
        self.last_shot = 0 # Time of last shot for cooldown (can't spam)
        self.bullet_count = 0

    def move(self, direction):
        self.rect.x += direction * self.speed
        
        # Prevent out of bound movement
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def shoot(self, difficulty):
        curr_time = pygame.time.get_ticks()
        if (curr_time - self.last_shot) >= SHOOT_COOLDOWN:

            # On Expert mode, limit spaceship's total bullets
            if difficulty < 3 or self.bullet_count < BULLET_LIMIT:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                self.bullets.append(bullet)

                self.last_shot = curr_time
                self.bullet_count += 1


class Alien(GameObject):
    def __init__(self, x_pos, y_pos):
        GameObject.__init__(
            self, 
            x_pos, y_pos, 
            ALIEN_WIDTH, ALIEN_HEIGHT, 
            BLACK
        )
        self.image = pygame.image.load("images/alien.png") 
        self.image = pygame.transform.scale(self.image, (ALIEN_WIDTH, ALIEN_HEIGHT))

        self.speed = ALIEN_SPEED


class Aliens:
    def __init__(self, alien_rows, alien_cols):
        # Distribute aliens evenly across top half to start
        self.speed = ALIEN_SPEED
        
        self.aliens = []
        self.bullets = []

        alien_spacing_x = ALIEN_WIDTH + 25
        alien_spacing_y = ALIEN_HEIGHT 

        space_distribution_x = (SCREEN_WIDTH - (alien_cols * alien_spacing_x)) // 2

        for row in range(alien_rows):
            for col in range(alien_cols):
                x_pos = space_distribution_x + (alien_spacing_x * col)
                y_pos = 50 + (alien_spacing_y * row)
                self.aliens.append(Alien(x_pos, y_pos))

    def move(self, difficulty):
        # Move aliens as group
        hit_wall = False
        for alien in self.aliens:
            alien.rect.x += self.speed
            if alien.rect.left <= 0 or alien.rect.right >= SCREEN_WIDTH:
                hit_wall = True

        # Reverse if any aliens hit wall (& move down if > easy mode)
        if hit_wall:
            self.speed *= -1

            if difficulty >= 1:
                for alien in self.aliens:
                    alien.rect.y += (ALIEN_HEIGHT // 5)

    def draw_to_screen(self, screen):
        for alien in self.aliens:
            alien.draw_to_screen(screen)

    # If aliens' x pos same, & some alien's y is greater, then not bottom
    def check_if_bottom(self, curr_alien):
        for other_alien in self.aliens:
            if other_alien.rect.x == curr_alien.rect.x:
                if other_alien.rect.y > curr_alien.rect.y:
                    return False
        return True

    def shoot(self):
        for alien in self.aliens:
            # If alien on the bottom, 0.2% chance of shooting on render
            if self.check_if_bottom(alien):
                if random.randint(1, ALIEN_SHOOT_PROB_DENOM) <= ALIEN_SHOOT_PROBABILITY:
                    bullet = Bullet(alien.rect.centerx, alien.rect.bottom)
                    self.bullets.append(bullet)


def setup_game(caption):
    pygame.init()
    pygame.font.init()

    global FONT_SMALL, FONT_LARGE
    FONT_SMALL = pygame.font.Font(None, 28)
    FONT_LARGE = pygame.font.Font(None, 40)

    pygame.display.set_caption(caption)
    
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock() # Loop speed (FPS, for consistent experience)

    return window, clock


def render_screen(screen, color, items_to_draw, difficulty = None):
    screen.fill(color)

    # Draw spaceships (+ bullets), aliens (+ bullets), buttons, etc
    for item in items_to_draw:
        item.draw_to_screen(screen)

        if isinstance(item, Spaceship) or isinstance(item, Aliens):
            for bullet in item.bullets:
                bullet.draw_to_screen(screen)
            
            if isinstance(item, Spaceship):
                # Formulate bullet counter text metric
                bullet_metric_text = f"Bullets Fired:  {item.bullet_count}"

                if difficulty and difficulty >= 3:
                    bullet_metric_text += f"  /  {BULLET_LIMIT}"
                else:
                    bullet_metric_text += f"  /  Unlimited"

                text_surface = FONT_SMALL.render(bullet_metric_text, True, BLACK)
                screen.blit(text_surface, (10, 10))

    pygame.display.flip()


def get_button_choice(buttons, selected_index):
    keys = pygame.key.get_pressed()

    if keys[pygame.K_DOWN]:
        selected_index = (selected_index + 1) % len(buttons)
    elif keys[pygame.K_UP]:
        selected_index = (selected_index - 1) % len(buttons)
    
    return selected_index


def launch_screen(which_screen):
    button_center_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
    button_center_y = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT // 2
    
    if which_screen == "welcome":
        window, _ = setup_game("Space Invaders! Choose your difficulty!")

        buttons = [
        Button("Easy", button_center_x, button_center_y - 1.5 * (BUTTON_SPACING + BUTTON_HEIGHT)),
        Button("Medium", button_center_x, button_center_y - 0.5 * (BUTTON_SPACING + BUTTON_HEIGHT)),
        Button("Hard", button_center_x, button_center_y + 0.5 * (BUTTON_SPACING + BUTTON_HEIGHT)),
        Button("Expert", button_center_x, button_center_y + 1.5 * (BUTTON_SPACING + BUTTON_HEIGHT)),
    ]

    elif which_screen == "end":
        window, _ = setup_game("Space Invaders! Play again?")

        buttons = [
            Button("Play Again", button_center_x, button_center_y - 0.5 * (BUTTON_SPACING + BUTTON_HEIGHT)),
            Button("Quit Game", button_center_x, button_center_y + 0.5 * (BUTTON_SPACING + BUTTON_HEIGHT)),
        ]

    # Default == Easy (if welcome) or Play Again (if end)
    selected_index = 0 

    running = True
    while running:
        render_screen(window, LIGHT_GREEN, buttons)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Choose mode & begin game on enter
            if event.type == pygame.KEYDOWN:
                selected_index = get_button_choice(buttons, selected_index)
                    
        for i, button in enumerate(buttons):
            button.selected = (i == selected_index)

        if pygame.key.get_pressed()[pygame.K_RETURN]:
            running = False

    pygame.quit()
    return selected_index


def handle_player_keys(spaceship, difficulty):
    keys = pygame.key.get_pressed() 

    if keys[pygame.K_LEFT]:
        spaceship.move(-1)
    if keys[pygame.K_RIGHT]:
        spaceship.move(1)

    if keys[pygame.K_SPACE]:
        spaceship.shoot(difficulty)


def check_bullets(spaceship, aliens):
    for bullet in spaceship.bullets.copy(): # Iterate on copy to avoid issues
        bullet.move(1)

        # Check if bullet left screen
        if bullet.off_screen():
            spaceship.bullets.remove(bullet)

        # Check for collisions
        for alien in aliens.aliens.copy():
            if bullet.rect.colliderect(alien.rect):
                aliens.aliens.remove(alien)
                spaceship.bullets.remove(bullet)
                break

    # Similar check, but for alien bullets
    for bullet in aliens.bullets.copy():
        bullet.move(-1)

        if bullet.off_screen():
            aliens.bullets.remove(bullet)

        # If spaceship hit, then game over
        if bullet.rect.colliderect(spaceship.rect):
            return True 

    return False 


def check_collisions(spaceship, aliens):
    for alien in aliens.aliens:
        if spaceship.rect.colliderect(alien.rect):
            return True

    # By default, game not over if no collisions
    return False 


# Main game loop
def run_game(window, clock, difficulty, level):
    # Top left of screen (0, 0) ... bottom right (WIDTH, HEIGHT)
    spaceship = Spaceship(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40) 

    # With each level upgrade, alternate between extra row/col of aliens
    extra_rows = level // 2
    extra_cols = (level + 1) // 2 if level > 0 else 0        
    aliens = Aliens(ALIEN_ROWS + extra_rows, ALIEN_COLS + extra_cols)

    successful = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False

        # Spaceship left/right arrow key movement
        handle_player_keys(spaceship, difficulty)

        aliens.move(difficulty)
        aliens.shoot()

        # Spaceship shot OR collides with alien == game over
        is_spaceship_shot = check_bullets(spaceship, aliens)
        is_spaceship_alien_collision = check_collisions(spaceship, aliens)

        is_game_over = is_spaceship_shot or is_spaceship_alien_collision

        if is_game_over:
            successful = False
            running = False

        # No more aliens == level beat
        if not aliens.aliens:
            successful = True
            running = False

        # Update display
        render_screen(window, DEEP_GREEN, [spaceship, aliens], difficulty)
        clock.tick(60)

    pygame.quit()
    return successful


def main():
    level = 0
    successful = True
    difficulty = launch_screen("welcome")

    # Initialize game settings & run
    while successful:
        window, clock = setup_game("Space Invaders! Let's play!")
        successful = run_game(window, clock, difficulty, level)

        # On successful wave, move to next level 
        level += 1

    play_again = launch_screen("end")
    if play_again == 0: 
        main()


if __name__ == "__main__":
    main()     




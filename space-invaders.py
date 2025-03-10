import pygame


# Initialize game settings
pygame.init()

EASY_MODE = True # Alien difficulty

SPACESHIP_WIDTH = 20
SPACESHIP_HEIGHT = 40
SPACESHIP_COLOR = (0, 0, 0)
SPACESHIP_SPEED = 4

ALIEN_WIDTH = 30
ALIEN_HEIGHT = 30
ALIEN_COLOR = (0, 0, 0)
ALIEN_SPEED = 2

ALIEN_ROWS = 3
ALIEN_COLS = 5

BACKGROUND_COLOR = (170, 208, 188) 
WIDTH, HEIGHT = 800, 600

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders!")

clock = pygame.time.Clock() # Loop speed (FPS, see below)


# Basic functionality for moving pieces (spaceship, aliens, etc)
class GameObject:
    def __init__(self, x_pos, y_pos, width, height, color):
        self.image = pygame.Surface((width, height))
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.center = (x_pos, y_pos)
    
    def draw_to_screen(self, screen):
        screen.blit(self.image, self.rect)


class Spaceship(GameObject):
    def __init__(self, x_pos, y_pos):
        GameObject.__init__(
            self, 
            x_pos, y_pos, 
            SPACESHIP_WIDTH, SPACESHIP_HEIGHT, 
            SPACESHIP_COLOR
        )
        self.speed = SPACESHIP_SPEED

    def move(self, direction):
        self.rect.x += direction * self.speed
        
        # Prevent out of bound movement
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH


class Alien(GameObject):
    def __init__(self, x_pos, y_pos):
        GameObject.__init__(
            self, 
            x_pos, y_pos, 
            ALIEN_WIDTH, ALIEN_HEIGHT, 
            ALIEN_COLOR
        )
        self.speed = ALIEN_SPEED


class Aliens:
    def __init__(self, alien_rows, alien_cols):
        # Distribute aliens evenly across top half to start
        self.aliens = []
        self.speed = ALIEN_SPEED

        for row in range(alien_rows):
            for col in range(alien_cols):
                x_pos = (WIDTH // (alien_cols + 1)) * (col + 1)
                y_pos = (HEIGHT // 2 // (alien_rows + 1)) * (row + 1)
                self.aliens.append(Alien(x_pos, y_pos))

    def move(self):
        # Move aliens as group
        hit_wall = False
        for alien in self.aliens:
            alien.rect.x += self.speed
            if alien.rect.left <= 0 or alien.rect.right >= WIDTH:
                hit_wall = True

        # Reverse if any aliens hit wall (& move down if not easy mode)
        if hit_wall:
            self.speed *= -1

            if not EASY_MODE:
                for alien in self.aliens:
                    alien.rect.y += (ALIEN_HEIGHT // 2)

    def draw_to_screen(self, screen):
        for alien in self.aliens:
            alien.draw_to_screen(screen)


def render_screen(screen, spaceship, aliens):
    screen.fill(BACKGROUND_COLOR)
    spaceship.draw_to_screen(screen)
    aliens.draw_to_screen(screen)
    pygame.display.flip()


def handle_player_keys(spaceship):
    keys = pygame.key.get_pressed() 

    if keys[pygame.K_LEFT]:
        spaceship.move(-1)
    if keys[pygame.K_RIGHT]:
        spaceship.move(1)


# Main game loop
def run_game(spaceship, aliens):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False

        # Spaceship left/right arrow key movement
        handle_player_keys(spaceship)

        aliens.move()

        # Update display
        render_screen(window, spaceship, aliens)
        clock.tick(60)

    pygame.quit()


def main():
    # Top left of screen (0, 0) ... bottom right (WIDTH, HEIGHT)
    spaceship = Spaceship(WIDTH // 2, HEIGHT - 70) 
    aliens = Aliens(ALIEN_ROWS, ALIEN_COLS) if EASY_MODE else Aliens(ALIEN_ROWS + 1, ALIEN_COLS + 2)

    run_game(spaceship, aliens)


if __name__ == "__main__":
    main()     




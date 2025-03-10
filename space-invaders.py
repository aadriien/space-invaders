# Difficulty modes:
#   Easy -> only spaceship shoots (unlimited bullets), alien y axis consistent
#   Medium -> only spaceship shoots (unlimited), aliens descend when hit wall
#   Hard -> spaceship (unlimited) AND aliens shoot, aliens descend when hit wall
#   Expert -> spaceship (limited bullets) AND aliens shoot, aliens descend when hit wall


import pygame


EASY_MODE = True # Alien difficulty

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PASTEL_GREEN = (170, 208, 188) 
LIGHT_BLUE = (141, 214, 236)
DEEP_BLUE = (46, 147, 177)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BUTTON_WIDTH, BUTTON_HEIGHT = 250, 125
BUTTON_SPACING = 20

BULLET_WIDTH, BULLET_HEIGHT = 8, 8
BULLET_SPEED = 4
SHOOT_COOLDOWN = 500 # 500 millisec == 0.5 sec

SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 20, 40
SPACESHIP_SPEED = 5

ALIEN_WIDTH, ALIEN_HEIGHT = 30, 30
ALIEN_SPEED = 3

ALIEN_ROWS = 3
ALIEN_COLS = 5


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
        text_surface = FONT.render(self.text, True, WHITE)
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

    def move(self):
        self.rect.y -= self.speed

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
        self.speed = SPACESHIP_SPEED
        self.bullets = []
        self.last_shot = 0 # Time of last shot for cooldown (can't spam)

    def move(self, direction):
        self.rect.x += direction * self.speed
        
        # Prevent out of bound movement
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def shoot(self):
        curr_time = pygame.time.get_ticks()
        if (curr_time - self.last_shot) >= SHOOT_COOLDOWN:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            self.bullets.append(bullet)
            self.last_shot = curr_time


class Alien(GameObject):
    def __init__(self, x_pos, y_pos):
        GameObject.__init__(
            self, 
            x_pos, y_pos, 
            ALIEN_WIDTH, ALIEN_HEIGHT, 
            BLACK
        )
        self.speed = ALIEN_SPEED


class Aliens:
    def __init__(self, alien_rows, alien_cols):
        # Distribute aliens evenly across top half to start
        self.aliens = []
        self.speed = ALIEN_SPEED

        for row in range(alien_rows):
            for col in range(alien_cols):
                x_pos = (SCREEN_WIDTH // (alien_cols + 1)) * (col + 1)
                y_pos = (SCREEN_HEIGHT // 2 // (alien_rows + 1)) * (row + 1)
                self.aliens.append(Alien(x_pos, y_pos))

    def move(self):
        # Move aliens as group
        hit_wall = False
        for alien in self.aliens:
            alien.rect.x += self.speed
            if alien.rect.left <= 0 or alien.rect.right >= SCREEN_WIDTH:
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


def setup_game():
    pygame.init()
    pygame.font.init()

    global FONT 
    FONT = pygame.font.Font(None, 32)

    pygame.display.set_caption("Space Invaders!")
    
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock() # Loop speed (FPS, see below)

    return window, clock


def launch_welcome_screen(screen):
    button_center_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
    button_center_y = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT // 2

    buttons = [
        Button("Easy", button_center_x, button_center_y - 1.5 * (BUTTON_SPACING + BUTTON_HEIGHT)),
        Button("Medium", button_center_x, button_center_y - 0.5 * (BUTTON_SPACING + BUTTON_HEIGHT)),
        Button("Hard", button_center_x, button_center_y + 0.5 * (BUTTON_SPACING + BUTTON_HEIGHT)),
        Button("Expert", button_center_x, button_center_y + 1.5 * (BUTTON_SPACING + BUTTON_HEIGHT)),
    ]
    selected_index = 0 # Default == easy

    running = True
    while running:
        render_screen(screen, PASTEL_GREEN, buttons)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                selected_index = get_difficulty(buttons, selected_index)
                    

        for i, button in enumerate(buttons):
            button.selected = (i == selected_index)

        if pygame.key.get_pressed()[pygame.K_RETURN]:
            running = False

    return ["Easy", "Medium", "Hard", "Expert"][selected_index]
            

def get_difficulty(buttons, selected_index):
    keys = pygame.key.get_pressed()

    # Up arrow == easier, down == harder
    if keys[pygame.K_DOWN]:
        selected_index = (selected_index + 1) % len(buttons)
    elif keys[pygame.K_UP]:
        selected_index = (selected_index - 1) % len(buttons)
    
    return selected_index


def render_screen(screen, color, items_to_draw):
    screen.fill(color)

    # Draw spaceships (+ bullets), aliens, buttons, etc
    for item in items_to_draw:
        item.draw_to_screen(screen)

        if isinstance(item, Spaceship):
            for bullet in item.bullets:
                bullet.draw_to_screen(screen)

    pygame.display.flip()


def handle_player_keys(spaceship):
    keys = pygame.key.get_pressed() 

    if keys[pygame.K_LEFT]:
        spaceship.move(-1)
    if keys[pygame.K_RIGHT]:
        spaceship.move(1)

    if keys[pygame.K_SPACE]:
        spaceship.shoot()


def check_bullets(spaceship, aliens):
    for bullet in spaceship.bullets.copy(): # Iterate on copy to avoid issues
        bullet.move()

        # Check if bullet left screen
        if bullet.off_screen():
            spaceship.bullets.remove(bullet)

        # Check for collisions
        for alien in aliens.aliens.copy():
            if bullet.rect.colliderect(alien.rect):
                aliens.aliens.remove(alien)
                spaceship.bullets.remove(bullet)
                break


# Main game loop
def run_game(window, clock, difficulty):
    # Top left of screen (0, 0) ... bottom right (WIDTH, HEIGHT)
    spaceship = Spaceship(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70) 
    aliens = Aliens(ALIEN_ROWS, ALIEN_COLS) if EASY_MODE else Aliens(ALIEN_ROWS + 1, ALIEN_COLS + 2)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False

        # Spaceship left/right arrow key movement
        handle_player_keys(spaceship)

        aliens.move()
        check_bullets(spaceship, aliens)

        # Update display
        render_screen(window, PASTEL_GREEN, [spaceship, aliens])
        clock.tick(60)

    pygame.quit()


def main():
    # Initialize game settings & run
    window, clock = setup_game()

    difficulty = launch_welcome_screen(window)
    run_game(window, clock, difficulty)


if __name__ == "__main__":
    main()     




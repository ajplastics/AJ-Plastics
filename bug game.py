"""
Bug Catcher
-----------
A simple arcade-style game built with pygame.

Catch the good bugs (ladybugs & butterflies) with your net for points.
Avoid the bad bugs (spiders) — catching one costs you a life!
Bugs fall faster and spawn more often as your score increases.

Controls:
    LEFT / RIGHT arrow keys or A / D  -> move the net
    Mouse movement                    -> also moves the net
    SPACE                             -> start game / restart after game over
    Q or ESC                          -> quit

Run with:
    pip install pygame
    python bug_catcher.py
"""

import pygame
import random
import sys

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bug Catcher")
clock = pygame.time.Clock()

font_large = pygame.font.SysFont("arial", 64, bold=True)
font_medium = pygame.font.SysFont("arial", 36, bold=True)
font_small = pygame.font.SysFont("arial", 24)

# Colors
SKY_TOP = (135, 206, 235)
SKY_BOTTOM = (200, 235, 245)
GROUND_GREEN = (86, 160, 70)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (220, 40, 40)
DARK_RED = (150, 20, 20)
ORANGE = (255, 150, 30)
YELLOW = (250, 220, 60)
PURPLE = (150, 60, 180)
DARK_BROWN = (80, 50, 30)
NET_COLOR = (240, 240, 240)
NET_RIM = (180, 130, 60)


def draw_vertical_gradient(surface, top_color, bottom_color):
    """Draws a simple vertical gradient background."""
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))


# ---------------------------------------------------------------------------
# Bug types: name -> (color, points, radius, speed_multiplier, is_bad)
# ---------------------------------------------------------------------------
BUG_TYPES = {
    "ladybug": {"color": RED, "points": 10, "radius": 14, "speed_mult": 1.0, "bad": False, "weight": 55},
    "butterfly": {"color": PURPLE, "points": 25, "radius": 12, "speed_mult": 1.3, "bad": False, "weight": 20},
    "beetle": {"color": ORANGE, "points": 15, "radius": 15, "speed_mult": 0.85, "bad": False, "weight": 15},
    "spider": {"color": DARK_BROWN, "points": 0, "radius": 14, "speed_mult": 1.1, "bad": True, "weight": 10},
}


def pick_bug_type():
    names = list(BUG_TYPES.keys())
    weights = [BUG_TYPES[n]["weight"] for n in names]
    return random.choices(names, weights=weights, k=1)[0]


class Bug:
    """A single falling bug."""

    def __init__(self, base_speed):
        self.type_name = pick_bug_type()
        info = BUG_TYPES[self.type_name]
        self.radius = info["radius"]
        self.color = info["color"]
        self.points = info["points"]
        self.is_bad = info["bad"]
        self.speed = base_speed * info["speed_mult"]
        self.x = random.randint(self.radius + 10, SCREEN_WIDTH - self.radius - 10)
        self.y = -self.radius
        self.wobble_phase = random.uniform(0, 6.28)
        self.wobble_speed = random.uniform(1.5, 3.0)
        self.wobble_amount = random.uniform(0.4, 1.2)

    def update(self, dt):
        self.y += self.speed * dt
        self.wobble_phase += self.wobble_speed * dt

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surface):
        import math
        wobble_x = self.x + math.sin(self.wobble_phase) * (self.wobble_amount * 6)
        cx, cy = int(wobble_x), int(self.y)

        if self.type_name == "ladybug":
            pygame.draw.circle(surface, self.color, (cx, cy), self.radius)
            pygame.draw.line(surface, BLACK, (cx, cy - self.radius), (cx, cy + self.radius), 2)
            pygame.draw.circle(surface, BLACK, (cx - 5, cy - 3), 2)
            pygame.draw.circle(surface, BLACK, (cx + 5, cy - 3), 2)
            pygame.draw.circle(surface, BLACK, (cx - 4, cy + 5), 2)
            pygame.draw.circle(surface, BLACK, (cx, cy - self.radius - 2), self.radius // 2)
        elif self.type_name == "butterfly":
            wing_flap = math.sin(self.wobble_phase * 2) * 4
            pygame.draw.ellipse(surface, self.color,
                                 (cx - self.radius - wing_flap, cy - self.radius, self.radius, self.radius * 2))
            pygame.draw.ellipse(surface, self.color,
                                 (cx + wing_flap, cy - self.radius, self.radius, self.radius * 2))
            pygame.draw.line(surface, BLACK, (cx, cy - self.radius), (cx, cy + self.radius), 2)
        elif self.type_name == "beetle":
            pygame.draw.ellipse(surface, self.color,
                                 (cx - self.radius, cy - self.radius, self.radius * 2, self.radius * 2))
            pygame.draw.line(surface, BLACK, (cx, cy - self.radius), (cx, cy + self.radius), 2)
            pygame.draw.circle(surface, BLACK, (cx, cy - self.radius - 3), 3)
        else:  # spider
            pygame.draw.circle(surface, self.color, (cx, cy), self.radius)
            for angle in range(0, 360, 45):
                ex = cx + math.cos(math.radians(angle)) * (self.radius + 8)
                ey = cy + math.sin(math.radians(angle)) * (self.radius + 8)
                pygame.draw.line(surface, BLACK, (cx, cy), (ex, ey), 2)
            pygame.draw.circle(surface, RED, (cx - 4, cy - 2), 2)
            pygame.draw.circle(surface, RED, (cx + 4, cy - 2), 2)


class Player:
    """The net the player controls."""

    def __init__(self):
        self.width = 90
        self.height = 20
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 60
        self.speed = 500  # pixels per second (keyboard)

    def update(self, dt, keys, mouse_x, mouse_moved):
        if mouse_moved:
            self.x = mouse_x - self.width // 2
        else:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.x -= self.speed * dt
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.x += self.speed * dt
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()
        pygame.draw.arc(surface, NET_RIM, rect.inflate(0, 20), 3.4, 6.0, 4)
        pygame.draw.ellipse(surface, NET_COLOR, rect)
        pygame.draw.ellipse(surface, NET_RIM, rect, 3)
        pole_x = rect.centerx
        pygame.draw.line(surface, NET_RIM, (pole_x, rect.bottom), (pole_x, rect.bottom + 25), 5)


class Game:
    STATE_START = "start"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"

    def __init__(self):
        self.reset()
        self.state = Game.STATE_START

    def reset(self):
        self.player = Player()
        self.bugs = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.spawn_timer = 0.0
        self.spawn_interval = 1.1
        self.base_bug_speed = 160
        self.state = Game.STATE_PLAYING

    def level_up_check(self):
        new_level = self.score // 100 + 1
        if new_level != self.level:
            self.level = new_level
            self.spawn_interval = max(0.35, 1.1 - 0.07 * (self.level - 1))
            self.base_bug_speed = 160 + 18 * (self.level - 1)

    def update(self, dt, keys, mouse_x, mouse_moved):
        if self.state != Game.STATE_PLAYING:
            return

        self.player.update(dt, keys, mouse_x, mouse_moved)

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            self.bugs.append(Bug(self.base_bug_speed))

        player_rect = self.player.get_rect()
        remaining_bugs = []
        for bug in self.bugs:
            bug.update(dt)
            bug_rect = bug.get_rect()

            if bug_rect.colliderect(player_rect):
                if bug.is_bad:
                    self.lives -= 1
                else:
                    self.score += bug.points
                    self.level_up_check()
                continue  # bug is caught/removed either way

            if bug.y - bug.radius > SCREEN_HEIGHT:
                if not bug.is_bad:
                    self.lives -= 1  # missed a good bug
                continue

            remaining_bugs.append(bug)

        self.bugs = remaining_bugs

        if self.lives <= 0:
            self.lives = 0
            self.state = Game.STATE_GAME_OVER

    def draw_hud(self, surface):
        score_text = font_medium.render(f"Score: {self.score}", True, BLACK)
        level_text = font_small.render(f"Level: {self.level}", True, BLACK)
        surface.blit(score_text, (20, 15))
        surface.blit(level_text, (20, 55))

        for i in range(3):
            cx = SCREEN_WIDTH - 30 - i * 35
            cy = 30
            color = RED if i < self.lives else (200, 200, 200)
            pygame.draw.circle(surface, color, (cx, cy), 12)
            pygame.draw.circle(surface, BLACK, (cx, cy), 12, 2)

    def draw(self, surface):
        draw_vertical_gradient(surface, SKY_TOP, SKY_BOTTOM)
        pygame.draw.rect(surface, GROUND_GREEN, (0, SCREEN_HEIGHT - 30, SCREEN_WIDTH, 30))

        if self.state == Game.STATE_START:
            self.draw_start_screen(surface)
        elif self.state == Game.STATE_PLAYING:
            for bug in self.bugs:
                bug.draw(surface)
            self.player.draw(surface)
            self.draw_hud(surface)
        elif self.state == Game.STATE_GAME_OVER:
            for bug in self.bugs:
                bug.draw(surface)
            self.player.draw(surface)
            self.draw_hud(surface)
            self.draw_game_over_screen(surface)

    def draw_start_screen(self, surface):
        title = font_large.render("BUG CATCHER", True, DARK_RED)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 180)))

        lines = [
            "Catch ladybugs, butterflies, and beetles for points.",
            "Avoid the spiders  -  they cost you a life!",
            "Missed good bugs also cost a life.",
            "",
            "Move: Arrow keys / A,D / Mouse",
            "",
            "Press SPACE to start",
        ]
        for i, line in enumerate(lines):
            surf = font_small.render(line, True, BLACK)
            surface.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, 280 + i * 32)))

    def draw_game_over_screen(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        title = font_large.render("GAME OVER", True, WHITE)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 220)))

        score_line = font_medium.render(f"Final Score: {self.score}", True, YELLOW)
        surface.blit(score_line, score_line.get_rect(center=(SCREEN_WIDTH // 2, 290)))

        level_line = font_small.render(f"Reached Level {self.level}", True, WHITE)
        surface.blit(level_line, level_line.get_rect(center=(SCREEN_WIDTH // 2, 330)))

        restart_line = font_small.render("Press SPACE to play again  -  Q to quit", True, WHITE)
        surface.blit(restart_line, restart_line.get_rect(center=(SCREEN_WIDTH // 2, 400)))


def main():
    game = Game()
    game.state = Game.STATE_START

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        mouse_moved = False
        mouse_x = pygame.mouse.get_pos()[0]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                mouse_moved = True
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
                elif event.key == pygame.K_SPACE:
                    if game.state in (Game.STATE_START, Game.STATE_GAME_OVER):
                        game.reset()

        keys = pygame.key.get_pressed()
        game.update(dt, keys, mouse_x, mouse_moved)
        game.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
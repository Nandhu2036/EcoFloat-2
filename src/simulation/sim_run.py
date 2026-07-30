import pygame
import math
import random
import time

# Pygame Init
pygame.init()
pygame.font.init()

# Window Setup
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EcoFloat-2: Closed-Loop Catamaran Simulator")

# Colors (Aesthetic Palette)
COLOR_WATER = (32, 60, 80)
COLOR_HULL = (230, 200, 50)
COLOR_TEXT = (240, 240, 240)
COLOR_TRASH = (240, 60, 50)
COLOR_LASER = (50, 240, 60)
COLOR_TRAIL = (45, 80, 105)

# Fonts
font_title = pygame.font.SysFont("Consolas", 18, bold=True)
font_body = pygame.font.SysFont("Consolas", 14)

class Catamaran:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = -90.0  # Pointing up initially
        self.speed = 0.0
        self.port_speed = 0.0
        self.starboard_speed = 0.0
        self.length = 50.0
        self.width = 30.0
        self.net_capacity = 0
        self.state = "EXPLORATORY_SEARCH"
        self.trail = []

    def update(self):
        # Differential kinematics
        thrust = (self.port_speed + self.starboard_speed) / 2.0 * 0.05
        yaw_rate = (self.port_speed - self.starboard_speed) * 0.04
        
        self.speed = thrust
        self.angle += yaw_rate
        
        # Calculate velocity components
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y += self.speed * math.sin(rad)
        
        # Enforce boundaries
        self.x = max(50, min(WIDTH - 50, self.x))
        self.y = max(50, min(HEIGHT - 100, self.y))

        # Log trail
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 120:
            self.trail.pop(0)

    def draw(self, surface):
        # Draw Trail
        if len(self.trail) > 1:
            pygame.draw.lines(surface, COLOR_TRAIL, False, self.trail, 2)

        # Draw Catamaran hulls
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        # Hulls are spaced by half beam width
        dx = -self.width / 2.0 * sin_a
        dy = self.width / 2.0 * cos_a
        
        # Port hull center
        px, py = self.x + dx, self.y + dy
        # Starboard hull center
        sx, sy = self.x - dx, self.y - dy
        
        # Draw hulls as rounded rectangles
        for cx, cy in [(px, py), (sx, sy)]:
            # Compute endpoints
            start = (cx - (self.length/2.0) * cos_a, cy - (self.length/2.0) * sin_a)
            end = (cx + (self.length/2.0) * cos_a, cy + (self.length/2.0) * sin_a)
            pygame.draw.line(surface, COLOR_HULL, start, end, 8)

        # Draw connecting deck & mesh net backing
        pygame.draw.line(surface, (150, 150, 150), (px - 10*cos_a, py - 10*sin_a), (sx - 10*cos_a, sy - 10*sin_a), 4)
        
        # Draw rear collection net
        net_pts = [
            (px - (self.length/2.0) * cos_a, py - (self.length/2.0) * sin_a),
            (px - (self.length/1.2) * cos_a - (self.width/4.0)*sin_a, py - (self.length/1.2) * sin_a + (self.width/4.0)*cos_a),
            (sx - (self.length/1.2) * cos_a + (self.width/4.0)*sin_a, sy - (self.length/1.2) * sin_a - (self.width/4.0)*cos_a),
            (sx - (self.length/2.0) * cos_a, sy - (self.length/2.0) * sin_a)
        ]
        pygame.draw.polygon(surface, (60, 150, 100), net_pts, 1)

class Debris:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8.0

    def draw(self, surface):
        pygame.draw.circle(surface, COLOR_TRASH, (int(self.x), int(self.y)), int(self.radius))

def run():
    clock = pygame.time.Clock()
    boat = Catamaran(WIDTH // 2, HEIGHT // 2)
    debris_list = []
    
    # Lawnmower pattern variables
    base_speed = 40
    nav_dir = 1
    last_turn = time.time()

    running = True
    while running:
        # Event Processing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if my < HEIGHT - 80:
                    debris_list.append(Debris(mx, my))

        # Clear Screen
        screen.fill(COLOR_WATER)

        # 1. Update State & Control Loop
        if len(debris_list) > 0:
            # Active interception mode
            target = debris_list[0]
            boat.state = "ACTIVE_INTERCEPTION"
            
            # Vector math to target
            dx = target.x - boat.x
            dy = target.y - boat.y
            dist = math.hypot(dx, dy)
            
            # Target angle
            target_angle = math.degrees(math.atan2(dy, dx))
            
            # Steering error
            angle_err = (target_angle - boat.angle + 180) % 360 - 180
            
            # Proportional correction
            kp = 2.5
            correction = kp * angle_err
            
            # Differential motor speed
            boat.port_speed = base_speed + correction
            boat.starboard_speed = base_speed - correction
            
            # Cap speeds
            boat.port_speed = max(0, min(100, boat.port_speed))
            boat.starboard_speed = max(0, min(100, boat.starboard_speed))
            
            # Draw laser visual lock line
            pygame.draw.line(screen, COLOR_LASER, (int(boat.x), int(boat.y)), (int(target.x), int(target.y)), 1)
            
            # Capture check
            if dist < 25:
                # Trash collected!
                debris_list.pop(0)
                boat.net_capacity += 1
                boat.state = "DEBRIS_CAPTURE"
                # Flash screen
                pygame.draw.rect(screen, (50, 200, 80), (0, 0, WIDTH, HEIGHT), 5)
        else:
            # Lawnmower sweep exploration
            boat.state = "EXPLORATORY_SEARCH"
            now = time.time()
            if now - last_turn > 8:
                nav_dir *= -1
                last_turn = now
                boat.port_speed = base_speed + 50 * nav_dir
                boat.starboard_speed = base_speed - 50 * nav_dir
            else:
                boat.port_speed = base_speed
                boat.starboard_speed = base_speed

        # 2. Physics & Draw
        boat.update()
        boat.draw(screen)
        
        for d in debris_list:
            d.draw(screen)

        # 3. Draw UI Dashboard
        pygame.draw.rect(screen, (20, 30, 40), (0, HEIGHT - 80, WIDTH, 80))
        pygame.draw.line(screen, (80, 80, 80), (0, HEIGHT - 80), (WIDTH, HEIGHT - 80), 2)
        
        # Status text
        txt_state = font_title.render(f"VESSEL STATE: {boat.state}", True, COLOR_TEXT)
        txt_motors = font_body.render(f"Port Motor: {int(boat.port_speed)}% | Starboard Motor: {int(boat.starboard_speed)}%", True, COLOR_TEXT)
        txt_cap = font_body.render(f"Collected Debris Count: {boat.net_capacity} units", True, COLOR_LASER)
        txt_instruct = font_body.render("Click anywhere on the water to spawn plastic debris targets.", True, (150, 150, 150))

        screen.blit(txt_state, (20, HEIGHT - 70))
        screen.blit(txt_motors, (20, HEIGHT - 45))
        screen.blit(txt_cap, (WIDTH - 300, HEIGHT - 70))
        screen.blit(txt_instruct, (WIDTH - 500, HEIGHT - 45))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    run()
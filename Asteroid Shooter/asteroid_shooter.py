import pygame
import random
import sys


pygame.init()
width = 800
height = 680
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Asteroid Shooter")
pygame.display.set_icon(pygame.image.load("Sprites/spaceship_icon.png"))
clock = pygame.time.Clock()
fps = 30


white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

bg = pygame.image.load("Sprites/bg.png").convert_alpha()

jetX = width // 2
jetY = height - 60
jet_delX = 0
jet_size = 75
jet_vel = 0.5
jet = pygame.transform.scale(pygame.image.load("Sprites/fighterjet.png"), (jet_size, jet_size))
    
laser = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("Sprites/laser.png").convert_alpha(), (10, 30)), 0)
lasers = []
laser_vel = 8

asteroid_small = pygame.transform.scale(pygame.image.load("Sprites/asteroidSmall.png"), (45, 45))
asteroid_big = pygame.transform.scale(pygame.image.load("Sprites/asteroidBig.png"), (75, 75))

asteroids = []
for i in range(3):
    asteroids.append({
        "img": asteroid_small,
        "x": random.randint(0, width - 30),
        "y": random.randint(50, 150),
        "ast_vel": random.randint(3, 6),
        "size": "small"
    })

for i in range(2):
    asteroids.append({
        "img": asteroid_big,
        "x": random.randint(0, width - 50),
        "y": random.randint(50, 150),
        "ast_vel": random.randint(2, 4),
        "size": "big"
    })

explosion = pygame.transform.scale(pygame.image.load("Sprites/explosion.png").convert_alpha(), (256, 256))
frame_rows = 8
frame_col = 8
frame_width = explosion.get_width()//frame_col
frame_height = explosion.get_height()//frame_rows

explosion_frame = []
for row in range(frame_rows):
    for col in range(frame_col):
        frame = explosion.subsurface(
            (col*frame_width, row*frame_height, frame_width, frame_height)
        )
        explosion_frame.append(frame)

lives = 1
score = 0
fontSmall = pygame.font.SysFont("comicsans", 24)
fontMed = pygame.font.SysFont("comicsans", 36)
fontBig = pygame.font.SysFont("comicsans", 48)

fire = pygame.mixer.Sound("SFX/fire.wav")
gameOver = pygame.mixer.Sound("SFX/gameover.wav")
explosion_sound = pygame.mixer.Sound("SFX/explosion1.mp3")
pygame.mixer.music.load("SFX/8-bit-background-music-for-arcade-game-come-on-mario-164702.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)
fire.set_volume(0.6)
gameOver.set_volume(0.2)

def player(x, y):
    jet_rect = jet.get_rect()
    jet_rect.center = (x, y)
    screen.blit(jet, jet_rect)
    return jet_rect

def text(t, f, col, x, y):
    img = f.render(t, True, col)
    screen.blit(img, (x, y))

def reset_asteroid(asteroid):
    asteroid["x"] = random.randint(0, width - (30 if asteroid["size"] == "small" else 50))
    asteroid["y"] = random.randint(-150, -50)
    asteroid["ast_vel"] = random.randint(3, 6) if asteroid["size"] == "small" else random.randint(2, 4)

class Explosion:
    def __init__(self, x, y):
        self.frames = explosion_frame
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center = (x, y))
        self.frame_rate = 4
        self.counter = 0
        self.active = True
        
    def update(self, screen):
        if not self.active:
            return
        self.counter += 1
        if self.counter >= self.frame_rate:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.frames):
                self.active = False
                return
            self.image = self.frames[self.index]
        screen.blit(self.image, self.rect)
        return True
        
    
running = True
explosions = []
while running:
    screen.blit(bg, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                jet_delX = -jet_vel
            if event.key == pygame.K_RIGHT:
                jet_delX = jet_vel
            if event.key == pygame.K_SPACE:
                if len(lasers) < 8:
                    lasers.append(pygame.Rect(jetX - 5, jetY - 60, 10, 40))
                    fire.play()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                jet_delX = 0
    
    jetX += jet_delX*fps
    if jetX < jet_size//2:
        jetX = jet_size//2
    if jetX > width - jet_size//2:
        jetX = width - jet_size//2
    
    for l in lasers[:]:
        l.y -= laser_vel
        if l.bottom < 0:
            lasers.remove(l)
        else:
            screen.blit(laser, l)
    
    player_rect = player(jetX, jetY)
    
    for ast in asteroids:
        ast["y"] += ast["ast_vel"]
        if ast["y"] > height:
            reset_asteroid(ast)
        
        ast_rect = ast["img"].get_rect(topleft = (ast["x"], ast["y"]))
        screen.blit(ast["img"], ast_rect)
        
        for l in lasers[:]:
            if ast_rect.colliderect(l):
                explosions.append(Explosion(*ast_rect.center))
                reset_asteroid(ast)
                lasers.remove(l)
                if ast["size"] == "small":
                    score += 10
                else:
                    score += 20
                explosion_sound.play()         
                break
        
        if ast_rect.colliderect(player_rect):
            explosions.append(Explosion(*ast_rect.center))
            reset_asteroid(ast)
            lives -= 1
            explosion_sound.play()
            if lives <= 0:
                gameOver.play()
                running = False
    
    for exp in explosions[:]:
        exp.update(screen)
        if not exp.active:
            explosions.remove(exp)
    text(f"Lives: {lives}", fontMed, white, 10, 10)
    text(f"Score: {score}", fontMed, white, width - 200, 10)
    
    pygame.display.update()
    clock.tick(fps)

pygame.mixer.music.stop()    
screen.fill(black)
text("Game Over", fontBig, red, (width//2) - 100, (height//2) - 50)
text(f"Score: {score}", fontMed, white, (width//2) - 60, (height//2) + 20)
text("Press ESC to Exit", fontSmall, white, (width//2) - 77, (height//2) + 80)
pygame.display.update()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
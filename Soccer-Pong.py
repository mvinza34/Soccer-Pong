import pygame, sys, random
from pathlib import Path


class Block(pygame.sprite.Sprite):
	def __init__(self,path,x_pos,y_pos):
		super().__init__()
		self.image = pygame.image.load(path)
		self.rect = self.image.get_rect(center = (x_pos,y_pos))

class Player(Block):
	def __init__(self,path,x_pos,y_pos,speed):
		super().__init__(path,x_pos,y_pos)
		self.speed = speed
		self.movement = 0
	def screen_constrain(self):
		if self.rect.top <= 9: self.rect.top = 9
		if self.rect.bottom >= 905: self.rect.bottom = 905
	def update(self,ball_group):
		self.rect.y += self.movement
		self.screen_constrain()

class Opponent(Block):
	def __init__(self,path,x_pos,y_pos,speed):
		super().__init__(path,x_pos,y_pos)
		self.speed = speed
	def update(self,ball_group):
		if self.rect.top < ball_group.sprite.rect.y:
			self.rect.y += self.speed
		if self.rect.bottom > ball_group.sprite.rect.y:
			self.rect.y -= self.speed
		self.constrain()
	def constrain(self):
		if self.rect.top <= 9: self.rect.top = 9
		if self.rect.bottom >= 905: self.rect.bottom = 905

class Ball(Block):
    def __init__(self,path,x_pos,y_pos,speed_x,speed_y,paddles):
        super().__init__(path,x_pos,y_pos)
        self.speed_x = speed_x * random.choice((-1,1))
        self.speed_y = speed_y * random.choice((-1,1))
        self.paddles = paddles
        self.active = False
        self.score_time = 0
    def update(self):
        if self.active:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            self.screen_constrain()
            self.collisions()
        else:
            self.restart_counter()
    def collisions(self):
        if self.rect.top <= 0 or self.rect.bottom >= screen_height:
            pygame.mixer.Sound.play(hit_sound)
            self.speed_y *= -1
        if pygame.sprite.spritecollide(self,self.paddles,False):
            pygame.mixer.Sound.play(hit_sound)
            collision_paddle = pygame.sprite.spritecollide(self,self.paddles,False)[0].rect
            if abs(self.rect.right - collision_paddle.left) < 10 and self.speed_x > 0: 
                self.speed_x *= -1
            if abs(self.rect.left - collision_paddle.right) < 10 and self.speed_x < 0: 
                self.speed_x *= -1
            if abs(self.rect.top - collision_paddle.bottom) < 10 and self.speed_y < 0: 
                self.rect.top = collision_paddle.bottom
                self.speed_y *= -1
            if abs(self.rect.bottom - collision_paddle.top) < 10 and self.speed_y > 0:
               self.rect.bottom = collision_paddle.top
               self.speed_y *= -1
    def screen_constrain(self):
        # Keep the ball from leaving the top and bottom of the pitch
        if self.rect.top <= 9 and self.speed_y < 0: 
            pygame.mixer.Sound.play(hit_sound)
            self.speed_y *= -1
            self.rect.top = 9
        if self.rect.bottom >= 905 and self.speed_y > 0: 
            pygame.mixer.Sound.play(hit_sound)
            self.speed_y *= -1
            self.rect.bottom = 905
        # Keep the ball from leaving the left and right of the pitch except the goals
        if 595 <= self.rect.bottom <= 905 and self.rect.left <= 10 and self.speed_x < 0: 
            pygame.mixer.Sound.play(hit_sound)
            self.speed_x *= -1
            self.rect.left = 10
        if 10 <= self.rect.top <= 320 and self.rect.right >= 1210 and self.speed_x > 0: 
            pygame.mixer.Sound.play(hit_sound)
            self.speed_x *= -1
            self.rect.right = 1210
        if 10 <= self.rect.top <= 320 and self.rect.left <= 10 and self.speed_x < 0: 
            pygame.mixer.Sound.play(hit_sound)
            self.speed_x *= -1
            self.rect.left = 10
        if 595 <= self.rect.bottom <= 905 and self.rect.right >= 1210 and self.speed_x > 0: 
            pygame.mixer.Sound.play(hit_sound)
            self.speed_x *= -1
            self.rect.right = 1210
    def reset_ball(self):
        self.active = False
        self.speed_x *= random.choice((-1,1))
        self.speed_y *= random.choice((-1,1))
        self.score_time = pygame.time.get_ticks()
        self.rect.center = (screen_width/2,screen_height/2)
        pygame.mixer.Sound.play(goal_sound)
    def restart_counter(self):
        current_time = pygame.time.get_ticks()
        countdown_number = 3
        if current_time - self.score_time <= 700:
            countdown_number = 3
        if 700 < current_time - self.score_time <= 1400:
            countdown_number = 2
        if 1400 < current_time - self.score_time <= 2100:
            countdown_number = 1
        if current_time - self.score_time >= 2100:
            pygame.mixer.Sound.play(start_sound)
            self.active = True
        time_counter = game_font.render(str(countdown_number),True,accent_color)
        time_counter_rect = time_counter.get_rect(center = (screen_width/2,screen_height/2 + 50))
        pygame.draw.rect(screen,bg_color,time_counter_rect)
        screen.blit(time_counter,time_counter_rect)

class GameManager:
	def __init__(self,ball_group,paddle_group):
		self.player_score = 0
		self.opponent_score = 0
		self.ball_group = ball_group
		self.paddle_group = paddle_group
	def run_game(self):
		# Drawing the game objects
		self.paddle_group.draw(screen)
		self.ball_group.draw(screen)
		# Updating the game objects
		self.paddle_group.update(self.ball_group)
		self.ball_group.update()
		self.reset_ball()
		self.draw_score()
	def reset_ball(self):
		if 320 <= self.ball_group.sprite.rect.top <= 595 and self.ball_group.sprite.rect.right >= screen_width:
			self.opponent_score += 1
			self.ball_group.sprite.reset_ball()
		if 320 <= self.ball_group.sprite.rect.bottom <= 595 and self.ball_group.sprite.rect.left <= 0:
			self.player_score += 1
			self.ball_group.sprite.reset_ball()
	def draw_score(self):
		player_score = game_font.render(str(self.player_score),True,accent_color)
		opponent_score = game_font.render(str(self.opponent_score),True,accent_color)

		player_score_rect = player_score.get_rect(midleft = (screen_width / 2 + 40,screen_height/2))
		opponent_score_rect = opponent_score.get_rect(midright = (screen_width / 2 - 40,screen_height/2))

		screen.blit(player_score,player_score_rect)
		screen.blit(opponent_score,opponent_score_rect)

# This prevents "FileNotFoundError" errors from occuring
PROJECT_ROOT = Path(__file__).parent.parent

# General setup
pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()
clock = pygame.time.Clock()

# Main window
screen_width = 1280/1.05
screen_height = 960/1.05
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Soccer-Pong')

# Variables
## Colors
bg_color = pygame.Color(0,130,0)
accent_color = (255,255,255) 
## Score Text
game_font = pygame.font.Font(PROJECT_ROOT / "Soccer-Pong/JustMyType-KePl.ttf",32)
## Sound
hit_sound = pygame.mixer.Sound(PROJECT_ROOT / "Soccer-Pong/hit.ogg")
countdown_sound = pygame.mixer.Sound(PROJECT_ROOT / "Soccer-Pong/countdown.ogg")
start_sound = pygame.mixer.Sound(PROJECT_ROOT / "Soccer-Pong/ref-whistle.mp3")
goal_sound = pygame.mixer.Sound(PROJECT_ROOT / "Soccer-Pong/Goal_Sound.ogg")

# Game objects
## Paddles
player_goalie = Player(PROJECT_ROOT / "Soccer-Pong/Player_Paddle.png",screen_width - 20,screen_height/2,5)
player_forward = Player(PROJECT_ROOT / "Soccer-Pong/Player_Paddle.png",screen_width - 300,screen_height/2,5)
opponent_goalie = Opponent(PROJECT_ROOT / "Soccer-Pong/Opponent_Paddle.png",20,screen_width/2,5)
opponent_forward = Opponent(PROJECT_ROOT / "Soccer-Pong/Opponent_Paddle.png",350,600,5)
paddle_group = pygame.sprite.Group()
paddle_group.add(player_goalie)
paddle_group.add(player_forward)
paddle_group.add(opponent_goalie)
paddle_group.add(opponent_forward)
## Ball
ball = Ball(PROJECT_ROOT / "Soccer-Pong/football.png",screen_width/2,screen_height/2,4,4,paddle_group)
ball_sprite = pygame.sprite.GroupSingle()
ball_sprite.add(ball)
# Pitch
pitch = pygame.image.load(PROJECT_ROOT / "Soccer-Pong/Field.png").convert_alpha()
pitch = pygame.transform.scale(pitch,(screen_width,screen_height))

game_manager = GameManager(ball_sprite,paddle_group)
game_active = False
    
while True:
	# Handling input
	x,y = pygame.mouse.get_pos()
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_DOWN: player_goalie.movement += player_goalie.speed
			if event.key == pygame.K_UP: player_goalie.movement -= player_goalie.speed
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_DOWN: player_goalie.movement -= player_goalie.speed
			if event.key == pygame.K_UP: player_goalie.movement += player_goalie.speed
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_s: player_forward.movement += player_forward.speed
			if event.key == pygame.K_w: player_forward.movement -= player_forward.speed
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_s: player_forward.movement -= player_forward.speed
			if event.key == pygame.K_w: player_forward.movement += player_forward.speed
		if event.type == pygame.MOUSEBUTTONDOWN:
			print(x,y)

	# Visuals
	# Generate the soccer pitch
	screen.blit(pitch,(0,0))
	## goal
	left_goal = pygame.draw.line(screen,(0,130,0),(0,320),(0,595),22)
	right_goal = pygame.draw.line(screen,(0,130,0),(1280/1.05,320),(1280/1.05,595),22)
	
	# Run the game
	game_manager.run_game()

	# Updating the window 
	pygame.display.flip()
	clock.tick(60)

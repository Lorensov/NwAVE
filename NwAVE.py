#! /usr/bin/env python
import pygame;
from pygame.locals import *;
from sys import exit;
from random import randrange;
from random import choice
import random
import time
pygame.init();
pygame.mixer.pre_init(44100, 32, 2, 4096);

splash_filename = 'splashscreen.png'

splash = pygame.mixer.Sound('splash.ogg');

font_name = pygame.font.get_default_font();
game_font = pygame.font.SysFont("comicsansms", 72);
screen = pygame.display.set_mode((956,560),0,32);

pygame.display.set_caption("NwAVE");

background_filename = 'background.png';
background = pygame.image.load(background_filename).convert();

splashscreen = pygame.image.load(splash_filename).convert();


screen.blit(splashscreen,(0,0));
pygame.display.update();
splash.play();
time.sleep(4);

ship_filename = 'ship.png';
ship = pygame.image.load(ship_filename).convert_alpha();
ship_position = [ randrange(956) ,randrange(560)];

ship = { 
	'surface': pygame.image.load('ship.png').convert_alpha(),
	'position': [20, randrange(560)],
	'speed': {'x':0,'y':0}
	}
exploded_ship = {
	'surface': pygame.image.load('ship_exploded.png').convert_alpha(),
	'position': [],
	'speed': {'x':0,'y':0},
	'rect': Rect(0, 0, 48, 48)
	}

fortified_ship = {
	'surface': pygame.image.load('ship_fortified.png').convert_alpha(),
	'position': [],
	'speed': {'x':0,'y':0},
	'rect': Rect(0, 0, 48, 48)
	}

explosion_played = False;
fortified_played = False;
endgame_played = False;



clock = pygame.time.Clock();

def create_dmg():
	return {'surface': pygame.image.load('dmg.png').convert_alpha(),
		'position': [956, randrange(560)],
		'speed': randrange(1,11)
	}

def create_bar():
	return {'surface': pygame.image.load('bar.png').convert_alpha(),
		'position': [956, 0],
		'speed': 10
	}

ticks_to_bar = 20;
bars = [];
ticks_to_dmg = 10;
dmgs = [];

def move_bars():
	for bar in bars:
		bar['position'][0] -= bar ['speed'];
def remove_used_bars():
	for bar in bars:
		if bar['position'][0] == 0:
			bars.remove(bar);

def move_dmgs():
	for dmg in dmgs:
		dmg['position'][0] -= dmg ['speed'];
def remove_used_dmgs():
	for dmg in dmgs:
		if dmg['position'][0] == 0:
			dmgs.remove(dmg);

def rot_center(image, angle):
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

def get_rect(obj):
	return Rect(obj['position'][0],
			obj['position'][1],
			obj['surface'].get_width(),
			obj['surface'].get_height())

def ship_collided():
	ship_rect = get_rect(ship);
	for dmg in dmgs:
		if ship_rect.colliderect(get_rect(dmg)):
			return True
	return False

def ship_barCollided():
	ship_rect = get_rect(ship);
	for bar in bars:
		if ship_rect.colliderect(get_rect(bar)):
			return True
	return False

def ship_bar_collided():
	ship_rect = get_rect(ship);
	for bar in bars:
		if ship_rect.colliderect(get_rect(bar)):
			return True
	return False

last = pygame.time.get_ticks();
cooldown = 400;

collided = False;
barCollided = False;
collision_animation_counter = 0;
score = 0;
hiscorePrinted = False;

explosion_sound = pygame.mixer.Sound('boom.wav');
fortified_sound = pygame.mixer.Sound('fortified.wav');
music = pygame.mixer.Sound('wavering.ogg');
endMusic = pygame.mixer.Sound('endgame.ogg');

music.play();



while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			exit();
	
	random_number = random.choice([15,7,4])

	ship['speed']={'x':0,'y':0}

	if not ticks_to_dmg:
		ticks_to_dmg = 90;
		dmgs.append(create_dmg())
	else:
		ticks_to_dmg -= 5;

	if not ticks_to_bar:
		ticks_to_bar = random_number; #or 7.5 pra criar barra dupla ou 4.25
		bars.append(create_bar())
	else:
		ticks_to_bar -= 1;

	pressed_keys = pygame.key.get_pressed();
	if pressed_keys[K_UP]:
		if ship['position'][1] > 0:
			ship['speed']['y'] = -5
	elif pressed_keys[K_DOWN]:
		if ship['position'][1] < 510:
			ship['speed']['y'] = 5

	if pressed_keys[K_ESCAPE]:
		exit();

	screen.blit(background,(0,0));

	move_dmgs();
	for dmg in dmgs:
		screen.blit(rot_center(dmg['surface'], ticks_to_dmg), dmg['position']);

	move_bars();
	for bar in bars:
		screen.blit(bar['surface'], bar['position']);

	if not collided:
		collided = ship_collided()
		ship['position'][0] += ship['speed']['x'];
		ship['position'][1] += ship['speed']['y'];
		
		screen.blit(ship['surface'],ship['position']);
	else:
		if not explosion_played:
			now = pygame.time.get_ticks()
			if now - last >= cooldown:
				last = now
				explosion_played = True
				explosion_sound.play()
				score = score/2;
			
		elif collision_animation_counter == 3:
			collided = False;
			explosion_played = False;
			collision_animation_counter = 0;
		else:
			exploded_ship['rect'].x = collision_animation_counter * 48;
			exploded_ship['position'] = ship['position']
			screen.blit(exploded_ship['surface'], exploded_ship['position'], exploded_ship['rect'])
			collision_animation_counter += 1;
	
	score += 1;
	txtScore = str(score);
	text_score = game_font.render(txtScore, 1, (255,255,0));
	screen.blit(text_score, (450, 50));

	if pressed_keys[K_SPACE]:
		if not barCollided:
			barCollided = ship_barCollided()
			ship['position'][0] += ship['speed']['x'];
			ship['position'][1] += ship['speed']['y'];		
			screen.blit(ship['surface'],ship['position']);
		else:
			score += 500;
			if not fortified_played:
				fortified_played = True;
				fortified_sound.play();
			elif collision_animation_counter == 3:		
				collided = False;
				fortified_played = False;
				collision_animation_counter = 0;
			else:
				fortified_ship['rect'].x = collision_animation_counter * 48;
				fortified_ship['position'] = ship['position']
				screen.blit(fortified_ship['surface'], fortified_ship['position'], fortified_ship['rect'])
				collision_animation_counter += 1;
			barCollided = False;

	if pygame.time.get_ticks() > 91000:
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					exit();
			pressed_keys = pygame.key.get_pressed();
			if pressed_keys[K_ESCAPE]:
				exit();
		
			if not endgame_played:
				endgame_played = True
				endMusic.play()

			text = game_font.render("THANK YOU FOR PLAYING!!!", 1, (255,255,0))
			screen.blit(text, (200,250))

			if hiscorePrinted == False:
				finalScore = str(score);
				hiscore = game_font.render(str(score),1, (0,255,255))	
				hiscorePrinted = True;
			screen.blit(hiscore, (470, 300))			
			pygame.display.update();
			time_passed = clock.tick(30);

	pygame.display.update();
	time_passed = clock.tick(30);
	
	remove_used_dmgs();
	remove_used_bars();

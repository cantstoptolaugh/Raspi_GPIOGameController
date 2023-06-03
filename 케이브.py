import pygame
import random
import copy
import spidev
import time
import RPi.GPIO as GPIO

# 버튼과 연결된 GPIO 핀 번호를 리스트로 저장
button_pins = [22,25]

GPIO.setmode(GPIO.BCM) 
GPIO.setup(21, GPIO.OUT)
#GPIO.setup(25, GPIO.IN)
GPIO.output(21, GPIO.HIGH)  # LED 켜기

# 버튼 핀을 입력으로 설정
for pin in button_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# 버튼의 이전 입력 상태 저장
previous_input = [GPIO.LOW] * len(button_pins)

# MCP3008의 SPI 버스와 CS(Chip Select) 핀 설정
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000
spi.mode = 0
cs = 8

# MCP3008에서 아날로그 값 읽기
def read_adc(adcnum):
    if adcnum < 0 or adcnum > 7:
        return -1
    r = spi.xfer2([1, (8 + adcnum) << 4, 0])
    adcout = ((r[1] & 3) << 8) + r[2]
    return adcout

# 조이스틱의 초기 위치값
x_initial = 502
y_initial = 517

# 조이스틱의 현재 위치값 계산
def read_joystick():
    x = read_adc(0)
    y = read_adc(1)
    x_diff = x - x_initial
    y_diff = y - y_initial
    return x_diff, y_diff
    
pygame.init() 

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
large_font = pygame.font.SysFont(None, 72)
small_font = pygame.font.SysFont(None, 36)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) 

airplane_image = pygame.image.load('airplane.bmp')
airplane_image = pygame.transform.scale(airplane_image, (60, 80))
airplane = airplane_image.get_rect(left=0, centery=SCREEN_HEIGHT // 2)

explosion_image = pygame.image.load('explosion.bmp')
explosion_image = pygame.transform.scale(explosion_image, (60, 60))
clock = pygame.time.Clock()

rects = [] 
for column_index in range(80):
    rect = pygame.Rect(column_index * 10, 100, 10, 400)
    rects.append(rect)


def runGame():
    score = 0
    game_over = False
    slope = 2
    airplane_dy = 0 # 초기값을 0으로 설정합니다.

    while True: 
        screen.fill(GREEN)

        event = pygame.event.poll() 
        if event.type == pygame.QUIT:
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                airplane_dy = -5 
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                airplane_dy = 5 
        
        for i, pin in enumerate(button_pins):
            # 버튼의 현재 입력 상태
            input_state = GPIO.input(pin)
            # 버튼 입력 상태가 변경되면 출력
            if input_state != previous_input[i]:
                previous_input[0] = input_state
                if input_state == GPIO.HIGH:
                    airplane_dy = -5
                else:
                    airplane_dy = 5
                    
        
        for i, pin in enumerate(button_pins):
            # 버튼의 현재 입력 상태
            input_state = GPIO.input(pin)
            # 버튼 입력 상태가 변경되면 출력
            if input_state != previous_input[i]:
                previous_input[1] = input_state
                if input_state == GPIO.HIGH:
                    GPIO.output(21, GPIO.LOW)
                    pygame.quit() 
        
        score += 1

        new_rect = copy.deepcopy(rects[-1])
        test_rect = copy.deepcopy(rects[-1])
        test_rect.top = test_rect.top + slope
        if test_rect.top <= 0 or test_rect.bottom >= SCREEN_HEIGHT:
            slope = random.randint(2, 6) * (-1 if slope > 0 else 1) 
            new_rect.height = new_rect.height + -20 
        new_rect.left = new_rect.left + 10
        new_rect.top = new_rect.top + slope
        rects.append(new_rect)
        for rect in rects:
            rect.left = rect.left - 10
        del rects[0]

        airplane.top += airplane_dy 

        if airplane.top < rects[0].top or airplane.bottom > rects[0].bottom:
            game_over = True

        for rect in rects:
            pygame.draw.rect(screen, BLACK, rect)

        screen.blit(airplane_image, airplane)

        score_image = small_font.render('Point {}'.format(score), True, YELLOW)
        screen.blit(score_image, (10, 10))

        if game_over == True:
            screen.blit(explosion_image, (0, airplane.top - 40))

            game_over_image = large_font.render('Game over', True, RED)
            screen.blit(game_over_image, game_over_image.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 2))

        pygame.display.update() 
        clock.tick(30) 

runGame()
pygame.quit()

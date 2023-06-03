import pygame
import random
import time
import spidev
import RPi.GPIO as GPIO

# 버튼과 연결된 GPIO 핀 번호를 리스트로 저장
button_pins = [25]

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
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
large_font = pygame.font.SysFont(None, 72)
small_font = pygame.font.SysFont(None, 36)
screen_width = 600
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height)) 

clock = pygame.time.Clock() 

def runGame():
    score = 0
    missed = 0
    SUCCESS = 1
    FAILURE = 2
    game_over = 0

    bricks = []
    COLUMN_COUNT = 8
    ROW_COUNT = 7
    for column_index in range(COLUMN_COUNT):
        for row_index in range(ROW_COUNT):
            brick = pygame.Rect(column_index * (60 + 10) + 35, row_index * (16 + 5) + 35, 60, 16)
            bricks.append(brick)      

    ball = pygame.Rect(screen_width // 2 - 16 // 2, screen_height // 2 - 16 // 2, 16, 16)
    ball_dx = 7
    ball_dy = -7

    paddle = pygame.Rect(screen_width // 2 - 80 // 2, screen_height - 16, 80, 16)
    paddle_dx = 0

    while True: 
        clock.tick(30)
        screen.fill(BLACK) 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    paddle_dx = -5
                elif event.key == pygame.K_RIGHT:
                    paddle_dx = 5
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    paddle_dx = 0
                elif event.key == pygame.K_RIGHT:
                    paddle_dx = 0        
        for i, pin in enumerate(button_pins):
            # 버튼의 현재 입력 상태
            input_state = GPIO.input(pin)
            # 버튼 입력 상태가 변경되면 출력
            if input_state != previous_input[i]:
                previous_input[i] = input_state
                if input_state == GPIO.HIGH:
                    GPIO.output(21, GPIO.LOW)
                    pygame.quit()       
                     
        # 조이스틱 값 읽어들이기
        x_diff, y_diff = read_joystick()
        if x_diff > 100:
            paddle_dx = 10
        elif x_diff < -100:
            paddle_dx = -10
        else:
            paddle_dx = 0
            
            
        paddle.left += paddle_dx

        ball.left += ball_dx
        ball.top  += ball_dy

        if ball.left <= 0:
            ball.left = 0
            ball_dx = -ball_dx
        elif ball.left >= screen_width - ball.width: 
            ball.left = screen_width - ball.width
            ball_dx = -ball_dx
        if ball.top < 0:
            ball.top = 0
            ball_dy = -ball_dy
        elif ball.top >= screen_height:
            missed += 1
            ball.left = screen_width // 2 - ball.width // 2
            ball.top = screen_height // 2 - ball.width // 2
            ball_dy = -ball_dy 

        if missed >= 3:
            game_over = FAILURE 

        if paddle.left < 0:
            paddle.left = 0
        elif paddle.left > screen_width - paddle.width:
            paddle.left = screen_width - paddle.width

        for brick in bricks:
            if ball.colliderect(brick):
                bricks.remove(brick)
                ball_dy = -ball_dy
                score += 1
                break

        if ball.colliderect(paddle):
            ball_dy = -ball_dy
            if ball.centerx <= paddle.left or ball.centerx > paddle.right:
                ball_dx = ball_dx * -1

        if len(bricks) == 0:
            print('success')
            game_over = SUCCESS

        #화면 그리기

        for brick in bricks:
            pygame.draw.rect(screen, GREEN, brick)

        if game_over == 0:
            pygame.draw.circle(screen, WHITE, (ball.centerx, ball.centery), ball.width // 2)

        pygame.draw.rect(screen, BLUE, paddle)

        score_image = small_font.render('Point {}'.format(score), True, YELLOW)
        screen.blit(score_image, (10, 10))

        missed_image = small_font.render('Missed {}'.format(missed), True, YELLOW)
        screen.blit(missed_image, missed_image.get_rect(right=screen_width - 10, top=10))

        if game_over > 0:
            if game_over == SUCCESS:
                success_image = large_font.render('성공', True, RED)
                screen.blit(success_image, success_image.get_rect(centerx=screen_width // 2, centery=screen_height // 2))
            elif game_over == FAILURE:
                failure_image = large_font.render('실패', True, RED)
                screen.blit(failure_image, failure_image.get_rect(centerx=screen_width // 2, centery=screen_height // 2))

        pygame.display.update()
        
            # 게임 종료시 LED 끄기
    GPIO.output(21, GPIO.LOW)

    # GPIO 설정 해제
    GPIO.cleanup()
    # MCP3008 연결 해제
    spi.close()
runGame()
pygame.quit()



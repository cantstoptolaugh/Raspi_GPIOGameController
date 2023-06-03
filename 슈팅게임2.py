import pygame
import random
import spidev
import time
import RPi.GPIO as GPIO

# 버튼과 연결된 GPIO 핀 번호를 리스트로 저장
button_pins = [25]

# 21번 핀 설정
GPIO.setmode(GPIO.BCM) 
GPIO.setup(21, GPIO.OUT)
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
    
# 초기화
pygame.init()

# 창 크기
size = (400, 400)
screen = pygame.display.set_mode(size)

# 색상
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

# 적 초기 위치
enemy_x = random.randint(0, 400)
enemy_y = 0

# 플레이어 초기 위치
player_x = 200
player_y = 375

# 플레이어 이동 속도
player_speed = 1

# 적 이동 속도
enemy_speed = 0.5

# 게임 루프
while True:
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            GPIO.output(21, GPIO.LOW)
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_x -= player_speed
            elif event.key == pygame.K_RIGHT:
                player_x += player_speed
    
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
        player_x += player_speed
    elif x_diff < -100:
        player_x -= player_speed
    
    # 적 이동
    enemy_y += enemy_speed

    # 적 충돌 체크
    if enemy_y > 400:
        enemy_x = random.randint(0, 400)
        enemy_y = 0

    # 플레이어 충돌 체크
    if enemy_y == player_y and enemy_x >= player_x and enemy_x <= player_x + 50:
        GPIO.output(21, GPIO.LOW)
        pygame.quit()
        quit()

    # 그리기
    screen.fill(white)
    pygame.draw.rect(screen, black, [enemy_x, enemy_y, 10, 10])
    pygame.draw.rect(screen, red, [player_x, player_y, 50, 25])
    pygame.display.update()
    
rungame()
pygame.quit()

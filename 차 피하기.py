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
    
# 게임 초기화
pygame.init()

# 창 크기 설정
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("레이싱 게임")

# 게임 변수 설정
car_width = 50
car_height = 100
car_x = SCREEN_WIDTH // 2 - car_width // 2
car_y = SCREEN_HEIGHT - car_height - 20
car_speed = 5

enemy_width = 50
enemy_height = 50
enemy_x = random.randint(0, SCREEN_WIDTH - enemy_width)
enemy_y = -enemy_height
enemy_speed = 11

font = pygame.font.SysFont(None, 50)

clock = pygame.time.Clock()

# 자동차 이미지 불러오기
car_img = pygame.image.load("Car02.bmp")
enemy_img = pygame.image.load("Car32.bmp")

# 게임 루프
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    
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
        car_x += car_speed
    elif x_diff < -100:
        car_x -= car_speed
    
    # 배경 그리기
    screen.fill((255, 255, 255))

    # 적 그리기
    screen.blit(enemy_img, (enemy_x, enemy_y))

    # 플레이어 그리기
    screen.blit(car_img, (car_x, car_y))

    # 적 이동
    enemy_y += enemy_speed
    if enemy_y > SCREEN_HEIGHT:
        enemy_x = random.randint(0, SCREEN_WIDTH - enemy_width)
        enemy_y = -enemy_height

    # 입력 처리
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        car_x -= car_speed
    if keys[pygame.K_RIGHT]:
        car_x += car_speed

    # 충돌 검사
    car_rect = pygame.Rect(car_x, car_y, car_width, car_height)
    enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_width, enemy_height)
    if car_rect.colliderect(enemy_rect):
        # 충돌 시 게임 오버 메시지 출력
        game_over_text = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
        pygame.display.update()
        pygame.time.delay(2000)
        # 게임 종료시 LED 끄기
        GPIO.output(21, GPIO.LOW)
        # GPIO 설정 해제
        GPIO.cleanup()
        pygame.quit()
        quit()

    # 화면 업데이트
    pygame.display.update()

    # FPS 설정
    clock.tick(60)

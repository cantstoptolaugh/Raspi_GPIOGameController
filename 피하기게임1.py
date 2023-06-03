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

# 창 설정
screen_width = 800
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Running Game")

# 색상 설정
white = (255, 255, 255)
black = (0, 0, 0)

# 폰트 설정
font = pygame.font.SysFont(None, 50)

# 이미지 로드
player_image = pygame.image.load("stock.bmp").convert_alpha()
player_image = pygame.transform.scale(player_image, (50, 50))
obstacle_image = pygame.image.load("hurdle-cone.bmp").convert_alpha()
obstacle_image = pygame.transform.scale(obstacle_image, (50, 50))

# 변수 초기화
player_x = 50
player_y = 200
player_speed = 5
obstacle_x = screen_width
obstacle_y = 200
obstacle_speed = 3
score = 0
is_game_over = False
running = True  # running 변수를 초기화

# 게임 루프
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
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
    if y_diff > 100:
        player_y += player_speed
    elif y_diff < -100:
        player_y -= player_speed
    
    # 키 상태 가져오기
    keys = pygame.key.get_pressed()

    # 위쪽 화살표 키가 눌렸으면 플레이어를 위로 이동
    if keys[pygame.K_UP]:
        player_y -= player_speed

    # 아래쪽 화살표 키가 눌렸으면 플레이어를 아래로 이동
    if keys[pygame.K_DOWN]:
        player_y += player_speed


    # 장애물 이동
    obstacle_x -= obstacle_speed
    if obstacle_x < -obstacle_image.get_width():
        obstacle_x = screen_width
        obstacle_y = random.randint(0, screen_height - obstacle_image.get_height())
        score += 10
        obstacle_speed += 0.5

    # 충돌 체크
    player_rect = player_image.get_rect(left=player_x, top=player_y, width=player_image.get_width(), height=player_image.get_height())
    obstacle_rect = obstacle_image.get_rect(left=obstacle_x, top=obstacle_y, width=obstacle_image.get_width(), height=obstacle_image.get_height())
    if player_rect.colliderect(obstacle_rect):
        is_game_over = True

    # 배경 색칠
    screen.fill(white)

    # 이미지 그리기
    screen.blit(player_image, (player_x, player_y))
    screen.blit(obstacle_image, (obstacle_x, obstacle_y))

    # 점수 표시
    text = font.render("Score: " + str(score), True, black)
    screen.blit(text, (10, 10))

    # 게임 오버 처리
    if is_game_over:
        game_over_text = font.render("Game Over!", True, black)
        screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - game_over_text.get_height() // 2))
        pygame.display.update()
        pygame.time.wait(2000)
        running = False

    # 화면 업데이트
    pygame.display.flip()

# 게임 종료시 LED 끄기
GPIO.output(21, GPIO.LOW)
    
# 게임 종료
pygame.quit()

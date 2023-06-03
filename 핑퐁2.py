import pygame
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
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pong Game")

# 색깔 설정
white = (255, 255, 255)
black = (0, 0, 0)

# 폰트 설정
font = pygame.font.SysFont(None, 50)

# 변수 초기화
ball_x = screen_width // 2
ball_y = screen_height // 2
ball_speed_x = 1.5
ball_speed_y = 1.5
paddle_left_y = screen_height // 2
paddle_right_y = screen_height // 2
paddle_width = 10
paddle_height = 80
paddle_speed = 5
left_score = 0
right_score = 0

# 게임 루프
running = True
left_paddle_move_up = False
left_paddle_move_down = False

while running:
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                left_paddle_move_up = True
            elif event.key == pygame.K_s:
                left_paddle_move_down = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                left_paddle_move_up = False
            elif event.key == pygame.K_s:
                left_paddle_move_down = False
    
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
        paddle_left_y += paddle_speed
        if paddle_left_y > screen_height - paddle_height:
            paddle_left_y = screen_height - paddle_height
    elif y_diff < -100:
        paddle_left_y -= paddle_speed
        if paddle_left_y < 0:
            paddle_left_y = 0
    
    # 왼쪽 패들 이동 처리
    if left_paddle_move_up:
        paddle_left_y -= paddle_speed
        if paddle_left_y < 0:
            paddle_left_y = 0
    elif left_paddle_move_down:
        paddle_left_y += paddle_speed
        if paddle_left_y > screen_height - paddle_height:
            paddle_left_y = screen_height - paddle_height

    # 컴퓨터가 오른쪽 패들 움직이도록 처리
    if ball_y < paddle_right_y:
        paddle_right_y -= paddle_speed
    elif ball_y > paddle_right_y + paddle_height:
        paddle_right_y += paddle_speed

    # 공 이동 처리
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # 공 벽 충돌 처리
    if ball_y < 0 or ball_y > screen_height:
        ball_speed_y *= -1

    # 공 패들 충돌 처리
    if ball_x < paddle_width and paddle_left_y < ball_y < paddle_left_y + paddle_height:
        ball_speed_x *= -1
    elif ball_x > screen_width - paddle_width and paddle_right_y < ball_y < paddle_right_y + paddle_height:
        ball_speed_x *= -1

    # 공 아웃 처리
    if ball_x < 0:
        right_score += 1
        ball_x = screen_width // 2
        ball_y = screen_height // 2
        ball_speed_x *= -1
    elif ball_x > screen_width:
        left_score += 1
        ball_x = screen_width // 2
        ball_y = screen_height // 2
        ball_speed_x *= -1

    # 배경 색칠
    screen.fill(black)

    # 패들 그리기
    pygame.draw.rect(screen, white, (0, paddle_left_y, paddle_width, paddle_height))
    pygame.draw.rect(screen, white, (screen_width - paddle_width, paddle_right_y, paddle_width, paddle_height))

    # 공 그리기
    pygame.draw.circle(screen, white, (int(ball_x), int(ball_y)), 10)

    # 점수 표시
    left_score_text = font.render(str(left_score), True, white)
    right_score_text = font.render(str(right_score), True, white)
    screen.blit(left_score_text, (screen_width // 2 - 50, 10))
    screen.blit(right_score_text, (screen_width // 2 + 50, 10))

    # 화면 업데이트
    pygame.display.update()
    
GPIO.output(21, GPIO.LOW)
# 게임 종료
pygame.quit()

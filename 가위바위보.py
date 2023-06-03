import pygame
import random
import spidev
import time
import RPi.GPIO as GPIO

# 버튼과 연결된 GPIO 핀 번호를 리스트로 저장
button_pins = [22, 25]

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
    
# 파이게임 초기화
pygame.init()

# 창 설정
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Rock Paper Scissors")

# 색상 설정
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

# 폰트 설정
font = pygame.font.SysFont(None, 30)

# 컴퓨터의 선택
computer_choice = random.choice(["rock", "paper", "scissors"])

# 플레이어의 선택
player_choice = None

# 게임 루프
running = True
while running:
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 배경 그리기
    screen.fill(white)

    # 텍스트 그리기
    text = font.render("Choose rock, paper or scissors with arrow keys and press a button.", True, black)
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 4))
    screen.blit(text, text_rect)

    # 선택지 그리기
    options = ["rock", "paper", "scissors"]
    option_y = screen_height // 2
    for option in options:
        option_text = font.render(option, True, black)
        option_rect = option_text.get_rect(center=(screen_width // 2, option_y))
        screen.blit(option_text, option_rect)
        option_y += 40

    # 키 입력 처리
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_choice = "rock"
    elif keys[pygame.K_DOWN]:
        player_choice = "paper"
    elif keys[pygame.K_LEFT]:
        player_choice = "scissors"
    
    for i, pin in enumerate(button_pins):
            # 버튼의 현재 입력 상태
            input_state = GPIO.input(pin)
            # 버튼 입력 상태가 변경되면 출력
            if input_state != previous_input[i]:
                previous_input[0] = input_state
                if input_state == GPIO.HIGH:
                    if player_choice == computer_choice:
                        result = "Tie!"
                    elif player_choice == "rock" and computer_choice == "scissors":
                        result = "You win!"
                    elif player_choice == "paper" and computer_choice == "rock":
                        result = "You win!"
                    elif player_choice == "scissors" and computer_choice == "paper":
                        result = "You win!"
                    else:
                        result = "You lose!"
                    text = font.render(f"You chose {player_choice}. Computer chose {computer_choice}. {result}", True, black)
                    text_rect = text.get_rect(center=(screen_width // 2, screen_height - screen_height // 4))
                    screen.blit(text, text_rect)
                    
            if input_state != previous_input[i]:
                previous_input[1] = input_state
                if input_state == GPIO.HIGH:
                    GPIO.output(21, GPIO.LOW)
                    pygame.quit() 
                    
    # 조이스틱 값 읽어들이기
    x_diff, y_diff = read_joystick()
    if x_diff < -100:
        player_choice = "scissors"
    elif y_diff > 100:
        player_choice = "paper"
    elif y_diff < -100:
        player_choice = "rock"
    
    # 선택 확인 및 결과 출력
    if player_choice is not None and keys[pygame.K_RETURN]:
        if player_choice == computer_choice:
            result = "Tie!"
        elif player_choice == "rock" and computer_choice == "scissors":
            result = "You win!"
        elif player_choice == "paper" and computer_choice == "rock":
            result = "You win!"
        elif player_choice == "scissors" and computer_choice == "paper":
            result = "You win!"
        else:
            result = "You lose!"
        text = font.render(f"You chose {player_choice}. Computer chose {computer_choice}. {result}", True, black)
        text_rect = text.get_rect(center=(screen_width // 2, screen_height - screen_height // 4))
        screen.blit(text, text_rect)

    pygame.display.update()
GPIO.output(21, GPIO.LOW)
# 파이게임 종료
pygame.quit()

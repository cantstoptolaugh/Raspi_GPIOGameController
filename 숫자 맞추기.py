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

# 화면 설정
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("숫자 맞추기 게임")

# 색상 설정
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# 시계 설정
clock = pygame.time.Clock()

# 글꼴 설정
font = pygame.font.Font(None, 30)

# 게임 루프
def game():
    # 변수 초기화
    answer = random.randint(1, 100)
    guess = 50
    game_over = False

    # 게임 루프
    while not game_over:
        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    guess -= 1
                elif event.key == pygame.K_RIGHT:
                    guess += 1
                elif event.key == pygame.K_UP:
                    if guess == answer:
                        display_message("get the right answer")
                    else:
                        display_message("That’s a wrong answer.")
                        guess = 50
                        answer = random.randint(1, 100)
        
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
        if x_diff < -100:
            guess -= 1
        elif x_diff > 100:
            guess += 1
        elif y_diff < -100:
            if guess == answer:
                display_message("get the right answer")
            else:
                display_message("That’s a wrong answer.")
                guess = 50
                answer = random.randint(1, 100)
        
        # 화면 업데이트
        screen.fill(WHITE)

        # 텍스트 표시
        guess_text = "Guess: " + str(guess)
        label = font.render(guess_text, True, BLACK)
        screen.blit(label, (screen_width/2-50, screen_height/2-50))

        # 화면 업데이트
        pygame.display.update()

        # 초당 프레임 설정
        clock.tick(60)


# 메시지 표시
def display_message(message):
    # 메시지 텍스트 표시
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(center=(screen_width/2, screen_height-30))
    screen.blit(text, text_rect)
    
    # 화면 업데이트
    pygame.display.update()
    
    # 2초 대기
    pygame.time.wait(2000)

# 게임 실행
game()

# 게임 종료시 LED 끄기
GPIO.output(21, GPIO.LOW)

# GPIO 설정 해제
GPIO.cleanup()

# 게임 종료
pygame.quit()

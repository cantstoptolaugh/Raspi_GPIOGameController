import pygame
import time
import time
import RPi.GPIO as GPIO
import spidev

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
size = (600, 800)
screen = pygame.display.set_mode(size)

# 색상
white = (255, 255, 255)
black = (0, 0, 0)

# 배경 이미지
background = pygame.image.load("pngwing.bmp")

# 새 이미지
bird = pygame.image.load("bluebird.bmp")
bird_x = 25
bird_y = 100
bird_speed = 0

# 폰트 설정
font = pygame.font.SysFont('malgungothic', 30)

# 클럭 객체 생성
clock = pygame.time.Clock()

# 시작 시간 기록
start_time = time.time()

# 게임 루프
while True:
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_speed = -10
    
    for i, pin in enumerate(button_pins):
        # 버튼의 현재 입력 상태
        input_state = GPIO.input(pin)
        # 버튼 입력 상태가 변경되면 출력
        if input_state != previous_input[i]:
            previous_input[0] = input_state
            if input_state == GPIO.HIGH:
                GPIO.output(21, GPIO.LOW)
                pygame.quit()   
    
    x_diff, y_diff = read_joystick()
    if y_diff < -100:
        bird_speed = -10
   
    # 새 이동
    bird_speed += 1
    bird_y += bird_speed

    # 그리기
    screen.blit(background, [0, 0])
    screen.blit(bird, [bird_x, bird_y])

    # 현재 시간과 시작 시간을 비교하여 게임 진행 시간 계산
    current_time = time.time()
    elapsed_time = current_time - start_time

    # 게임 진행 시간과 Keep the bird alive! 문구를 화면에 출력
    elapsed_time_text = font.render(f"Time: {int(elapsed_time)}", True, black)
    screen.blit(elapsed_time_text, [10, 10])

    keep_alive_text = font.render("Keep the bird alive!", True, black)
    screen.blit(keep_alive_text, [size[0] - keep_alive_text.get_width() - 10, 10])

    pygame.display.update()

    # 게임 종료
    if bird_y < -20 or bird_y > 472:
        # 게임 종료시 LED 끄기
        GPIO.output(21, GPIO.LOW)
        pygame.quit()
        quit()

    # 클럭 틱 설정
    clock.tick(60)

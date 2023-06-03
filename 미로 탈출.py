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

# 게임 창 크기 설정
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))

# 게임 창 제목 설정
pygame.display.set_caption("Maze Escape Game")

# 게임 오브젝트 초기화
player_size = 20
player_x = player_size
player_y = player_size
player_color = (255, 255, 0)

exit_size = 20
exit_x = screen_width - exit_size
exit_y = screen_height - exit_size
exit_color = (255, 0, 0)

wall_size = 20
wall_color = (0, 0, 255)
wall_list = []
for i in range(30):
    x = random.randint(0, screen_width // wall_size - 1) * wall_size
    y = random.randint(0, screen_height // wall_size - 1) * wall_size
    wall_list.append((x, y))

# 게임 루프
clock = pygame.time.Clock()
done = False
while not done:
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and (player_x - player_size, player_y) not in wall_list:
                player_x -= player_size
            elif event.key == pygame.K_RIGHT and (player_x + player_size, player_y) not in wall_list:
                player_x += player_size
            elif event.key == pygame.K_UP and (player_x, player_y - player_size) not in wall_list:
                player_y -= player_size
            elif event.key == pygame.K_DOWN and (player_x, player_y + player_size) not in wall_list:
                player_y += player_size
    
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
        player_x += player_size
    elif x_diff < -100:
        player_x -= player_size
    elif y_diff > 100:
        player_y += player_size
    elif y_diff < -100:
        player_y -= player_size
    
    # 게임 오브젝트 업데이트
    if (player_x, player_y) == (exit_x, exit_y):
        print("You Win!")
        done = True

    # 게임 오브젝트 그리기
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, player_color, (player_x, player_y, player_size, player_size))
    pygame.draw.rect(screen, exit_color, (exit_x, exit_y, exit_size, exit_size))
    for wall in wall_list:
        pygame.draw.rect(screen, wall_color, (wall[0], wall[1], wall_size, wall_size))

    # 게임 화면 업데이트
    pygame.display.flip()

    # 초당 프레임 설정
    clock.tick(10)
    
# 게임 종료시 LED 끄기
GPIO.output(21, GPIO.LOW)

# GPIO 설정 해제
GPIO.cleanup()
# MCP3008 연결 해제
spi.close()
    
# 게임 종료
pygame.quit()

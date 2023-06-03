import pygame # 1. pygame 선언
import random
from datetime import datetime
from datetime import timedelta
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
    
pygame.init() # 2. pygame 초기화
 
# 3. pygame에 사용되는 전역변수 선언
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
size = [400,400]
screen = pygame.display.set_mode(size)
 
done= False
clock= pygame.time.Clock()
last_moved_time = datetime.now()
 
KEY_DIRECTION = {
    pygame.K_UP: 'N',
    pygame.K_DOWN: 'S',
    pygame.K_LEFT: 'W',
    pygame.K_RIGHT: 'E',
}
 
def draw_block(screen, color, position):
    block = pygame.Rect((position[1] * 20, position[0] * 20),
                        (20, 20))
    pygame.draw.rect(screen, color, block)
 
class Snake:
    def __init__(self):
        self.positions = [(0,2),(0,1),(0,0)]  # 뱀의 위치
        self.direction = ''
 
    def draw(self):
        for position in self.positions: 
            draw_block(screen, GREEN, position)
 
    def move(self):
        head_position = self.positions[0]
        y, x = head_position
        if self.direction == 'N':
            self.positions = [(y - 1, x)] + self.positions[:-1]
        elif self.direction == 'S':
            self.positions = [(y + 1, x)] + self.positions[:-1]
        elif self.direction == 'W':
            self.positions = [(y, x - 1)] + self.positions[:-1]
        elif self.direction == 'E':
            self.positions = [(y, x + 1)] + self.positions[:-1]
 
    def grow(self):
        tail_position = self.positions[-1]
        y, x = tail_position
        if self.direction == 'N':
            self.positions.append((y - 1, x))
        elif self.direction == 'S':
            self.positions.append((y + 1, x))
        elif self.direction == 'W':
            self.positions.append((y, x - 1))
        elif self.direction == 'C':
            self.positions.append((y, x + 1))    
 
 
class Apple:
    def __init__(self, position=(5, 5)):
        self.position = position
 
    def draw(self):
        draw_block(screen, RED, self.position)

def runGame():
    global done, last_moved_time, x_initial, y_initial
    #게임 시작 시, 뱀과 사과를 초기화
    snake = Snake() 
    apple = Apple()
            
    while not done:
        clock.tick(10)
        screen.fill(WHITE)
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done=True
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_DIRECTION:
                    snake.direction = KEY_DIRECTION[event.key]

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
            snake.direction = 'E'
        elif x_diff < -100:
            snake.direction = 'W'
        elif y_diff > 100:
            snake.direction = 'S'
        elif y_diff < -100:
            snake.direction = 'N'
        
        if timedelta(seconds=0.1) <= datetime.now() - last_moved_time:
            snake.move()
            last_moved_time = datetime.now()
 
        if snake.positions[0] == apple.position:
            snake.grow()    
            apple.position = (random.randint(0, 19), random.randint(0, 19))
        
        if snake.positions[0] in snake.positions[1:]:
            done = True
 
 
        snake.draw()
        apple.draw()
        pygame.display.update()
            
    # 게임 종료시 LED 끄기
    GPIO.output(21, GPIO.LOW)

    # GPIO 설정 해제
    GPIO.cleanup()
    # MCP3008 연결 해제
    spi.close()
    
runGame()
pygame.quit()

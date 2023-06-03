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


# 게임화면 크기 설정
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

# 색깔 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# 캐릭터 클래스 정의
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 50])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()

    def update(self):
        # 사용자의 입력에 따라 캐릭터를 이동
             # 조이스틱 값 읽어들이기
        x_diff, y_diff = read_joystick()
        if x_diff > 100:
            self.rect.x += 5
        elif x_diff < -100:
            self.rect.x -= 5
        elif y_diff > 100:
            self.rect.y += 5
        elif y_diff < -100:
            self.rect.y -= 5

        # 화면 밖으로 나가는 것을 방지
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > SCREEN_WIDTH - 50:
            self.rect.x = SCREEN_WIDTH - 50
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > SCREEN_HEIGHT - 50:
            self.rect.y = SCREEN_HEIGHT - 50

# 장애물 클래스 정의
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([30, 30])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()

        # 장애물의 초기 위치 설정
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -self.rect.height)

    def update(self):
        # 장애물을 아래로 이동시킴
        self.rect.y += 5

        # 장애물이 화면 밖으로 나가면 재생성
        if self.rect.y > SCREEN_HEIGHT:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -self.rect.height)

# Pygame 초기화
pygame.init()

# 게임 화면 생성
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

# 게임 타이틀 설정
pygame.display.set_caption("Avoid the Obstacles")

# 캐릭터와 장애물 그룹 생성
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
obstacles = pygame.sprite.Group()

# 게임 루프
clock = pygame.time.Clock()
running = True
while running:
    # 이벤트 처리
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
 #   x_diff, y_diff = read_joystick()
  #  if x_diff > 100:
   #     self.rect.x -= 5
    #elif x_diff < -100:
     #   self.rect.x += 5
    #elif y_diff > 100:
    #    self.rect.y -= 5
    #elif y_diff < -100:
     #   self.rect.y += 5
    
    # 새로운 장애물 생성
    if len(obstacles) < 10 and random.randrange(100) < 3:
        obstacle = Obstacle()
        obstacles.add(obstacle)
        all_sprites.add(obstacle)

    # 화면 업데이트
    all_sprites.update()
    screen.fill(BLACK)
    all_sprites.draw(screen)
    pygame.display.flip()

    # 충돌 체크
    if pygame.sprite.spritecollide(player, obstacles, False):
        running = False

    # 프레임 수 설정
    clock.tick(60)
# 게임 종료시 LED 끄기
GPIO.output(21, GPIO.LOW)

# GPIO 설정 해제
GPIO.cleanup()
# MCP3008 연결 해제
spi.close()
# 게임 종료
pygame.quit()

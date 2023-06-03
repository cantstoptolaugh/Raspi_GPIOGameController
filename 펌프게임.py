import pygame
import random
from pygame.rect import *
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
 
#pygame 초기화
pygame.init()
pygame.display.set_caption("codingnow.co.kr")

##yellow,red 오류로 pygame.Color객체를 사용하기 위해 추가함.
YELLOW = pygame.Color('yellow')
RED = pygame.Color('red')
#======== 함수 ===============================
#키 이벤트 처리하기
def resultProcess(direction):
    global isColl, score, DrawResult, result_ticks

    if isColl and CollDirection.direction == direction:
        score += 10
        CollDirection.y = -1
        DrawResult = 1
    else:
        DrawResult = 2
    result_ticks = pygame.time.get_ticks()

def eventProcess():
    global isActive, score, chance
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                GPIO.output(21, GPIO.LOW)
                isActive = False
            if chance > 0:
                if event.key == pygame.K_UP:  # 0
                    resultProcess(0)
                if event.key == pygame.K_LEFT:  # 1
                    resultProcess(1)
                if event.key == pygame.K_DOWN:  # 2
                    resultProcess(2)
                if event.key == pygame.K_RIGHT:  # 3
                    resultProcess(3)
            else:
                if event.key == pygame.K_SPACE:
                    score = 0
                    chance = chance_MAX
                    for direc in Directions:
                        direc.y = -1
    
    for i, pin in enumerate(button_pins):
        # 버튼의 현재 입력 상태
        input_state = GPIO.input(pin)
        # 버튼 입력 상태가 변경되면 출력
        if input_state != previous_input[i]:
            previous_input[0] = input_state
            if input_state == GPIO.HIGH:
                GPIO.output(21, GPIO.LOW)
                isActive = False 
                    
         # 조이스틱 값 읽어들이기
    x_diff, y_diff = read_joystick()
    if x_diff > 100:
        resultProcess(3)
    elif x_diff < -100:
        resultProcess(1)
    elif y_diff > 100:
        resultProcess(2)
    elif y_diff < -100:
        resultProcess(0)
    
                        
###################################################################################
#방향 아이콘 클래스
class Direction(object):
    def __init__(self):
        self.pos = None
        self.direction = 0
        self.image = pygame.image.load("direction.bmp")
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rotated_image = pygame.transform.rotate(self.image, 0)
        self.y = -1
        self.x = int(SCREEN_WIDTH*0.75)-(self.image.get_width()/2)

    def rotate(self, direction=0):
        self.direction = direction
        self.rotated_image = pygame.transform.rotate(
            self.image, 90*self.direction)

    def draw(self):
        if self.y >= SCREEN_HEIGHT:
            self.y = -1
            return True
        elif self.y == -1:
            return False
        else:
            self.y += 1
            self.pos = screen.blit(self.rotated_image, (self.x, self.y))
            return False
###################################################################################
#방향 아이콘 생성과 그리기
def drawIcon():
    global start_ticks,chance

    if chance <= 0:
        return

    elapsed_time = (pygame.time.get_ticks() - start_ticks)
    if elapsed_time > 400:
        start_ticks = pygame.time.get_ticks()
        for direc in Directions:
            if direc.y == -1:
                direc.y = 0
                direc.rotate(direction=random.randint(0, 3))
                break

    for direc in Directions:
        if direc.draw():            
            chance -= 1
###################################################################################
#타겟 영역 그리기와 충돌 확인하기
def draw_targetArea():
    global isColl, CollDirection
    isColl = False
    for direc in Directions:
        if direc.y == -1:
            continue
        if direc.pos.colliderect(targetArea):
            isColl = True
            CollDirection = direc
            pygame.draw.rect(screen, (255, 0, 0), targetArea)
            break
    pygame.draw.rect(screen, (0, 255, 0), targetArea, 5)
###################################################################################
#문자 넣기
def setText():
    global score, chance
    mFont = pygame.font.SysFont("굴림", 40)

    mtext = mFont.render(f'score : {score}', True, YELLOW)
    screen.blit(mtext, (10, 10, 0, 0))

    mtext = mFont.render(f'chance : {chance}', True, YELLOW)
    screen.blit(mtext, (10, 42, 0, 0))

    if chance <= 0:
        mFont = pygame.font.SysFont("굴림", 90)
        mtext = mFont.render(f'Game over!!', True, RED)
        tRec = mtext.get_rect()
        tRec.centerx = SCREEN_WIDTH/2
        tRec.centery = SCREEN_HEIGHT/2 - 40
        screen.blit(mtext, tRec)
###################################################################################
#결과 이모티콘 그리기
def drawResult():
    global DrawResult, result_ticks
    if result_ticks > 0:
        elapsed_time = (pygame.time.get_ticks() - result_ticks)
        if elapsed_time > 400:
            result_ticks = 0
            DrawResult = 0
    screen.blit(resultImg[DrawResult], resultImgRec)
###################################################################################
#========= 변수 =================================
isActive = True
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
chance_MAX = 30
score = 0
chance = chance_MAX
isColl = False
CollDirection = 0
DrawResult, result_ticks = 0,0
start_ticks = pygame.time.get_ticks()

clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

#방향 아이콘
Directions = [Direction() for i in range(0, 5)]
#타겟 박스
targetArea = Rect(SCREEN_WIDTH/2, 400, SCREEN_WIDTH/2, 80)
#결과 이모티콘
resultFileNames = ["normal.bmp", "good.bmp", "bad.bmp"]
resultImg = []
for i, name in enumerate(resultFileNames):
    resultImg.append(pygame.image.load(name))
    resultImg[i] = pygame.transform.scale(resultImg[i], (150, 75))

resultImgRec = resultImg[0].get_rect()
resultImgRec.centerx = SCREEN_WIDTH/2 - resultImgRec.width/2 - 40
resultImgRec.centery = targetArea.centery

#========= 반복문 ===============================
while(isActive):
    screen.fill((0, 0, 0))
    eventProcess()
    # Directions[0].y = 100
    # Directions[0].rotate(1)
    # Directions[0].draw()
    draw_targetArea()
    drawIcon()
    setText()
    drawResult()
    pygame.display.update()
    clock.tick(400)

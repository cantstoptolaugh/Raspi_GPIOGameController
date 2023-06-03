import pygame
from pygame.locals import *
import random
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

pygame.init()
pygame.display.set_caption("codingnow.co.kr")

WHITE = pygame.Color('white')
###################################################################################
def eventProcess():
    global isClick, isActive
    for event in pygame.event.get():
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)\
                or event.type == QUIT:
            GPIO.output(21, GPIO.LOW)
            isActive = False
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
            if isClick == 0:
                isClick = 1
    for i, pin in enumerate(button_pins):
            # 버튼의 현재 입력 상태
            input_state = GPIO.input(pin)
            # 버튼 입력 상태가 변경되면 출력
            if input_state != previous_input[i]:
                previous_input[0] = input_state
                if input_state == GPIO.HIGH:
                    if isClick == 0:
                        isClick = 1
                    
                    
            if input_state != previous_input[i]:
                previous_input[1] = input_state
                if input_state == GPIO.HIGH:
                    GPIO.output(21, GPIO.LOW)
                    isActive = False                          
###################################################################################
def clickProcess():
    global isClick, diceCurr, yCurr
    if isClick == 1:  # space bar & 위로 던질때
        yCurr -= 1
        if yCurr <= ThrowEndY:
            isClick = 2
    elif isClick == 2:  # 떨어질때
        yCurr += 1
        if yCurr >= ThrowStartY:  # 바닥에 내려왔을때
            isClick = 0
    else:  # 완료 및 아무것도 안할때
        setText()
        yCurr = ThrowStartY
        dices[diceCurr].rotate(angle=0)
    if isClick:  # 던져지고 있을때
        diceCurr = random.randint(0, len(dices)-1)
        dices[diceCurr].y = yCurr
        dices[diceCurr].rotate()
    dices[diceCurr].draw()
###################################################################################
def setText():
    mFont = pygame.font.SysFont("arial", 40)
    mtext = mFont.render(f'Press the A', True, WHITE)
    tRec = mtext.get_rect()
    tRec.centerx = SCREEN_WIDTH/2
    tRec.centery = tRec.height + 40
    screen.blit(mtext, tRec)
###################################################################################
class Dice():
    def __init__(self, idx, y):
        self.image = pygame.image.load(f"{idx}.bmp")
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.x = SCREEN_WIDTH/2-(self.image.get_width()/2)
        self.y = y
        self.angle = 0
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)

    def rotate(self, angle=None):
        if angle != None:
            self.angle = 0
        else:
            self.angle = random.randint(0, 360)
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)

    def draw(self):
        screen.blit(self.rotated_image, (self.x, self.y))
###################################################################################
isClick = False
isActive = True
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
ThrowStartY = SCREEN_HEIGHT - 150

ThrowEndY = 100
yCurr = SCREEN_HEIGHT/2
diceCurr = 0

clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

bg = pygame.image.load('bg.bmp')
bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

dices = [Dice(i, ThrowStartY) for i in range(1, 6+1)]

while(isActive):
    screen.fill((255, 255, 255))
    screen.blit(bg, (10, 0))
    eventProcess()
    clickProcess()
    pygame.display.update()
    clock.tick(200)

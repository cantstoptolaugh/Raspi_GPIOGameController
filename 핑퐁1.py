import pygame # 1. pygame 선언
import time
import spidev
import RPi.GPIO as GPIO

# 버튼과 연결된 GPIO 핀 번호를 리스트로 저장
button_pins = [25]

GPIO.setmode(GPIO.BCM) 
GPIO.setup(21, GPIO.OUT)
#GPIO.setup(25, GPIO.IN)
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
BLACK = (0, 0, 0)
size = [400, 300]
screen = pygame.display.set_mode(size)

done = False
clock = pygame.time.Clock()

# 4. pygame 무한루프
def runGame():
    global done

    ## 게임판 크기
    screen_width = size[0]
    screen_height = size[1]

    ## 탁구채 크기 (width, height)
    bar_width = 9
    bar_height = 50

    ## 탁구채의 시작점 (x,y), 좌측 맨끝 중앙
    bar_x = bar_start_x = 0
    bar_y = bar_start_y = (screen_height - bar_height) / 2

    ## 탁구공 크기 (반지름)
    circle_radius = 9
    circle_diameter = circle_radius * 2

    ## 탁구공 시작점 (x, y), 우측 맨끝 중앙
    circle_x = circle_start_x =  screen_width - circle_diameter ## 원의 지름 만큼 빼기
    circle_y = circle_start_y =  (screen_width - circle_diameter) / 2

    bar_move = 0
    speed_x, speed_y, speed_bar = -screen_width / 1.28, screen_height / 1.92, screen_height * 1.2

    while not done:
        time_passed = clock.tick(30)
        time_sec = time_passed / 1000.0
        screen.fill(BLACK)

        circle_x += speed_x * time_sec
        circle_y += speed_y * time_sec
        ai_speed = speed_bar * time_sec 
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  
                done = True
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    bar_move = -ai_speed
                elif event.key == pygame.K_DOWN:
                    bar_move = ai_speed
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    bar_move = 0
                elif event.key == pygame.K_DOWN:
                    bar_move = 0
        
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
            bar_move = ai_speed
        elif x_diff < -100:
            bar_move = -ai_speed
        else:
            bar_move = 0
                
        if y_diff > 100:
            bar_move = -ai_speed
        elif y_diff < -100:
            bar_move = ai_speed
        else:
            bar_move = 0

        ## 탁구채 이동
        bar_y += bar_move
    
        ## 탁구채 범위 확인
        if bar_y >= screen_height:
            bar_y = screen_height
        elif bar_y <= 0:
            bar_y = 0

        ## 탁구공 범위 확인 
        ## 1) 진행 방향을 바꾸는 행위
        ## 2) 게임이 종료되는 행위
        if circle_x < bar_width: ## bar에 닿았을 때
            if circle_y >= bar_y - circle_radius and circle_y <= bar_y + bar_height + circle_radius:
                circle_x = bar_width
                speed_x = -speed_x
        if circle_x < -circle_radius: ## bar에 닿지 않고 좌측 벽면에 닿았을 때, 게임 종료 및 초기화
            circle_x, circle_y = circle_start_x, circle_start_y
            bar_x, bar_y = bar_start_x, bar_start_y
        elif circle_x > screen_width - circle_diameter: ## 우측 벽면에 닿았을 때
            speed_x = -speed_x
        if circle_y <= 0: ## 위측 벽면에 닿았을때
            speed_y = -speed_y
            circle_y = 0
        elif circle_y >= screen_height - circle_diameter: ## 아래 벽면에 닿았을때
            speed_y = -speed_y
            circle_y = screen_height - circle_diameter

        ## 탁구채
        pygame.draw.rect(screen, 
                         WHITE, 
                        (bar_x, bar_y, int(bar_width), int(bar_height)))
        ## 탁구공
        pygame.draw.circle(screen, 
                            WHITE, 
                            (int(circle_x), int(circle_y)), 
                            int(circle_radius))
    
        pygame.display.update()
                # 게임 종료시 LED 끄기
    GPIO.output(21, GPIO.LOW)

    # GPIO 설정 해제
    GPIO.cleanup()
    # MCP3008 연결 해제
    spi.close()
    
runGame()
pygame.quit()

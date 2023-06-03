import subprocess
import sys
import sqlite3
import pygame
from PyQt5.QtWidgets import QListWidget, QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QDialog, QVBoxLayout
from PyQt5.QtWidgets import QDialog, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# 데이터베이스 연결
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# 로그인 버튼 클릭 시 실행되는 함수


def check_duplicate_user(cursor, username):
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user:
        return True
    else:
        return False


def add_user(cursor, username, password):
    user = cursor.fetchone()
    if check_duplicate_user(cursor, username):
        return True
    else:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return False


def check_user(cursor, username, password):
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    if user:
        return username
    else:
        return password


def login():
    # 아이디와 비밀번호를 가져와서 처리하는 로직을 작성
    username = edit_username.text()
    password = edit_password.text()

    # 사용자 확인
    result = check_user(cursor, username, password)

    # 데이터베이스 연결 해제

    if result:
        # 로그인 성공
        QMessageBox.information(login_window, '로그인 성공', '로그인에 성공하였습니다.')
    else:
        # 로그인 실패
        QMessageBox.warning(login_window, '로그인 실패', '아이디 또는 비밀번호가 일치하지 않습니다.')

# 회원가입 창 열기 버튼 클릭 시 실행되는 함수


def open_signup():
    signup_window.show()

# 회원가입 버튼 클릭 시 실행되는 함수


def signup():
    # 아이디와 비밀번호를 가져와서 처리하는 로직을 작성
    username = edit_username.text()
    password = edit_password.text()

    # 사용자 확인
    result = check_duplicate_user(cursor, username)

    if result:
        # 회원가입 성공
        add_user(cursor, username, password)
        QMessageBox.information(signup_window, '회원가입 성공', '회원가입 성공하였습니다.')

    else:
        # 회원가입 실패
        QMessageBox.information(signup_window, '회원가입 실패', '회원가입 실패하였습니다.')

# 회원가입 창 열기 버튼 클릭 시 실행되는 함수


def open_signup():
    signup_window.show()


def open_main():
    main_window.show()
    username = edit_username


# GUI 설정
app = QApplication(sys.argv)

# 윈도우 생성
login_window = QWidget()
login_window.setWindowTitle('로그인')

# 이미지 불러오기
pixmap = QPixmap('background.png')  # 이미지 파일 경로

# QLabel에 이미지 설정
label = QLabel(login_window)
label.setPixmap(pixmap)

# QLabel에 이미지가 윈도우에 꽉 차도록 조정
label.setScaledContents(True)

# 윈도우 크기 설정
window_width = 900
window_height = 650
login_window.setGeometry(0, 0, window_width, window_height)

# 수직 레이아웃 생성
layout = QVBoxLayout(login_window)

# 윈도우를 화면의 정중앙으로 이동
screen_width = app.desktop().screen().width()
screen_height = app.desktop().screen().height()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
login_window.move(x, y)

# 이미지 불러오기
pixmap = QPixmap('background.png')  # 이미지 파일 경로

# QLabel에 이미지 설정
label = QLabel(login_window)
label.setPixmap(pixmap)

# QLabel에 이미지가 윈도우에 꽉 차도록 조정
label.setScaledContents(True)

# 배경 이미지의 크기를 윈도우 크기에 맞게 조정
label.setGeometry(0, 0, login_window.width(), login_window.height())

# 창의 플래그 설정 (프레임 제거)
login_window.setWindowFlags(Qt.FramelessWindowHint)

# 아이디 입력 칸
label_username = QLabel("아이디:", login_window)
label_username.setGeometry(350, 355, 50, 20)
edit_username = QLineEdit(login_window)
edit_username.setGeometry(350, 380, 200, 30)

# 비밀번호 입력 칸
label_password = QLabel("비밀번호:", login_window)
label_password.setGeometry(350, 415, 50, 20)
edit_password = QLineEdit(login_window)
edit_password.setEchoMode(QLineEdit.Password)  # 입력한 비밀번호를 가려줌
edit_password.setGeometry(350, 440, 200, 30)

# 로그인 버튼
login_button = QPushButton('로그인', login_window)
login_button.setGeometry(350, 480, 100, 50)
login_button.clicked.connect(open_main)

# 회원가입 버튼
signup_button = QPushButton('회원가입', login_window)
signup_button.setGeometry(450, 480, 100, 50)
signup_button.clicked.connect(open_signup)

# 회원가입 창 불러오기
signup_window = QWidget()
signup_window.setWindowTitle('회원가입')

# 윈도우 크기 설정
swindow_width = 450
swindow_height = 250
signup_window.setGeometry(0, 0, swindow_width, swindow_height)

signup_window.setWindowFlags(Qt.FramelessWindowHint)

# 이미지 불러오기
pixmap = QPixmap('background2.png')  # 이미지 파일 경로

# QLabel에 이미지 설정
label = QLabel(signup_window)
label.setPixmap(pixmap)

# QLabel에 이미지가 윈도우에 꽉 차도록 조정
label.setScaledContents(True)

# 배경 이미지의 크기를 윈도우 크기에 맞게 조정
label.setGeometry(0, 0, signup_window.width(), signup_window.height())

# 윈도우를 화면의 정중앙으로 이동
screen_width = app.desktop().screen().width()
screen_height = app.desktop().screen().height()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
signup_window.move(x, y)

# 아이디 입력 칸
label_username = QLabel("회원가입할 아이디를 입력:", signup_window)
label_username.setGeometry(10, 80, 200, 30)
edit_username = QLineEdit(signup_window)
edit_username.setGeometry(220, 80, 200, 30)

# 비밀번호 입력 칸
label_password = QLabel("회원가입할 비밀번호를 입력:", signup_window)
label_password.setGeometry(10, 120, 200, 30)
edit_password = QLineEdit(signup_window)
edit_password.setGeometry(220, 120, 200, 30)

# 회원가입 버튼
signup_button = QPushButton('회원가입', signup_window)
signup_button.setGeometry(150, 180, 150, 40)
signup_button.clicked.connect(signup)

# MAIN 윈도우 ( 게임 실행 )
main_window = QWidget()

# 윈도우 크기 설정
main_window_width = 300
main_window_height = 450
main_window.setGeometry(0, 0, main_window_width, main_window_height)

# 윈도우를 화면의 정중앙으로 이동
screen_width = app.desktop().screen().width()
screen_height = app.desktop().screen().height()
x = (screen_width - main_window_width) // 2
y = (screen_height - main_window_height) // 2
main_window.move(x, y)

# 창의 플래그 설정 (프레임 제거)
main_window.setWindowFlags(Qt.FramelessWindowHint)


# 이미지 불러오기
pixmap = QPixmap('background2.png')  # 이미지 파일 경로

# QLabel에 이미지 설정
label = QLabel(main_window)
label.setPixmap(pixmap)

# QLabel에 이미지가 윈도우에 꽉 차도록 조정
label.setScaledContents(True)

# 배경 이미지의 크기를 윈도우 크기에 맞게 조정
label.setGeometry(0, 0, main_window.width(), main_window.height())

layout = QVBoxLayout(main_window)

# 종료 버튼
exit_button = QPushButton('X', main_window)
exit_button.setGeometry(250, 0, 45, 40)

# 종료 버튼 클릭 시 애플리케이션 종료
exit_button.clicked.connect(app.quit)

label = QLabel('선택할 파일을 선택하세요.', main_window)
layout.addWidget(label)

file_list_widget = QListWidget(main_window)
layout.addWidget(file_list_widget)

# 파일 리스트에 아이템 추가 (예시로 파일명을 리스트로 받아서 추가)
file_names = ['pacman.pyw','스네이크.py', '핑퐁1.py', '핑퐁2.py','핑퐁3.py','케이브.py', '슈팅게임1.py', '슈팅게임2.py', '폭탄피하기.py', '미로 탈출.py','가위바위보.py', '숫자 맞추기.py', '날아다니는 새.py','롤링다이스.py','펌프게임.py', '테트리스.py', '피하기게임1.py', '피하기게임2.py', '차 피하기.py']
for file_name in file_names:
    file_list_widget.addItem(file_name)


def open_selected_file():
    selected_item = file_list_widget.currentItem()
    if selected_item is not None:
        file_name = selected_item.text()
        # 선택된 파일 처리 코드 작성
        if file_name == "pacman.pyw":
            file_path = "pacman/pacman/pacman.pyw"
            subprocess.run(["python3", file_path])
        else:
            print(f'Selected file: {file_name}')
            subprocess.run(["python3", file_name])


button = QPushButton('파일 열기', main_window)
button.clicked.connect(open_selected_file)
layout.addWidget(button)

# 사용자 데이터와 플레이타임 출력
username_label = QLabel(main_window)
username_label.setText('아이디명: 이민우')
layout.addWidget(username_label)

# 회원가입 뒤로가기 버튼
sexit_button = QPushButton('X', signup_window)
sexit_button.setGeometry(400, 0, 50, 50)

# 회원가입 뒤로가기 버튼 클릭 시 애플리케이션 종료
sexit_button.clicked.connect(app.quit)

# 로그인 종료 버튼
exit_button = QPushButton('종료', login_window)
exit_button.setGeometry(800, 0, 100, 50)

# 로그인 종료 버튼 클릭 시 애플리케이션 종료
exit_button.clicked.connect(app.quit)

login_window.show()

sys.exit(app.exec_())

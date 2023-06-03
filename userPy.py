import sqlite3

# 0. SQLite 데이터베이스 생성
conn = sqlite3.connect('users.db')  # 데이터베이스 파일명 지정
cursor = conn.cursor()

# 1. 사용자 테이블 생성
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')


# 중복된 사용자명 체크 함수 추가
def check_duplicate_user(cursor, username):
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user:
        return True
    else:
        return False


# 3.사용자 데이터 추가 (회원가입)


def add_user(cursor, username, password):
    user = cursor.fetchone()
    if check_duplicate_user(cursor, username):
        return True
    else:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, password))
        conn.commit()
        return False


# 4. 사용자 데이터 확인 (로그인)


def check_user(cursor, username, password):
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    if user:
        return username
    else:
        return password

# 5. 모든 사용자 데이터 출력


def show_all_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for user in users:
        print(f"사용자명: {user[1]}, 비밀번호: {user[2]}")

# 6. 사용자 데이터 삭제


def delete_user(username):
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    print(f"사용자 {username}이(가) 삭제되었습니다.")

# 7. 사용자 데이터 수정


def update_user(username, password):
    cursor.execute(
        "UPDATE users SET password = ? WHERE username = ?", (password, username))
    conn.commit()
    print(f"사용자 {username}의 비밀번호가 변경되었습니다.")


# 사용자 전체 삭제
def delete_ALL():
    cursor.execute("DELETE FROM users")
    conn.commit()


# 8. 사용자 데이터 확인 (로그인)
add_user(cursor, "joohyeok2", "1234")
# show_all_users()
# print(check_user(cursor, "joohyeok3", 1234))
# print(check_duplicate_user(cursor, "joohyeok2"))
# check_user("joohyeok2", "1234")
# check_user("joohyeok1", "12345")

# update_user("joohyeok1", "4321")
show_all_users()
# 9. 데이터베이스 연결 닫기
conn.close()

#### 사전 환경 설정

```shell
# requirements.txt에 포함해놓긴 함
pip install scikit-learn
python manage.py shell
```

-> shell 명령어

```python
# message, chat 데이터 삭제하고 auto_increment 리셋
from django.db import connection

def reset_autoincrement():
    with connection.cursor() as cursor:
        # Reset the AUTO_INCREMENT for Message
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='chatgpt_message';")
        cursor.execute("DELETE FROM chatgpt_message;")

        # Reset the AUTO_INCREMENT for Chat
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='chatgpt_chat';")
        cursor.execute("DELETE FROM chatgpt_chat;")

# Call the function to reset the AUTO_INCREMENT fields
reset_autoincrement()

# 캐시용 데이터베이스 생성
import sqlite3

# 데이터베이스 연결 (기본 SQLite 사용)
conn = sqlite3.connect('chat_cache.db')
c = conn.cursor()

# 테이블 생성
c.execute('''
    CREATE TABLE IF NOT EXISTS chat_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT UNIQUE,
        answer TEXT
    )
''')

# 변경 사항 커밋
conn.commit()

# 연결 닫기
conn.close()
```



#### 현재 웹 동작 flow

**변경하고 싶으면 의견 말해주세요!!**

chatgpt 클릭 -> http://127.0.0.1:8000/chatgpt/chat_view/admin/8/ 이동

- chatgpt/chat_view/{str:user_id}/{int:chat_id}
  - 둘다 생략하고 접근 시 
    - user_id = 'admin'
    - chat_id = 모든 채팅중에 제일 최근 채팅방 id
  - chat_id만 생략하고 접근 시
    - user_id = user_id
    - chat_id = 해당 유저의 가장 최근 채팅방 id
- user_id = 'admin'
  - 모든 채팅창 열람 가능
  - 나머지 id들은 본인 채팅창만 열람 가능

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

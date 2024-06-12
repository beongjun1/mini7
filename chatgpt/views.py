from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django import forms
from django.urls import reverse
from django.utils import timezone


from chatgpt.models import Message,ChatRoom, Chat
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory , ChatMessageHistory 
from langchain.schema import Document
from langchain.cache import SQLiteCache
from datetime import timedelta

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache
import sqlite3

import pandas as pd
import json
import csv

from django.views.decorators.csrf import csrf_exempt


# Create your views here.

# Chroma 데이터베이스 초기화 - 사전에 database가 완성 되어 있다는 가정하에 진행 - aivleschool_qa.csv 내용이 저장된 상태임
embeddings = OpenAIEmbeddings(model = "text-embedding-ada-002")
database = Chroma(persist_directory = "./db", embedding_function = embeddings)
# SQLiteCache 설정
cache = SQLiteCache(database_path="chat_cache.db")

def chat_view(request, user_id = 'admin', chat_id = None):
    if user_id == 'admin':
        chats = Chat.objects.all().order_by('-timestamp')
    else:
        chats = Chat.objects.filter(user_id=user_id).order_by('-timestamp')
    # 처음 chat_id 없이 url 입력한 경우, 가장 최근 chat으로 리디렉션
    if chat_id is None:
        latest_chat = chats.first()
        if latest_chat:
            return HttpResponseRedirect(f'/chatgpt/chat_view/{user_id}/{latest_chat.id}/')
        else:
            # 만약 chat 데이터가 없다면 빈 페이지를 렌더링
            return render(request, 'gpt/result.html', {'chat_id': None, 'messages': [], 'chats': chats, 'user_id':user_id})
    
    chat = get_object_or_404(Chat, pk=chat_id)
    messages = Message.objects.filter(chat=chat).order_by('timestamp')
    return render(request, 'gpt/result.html', {'chat_id': chat_id, 'messages': messages, 'chats': chats, 'user_id':user_id})

def get_memory_from_messages(messages):
    memory = ConversationBufferMemory(memory_key="chat_history", input_key="question", output_key="answer", return_messages=True)
    for message in messages:
        if message.user == 'User':
            memory.chat_memory.add_message(HumanMessage(content=message.text))
        else:
            memory.chat_memory.add_message(AIMessage(content=message.text))
    return memory

# 유사성 계산 함수
def compute_similarity(query, questions):
    vectorizer = TfidfVectorizer().fit_transform([query] + questions)
    vectors = vectorizer.toarray()
    cosine_similarities = cosine_similarity([vectors[0]], vectors[1:])[0]
    return cosine_similarities

# 메모리 캐시 설정
@lru_cache(maxsize=100)
def get_cached_answer_memory(question):
    conn = sqlite3.connect('chat_cache.db')
    c = conn.cursor()

    # 모든 질문과 답변 가져오기
    c.execute("SELECT question, answer FROM chat_cache")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return None
    
    questions = [row[0] for row in rows]
    cosine_similarities = compute_similarity(question, questions)
    most_similar_index = cosine_similarities.argmax()

    if cosine_similarities[most_similar_index] > 0.8:  # 유사성 임계값 설정 (0.8)
        return rows[most_similar_index][1]
    
    return None

# SQLite 데이터베이스에 답변 캐시 저장
def cache_answer(question, answer):
    conn = sqlite3.connect('chat_cache.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO chat_cache (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()
    conn.close()


@csrf_exempt   # 기본적으로 미들웨어에서 CSRF에 대한 방어를 하기 때문에 403 에러를 마주할 수 있음. 이를 해제하기 위해 csrf_exempt 데코레이터를 이용.
def chat(request):
    if request.method == 'POST':    
        #post로 받은 question (index.html에서 name속성이 question인 input태그의 value값)을 가져옴
        human_message = request.POST.get('question')
        chat_id = request.POST.get('chat_id', None)
        user_id = request.POST.get('user_id', 'admin')

        if chat_id:
            chat = get_object_or_404(Chat, pk=chat_id)
            messages = Message.objects.filter(chat_id=chat_id, user_id=user_id).order_by('timestamp')
            memory = get_memory_from_messages(messages)
        else:
            chat = Chat.objects.create(thumbnail=human_message[:10], user_id=user_id)
            chat_id = chat.id
            memory = ConversationBufferMemory(memory_key="chat_history", input_key="question", output_key="answer", return_messages=True)
            messages = []
        memory.chat_memory.add_message(HumanMessage(content=human_message))
        # 입력 문자열을 정규화하여 공백, 대소문자 등을 통일
        # normalized_query = ' '.join(human_message.lower().strip().split())

        # 메모리 캐시에서 답변 가져오기
        cached_answer = get_cached_answer_memory(human_message)
        if cached_answer:
            print("Cache hit")
            ai_message = cached_answer
        else:
            print("Cache miss")
            # memory 확인 로그
            # print(memory.load_memory_variables({}))

            #chatgpt API 및 lang chain을 사용을 위한 선언
            chat_gpt = ChatOpenAI(model="gpt-3.5-turbo")
            k = 3
            retriever = database.as_retriever(search_kwargs={"k": k})
            qa = ConversationalRetrievalChain.from_llm(
                llm=chat_gpt, 
                retriever=retriever, 
                memory=memory, 
                return_source_documents=True, 
                output_key="answer"
            )
            result = qa(human_message)
            ai_message = result["answer"]

            # 봇 메시지 메모리에 추가
            memory.chat_memory.add_message(AIMessage(content=ai_message))
        
        # Message 데이터 추가
        Message.objects.create(user='User', text=human_message, chat=chat, user_id=user_id)
        Message.objects.create(user='Bot', text=ai_message, chat=chat, user_id=user_id)

        # 캐시에 답변 저장 (메모리 캐시와 SQLite 캐시 모두)
        cache_answer(human_message, ai_message)

        # 캐시 상태 확인
        # print(get_cached_answer_memory.cache_info())

        # 응답을 보여주기 위한 html 선택 (위에서 처리한 context를 함께 전달)
        return JsonResponse({'success': True, 'chat_id': chat.id, 'message': ai_message, 'user_id':user_id})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def add_chat_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('name')
        if room_name:
            new_room = ChatRoom.objects.create(name=room_name)
            return JsonResponse({'name': new_room.name, 'url': reverse('chatgpt:chat_view', args=[new_room.id])})
        return JsonResponse({'error': 'Room name is required'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def download(request):
    messages = Message.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="chat_history.csv"'
    response.write('\ufeff'.encode('utf8'))

    writer = csv.writer(response)
    writer.writerow(['User', 'Message', 'Timestamp'])
    for message in messages:
        writer.writerow([message.user, message.text, message.timestamp])

    return response

@csrf_exempt 
def session_out(request):
    if request.method == 'POST': 
        Message.objects.all().delete()
    return render(request, 'main.html')
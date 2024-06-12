import csv
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django import forms
from django.urls import reverse
from django.utils import timezone


from chatgpt.models import Message,ChatRoom
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory , ChatMessageHistory 
from langchain.schema import Document

import pandas as pd
import json
import csv

from django.views.decorators.csrf import csrf_exempt


# Create your views here.

# Chroma 데이터베이스 초기화 - 사전에 database가 완성 되어 있다는 가정하에 진행 - aivleschool_qa.csv 내용이 저장된 상태임
embeddings = OpenAIEmbeddings(model = "text-embedding-ada-002")
database = Chroma(persist_directory = "./db", embedding_function = embeddings)

# def index(request):
#     return render(request, 'gpt/index.html')




def chat_view(request):
    messages = Message.objects.all().order_by('timestamp')
    return render(request, 'gpt/result.html', {'messages': messages})


@csrf_exempt   # 기본적으로 미들웨어에서 CSRF에 대한 방어를 하기 때문에 403 에러를 마주할 수 있음. 이를 해제하기 위해 csrf_exempt 데코레이터를 이용.
def chat(request):
    if request.method == 'POST':    
        #post로 받은 question (index.html에서 name속성이 question인 input태그의 value값)을 가져옴
        user_message = request.POST.get('question')

        memory = ConversationBufferMemory(memory_key="chat_history", input_key="question", output_key="result", return_messages=True)
        chat = ChatOpenAI(model="gpt-3.5-turbo")
        k = 3
        retriever = database.as_retriever(search_kwargs={"k": k})
        qa = ConversationalRetrievalChain.from_llm(llm=chat, retriever=retriever, return_source_documents=True,memory=memory,output_key='result')

        result = qa(user_message)
        bot_message = result["result"]

        Message.objects.create(user='User', text=user_message)
        Message.objects.create(user='Bot', text=bot_message)

        return JsonResponse({'message': bot_message})

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
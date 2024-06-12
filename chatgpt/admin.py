from django.contrib import admin
from django.urls import path
from django import forms
from django.shortcuts import render, redirect
from .models import Message, EmbeddingFulltextSearchContent, QA
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from django.core.exceptions import ValidationError
from datetime import datetime

import logging
import csv
import pandas as pd

logger = logging.getLogger(__name__)
# Register your models here.

class Postmessage(admin.ModelAdmin):
    list_display = ['user','text','timestamp']
    list_filter = ['timestamp']
    search_fields=['timestamp']
    list_per_page = 15
    
    
admin.site.register(Message, Postmessage)

class Postfulltext(admin.ModelAdmin):
    list_display = ['id', 'c0', 'string_value']
    list_filter = ['string_value']
    
admin.site.register(EmbeddingFulltextSearchContent, Postfulltext)

# admin에 csv 업로드 후 vectordb로 변환 -> gpt의 입력으로 사용
class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()
    
def handle_uploaded_file(csv_file):
    # CSV 파일을 읽어들여 데이터프레임으로 변환
    df = pd.read_csv(csv_file, encoding='utf-8')

    # ChromaDB 설정
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    database = Chroma(persist_directory='./db', embedding_function=embeddings)

    # 기존 데이터 삭제
    pre_docs = database.get()
    for doc in pre_docs['ids']:
        database.delete(ids=doc)

    # 새로운 데이터 추가
    text_list = df['QA'].tolist()
    metadata = [{'category': df['구분'][i]} for i in range(len(df))]
    documents = [Document(page_content=text_list[i], metadata=metadata[i]) for i in range(len(text_list))]
    database.add_documents(documents)

    # Django 모델에 데이터 저장
    for _, row in df.iterrows():

        QA.objects.create(
            category=row['구분'],
            qa=row['QA']
        )
        
@admin.register(QA)
class NewDataAdmin(admin.ModelAdmin):
    change_list_template = "gpt/csv_upload.html"

    def get_urls(self):

        urls = super().get_urls()
        my_urls = [
            path('upload-csv/', self.upload_csv),
        ]
        return my_urls + urls

    def upload_csv(self, request):
        logger.info("upload_csv 뷰 함수 호출됨")
        if request.method == "POST":
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                logger.info("폼 유효성 검사 통과")
                csv_file = request.FILES['csv_file']
                handle_uploaded_file(csv_file)
                self.message_user(request, "CSV 파일이 업로드되고 데이터가 저장되었습니다.")
                return redirect("..")
            else:
                logger.error("폼 유효성 검사 실패")
        else:
            logger.info("GET 요청")
            form = CSVUploadForm()
        return render(request, "gpt/csv_form.html", {"form": form})
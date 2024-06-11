from django.contrib import admin
from django.urls import path
from .models import Message, EmbeddingFulltextSearchContent
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

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
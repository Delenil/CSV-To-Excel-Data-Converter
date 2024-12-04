from django.urls import path
from .views import upload_csv, character_list, export_to_excel

urlpatterns = [
    path('upload_csv/', upload_csv, name='upload_csv'),
    path('characters/', character_list, name='character_list'),
    path('export_to_excel/', export_to_excel, name='export_to_excel'),
]


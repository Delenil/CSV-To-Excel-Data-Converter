from django.urls import path
from .views import (
    upload_csv, character_list, export_to_excel,
    add_character, delete_character, register,
    user_login, user_logout, landing_page
)

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('upload_csv/', upload_csv, name='upload_csv'),
    path('characters/', character_list, name='character_list'),
    path('export_to_excel/', export_to_excel, name='export_to_excel'),
    path('add_character/', add_character, name='add_character'),
    path('delete_character/<int:character_id>/', delete_character, name='delete_character'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]



from django.contrib import admin
from .models import Client  # Импортируем модель Клиента

@admin.register(Client)  # Регистрируем модель
class ClientAdmin(admin.ModelAdmin):
    # Поля, которые будут отображаться в списке
    list_display = ('name', 'inn', 'company_phone', 'is_active')
    # Поля, по которым можно искать
    search_fields = ('name', 'inn')
    # Фильтры справа
    list_filter = ('is_active', 'created_at')
    # Разбивка на страницы
    list_per_page = 20
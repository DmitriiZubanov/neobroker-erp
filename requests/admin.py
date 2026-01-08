from django.contrib import admin
from .models import Request, Shipment  # Импортируем обе модели
from django.urls import reverse
from django.utils.html import format_html

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('request_number', 'request_date_display', 'client', 'transport_type', 'pdf_link', 'created_at')
    search_fields = ('client', 'consignor', 'tracking_number')
    list_filter = ('client', 'transport_type', 'created_at', ('request_date', admin.DateFieldListFilter))
    # Добавляем возможность быстрого поиска по клиенту прямо в списке
    autocomplete_fields = ['client']  # Теперь при создании/редактировании можно искать клиента
    change_form_template = 'admin/requests/request_change_form.html'
    list_per_page = 20

    # Добавляем метод для отображения только даты
    def request_date_display(self, obj):
        return obj.request_date.date()  # Преобразуем DateTime в только дату
    request_date_display.short_description = 'Дата заявки'  # Заголовок колонки
    request_date_display.admin_order_field = 'request_date'  # Позволяет сортировать по этому полю

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['pdf_url'] = reverse('request_pdf', args=[object_id])
        return super().change_view(request, object_id, form_url, extra_context)

    def pdf_link(self, obj):
        if obj.id:
            url = reverse('request_pdf', args=[obj.id])
            return format_html(
                '<a href="{}" class="button" target="_blank" style="'
                'background:#4CAF50;color:white;padding:5px 10px;'
                'text-decoration:none;border-radius:3px;">📄 PDF</a>', 
                url
            )
        return "-"
    pdf_link.short_description = 'Отчет'
    pdf_link.allow_tags = True

    # Добавляем действие для массовой генерации PDF
    actions = ['download_pdf_report']
    
    def download_pdf_report(self, request, queryset):
        if queryset.count() == 1:
            obj = queryset.first()
            url = reverse('request_pdf', args=[obj.id])
            from django.shortcuts import redirect
            return redirect(url)
        else:
            from django.contrib import messages
            messages.warning(request, "Выберите только одну заявку для генерации PDF.")
    download_pdf_report.short_description = "Сгенерировать PDF для выбранных заявок"

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('get_request_number', 'status', 'eta', 'delivery_date')
    list_filter = ('status', 'document_type')
    list_per_page = 20

    # Метод для отображения номера связанной заявки в списке
    def get_request_number(self, obj):
        return obj.request.request_number if obj.request.request_number else '—'
    get_request_number.short_description = 'Номер заявки'
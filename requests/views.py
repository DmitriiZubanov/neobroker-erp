from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
#from io import BytesIO #мой коммент
from .models import Request
import pdfkit
import os

def generate_pdf(template_src, context_dict):
    """Вспомогательная функция для создания PDF из HTML-шаблона"""
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    
    # Конвертируем HTML в PDF
    pdf = pisaDocument(
        src=BytesIO(html.encode("UTF-8")),
        dest=result,
        encoding='UTF-8'
    )

    if not pdf.err:
        return result.getvalue()
    return None

def request_pdf(request, pk):
    """Основной view для генерации PDF по заявке"""
    # Получаем объект заявки
    try:
        request_obj = Request.objects.get(pk=pk)
    except Request.DoesNotExist:
        return HttpResponse("Заявка не найдена", status=404)
    
    # Подготавливаем контекст для шаблона
    context = {
        'request': request_obj,
        'current_time': timezone.now(),
    }
    
    # Генерируем PDF
    pdf = generate_pdf('requests/request_pdf.html', context)
    
    if pdf:
        # Формируем ответ с PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f'Заявка_{request_obj.request_number}_{request_obj.request_date:%Y%m%d}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        return HttpResponse('Ошибка при создании PDF', status=500)
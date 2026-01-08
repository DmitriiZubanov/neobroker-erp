from django.db import models
# Пока НЕ импортируем Client, чтобы избежать циклических зависимостей
from clients.models import Client

class Request(models.Model):
    """
    Модель заявки на перевозку от клиента.
    Соответствует документу "1. Заявка.docx"
    """
    client = models.ForeignKey(
    Client,
    on_delete=models.CASCADE,
    verbose_name="Клиент",
    related_name='requests'
    )

    # ==== Основные номера и даты ====
    request_number = models.IntegerField(
        verbose_name="Номер заявки", 
        null=True, 
        blank=True,
        help_text="Автоматическая нумерация для этого клиента"
    )
    request_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания заявки")
    
    shipment_number = models.IntegerField(
        verbose_name="Номер поставки", 
        null=True, 
        blank=True,
        help_text="Общая нумерация поставок компании"
    )
    
    # ==== Транспорт и маршрут ====
    TRANSPORT_CHOICES = [
        ('air', 'Авиа'),
        ('sea', 'Море'),
        ('rail', 'Ж/Д'),
        ('auto', 'Авто'),
        ('multimodal', 'Мультимодальная'),
    ]
    
    transport_type = models.CharField(
        max_length=20, 
        choices=TRANSPORT_CHOICES, 
        verbose_name="Основной вид транспорта"
    )
    
    transport_at_border = models.CharField(
        max_length=20, 
        choices=TRANSPORT_CHOICES, 
        verbose_name="Вид транспорта на границе ЕАЭС",
        blank=True
    )
    
    # ==== Груз и отправитель ====
    consignor = models.TextField(verbose_name="Грузоотправитель")
    consignee = models.TextField(
        verbose_name="Грузополучатель", 
        blank=True,
        help_text="Если не указан, совпадает с клиентом"
    )
    
    country_of_origin = models.CharField(
        max_length=100, 
        verbose_name="Страна происхождения груза", 
        default="Китай"
    )
    
    # ==== Физические параметры груза ====
    gross_weight = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Вес брутто, кг.",
        null=True,
        blank=True
    )
    
    volume = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Объем, м³",
        null=True,
        blank=True
    )
    
    # ==== Финансы ====
    CURRENCY_CHOICES = [
        ('RUB', 'Рубли (RUB)'),
        ('USD', 'Доллары (USD)'),
        ('EUR', 'Евро (EUR)'),
        ('CNY', 'Юани (CNY)'),
    ]
    
    declared_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name="Объявленная стоимость",
        null=True,
        blank=True
    )
    
    currency = models.CharField(
        max_length=3, 
        choices=CURRENCY_CHOICES, 
        default='RUB',
        verbose_name="Валюта стоимости"
    )
    
    # ==== Дополнительная информация ====
    insurance_required = models.BooleanField(default=False, verbose_name="Требуется страхование")
    special_notes = models.TextField(verbose_name="Особые отметки", blank=True)
    
    # ==== Служебные поля ====
    manager = models.CharField(max_length=100, verbose_name="Ответственный менеджер", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def save(self, *args, **kwargs):
        """Автоматически присваивает номер заявки для конкретного клиента."""
        # Генерируем номер только при ПЕРВОМ сохранении новой заявки
        if not self.pk and not self.request_number:
            # Ищем последнюю заявку этого клиента
            last_request = Request.objects.filter(client=self.client).order_by('-request_number').first()
            # Присваиваем следующий номер
            self.request_number = (last_request.request_number + 1) if last_request else 1
        # Сохраняем объект стандартным способом
        super().save(*args, **kwargs)

    def __str__(self):
        client_name_for_display = self.client.name if self.client else 'Клиент не выбран'
        transport_display = self.get_transport_type_display()
        num = self.request_number or 'без номера'
        return f"Заявка #{num} - {client_name_for_display} ({transport_display})"
    
    class Meta:
        verbose_name = "Заявка на перевозку"
        verbose_name_plural = "Заявки на перевозку"
        ordering = ['-request_date']


class Shipment(models.Model):
    """
    Модель поставки (связана 1 к 1 с заявкой).
    Соответствует модулю "Финансист" и отслеживанию.
    """
    # Связь с заявкой
    request = models.OneToOneField(
        Request,
        on_delete=models.CASCADE,
        related_name='shipment',
        verbose_name="Заявка"
    )
    
    # ==== Статусы ====
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('processing', 'В обработке'),
        ('in_transit', 'В пути'),
        ('at_warehouse', 'На складе'),
        ('customs', 'Таможня'),
        ('delivered', 'Доставлено'),
        ('closed', 'Закрыто'),
        ('cancelled', 'Отменено'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Статус поставки"
    )
    
    # ==== Даты ====
    etd = models.DateField(verbose_name="ETD (План. отправления)", null=True, blank=True)
    eta = models.DateField(verbose_name="ETA (План. прибытия)", null=True, blank=True)
    actual_departure = models.DateField(verbose_name="Факт. отправления", null=True, blank=True)
    actual_arrival = models.DateField(verbose_name="Факт. прибытия", null=True, blank=True)
    delivery_date = models.DateField(verbose_name="Дата доставки клиенту", null=True, blank=True)
    
    # ==== Транспортные документы ====
    DOCUMENT_TYPES = [
        ('awb', 'Авианакладная (AWB)'),
        ('bl', 'Коносамент (BL)'),
        ('cargo_note', 'ЖД накладная'),
        ('cmr', 'Дорожная накладная (CMR)'),
        ('tir', 'Книжка МДП (TIR)'),
    ]
    
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        verbose_name="Тип транспортного документа",
        blank=True
    )
    
    document_number = models.CharField(
        max_length=100,
        verbose_name="Номер транспортного документа",
        blank=True
    )
    
    # ==== Дополнительная информация ====
    carrier = models.CharField(max_length=255, verbose_name="Перевозчик", blank=True)
    tracking_number = models.CharField(max_length=100, verbose_name="Трек-номер", blank=True)
    customs_declaration = models.CharField(max_length=100, verbose_name="№ ДТ/ГТД", blank=True)
    comments = models.TextField(verbose_name="Комментарии менеджера", blank=True)
    
    # ==== Служебные поля ====
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def __str__(self):
        return f"Поставка к заявке #{self.request.request_number}"
    
    class Meta:
        verbose_name = "Поставка"
        verbose_name_plural = "Поставки"
        ordering = ['-created_at']

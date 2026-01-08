from django.db import models

class Client(models.Model):
    """
    Модель для хранения информации о клиентах компании.
    Соответствует документу "Справочник клиентов".
    """
    # Основные реквизиты
    name = models.CharField(max_length=255, verbose_name="Наименование компании")
    inn = models.CharField(max_length=20, verbose_name="ИНН", blank=True)
    kpp = models.CharField(max_length=20, verbose_name="КПП", blank=True)
    ogrn = models.CharField(max_length=20, verbose_name="ОГРН", blank=True)
    legal_address = models.TextField(verbose_name="Юридический адрес", blank=True)
    
    # Контактная информация компании
    company_phone = models.CharField(max_length=50, verbose_name="Телефон организации", blank=True)
    company_email = models.EmailField(verbose_name="E-mail организации", blank=True)
    director = models.CharField(max_length=255, verbose_name="Руководитель", blank=True)
    
    # Банковские реквизиты
    bank_name = models.CharField(max_length=255, verbose_name="Банк", blank=True)
    bik = models.CharField(max_length=20, verbose_name="БИК", blank=True)
    correspondent_account = models.CharField(max_length=50, verbose_name="Корр. счёт", blank=True)
    payment_account = models.CharField(max_length=50, verbose_name="Расчётный счёт", blank=True)
    
    # Контактные лица (основное)
    contact_person1 = models.CharField(max_length=255, verbose_name="Контактное лицо 1", blank=True)
    contact_phone1 = models.CharField(max_length=50, verbose_name="Телефон 1", blank=True)
    contact_email1 = models.EmailField(verbose_name="E-mail 1", blank=True)
    
    # Контактные лица (дополнительное)
    contact_person2 = models.CharField(max_length=255, verbose_name="Контактное лицо 2", blank=True)
    contact_phone2 = models.CharField(max_length=50, verbose_name="Телефон 2", blank=True)
    contact_email2 = models.EmailField(verbose_name="E-mail 2", blank=True)
    
    # Служебные поля
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    def __str__(self):
        return f"{self.name} (ИНН: {self.inn})" if self.inn else self.name
    
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ['name']  # Сортировка по имени по умолчанию
        
from django.contrib import admin
from .models import UploadedFile, EquipmentData

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'uploaded_at')
    list_filter = ('uploaded_at',)

@admin.register(EquipmentData)
class EquipmentDataAdmin(admin.ModelAdmin):
    list_display = ('equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature')
    list_filter = ('equipment_type',)
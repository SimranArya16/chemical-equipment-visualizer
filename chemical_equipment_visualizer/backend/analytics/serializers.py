from rest_framework import serializers
from .models import UploadedFile, EquipmentData

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['id', 'file_name', 'uploaded_at']
        read_only_fields = ['uploaded_at']

class EquipmentDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentData
        fields = ['id', 'equipment_name', 'equipment_type', 
                 'flowrate', 'pressure', 'temperature']
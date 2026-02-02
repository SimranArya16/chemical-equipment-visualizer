from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')  # user field HATAO
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.file_name

class EquipmentData(models.Model):
    upload = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    equipment_name = models.CharField(max_length=200)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
    
    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"
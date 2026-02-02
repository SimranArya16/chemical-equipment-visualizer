import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from .models import UploadedFile, EquipmentData
from .serializers import UploadedFileSerializer

class FileUploadView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=400)
        
        file = request.FILES['file']
        
        try:
            df = pd.read_csv(file)
            df.columns = [str(col).strip() for col in df.columns]
            
            column_mapping = {}
            for col in df.columns:
                col_lower = col.lower()
                if 'equip' in col_lower and 'name' in col_lower:
                    column_mapping[col] = 'Equipment Name'
                elif 'type' in col_lower:
                    column_mapping[col] = 'Type'
                elif 'flow' in col_lower:
                    column_mapping[col] = 'Flowrate'
                elif 'press' in col_lower:
                    column_mapping[col] = 'Pressure'
                elif 'temp' in col_lower:
                    column_mapping[col] = 'Temperature'
            
            df.rename(columns=column_mapping, inplace=True)
            
            uploaded_file = UploadedFile.objects.create(
                file=file,
                file_name=file.name
            )
            
            equipment_data = []
            for _, row in df.iterrows():
                equipment_data.append(EquipmentData(
                    upload=uploaded_file,
                    equipment_name=str(row.get('Equipment Name', 'Unknown')),
                    equipment_type=str(row.get('Type', 'Unknown')),
                    flowrate=float(row.get('Flowrate', 0)),
                    pressure=float(row.get('Pressure', 0)),
                    temperature=float(row.get('Temperature', 0))
                ))
            
            EquipmentData.objects.bulk_create(equipment_data)
            
            UploadedFile.objects.exclude(
                id__in=UploadedFile.objects.all().order_by('-uploaded_at')[:5].values_list('id', flat=True)
            ).delete()
            
            summary = {
                'total_count': len(df),
                'avg_flowrate': float(df['Flowrate'].mean()) if 'Flowrate' in df.columns else 0,
                'avg_pressure': float(df['Pressure'].mean()) if 'Pressure' in df.columns else 0,
                'avg_temperature': float(df['Temperature'].mean()) if 'Temperature' in df.columns else 0,
                'type_distribution': df['Type'].value_counts().to_dict() if 'Type' in df.columns else {'Unknown': len(df)}
            }
            
            return Response({
                'message': 'File uploaded successfully',
                'summary': summary,
                'data': df.head(5).to_dict('records')
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class DataSummaryView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        upload_id = request.GET.get('upload_id')
        
        if upload_id:
            data = EquipmentData.objects.filter(upload_id=upload_id)
        else:
            data = EquipmentData.objects.all()
        
        if not data.exists():
            return Response({'error': 'No data found'}, status=404)
        
        df = pd.DataFrame(list(data.values()))
        
        summary = {
            'total_count': len(df),
            'avg_flowrate': float(df['flowrate'].mean()),
            'avg_pressure': float(df['pressure'].mean()),
            'avg_temperature': float(df['temperature'].mean()),
            'type_distribution': df['equipment_type'].value_counts().to_dict()
        }
        
        return Response(summary)

class UploadHistoryView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        uploads = UploadedFile.objects.all().order_by('-uploaded_at')[:5]
        serializer = UploadedFileSerializer(uploads, many=True)
        return Response(serializer.data)

class GeneratePDFView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Chemical Equipment Analysis Report")
        p.setFont("Helvetica", 12)
        p.drawString(100, 730, "Generated from Chemical Equipment Visualizer")
        p.line(100, 720, 500, 720)
        
        data = EquipmentData.objects.all()
        if data.exists():
            df = pd.DataFrame(list(data.values()))
            
            p.setFont("Helvetica-Bold", 14)
            p.drawString(100, 690, "Summary Statistics")
            p.setFont("Helvetica", 12)
            
            p.drawString(100, 670, f"Total Equipment: {len(df)}")
            p.drawString(100, 650, f"Average Flowrate: {df['flowrate'].mean():.2f}")
            p.drawString(100, 630, f"Average Pressure: {df['pressure'].mean():.2f}")
            p.drawString(100, 610, f"Average Temperature: {df['temperature'].mean():.2f}")
            
            p.setFont("Helvetica-Bold", 14)
            p.drawString(100, 580, "Equipment List:")
            p.setFont("Helvetica", 10)
            
            y = 560
            for i, item in enumerate(data[:15]):
                text = f"{i+1}. {item.equipment_name} ({item.equipment_type})"
                p.drawString(100, y, text)
                y -= 15
        else:
            p.drawString(100, 690, "No data available")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="equipment_report.pdf"'
        return response
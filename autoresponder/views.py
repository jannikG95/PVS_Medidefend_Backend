import csv
import threading
from io import StringIO

import pytesseract
from PIL import Image
from django.http import Http404
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Generated_Record
from .serializers import FileUploadSerializer, GeneratedRecordSerializer
from .services.analog_service import AnalogService
from .services.regular_service import RegularService

import logging


class ExtractText(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        operation_description="Upload an image file",
        request_body=FileUploadSerializer,
        responses={201: 'file uploaded successfully'},
    )
    def post(self, request):
        try:
            file_serializer = FileUploadSerializer(data=request.data)

            if file_serializer.is_valid():
                uploaded_file = request.FILES.get('file')
                if not uploaded_file.name.endswith(('.png', '.jpg', '.jpeg')):
                    return Response({'detail': 'Only image files (PNG, JPG) are allowed'},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Open the image file directly with PIL
                image = Image.open(uploaded_file)

                # Extract text
                text = pytesseract.image_to_string(image, lang='deu')

                # Clean text
                text = ' '.join(text.replace('\n', ' ').split())

                return Response({'extracted': text}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExtractRecordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Include title field',
                              default=False),
            openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Include status field',
                              default=False),
            openapi.Parameter('input', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Include input field',
                              default=False),
            openapi.Parameter('analog_input', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
                              description='Include analog_input field', default=False),
            openapi.Parameter('output', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Include output field',
                              default=False),
            openapi.Parameter('rating', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Include rating field',
                              default=False),
            openapi.Parameter('comment', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
                              description='Include comment field', default=False),
            openapi.Parameter('created_at', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
                              description='Include created_at field', default=False),
            openapi.Parameter('costs', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
                              description='Include costs field', default=False)
        ]
    )
    def get(self, request, *args, **kwargs):
        # Alle Records abrufen
        records = Generated_Record.objects.all()
        serializer = GeneratedRecordSerializer(records, many=True)

        # Alle Felder von den Records
        data = serializer.data

        # Boolean Parameter aus der Anfrage
        params = request.query_params

        # Filterung der Felder
        filtered_data = []
        for record in data:
            filtered_record = {}
            for field in record:
                if params.get(field, 'false').lower() == 'true':
                    filtered_record[field] = record[field]
            filtered_data.append(filtered_record)

        return self._create_csv_response(filtered_data)

    def _create_csv_response(self, data):
        # Sicherstellen, dass die Kommentar-Spalte immer vorhanden ist
        for record in data:
            if 'notes' not in record:
                record['notes'] = ''

        if not data:
            return HttpResponse("No data available", content_type='text/csv')

        # CSV im Speicher erstellen
        csv_buffer = StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

        # HTTP-Antwort mit CSV-Inhalt erstellen
        response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="generated_records.csv"'
        return response


class AnalyzeView(APIView):
    logger = logging.getLogger('AnalyzeView')

    permission_classes = [IsAuthenticated]
    """
    Diese View dient der Analyse von übergebenem Text mithilfe eines GPT-Modells.

    POST:
    Erwartet einen Text ('goz_text') im Request-Body und gibt eine durch das GPT-Modell generierte Antwort zurück.
    """

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Task title'),
                'answer': openapi.Schema(type=openapi.TYPE_STRING, description='Answer text to analyze'),
                'analog': openapi.Schema(type=openapi.TYPE_STRING, description='Analog answer text to analyze')
            }
        ),
        responses={200: openapi.Response(description="Response from GOZ analysis")}
    )
    def post(self, request, *args, **kwargs):
        """
        Bearbeitet POST-Anfragen und verwendet den GPTModelManager, um den übergebenen Text zu analysieren.

        :param request: Das Request-Objekt, das den zu analysierenden Text enthält.
        :return: Eine Response mit der Antwort des GPT-Modells.
        """

        title = request.data.get('title', '')
        input_string = request.data.get('answer', '')
        analog_string = request.data.get('analog', '')

        generated_record = Generated_Record.objects.create(title=title, input=input_string, status="10")

        request_thread = threading.Thread(target=self.analyze_async,
                                          args=(generated_record, input_string, analog_string))
        request_thread.start()

        records = Generated_Record.objects.all()
        serializer = GeneratedRecordSerializer(records, many=True)
        return Response(serializer.data)

    def analyze_async(self, generated_record, input_string, analog_string):
        self.logger.info('Analyzing case info')
        if analog_string:
            self.logger.info('Creating AnalogService instance')
            analog_service = AnalogService()
            analog_service.process_analog_case(generated_record, input_string, analog_string)
        else:
            self.logger.info('Creating RegularService instance')
            regular_service = RegularService()
            regular_service.process_regular_case(generated_record, input_string)


class RatingView(APIView):
    permission_classes = [IsAuthenticated]
    """
    Diese View dient dem Absenden einer Bewertung

    PUT:
    Erwartet ein GeneratedRecord und legt basierend darauf die Rating Werte in die Tabelle
    """

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Text to analyze')
            }
        ),
        responses={200: openapi.Response(description="Response from GOZ analysis")}
    )
    def put(self, request, *args, **kwargs):
        """
        Bearbeitet PUT-Anfragen um eine Bewertung entgegen zunehmen

        :param request: Das Request-Objekt, enthält das Record Objekt mit der Bewertung.
        :return: Eine Response mit dem Status Text.
        """

        record_data = request.data.get('record')

        if not record_data:
            return Response({"message": "No record provided"}, status=status.HTTP_400_BAD_REQUEST)

        record_id = record_data.get('id')

        if not record_id:
            return Response({"message": "No record ID provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            record = Generated_Record.objects.get(pk=record_id)
            record.input = record_data.get('title', record.title)
            record.input = record_data.get('status', record.status)
            record.input = record_data.get('input', record.input)
            record.output = record_data.get('output', record.output)
            record.rating = record_data.get('rating', record.rating)
            record.comment = record_data.get('comment', record.comment)
            record.created_at = record_data.get('created_at', record.created_at)
            record.save()

            return Response({"message": "Record updated successfully", "record": record_data},
                            status=status.HTTP_200_OK)
        except Generated_Record.DoesNotExist:
            return Response({"message": "Record not found"}, status=status.HTTP_404_NOT_FOUND)


class GeneratedRecordView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        record_id = kwargs.get('record_id')
        if record_id is not None:
            try:
                record = Generated_Record.objects.get(pk=record_id)
                serializer = GeneratedRecordSerializer(record)
            except Generated_Record.DoesNotExist:
                raise Http404
        else:
            records = Generated_Record.objects.all()
            serializer = GeneratedRecordSerializer(records, many=True)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        record_id = kwargs.get('record_id')
        if record_id is not None:
            try:
                record = Generated_Record.objects.get(pk=record_id)
                record.delete()
                return Response({"message": "Record deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            except Generated_Record.DoesNotExist:
                return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "No record_id provided in the request"}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        record_id = kwargs.get('record_id')
        if record_id is None:
            return Response({"error": "No record_id provided in the request"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            record = Generated_Record.objects.get(pk=record_id)
        except Generated_Record.DoesNotExist:
            return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)

        new_title = request.data.get('title')
        if new_title is None:
            return Response({"error": "New title not provided"}, status=status.HTTP_400_BAD_REQUEST)

        record.title = new_title
        record.save()

        serializer = GeneratedRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

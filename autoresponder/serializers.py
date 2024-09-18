from rest_framework import serializers
from .models import UploadedFile, Generated_Record
from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['file']

class GeneratedRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generated_Record
        fields = '__all__'
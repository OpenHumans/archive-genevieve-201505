from django.db import models

class UploadFile(models.Model):
    """Model for uploaded file and its processed output."""
    uploadfile = models.FileField(upload_to='uploads/%Y/%m/%d')
    processedfile = models.FileField(blank=True, upload_to='processed/%Y/%m/%d')

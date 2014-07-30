from django import forms
from django.conf import settings


class UploadForm(forms.Form):
    """File upload form."""
    uploadfile = forms.FileField(
        label='Select a file'
    )

    
    #Must be gzipped and under Max_Upload_Size
    def clean_uploadfile(self):
        content = self.cleaned_data['uploadfile']
        print "Content Size =",
        print content.size
        if content.size > int(settings.MAX_UPLOAD_SIZE):
            raise forms.ValidationError('Please keep filesize under max size')
        if not content.name.endswith('.gz'):
            raise forms.ValidationError('Please upload a file')
        return content
            
            
        
        

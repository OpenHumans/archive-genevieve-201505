from django import forms
from django.conf import settings


class UploadForm(forms.Form):
    """File upload form."""
    uploadfile = forms.FileField(
        label='Select a file'
    )
    reportname = forms.CharField()

    
    #Must be gzipped and under Max_Upload_Size
    def clean_uploadfile(self):
        content = self.cleaned_data['uploadfile']
        print "Content Size =",
        print content.size
        if content.size > int(settings.MAX_UPLOAD_SIZE):
            raise forms.ValidationError('Your file was too large.')
        if not content.name.endswith('.gz'):
            raise forms.ValidationError('Are you sure you uploaded a gzipped VCF file?')
        return content

    def file_name(self):
        report = self.cleaned_data['reportname']
        print report
        if not report:
            raise forms.ValidationError('Please name your file.')
            
            
        
        

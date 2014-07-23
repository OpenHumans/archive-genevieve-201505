from django import forms

class UploadForm(forms.Form):
    """File upload form."""
    uploadfile = forms.FileField(
        label='Select a file'
    )

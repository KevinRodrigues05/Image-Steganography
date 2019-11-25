from django import forms 




class UploadForm(forms.Form):    
    file = forms.FileField() # for creating file input
    file2 = forms.FileField()

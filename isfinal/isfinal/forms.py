from django import forms 




class UploadForm(forms.Form):    
    Cover_image = forms.FileField() # for creating file input
    Image_to_be_merged = forms.FileField()

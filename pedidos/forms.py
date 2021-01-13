from django import forms

class formGpedidos(forms.Form):

    from django.contrib.admin.widgets import AdminDateWidget
    from django.forms.fields import DateField

    usuario = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder': 'Usuario'}))
    albaran = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder': 'Albaran'}))
    fecha = forms.DateTimeField(required=False)
    #date = forms.DateTimeField( input_formats=['%d/%m/%Y %H:%M'],widget=forms.DateTimeInput(attrs={'class': 'form-control datetimepicker-input','data-target': '#datetimepicker_ini'}))
    #date = forms.SelectDateWidget()
    
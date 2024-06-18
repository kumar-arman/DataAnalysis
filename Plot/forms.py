from django import forms
from .models import UploadedFile

class ExcelUploadForm(forms.Form):
     file = forms.FileField()

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']

GRAPH_CHOICES = [
    ('line', 'Line Graph'),
    ('bar', 'Bar Graph'),
    ('pie', 'Pie Chart')
]

class TitleColumnForm(forms.Form):
    title_column = forms.ChoiceField(label='Filter Column')

    def __init__(self, *args, **kwargs):
        columns = kwargs.pop('columns', [])
        super().__init__(*args, **kwargs)
        self.fields['title_column'].choices = [(col, col) for col in columns]

class GraphForm(forms.Form):
    x_axis = forms.ChoiceField(label='X-axis')
    y_axis = forms.MultipleChoiceField(label='Y-axis', widget=forms.CheckboxSelectMultiple)
    graph_type = forms.ChoiceField(label='Graph type', choices=[('line', 'Line Graph'), ('bar', 'Bar Graph'), ('pie', 'Pie Graph')])
    #title_values = forms.MultipleChoiceField(label='Filter Value', widget=forms.CheckboxSelectMultiple)
    title_values =forms.ChoiceField(label='Filter Value')
    width = forms.IntegerField(label='Graph Width', initial=900)
    height = forms.IntegerField(label='Graph Height', initial=600)

    def __init__(self, *args, **kwargs):
        columns = kwargs.pop('columns', [])
        title_values_choices = kwargs.pop('title_values_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['x_axis'].choices = [(col, col) for col in columns]
        self.fields['y_axis'].choices = [(col, col) for col in columns]
        self.fields['title_values'].choices = title_values_choices

class GraphCSVForm(forms.Form):
    x_axis = forms.ChoiceField(label='X-axis')
    y_axis = forms.MultipleChoiceField(label='Y-axis', widget=forms.CheckboxSelectMultiple)
    graph_type = forms.ChoiceField(label='Graph type', choices=[('line', 'Line'), ('bar', 'Bar'), ('pie', 'Pie')])
    title_values = forms.MultipleChoiceField(label='Filter Value', widget=forms.CheckboxSelectMultiple)
    width = forms.IntegerField(label='Graph Width', initial=900)
    height = forms.IntegerField(label='Graph Height', initial=600)

    def __init__(self, *args, **kwargs):
        columns = kwargs.pop('columns', [])
        title_values_choices = kwargs.pop('title_values_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['x_axis'].choices = [(col, col) for col in columns]
        self.fields['y_axis'].choices = [(col, col) for col in columns]
        self.fields['title_values'].choices = title_values_choices
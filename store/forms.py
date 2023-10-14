from django import forms
from store.models import Improve
class ImproveForm(forms.ModelForm):
    class Meta:
        model = Improve
        fields = ('field1', )
    def clean(self):
        field1 = self.cleaned_data['field1']

from django.forms import ModelForm
from .models import SwarmNode


class SwarmNodeForm(ModelForm):
    class Meta:
        model = SwarmNode
        fields = '__all__'
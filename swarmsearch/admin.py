from django.contrib import admin

# Register your models here.
from .models import SwarmNode,Tag

admin.site.register(SwarmNode)


admin.site.register(Tag)

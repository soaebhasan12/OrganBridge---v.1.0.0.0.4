from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Organ)
admin.site.register(models.Post)
# admin.site.register(models.User)
admin.site.register(models.Donor)
admin.site.register(models.Recipient)
from django.contrib import admin
from database.users import models

# Register your models here.
admin.site.register(models.User)

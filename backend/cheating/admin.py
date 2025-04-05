"""Admin for cheating app."""

from django.contrib import admin
from cheating import models

admin.site.register(models.CheatingGroups)
admin.site.register(models.CheatingGroupMembers)
admin.site.register(models.ConfirmedCheaters)
admin.site.register(models.FlaggedStudents)
admin.site.register(models.LongitudinalCheatingGroupInstances)

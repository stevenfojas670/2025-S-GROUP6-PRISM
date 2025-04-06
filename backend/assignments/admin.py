"""Admin configuration for the assignments app."""

from django.contrib import admin
from assignments import models

admin.site.register(models.Assignments)
admin.site.register(models.Submissions)
admin.site.register(models.BaseFiles)
admin.site.register(models.BulkSubmissions)
admin.site.register(models.Constraints)
admin.site.register(models.PolicyViolations)
admin.site.register(models.RequiredSubmissionFiles)

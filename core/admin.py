from django.contrib import admin
from .models import Track, Project, TeamMember, ProjectEvaluation

admin.site.register(Track)
admin.site.register(Project)
admin.site.register(TeamMember)
admin.site.register(ProjectEvaluation)

# Register your models here.

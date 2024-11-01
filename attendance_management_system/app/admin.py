from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Attendance,User,Team
from.forms import UserForm


class AttendanceAdmin(admin.ModelAdmin):
    exclude = ['extra_hours','total_hours'] 

admin.site.register(Attendance, AttendanceAdmin)

# admin.site.register(User)
admin.site.register(User)
admin.site.register(Team)





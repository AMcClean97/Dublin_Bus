from django.contrib import admin
from .models import Stop, Route, Calendar, CalendarDate, Trip, StopTime
# Register your models here.
admin.site.register(Stop)
admin.site.register(Route)
admin.site.register(Calendar)
admin.site.register(CalendarDate)
admin.site.register(Trip)
admin.site.register(StopTime)
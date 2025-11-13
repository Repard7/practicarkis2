from django.contrib import admin

from .models import Request, AdvUser, Status, Category

admin.site.register(Request)
admin.site.register(AdvUser)
admin.site.register(Status)
admin.site.register(Category)

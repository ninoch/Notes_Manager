from django.contrib import admin

from MyApp.models import *

admin.site.register(Person)
admin.site.register(Note)
admin.site.register(NoteBook)
from django.db import models
from django.contrib.auth.models import User, AbstractUser

class Person(User):
    birthday = models.DateField(null=True)

class NoteBook(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(Person)

    def __str__(self):
        return str(self.title)

class Note(models.Model):
    title = models.CharField(max_length=100)
    body = models.CharField(max_length=500)
    book = models.ForeignKey(NoteBook)

    def __str__(self):
        return str(self.title)

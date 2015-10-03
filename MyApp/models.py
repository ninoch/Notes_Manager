from django.db import models
from django.contrib.auth.models import User, AbstractUser


class Person(User):
    birthday = models.DateField(null=True)
    active = models.BooleanField(default=False)


class NoteBook(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(Person)

    def __str__(self):
        return str(self.title)


class Activation(models.Model):
    user = models.ForeignKey(Person)
    link = models.CharField(max_length=20)


class Note(models.Model):
    title = models.CharField(max_length=100)
    body = models.CharField(max_length=500)
    book = models.ForeignKey(NoteBook)
    public = models.BooleanField(default=False)

    def __str__(self):
        return str(self.title)
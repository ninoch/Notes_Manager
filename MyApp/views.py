from MyApp.models import Note, NoteBook

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect

def show_note(request, note_id):
    note = Note.objects.get(id=note_id)
    return render(request, "Note.html", {
        'note': note
    })

def show_book(request, post_id):
    book = NoteBook.objects.get(id=post_id)
    notes = Note.objects.filter(book=book)
    return render(request, "NoteBook.html", {
        'notes': notes,
        'title': book.title,
        'name': book.owner.get_full_name()
    })

def show_edit(request, note_id):
    note = Note.objects.get(id=note_id)
    books = NoteBook.objects.all()
    return render(request, "Edit.html", {
        'note': note,
        'books': books
    })

def save_edit(note_id, book_id):
    note = Note.objects.get(id=note_id)
    book = NoteBook.objects.get(id=book_id)
    note.book = book
    note.save()

from django.template.response import TemplateResponse
from MyApp.models import Note, NoteBook
from .form import *

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
def show_home(request):
    username = request.user.username
    user = Person.objects.get(username=username)
    if request.method == "POST":
        title = request.POST['title']
        book = NoteBook()
        book.title = title
        book.owner = user
        book.save()
    books = NoteBook.objects.filter(owner=user)
    return render(request, "home.html", {
        'books': books,
        'user': user,
    })


@login_required(login_url='/login/')
def show_note(request, note_id):
    user = Person.objects.get(username=request.user.username)
    note = Note.objects.get(id=note_id)
    if note.public or user == note.book.owner:
        return render(request, "Note.html", {
            'note': note
        })
    else:
        return TemplateResponse(request, 'Alert.html', {})


@login_required(login_url='/login/')
def show_edit(request, note_id):
    user = Person.objects.get(username=request.user.username)
    note = Note.objects.get(id=note_id)
    if note.public or user == note.book.owner:
        if request.method == 'POST':
            note = Note.objects.get(id=note_id)
            old_book = note.book
            new_book = NoteBook.objects.get(id = request.POST['book'])
            is_public = False
            if 'public' in request.POST:
                is_public = True
            note.book = new_book
            note.public = is_public
            note.save()
            return redirect("/notebook/" + str(old_book.id) + "/")
        user = request.user
        note = Note.objects.get(id=note_id)
        print(note.public)
        books = NoteBook.objects.filter(owner = user)
        return render(request, "Edit.html", {
            'note': note,
            'books': books
        })
    else:
        return TemplateResponse(request, 'Alert.html', {})


@login_required(login_url='/login/')
def show_book(request, book_id):
    book = NoteBook.objects.get(id=book_id)
    if request.method == "POST":
        title = request.POST['title']
        body = request.POST['body']
        note = Note()
        note.body = body
        note.title = title
        note.book = book
        note.public = False
        note.save()
    notes = Note.objects.filter(book=book)
    return render(request, "NoteBook.html", {
        'notes': notes,
        'booktitle': book.title,
    })


def show_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=True)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            return redirect('/login/')
    else:
        form = SignupForm()
    return render(request, "Signup.html", {
        'form': form
    })


def show_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username = username, password = password)
            if user is not None:
                auth_login(request, user)
                return redirect('/home/')
            else:
                message = "Username or password is wrong"
        else:
            form = LoginForm()
    form = LoginForm()
    return render(request, "Login.html", {
        'form': form,
    })

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('/login/')
import string
from django.core.mail import send_mail
from django.template.response import TemplateResponse
from django.utils.crypto import random
from .form import *
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required

cacheUsers = {}
cacheNotes = {}
cacheBooks = {}


def save_user(user):
    cacheUsers[user.username] = user
    user.save()


def save_note(note):
    cacheNotes[note.id] = note
    note.save()


def save_book(book):
    cacheBooks[book.id] = book
    book.save()


def get_user(username):
    if username not in cacheUsers:
        cacheUsers[username] = Person.objects.get(username=username)
    print(cacheUsers[username].birthday)
    print(cacheUsers[username].active)
    print(cacheUsers[username].username)
    print(cacheUsers[username].first_name)
    return cacheUsers[username]


def get_book(bid):
    if bid not in cacheBooks:
        cacheBooks[bid] = NoteBook.objects.get(id=bid)
    return cacheBooks[bid]


def get_note(nid):
    if nid not in cacheNotes:
        cacheNotes[nid] = Note.objects.get(id=nid)
    return cacheNotes[nid]


@login_required(login_url='/login/')
def show_home(request):
    user = get_user(username=request.user.username)
    if request.method == "POST":
        title = request.POST['title']
        book = NoteBook()
        book.title = title
        book.owner = user
        save_book(book)
    books = NoteBook.objects.filter(owner=user)
    return render(request, "home.html", {
        'books': books,
        'user': user,
    })


@login_required(login_url='/login/')
def show_note(request, note_id):
    user = get_user(username=request.user.username)
    note = get_note(note_id)
    if note.public or user == note.book.owner:
        return render(request, "Note.html", {
            'note': note
        })
    else:
        return TemplateResponse(request, 'Alert.html', {})


@login_required(login_url='/login/')
def show_edit(request, note_id):
    user = get_user(username=request.user.username)
    note = get_note(note_id)
    if note.public or user == note.book.owner:
        if request.method == 'POST':
            note = get_note(note_id)
            old_book = note.book
            new_book = get_book(request.POST['book'])
            is_public = False
            if 'public' in request.POST:
                is_public = True
            note.book = new_book
            note.public = is_public
            save_note(note)
            return redirect("/notebook/" + str(old_book.id) + "/")
        user = request.user
        note = get_note(note_id)
        print(note.public)
        books = NoteBook.objects.filter(owner=user)
        return render(request, "Edit.html", {
            'note': note,
            'books': books
        })
    else:
        return TemplateResponse(request, 'Alert.html', {})


@login_required(login_url='/login/')
def show_book(request, book_id):
    book = get_book(book_id)
    if request.method == "POST":
        title = request.POST['title']
        body = request.POST['body']
        note = Note()
        note.body = body
        note.title = title
        note.book = book
        note.public = False
        save_note(note)
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
            new_user.active = False
            save_user(new_user)
            send_activation_link(new_user)
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
            user = authenticate(username=username, password=password)
            my_user = get_user(username=username)
            if my_user.active and user is not None:
                auth_login(request, user)
                return redirect('/home/')
    form = LoginForm()
    return render(request, "Login.html", {
        'form': form,
    })


@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('/login/')


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def send_activation_link(user):
    activation_link = id_generator(20)
    al = Activation(link=activation_link, user=user)
    al.save()

    url = "http://localhost:8000/activate/" + activation_link
    msg = "با سلام"
    msg += "\n"
    msg += "\n"
    msg += user.first_name + " " + user.last_name
    msg += "\n"
    msg += "از ثبت نام شما متشکریم. با کلیک بر روی لینک زیر می توانید حساب کاربری خود را فعال سازی کنید."
    msg += "\n"
    msg += "\n"
    msg += url

    subject = "فعال سازی حساب کاربری"
    sender = 'simorgh1393tahlil@gmail.com'
    recipients = [user.email]

    print(recipients[0])
    send_mail(subject, msg, sender, recipients)


def activate_account(request, activation_url):
    try:
        al = Activation.objects.get(link=activation_url)
        my_user = al.user
        my_user.active = True
        save_user(my_user)
        al.delete()
    except Activation.DoesNotExist:
        return render(request, "Alert.html", {})

    form = LoginForm()
    return redirect("/login/", {'form': form})

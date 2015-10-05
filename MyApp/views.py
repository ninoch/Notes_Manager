# coding=UTF8
import string
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.crypto import random
from .form import *
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
import django.utils.html as html

@login_required()
def show_home(request):
    print("*********** HOME ")
    user = Person.objects.get(username=request.user.username)
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


def make_cache(rendered, note):
    if note.public:
        return 'T-owner:' + note.book.owner.username + ' ' + rendered
    else:
        return 'F-owner:' + note.book.owner.username + ' ' + rendered


def get_html(cached):
    ind = 0
    while cached[ind] != ' ':
        ind += 1
    return cached[ind:]


def has_access(cached, user):
    if cached[0] == 'T':
        return True
    ind = 8
    owner = ''
    while cached[ind] != ' ':
        owner = owner + cached[ind]
        ind += 1
    print("------------- in has acccess: ----------")
    print(user + " =?= " + owner)
    if user == owner:
        return True
    return False


@login_required()
def show_note(request, note_id):
    print("************** NOTE")
    user = Person.objects.get(username=request.user.username)
    rendered_page = cache.get('note'+note_id)
    if not rendered_page:
        note = Note.objects.get(id=note_id)
        rendered_page = make_cache(render_to_string("Note.html", {'note': note}), note)

    cache.add('note'+note_id, rendered_page)
    if has_access(rendered_page, request.user.username):
        return HttpResponse(get_html(rendered_page))
    else:
        return TemplateResponse(request, "Alert.html", {})

@login_required()
def show_edit(request, note_id):
    user = Person.objects.get(username=request.user.username)
    note = Note.objects.get(id=note_id)
    if note.public or user == note.book.owner:
        if request.method == 'POST':
            note = Note.objects.get(id=note_id)
            old_book = note.book
            new_book = NoteBook.objects.get(id=request.POST['book'])
            is_public = False
            if 'public' in request.POST:
                is_public = True
            note.book = new_book
            note.public = is_public
            note.save()
            cache.delete('note'+note_id)
            return redirect("/notebook/" + str(old_book.id) + "/")
        user = request.user
        note = Note.objects.get(id=note_id)
        print(note.public)
        books = NoteBook.objects.filter(owner=user)
        return render(request, "Edit.html", {
            'note': note,
            'books': books
        })
    else:
        return TemplateResponse(request, 'Alert.html', {})


@login_required()
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
            new_user.active = False
            new_user.save()
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
            my_user = Person.objects.get(username=username)
            if my_user.active and user is not None:
                auth_login(request, user)
                return redirect('/home/')
    form = LoginForm()
    return render(request, "Login.html", {
        'form': form,
    })


@login_required()
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
    msg = render_to_string("Email.html", {'url': url, 'user': user})

    subject = "Account activation"
    sender = 'simorgh1393tahlil@gmail.com'
    recipients = [user.email]

    print(recipients[0])
    send_mail(subject, msg, sender, recipients)


def activate_account(request, activation_url):
    try:
        al = Activation.objects.get(link=activation_url)
        my_user = al.user
        my_user.active = True
        my_user.save()
        al.delete()
    except Activation.DoesNotExist:
        return render(request, "Alert.html", {})

    form = LoginForm()
    return redirect("/login/", {'form': form})

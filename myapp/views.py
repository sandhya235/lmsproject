from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import Group,User
from . import forms,models
from django.contrib.auth.forms import AuthenticationForm,PasswordResetForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from datetime import date
from django.contrib.auth.decorators import login_required
from .models import IssuedBook, Book, StudentExtra,User
from django.core.mail import send_mail
import random
from .forms import AdminSignupForm
from django.contrib.auth.views import PasswordResetView

# Create your views here.
def home_view(request):
    if request.user.is_authenticated:
        return render(request, 'index.html')
    return render(request, 'index.html')



def adminclick_view(request):
    return render(request, 'adminclick.html')



def studentclick_view(request):
    return render(request, 'studentclick.html')



def adminsignup_view(request):
    form = AdminSignupForm()
    if request.method == 'POST':
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.email = form.cleaned_data['email']
            user.save()
            Group.objects.get_or_create(name='ADMIN')[0].user_set.add(user)
            return redirect('adminlogin')
    return render(request, 'adminsignup.html', {'form': form})



def adminlogin_view(request):
    form = AuthenticationForm(request, data=request.POST) if request.method == 'POST' else AuthenticationForm()
    if request.method == 'POST' and form.is_valid():
        user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user:
            login(request, user)
            return redirect('adminafterlogin')
    return render(request, 'adminlogin.html', {'form': form})



def admin_after_login_view(request):
    if request.user.groups.filter(name='ADMIN').exists():
        return render(request, 'adminafterlogin.html')
    else:
        return redirect('adminlogin')



def student_after_login_view(request):
    if request.user.groups.filter(name='STUDENT').exists():
        return render(request, 'studentafterlogin.html')  
    else:
        return redirect('studentlogin')




def studentsignup_view(request):
    form1 = forms.StudentUserForm()
    form2 = forms.StudentExtraForm()

    if request.method == 'POST':
        form1 = forms.StudentUserForm(request.POST)
        form2 = forms.StudentExtraForm(request.POST)
        
        if form1.is_valid() and form2.is_valid():
            try:
                # Create user and save it with hashed password
                user = form1.save(commit=False)
                user.set_password(form1.cleaned_data['password1'])  # Hash password
                user.save()

                # Create student extra data
                extra = form2.save(commit=False)
                extra.user = user  # Link user to extra data
                extra.save()

                # Assign user to 'STUDENT' group
                student_group, created = Group.objects.get_or_create(name='STUDENT')
                student_group.user_set.add(user)

                messages.success(request, "Signup successful! You can now log in.")
                return redirect('studentlogin')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            # Display form errors
            messages.error(request, "Please correct the errors below.")
            print("Form1 Errors:", form1.errors)  # Debugging output
            print("Form2 Errors:", form2.errors)  # Debugging output

    return render(request, 'studentsignup.html', {'form1': form1, 'form2': form2})



def studentlogin_view(request):
    form = AuthenticationForm(request, data=request.POST) if request.method == 'POST' else AuthenticationForm()
    
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('studentafterlogin')  # Redirect only if login is successful
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'studentlogin.html', {'form': form})





def addbook_view(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name='ADMIN').exists():
        return redirect('adminlogin')

    form = forms.BookForm()
    if request.method == 'POST':
        form = forms.BookForm(request.POST)
        if form.is_valid():
            form.save()
        return render(request, 'bookadded.html')
    return render(request, 'addbook.html', {'form': form})




def viewbook_view(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name='ADMIN').exists():
        return redirect('adminlogin')

    books = models.Book.objects.all()
    return render(request, 'viewbook.html', {'books': books})



@login_required(login_url='adminlogin')
def issuebook_view(request):
    form = forms.IssuedBookForm()
    
    if request.method == 'POST':
        form = forms.IssuedBookForm(request.POST)
        if form.is_valid():
            obj = models.IssuedBook()
            obj.enrollment = request.POST.get('enrollment2')

            # Fetch the selected book details using ISBN
            selected_book = models.Book.objects.get(isbn=request.POST.get('isbn2'))
            
            obj.isbn = selected_book.isbn
            obj.book_name = selected_book.name  # Store book name
            obj.author = selected_book.author  # Store author
            obj.branch = request.POST.get('branch')  # Get branch if applicable
            
            obj.save()
            return render(request, 'bookissued.html')
    
    return render(request, 'issuebook.html', {'form': form})



@login_required(login_url='adminlogin')
def viewissuedbook_view(request):
    issuedbooks = models.IssuedBook.objects.all()
    issued_books_list = []

    for ib in issuedbooks:
        issdate = f"{ib.issuedate.day}-{ib.issuedate.month}-{ib.issuedate.year}"
        expdate = f"{ib.expirydate.day}-{ib.expirydate.month}-{ib.expirydate.year}"

        # Fine calculation
        days = (date.today() - ib.issuedate).days
        fine = max(0, (days - 15) * 10) if days > 15 else 0

        book = models.Book.objects.filter(isbn=ib.isbn).first()
        student = models.StudentExtra.objects.filter(enrollment=ib.enrollment).first()

        if book and student:
            issued_books_list.append((
                student.get_name, student.enrollment, book.name, book.author, issdate, expdate, fine, ib.id
            ))

    return render(request, 'viewissuedbook.html', {'li': issued_books_list})


@login_required
def delete_issued_book_view(request, issued_book_id):
    if request.user.groups.filter(name='ADMIN').exists():
        issued_book = get_object_or_404(models.IssuedBook, id=issued_book_id)
        issued_book.delete()
    return redirect('viewissuedbook')


def viewstudent_view(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name='ADMIN').exists():
        return redirect('adminlogin')

    students = models.StudentExtra.objects.all()
    return render(request, 'viewstudent.html', {'students': students})



def logout_view(request):
    return render(request, 'logout.html')


def logoutstudent_view(request):
    return render(request, 'logoutstudent.html')



@login_required(login_url='studentlogin')
def viewissuedbookbystudent(request):
    student = models.StudentExtra.objects.filter(user_id=request.user.id).first()

    if student is None:
        return render(request, 'viewissuedbookbystudent.html', {'error': 'No student record found'})

    issuedbook = models.IssuedBook.objects.filter(enrollment=student.enrollment)

    li1 = []
    li2 = []

    for ib in issuedbook:
        books = models.Book.objects.filter(isbn=ib.isbn)
        for book in books:
            t = (request.user, student.enrollment, student.branch, book.name, book.author)
            li1.append(t)

        issdate = f"{ib.issuedate.day}-{ib.issuedate.month}-{ib.issuedate.year}"
        expdate = f"{ib.expirydate.day}-{ib.expirydate.month}-{ib.expirydate.year}"

        # Fine calculation
        days = (date.today() - ib.issuedate).days
        fine = max((days - 15) * 10, 0) if days > 15 else 0

        t = (issdate, expdate, fine)
        li2.append(t)

    return render(request, 'viewissuedbookbystudent.html', {'li1': li1, 'li2': li2})



def success_page(request):
    return render(request, 'success-page.html')


@login_required
def deletebook_view(request, book_id):
    if request.user.groups.filter(name='ADMIN').exists():
        book = get_object_or_404(Book, id=book_id)
        print(f"Deleting book: {book.name} (ID: {book.id})")  # Debug log
        book.delete()
        print("Book deleted successfully!")  # Confirm deletion
    else:
        print("User does not have permission to delete books!")
    return redirect('viewbook')


@login_required
def delete_student_view(request, student_id):
    if request.user.groups.filter(name='ADMIN').exists():
        student = get_object_or_404(StudentExtra, id=student_id)
        student.delete()
    return redirect('viewstudent')



def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            users = User.objects.filter(email=email)
            
            if users.exists():
                for user in users:
                    form.save(
                        request=request,
                        use_https=True,
                        from_email="your_email@example.com",
                        email_template_name="registration/password_reset_email.html",
                    )
            
            return redirect("password_reset_done")
    else:
        form = PasswordResetForm()
    
    return render(request, "registration/password_reset_form.html", {"form": form})




class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data['email']
        
        # Prevent multiple reset emails for the same session
        if not self.request.session.get('reset_email_sent'):
            self.request.session['reset_email_sent'] = True
            messages.success(self.request, "A password reset email has been sent!")
            return super().form_valid(form)
        else:
            messages.warning(self.request, "Reset email already sent. Please check your inbox.")
            return self.form_invalid(form)


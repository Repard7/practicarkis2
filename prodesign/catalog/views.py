import os
from tkinter.font import names

from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, RequestCreationForm, RequestEditForm, CategoryCreationForm

from catalog.models import Request, AdvUser, Category, Status

def index_view(request): #get Главная страничка с 4 выполненными заявками пользователя
    try:
        in_work_status = Status.objects.get(name="In_work")
        requests_in_work_count = Request.objects.filter(status=in_work_status).count()
        done_status = Status.objects.get(name="Done")
        latest_completed_request_list = Request.objects.filter(
            status=done_status
        ).order_by('-pub_date')[:4]

    except Status.DoesNotExist:
        latest_completed_request_list = Request.objects.none()
        requests_in_work_count = 0

    return render(request, 'catalog/index.html', {'latest_completed_request_list': latest_completed_request_list, 'requests_in_work_count': requests_in_work_count})

@login_required
def profile_view(request):
    return render(request, 'catalog/profile.html')

@login_required
def user_request_list_view(request): #get Страница со всеми заявками пользователя
    request_user_list = Request.objects.filter(user=request.user)
    return render(request, 'catalog/user_request_list.html', {'request_list':request_user_list})

@login_required
def admin_panel_include_all_requests_view(request): #get Страница со всеми заявками всех пользователей
    all_request_list = Request.objects.all()
    return render(request, 'catalog/admin_panel.html', {'all_request_list':all_request_list})

def register_view(request): #get post Страница с формой регистрации
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)


            user.set_password(form.cleaned_data['password1'])
            user.save()


            if form.cleaned_data.get('is_moderator'):
                permission = Permission.objects.get(codename='moderator_access')
                user.user_permissions.add(permission)

            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'catalog/register.html', {'form': form})

def login_view(request): #get post Страница с формой входа
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        return render(request, 'catalog/login.html', {'error': 'Неверное имя пользователя или пароль'})
    return render(request, 'catalog/login.html')

@login_required
def logout_view(request): #post
    logout(request)
    return redirect('index')

@login_required
def creating_request_view(request): #get post Страница с формой создания заявки
    if request.method == 'POST':
        form = RequestCreationForm(request.POST, request.FILES)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.user = request.user
            request_obj.status = Status.objects.get(name="New")
            request_obj.save()
            return redirect('user_requests')
    else:
        form = RequestCreationForm()

    return render(request, 'catalog/create_request.html', {
        'form': form,
        'list_categories': Category.objects.all()
    })


@login_required
@permission_required('catalog.moderator_access')
def category_view(request):

    if request.method == 'POST':
        category_name = request.POST.get('category')

        if category_name:
            Category.objects.create(name=category_name)
            return redirect('category')

    list_categories = Category.objects.all()
    return render(request, 'catalog/category.html', {
        'list_categories': list_categories
    })

@login_required
def deleting_category_view(request, pk): #post страница с подтверждением удаления заявки
    category_to_delete = get_object_or_404(Category, pk=pk)
    category_to_delete.delete()
    return redirect('category')

@login_required
def deleting_request_view(request, pk): #post страница с подтверждением удаления заявки
    request_to_delete = get_object_or_404(Request, pk=pk)
    request_to_delete.delete()
    return redirect('user_requests')

@login_required
@permission_required('catalog.moderator_access')
def edit_request_view(request, pk):
    changeable_request = get_object_or_404(Request, pk=pk)
    list_categories = Category.objects.all()

    if request.method == 'POST':

        if 'edit_category' in request.POST:
            category_id = request.POST.get('category')
            changeable_request.category = Category.objects.get(id=category_id)
            changeable_request.save()
            return redirect('admin_panel')

        elif 'edit_status_new' in request.POST or 'edit_status_in_work' in request.POST:
            worker_comment = request.POST.get('worker_comment')
            completed_image = request.FILES.get('completed_image')

            if completed_image:
                try:
                    validate_image_file(completed_image)
                except ValidationError as e:
                    return render(request, 'catalog/edit_request.html', {
                        'changeable_request': changeable_request,
                        'list_categories': list_categories,
                        'error': str(e)
                    })

            if 'edit_status_new' in request.POST:
                changeable_request.status = Status.objects.get(name="In_work")
            elif 'edit_status_in_work' in request.POST:
                changeable_request.status = Status.objects.get(name="Done")

            changeable_request.worker_comment = worker_comment
            if completed_image:
                changeable_request.completed_image = completed_image

            changeable_request.save()
            return redirect('admin_panel')

    return render(request, 'catalog/edit_request.html', {
        'changeable_request': changeable_request,
        'list_categories': list_categories
    })

def validate_image_file(file):
    max_size = 2 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError("Размер файла не должен превышать 2MB")

    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError("Недопустимый формат файла. Разрешены: JPG, JPEG, PNG, BMP")

from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView
from django.views import View
from django.views.generic import CreateView
from .forms import ParentUserRegistrationForm, UserEditForm, ChildUserForm, AppointmentForm
from django.contrib.auth.views import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import ParentUser, ChildUser, Menu, Group, Announcement, GalleryMedia, GalleryCategory, Appointment
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import translation

class UserRegisterView(View):
    def get_template_names(self):
        current_language = self.request.session.get("language", "ru")
        translation.activate(current_language)

        if current_language == "uz":
            return ["uz/user/register.html"]
        return ["user/register.html"]

    def get(self, request):
        form = ParentUserRegistrationForm()
        template_name = self.get_template_names()[0]
        return render(request, template_name, {'form': form})

    def post(self, request):
        current_language = self.request.session.get("language", "ru")
        form = ParentUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            user.send_confirmation_email()
            if current_language == "uz":
                messages.success(request, 'Ro‘yxatdan o‘tish muvaffaqiyatli amalga oshdi. Iltimos, elektron pochta manzilingizni tasdiqlang.')
            else:
                messages.success(request, 'Регистрация прошла успешно. Пожалуйста, подтвердите свою электронную почту.')

            return redirect('index')

        template_name = self.get_template_names()[0]
        return render(request, template_name, {'form': form})

class UserLoginView(LoginView):
    form_class = AuthenticationForm

    def get_template_names(self):
        current_language = self.request.session.get("language", "ru")
        translation.activate(current_language)

        if current_language == "uz":
            return ["uz/user/login.html"]
        return ["user/login.html"]

    def form_valid(self, form):
        current_language = self.request.session.get("language", "ru")
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            if user.email_confirmed:
                login(self.request, user, backend='core.backends.EmailBackend')
            else:
                if current_language == "uz":
                    messages.error(self.request, 'Iltimos, elektron pochta manzilingizni tasdiqlang!')
                else:
                    messages.error(self.request, 'Подтвердите почту!')
                return redirect('resend_confirmation_email')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('index')

def confirm_email(request, token):
    current_language = request.session.get("language", "ru")
    translation.activate(current_language)

    try:
        user = ParentUser.objects.get(confirmation_token=token)
        token_lifetime = timedelta(hours=24)

        if timezone.now() > user.token_created_at + token_lifetime:
            if current_language == "uz":
                messages.error(request, 'Token muddati o‘tdi. Yangi token so‘rang.')
            else:
                messages.error(request, 'Срок действия токена истек. Пожалуйста, запросите новый токен.')
        elif user.email_confirmed:
            if current_language == "uz":
                messages.success(request, 'Email allaqachon tasdiqlangan.')
            else:
                messages.success(request, 'Email уже подтвержден.')
        else:
            user.email_confirmed = True
            user.is_active = True
            user.confirmation_token = ''
            user.token_created_at = None
            user.save()

            if current_language == "uz":
                messages.success(request, 'Email muvaffaqiyatli tasdiqlandi.')
            else:
                messages.success(request, 'Email успешно подтвержден.')
    except ParentUser.DoesNotExist:
        if current_language == "uz":
            messages.error(request, 'Noto‘g‘ri tasdiqlash tokeni.')
        else:
            messages.error(request, 'Недействительный токен подтверждения.')

    return redirect('index')


def resend_confirmation_email(request):
    current_language = request.session.get("language", "ru")
    translation.activate(current_language)

    if current_language == "uz":
        template_name = "uz/user/resend_confirmation_email.html"
    else:
        template_name = "user/resend_confirmation_email.html"

    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = ParentUser.objects.get(email=email)
            if user.email_confirmed:
                if current_language == "uz":
                    messages.success(request, 'Sizning elektron pochta manzilingiz allaqachon tasdiqlangan.')
                else:
                    messages.success(request, 'Ваш адрес электронной почты уже подтвержден.')
            else:
                user.resend_confirmation_email()
                if current_language == "uz":
                    messages.success(request, 'Yangi tasdiqlash xati sizning elektron pochta manzilingizga yuborildi.')
                else:
                    messages.success(request, 'Новое письмо с подтверждением отправлено на вашу электронную почту.')
        except ParentUser.DoesNotExist:
            if current_language == "uz":
                messages.error(request, 'Bunday elektron pochta manzili bilan foydalanuvchi topilmadi.')
            else:
                messages.error(request, 'Пользователь с таким адресом электронной почты не найден.')

        return redirect('resend_confirmation_email')

    return render(request, template_name)


def request_password_reset(request):
    current_language = request.session.get("language", "ru")
    translation.activate(current_language)

    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = ParentUser.objects.get(email=email)
            user.send_password_reset_email()
            if current_language == 'uz':
                messages.success(request, 'Parolni tiklash havolasi elektron pochta manzilingizga yuborildi.')
            else:
                messages.success(request, 'Ссылка для сброса пароля отправлена на вашу почту.')
            return redirect('request_password_reset')
        except ParentUser.DoesNotExist:
            if current_language == 'uz':
                messages.error(request, 'Bunday elektron pochta manzili bilan foydalanuvchi topilmadi.')
            else:
                messages.error(request, 'Пользователь с такой почтой не найден.')

    if current_language == 'uz':
        template_name = 'uz/user/request_password_reset.html'
    else:
        template_name = 'user/request_password_reset.html'

    return render(request, template_name)

def reset_password(request, token):
    current_language = request.session.get("language", "ru")
    translation.activate(current_language)

    user = ParentUser.validate_password_reset_token(token)
    if user is None:
        if current_language == 'uz':
            messages.error(request, 'Parolni tiklash havolasi noto‘g‘ri yoki uning amal qilish muddati o‘tgani.')
        else:
            messages.error(request, 'Ссылка для сброса пароля недействительна или истек срок ее действия.')
        return redirect('index')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            if current_language == 'uz':
                messages.error(request, 'Parollar mos kelmayapti.')
            else:
                messages.error(request, 'Пароли не совпадают.')
        else:
            user.reset_password(new_password)
            if current_language == 'uz':
                messages.success(request, 'Parol muvaffaqiyatli o‘zgartirildi.')
            else:
                messages.success(request, 'Пароль успешно изменен.')
            return redirect('index')

    if current_language == 'uz':
        template_name = 'uz/user/reset_password.html'
    else:
        template_name = 'user/reset_password.html'

    return render(request, template_name, {'token': token})

def custom_logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def profile_view(request, user_id):
    current_language = request.session.get("language", "ru")
    translation.activate(current_language)

    user = get_object_or_404(ParentUser, id=user_id)

    if request.user.id != user.id:
        can_edit = False
        edit_form = None
        child_form = None
    else:
        can_edit = True
        if request.method == 'POST':
            edit_form = UserEditForm(request.POST, request.FILES, instance=user)
            if edit_form.is_valid():
                edit_form.save()
                return redirect('profile', user_id=user.id)
        else:
            edit_form = UserEditForm(instance=user)

        if 'add_child' in request.POST:
            current_language = request.session.get("language", "ru")
            child_form = ChildUserForm(request.POST)
            if child_form.is_valid():
                new_child = child_form.save(commit=False)
                new_child.save()
                new_child.parents.add(user)
                new_child.save()
                if current_language == 'uz':
                    messages.success(request, "Bolangiz muvaffaqiyatli qo'shildi!")
                else:
                    messages.success(request, "Ребенок успешно добавлен!")

                return redirect('profile', user_id=user.id)
        else:
            child_form = ChildUserForm()

    children = user.children.all()

    user_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'mobile': user.mobile,
        'address': user.address,
        'email': user.email,
        'image': user.image.url if user.image else 'https://st3.depositphotos.com/15648834/17930/v/600/depositphotos_179308454-stock-illustration-unknown-person-silhouette-glasses-profile.jpg',
    }

    template_name = "uz/user/profile.html" if current_language == "uz" else "user/profile.html"

    context = {
        'user_data': user_data,
        'edit_form': edit_form,
        'can_edit': can_edit,
        'profile_user': user,
        'child_form': child_form,
        'children': children,
    }

    return render(request, template_name, context)

def index(request):
    current_language = request.session.get("language", "ru")
    translation.activate(current_language)

    if current_language == 'uz':
        template_name = 'uz/index.html'
    else:
        template_name = 'index.html'

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = AppointmentForm()

    return render(request, template_name, {'form': form})

def about_us(request):
    current_language = request.session.get("language", "ru")
    translation.activate(current_language)

    if current_language == 'uz':
        template_name = 'uz/about.html'
    else:
        template_name = 'about.html'

    return render(request, template_name)

def classes(request):
    current_language = request.session.get("language", "ru")
    translation.activate(current_language)

    if current_language == 'uz':
        template_name = 'uz/classes.html'
    else:
        template_name = 'classes.html'

    return render(request, template_name)

def menu_list(request):
    menus = Menu.objects.all()

    current_language = request.session.get("language", "ru")
    translation.activate(current_language)

    if current_language == 'uz':
        template_name = 'uz/menu.html'
    else:
        template_name = 'menu.html'

    return render(request, template_name, {'menus': menus})

def contact(request):
    current_language = request.session.get("language", "ru")
    translation.activate(current_language)

    if current_language == 'uz':
        template_name = 'uz/contact.html'
    else:
        template_name = 'contact.html'

    return render(request, template_name)

def schedule(request):
    current_language = request.session.get("language", "ru")
    translation.activate(current_language)

    if current_language == 'uz':
        template_name = 'uz/schedule.html'
    else:
        template_name = 'schedule.html'
    return render(request, template_name)

def view_404(request):
    return render(request, '404.html')

def gallery(request):
    current_language = request.session.get("language", "ru")
    translation.activate(current_language)

    if current_language == 'uz':
        template_name = 'uz/gallery.html'
    else:
        template_name = 'gallery.html'

    categories = GalleryCategory.objects.all()
    media_filter = request.GET.get('media_type', 'all')

    if media_filter == 'image':
        media = GalleryMedia.objects.filter(media_type='image')
    elif media_filter == 'video':
        media = GalleryMedia.objects.filter(media_type='video')
    else:
        media = GalleryMedia.objects.all()

    category_filter = request.GET.get('category')
    if category_filter:
        media = media.filter(category__id=category_filter)

    return render(request, template_name, {
        'categories': categories,
        'media': media,
        'selected_category': int(category_filter) if category_filter else None,
    })

def custom_404(request):
    return render(request, '404.html', status=404)

def set_language(request, lang):
    request.session["language"] = lang
    return redirect(request.META.get("HTTP_REFERER", "/"))

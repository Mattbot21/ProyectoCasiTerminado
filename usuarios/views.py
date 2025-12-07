from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import RegistroUsuarioForm, RegistroAdminForm
from .models import Usuario
from biblioteca.models import Reseña, Favorito, Lista, Historial
from moderacion.models import Reporte


# -------------------------------
# Registro de usuario normal
# -------------------------------
def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'usuarios/registro.html', {'form': form})


# -------------------------------
# Login
# -------------------------------
def login_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect('homeGeneral')
        else:
            error = "Credenciales inválidas"
            return render(request, 'usuarios/login.html', {'error': error})
    return render(request, 'usuarios/login.html')


# -------------------------------
# Logout
# -------------------------------
def logout_usuario(request):
    logout(request)
    return redirect('login')


# -------------------------------
# Perfil
# -------------------------------
@login_required
def perfil_usuario(request):
    # Obtener pestaña activa (por defecto: reseñas)
    tab = request.GET.get('tab', 'reseñas')
    
    # Preparar querysets
    reseñas = request.user.reseñas.all().order_by('-fecha')
    favoritos = request.user.favoritos.select_related('libro').all()
    listas = request.user.listas.all().order_by('-fecha_creacion')
    reportes = request.user.reportes.all().order_by('-fecha') if hasattr(request.user, "reportes") else []
    historial = request.user.historial_libros.select_related('libro').all().order_by('-fecha')
    
    # Paginación según pestaña activa
    page_obj = None
    if tab == 'reseñas':
        paginator = Paginator(reseñas, 10)
        page_obj = paginator.get_page(request.GET.get('page', 1))
        reseñas = page_obj
    elif tab == 'favoritos':
        paginator = Paginator(favoritos, 20)
        page_obj = paginator.get_page(request.GET.get('page', 1))
        favoritos = page_obj
    elif tab == 'historial':
        paginator = Paginator(historial, 20)
        page_obj = paginator.get_page(request.GET.get('page', 1))
        historial = page_obj
    elif tab == 'listas':
        paginator = Paginator(listas, 10)
        page_obj = paginator.get_page(request.GET.get('page', 1))
        listas = page_obj

    return render(request, 'usuarios/perfil.html', {
        'usuario': request.user,
        'reseñas': reseñas,
        'favoritos': favoritos,
        'listas': listas,
        'reportes': reportes,
        'historial': historial,
        'tab': tab,
        'page_obj': page_obj
    })


# -------------------------------
# Editar perfil
# -------------------------------
@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = RegistroUsuarioForm(instance=request.user)
    return render(request, 'usuarios/editar_perfil.html', {'form': form})


# -------------------------------
# Registro de usuario admin
# -------------------------------
def registro_admin(request):
    if request.method == 'POST':
        form = RegistroAdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistroAdminForm()
    return render(request, 'usuarios/registro_admin.html', {'form': form})

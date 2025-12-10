from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg, Count
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache
from collections import Counter

from .forms import ListaForm, ReseñaForm, LibroForm, CategoriaForm, ComentarioForm
from .models import Libro, Reseña, Favorito, Historial, Lista, Comentario, ValoracionReseña, Notificacion, Seguimiento
from usuarios.models import Usuario


# -------------------------------
# Crear libro (solo admin o superusuario)
# -------------------------------
@login_required
def crear_libro(request):
    if not request.user.is_superuser and getattr(request.user, "rol", None) != "admin":
        return redirect("homeGeneral")

    if request.method == "POST":
        form = LibroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "El libro se agregó correctamente.")
            return redirect("lista_libros")
    else:
        form = LibroForm()

    return render(request, "biblioteca/libros/crear_libro.html", {"form": form})


# -------------------------------
# Editar libro (solo admin)
# -------------------------------
@login_required
def editar_libro(request, libro_id):
    if request.user.rol != "admin":
        return redirect('homeGeneral')

    libro = get_object_or_404(Libro, id=libro_id)
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES, instance=libro)
        if form.is_valid():
            form.save()
            messages.success(request, "Libro actualizado correctamente.")
            return redirect('lista_libros')
    else:
        form = LibroForm(instance=libro)
    return render(request, 'biblioteca/libros/editar_libro.html', {'form': form, 'libro': libro})


# -------------------------------
# Eliminar libro (solo admin)
# -------------------------------
@login_required
def eliminar_libro(request, libro_id):
    if request.user.rol != "admin":
        return redirect('homeGeneral')

    libro = get_object_or_404(Libro, id=libro_id)
    if request.method == 'POST':
        libro.delete()
        messages.success(request, "Libro eliminado correctamente.")
        return redirect('lista_libros')

    return render(request, 'biblioteca/libros/eliminar_libro.html', {'libro': libro})


# -------------------------------
# Home y búsqueda
# -------------------------------
def home(request):
    libros_destacados = Libro.objects.all()[:3]
    libros_recientes = Libro.objects.order_by('-id')[:6]

    categorias = [
        "Todos",
        "Romance",
        "Ciencia ficción",
        "Fantasía",
        "Cómics",
        "Misterio",
        "Historia"
    ]

    return render(request, 'biblioteca/home.html', {
        'libros_destacados': libros_destacados,
        'libros_recientes': libros_recientes,
        'categorias': categorias
    })


def buscar_libros(request):
    """
    H12: Como usuario, quiero filtrar los resultados de búsqueda,
    para encontrar rápidamente los libros mejor valorados o más recientes.
    """
    query = request.GET.get('q', '')
    orden = request.GET.get('orden', 'reciente')
    valoracion_min = request.GET.get('valoracion', '')
    genero = request.GET.get('genero', '')
    
    # Anotar libros con promedio de calificación y conteo de reseñas
    resultados = Libro.objects.annotate(
        promedio_calificacion_db=Avg('reseñas__calificacion'),
        total_reseñas_db=Count('reseñas')
    )

    # Filtro por búsqueda de texto
    if query:
        resultados = resultados.filter(
            Q(titulo__icontains=query) |
            Q(autor__icontains=query) |
            Q(genero__icontains=query)
        )
    
    # Filtro por género
    if genero:
        resultados = resultados.filter(genero=genero)
    
    # Filtro por valoración mínima
    if valoracion_min:
        try:
            val_min = int(valoracion_min)
            resultados = resultados.filter(promedio_calificacion_db__gte=val_min)
        except ValueError:
            pass
    
    # Ordenamiento
    if orden == 'reciente':
        resultados = resultados.order_by('-id')
    elif orden == 'antiguo':
        resultados = resultados.order_by('id')
    elif orden == 'titulo_az':
        resultados = resultados.order_by('titulo')
    elif orden == 'titulo_za':
        resultados = resultados.order_by('-titulo')
    elif orden == 'autor':
        resultados = resultados.order_by('autor')
    elif orden == 'valoracion':
        # Ordenar por mejor valoración (los sin valoración al final)
        resultados = resultados.order_by('-promedio_calificacion_db', '-total_reseñas_db')
    
    # Paginación: 20 libros por página
    paginator = Paginator(resultados, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Obtener géneros disponibles para el filtro
    generos_disponibles = Libro.objects.values_list('genero', flat=True).distinct().order_by('genero')

    return render(request, 'biblioteca/libros/buscar_libros.html', {
        'resultados': page_obj,
        'page_obj': page_obj,
        'query': query,
        'orden': orden,
        'valoracion_min': valoracion_min,
        'genero': genero,
        'generos_disponibles': generos_disponibles,
    })


def lista_libros(request):
    libros = Libro.objects.all().order_by('-id')
    
    # Paginación: 20 libros por página
    paginator = Paginator(libros, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'biblioteca/libros/lista_libros.html', {
        'libros': page_obj,
        'page_obj': page_obj
    })


# -------------------------------
# Listas de usuario
# -------------------------------
@login_required
def crear_lista(request):
    if request.method == 'POST':
        form = ListaForm(request.POST)
        if form.is_valid():
            lista = form.save(commit=False)
            lista.usuario = request.user
            lista.save()
            form.save_m2m()
            return redirect('perfil')
    else:
        form = ListaForm()
    return render(request, 'biblioteca/listas/crear_lista.html', {'form': form})


@login_required
def detalle_lista(request, lista_id):
    lista = get_object_or_404(Lista, id=lista_id, usuario=request.user)
    return render(request, 'biblioteca/listas/detalle_lista.html', {'lista': lista})


@login_required
def editar_lista(request, lista_id):
    lista = get_object_or_404(Lista, id=lista_id, usuario=request.user)
    if request.method == 'POST':
        form = ListaForm(request.POST, instance=lista)
        if form.is_valid():
            form.save()
            messages.success(request, "La lista se actualizó correctamente.")
            return redirect('perfil')
    else:
        form = ListaForm(instance=lista)
    return render(request, 'biblioteca/listas/editar_lista.html', {'form': form, 'lista': lista})


@login_required
def eliminar_lista(request, lista_id):
    lista = get_object_or_404(Lista, id=lista_id, usuario=request.user)
    if request.method == 'POST':
        lista.delete()
        messages.success(request, "La lista se eliminó correctamente.")
        return redirect('perfil')
    return render(request, 'biblioteca/listas/eliminar_lista.html', {'lista': lista})


# -------------------------------
# Libros y reseñas
# -------------------------------
@login_required
def detalle_libro(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    if request.user.is_authenticated and getattr(request.user, "is_usuario", False):
        Historial.objects.create(usuario=request.user, libro=libro)

    reseñas = Reseña.objects.filter(libro=libro)

    es_favorito = False
    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(usuario=request.user, libro=libro).exists()

    return render(request, 'biblioteca/libros/detalle_libro.html', {
        'libro': libro,
        'reseñas': reseñas,
        'es_favorito': es_favorito
    })


@login_required
def crear_reseña(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    if not getattr(request.user, "is_usuario", False):
        return redirect('homeGeneral')

    if request.method == 'POST':
        comentario = request.POST.get('comentario')
        calificacion = request.POST.get('calificacion')
        Reseña.objects.create(
            usuario=request.user,
            libro=libro,
            comentario=comentario,
            calificacion=calificacion
        )
        return HttpResponseRedirect(reverse('detalle_libro', args=[libro.id]))

    return render(request, 'biblioteca/reseña_form.html', {'libro': libro})


@login_required
def editar_reseña(request, reseña_id):
    reseña = get_object_or_404(Reseña, id=reseña_id, usuario=request.user)
    libro = reseña.libro
    
    if request.method == 'POST':
        form = ReseñaForm(request.POST, instance=reseña)
        if form.is_valid():
            reseña_actualizada = form.save(commit=False)
            reseña_actualizada.save()
            
            # Forzar recalculación del promedio del libro
            nuevo_promedio = libro.promedio_calificacion()
            
            messages.success(
                request, 
                f"La reseña se actualizó correctamente. Nueva calificación: {reseña_actualizada.calificacion} estrellas."
            )
            return redirect('perfil')
    else:
        form = ReseñaForm(instance=reseña)
    return render(request, 'biblioteca/reseñas/editar_reseña.html', {'form': form, 'reseña': reseña})


@login_required
def eliminar_reseña(request, reseña_id):
    reseña = get_object_or_404(Reseña, id=reseña_id, usuario=request.user)
    if request.method == 'POST':
        reseña.delete()
        messages.success(request, "La reseña se eliminó correctamente.")
        return redirect('perfil')
    return render(request, 'biblioteca/reseñas/eliminar_reseña.html', {'reseña': reseña})


# -------------------------------
# Favoritos
# -------------------------------
@login_required
def agregar_favorito(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    Favorito.objects.get_or_create(usuario=request.user, libro=libro)
    return redirect('detalle_libro', libro_id=libro.id)


@login_required
def quitar_favorito(request, libro_id):
    favorito = get_object_or_404(Favorito, usuario=request.user, libro_id=libro_id)
    if request.method == 'POST':
        favorito.delete()
        messages.success(request, "El libro se quitó de tus favoritos.")
        return redirect('perfil')
    return render(request, 'biblioteca/usuario/quitar_favorito.html', {'favorito': favorito})


# -------------------------------
# Historial
# -------------------------------
@login_required
def ver_historial(request):
    historial = Historial.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'biblioteca/usuario/historial.html', {'historial': historial})


# -------------------------------
# Categorías (solo admin o superusuario)
# -------------------------------
@login_required
def crear_categoria(request):
    if not request.user.is_superuser and getattr(request.user, "rol", None) != "admin":
        return redirect("homeGeneral")

    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría creada correctamente.")
            return redirect("homeGeneral")
    else:
        form = CategoriaForm()

    return render(request, "biblioteca/crear_categoria.html", {"form": form})


# -------------------------------
# Perfil de usuario
# -------------------------------
@login_required
@login_required
@never_cache
def perfil(request):
    # Forzar consultas frescas de la base de datos
    reseñas = Reseña.objects.filter(usuario=request.user).select_related('libro').order_by('-fecha')
    favoritos = Favorito.objects.filter(usuario=request.user).select_related('libro')
    listas = Lista.objects.filter(usuario=request.user).prefetch_related('libros')
    historial = Historial.objects.filter(usuario=request.user).select_related('libro').order_by('-fecha')

    return render(request, 'usuarios/perfil.html', {
        'reseñas': reseñas,
        'favoritos': favoritos,
        'listas': listas,
        'historial': historial
    })


# -------------------------------
# Comentarios en reseñas (H6, H7, H8)
# -------------------------------
@login_required
def crear_comentario(request, reseña_id):
    """H6: Como comentador, quiero comentar en una reseña para participar en la conversación."""
    reseña = get_object_or_404(Reseña, id=reseña_id)
    
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.usuario = request.user
            comentario.reseña = reseña
            comentario.save()
            
            # H14: Crear notificación para el autor de la reseña
            if reseña.usuario != request.user:
                Notificacion.objects.create(
                    usuario=reseña.usuario,
                    tipo='comentario',
                    mensaje=f"{request.user.username} comentó en tu reseña de '{reseña.libro.titulo}'",
                    comentario=comentario,
                    reseña=reseña,
                    libro=reseña.libro,
                    usuario_origen=request.user
                )
            
            messages.success(request, "Comentario publicado correctamente.")
            return redirect('detalle_libro', libro_id=reseña.libro.id)
    else:
        form = ComentarioForm()
    
    return render(request, 'biblioteca/comentarios/crear_comentario.html', {
        'form': form,
        'reseña': reseña
    })


@login_required
def editar_comentario(request, comentario_id):
    """H7: Como comentador, quiero editar mis comentarios para corregir errores o actualizar contenido."""
    comentario = get_object_or_404(Comentario, id=comentario_id, usuario=request.user)
    
    if request.method == 'POST':
        form = ComentarioForm(request.POST, instance=comentario)
        if form.is_valid():
            form.save()
            messages.success(request, "Comentario actualizado correctamente.")
            return redirect('detalle_libro', libro_id=comentario.reseña.libro.id)
    else:
        form = ComentarioForm(instance=comentario)
    
    return render(request, 'biblioteca/comentarios/editar_comentario.html', {
        'form': form,
        'comentario': comentario
    })


@login_required
def eliminar_comentario(request, comentario_id):
    """H8: Como comentador, quiero eliminar mis comentarios para gestionar lo que digo."""
    comentario = get_object_or_404(Comentario, id=comentario_id, usuario=request.user)
    
    if request.method == 'POST':
        libro_id = comentario.reseña.libro.id
        comentario.delete()
        messages.success(request, "Comentario eliminado correctamente.")
        return redirect('detalle_libro', libro_id=libro_id)
    
    return render(request, 'biblioteca/comentarios/eliminar_comentario.html', {
        'comentario': comentario
    })


# -------------------------------
# Valoración de reseñas (H9)
# -------------------------------
@login_required
def valorar_reseña(request, reseña_id):
    """
    H9: Como comentador, quiero valorar una reseña con estrellas o puntos,
    para identificar las reseñas más útiles o interesantes.
    """
    reseña = get_object_or_404(Reseña, id=reseña_id)
    
    # Verificar que el usuario no valore su propia reseña
    if reseña.usuario == request.user:
        messages.warning(request, "No puedes valorar tu propia reseña.")
        return redirect('detalle_libro', libro_id=reseña.libro.id)
    
    if request.method == 'POST':
        puntuacion = request.POST.get('puntuacion')
        
        if not puntuacion or not puntuacion.isdigit() or int(puntuacion) not in range(1, 6):
            messages.error(request, "Selecciona una puntuación válida entre 1 y 5 estrellas.")
            return redirect('detalle_libro', libro_id=reseña.libro.id)
        
        # Crear o actualizar valoración
        valoracion, created = ValoracionReseña.objects.update_or_create(
            usuario=request.user,
            reseña=reseña,
            defaults={'puntuacion': int(puntuacion)}
        )
        
        # H14: Crear notificación para el autor de la reseña
        if created and reseña.usuario != request.user:
            Notificacion.objects.create(
                usuario=reseña.usuario,
                tipo='valoracion',
                mensaje=f"{request.user.username} valoró tu reseña de '{reseña.libro.titulo}' con {puntuacion} estrellas",
                reseña=reseña,
                libro=reseña.libro,
                usuario_origen=request.user
            )
        
        if created:
            messages.success(request, f"Has valorado esta reseña con {puntuacion} estrellas.")
        else:
            messages.success(request, f"Tu valoración se actualizó a {puntuacion} estrellas.")
        
        return redirect('detalle_libro', libro_id=reseña.libro.id)
    
    # GET request - mostrar formulario de valoración
    valoracion_actual = ValoracionReseña.objects.filter(
        usuario=request.user, 
        reseña=reseña
    ).first()
    
    return render(request, 'biblioteca/reseñas/valorar_reseña.html', {
        'reseña': reseña,
        'valoracion_actual': valoracion_actual
    })


# -------------------------------
# Sistema de Notificaciones (H14)
# -------------------------------
@login_required
def ver_notificaciones(request):
    """
    H14: Como usuario registrado, quiero ver todas mis notificaciones
    en un feed personalizado.
    """
    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha')
    no_leidas = notificaciones.filter(leida=False).count()
    
    # Paginación (10 por página)
    paginator = Paginator(notificaciones, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'biblioteca/usuario/notificaciones.html', {
        'notificaciones': page_obj,
        'no_leidas': no_leidas
    })


@login_required
def marcar_notificacion_leida(request, notificacion_id):
    """Marca una notificación específica como leída"""
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.marcar_como_leida()
    
    # Redirigir al objeto relacionado si existe
    if notificacion.libro:
        return redirect('detalle_libro', libro_id=notificacion.libro.id)
    elif notificacion.reseña:
        return redirect('detalle_libro', libro_id=notificacion.reseña.libro.id)
    
    return redirect('ver_notificaciones')


@login_required
def marcar_todas_leidas(request):
    """Marca todas las notificaciones del usuario como leídas"""
    if request.method == 'POST':
        Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
        messages.success(request, "Todas las notificaciones han sido marcadas como leídas.")
    
    return redirect('ver_notificaciones')


@login_required
def eliminar_notificacion(request, notificacion_id):
    """Elimina una notificación específica"""
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    
    if request.method == 'POST':
        notificacion.delete()
        messages.success(request, "Notificación eliminada.")
    
    return redirect('ver_notificaciones')


# -------------------------------
# Respuestas a comentarios (H16)
# -------------------------------
@login_required
def responder_comentario(request, comentario_id):
    """
    H16: Como comentador, quiero responder a comentarios de otros usuarios en una reseña,
    para fomentar la discusión.
    """
    comentario_padre = get_object_or_404(Comentario, id=comentario_id)
    
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            respuesta = form.save(commit=False)
            respuesta.usuario = request.user
            respuesta.reseña = comentario_padre.reseña
            respuesta.padre = comentario_padre
            respuesta.save()
            
            # H14: Crear notificación para el autor del comentario padre
            if comentario_padre.usuario != request.user:
                Notificacion.objects.create(
                    usuario=comentario_padre.usuario,
                    tipo='respuesta',
                    mensaje=f"{request.user.username} respondió a tu comentario en '{comentario_padre.reseña.libro.titulo}'",
                    comentario=respuesta,
                    reseña=comentario_padre.reseña,
                    libro=comentario_padre.reseña.libro,
                    usuario_origen=request.user
                )
            
            messages.success(request, "Respuesta publicada correctamente.")
            return redirect('detalle_libro', libro_id=comentario_padre.reseña.libro.id)
    else:
        form = ComentarioForm()
    
    return render(request, 'biblioteca/comentarios/responder_comentario.html', {
        'form': form,
        'comentario_padre': comentario_padre
    })


# -------------------------------
# Sistema de Seguimiento (H20)
# -------------------------------
@login_required
def seguir_usuario(request, usuario_id):
    """H20: Seguir a un usuario"""
    usuario_a_seguir = get_object_or_404(Usuario, id=usuario_id)
    
    if usuario_a_seguir == request.user:
        messages.warning(request, "No puedes seguirte a ti mismo.")
        return redirect('perfil_usuario_publico', usuario_id=usuario_id)
    
    seguimiento, created = Seguimiento.objects.get_or_create(
        seguidor=request.user,
        seguido=usuario_a_seguir
    )
    
    if created:
        Notificacion.objects.create(
            usuario=usuario_a_seguir,
            tipo='seguidor',
            mensaje=f"{request.user.username} comenzó a seguirte",
            usuario_origen=request.user
        )
        messages.success(request, f"Ahora sigues a {usuario_a_seguir.username}.")
    else:
        messages.info(request, f"Ya sigues a {usuario_a_seguir.username}.")
    
    return redirect('perfil_usuario_publico', usuario_id=usuario_id)


@login_required
def dejar_seguir_usuario(request, usuario_id):
    """H20: Dejar de seguir"""
    usuario_seguido = get_object_or_404(Usuario, id=usuario_id)
    
    seguimiento = Seguimiento.objects.filter(
        seguidor=request.user,
        seguido=usuario_seguido
    ).first()
    
    if seguimiento:
        seguimiento.delete()
        messages.success(request, f"Has dejado de seguir a {usuario_seguido.username}.")
    
    return redirect('perfil_usuario_publico', usuario_id=usuario_id)


@login_required
def lista_siguiendo(request):
    """Lista de usuarios que sigue"""
    siguiendo = Seguimiento.objects.filter(seguidor=request.user).select_related('seguido')
    return render(request, 'biblioteca/usuario/lista_siguiendo.html', {'siguiendo': siguiendo})


@login_required
def lista_seguidores(request):
    """Lista de seguidores"""
    seguidores = Seguimiento.objects.filter(seguido=request.user).select_related('seguidor')
    return render(request, 'biblioteca/usuario/lista_seguidores.html', {'seguidores': seguidores})


@login_required
def feed_personalizado(request):
    """H20: Feed con actividad"""
    usuarios_seguidos = Seguimiento.objects.filter(
        seguidor=request.user
    ).values_list('seguido_id', flat=True)
    
    reseñas_feed = Reseña.objects.filter(
        usuario_id__in=usuarios_seguidos
    ).select_related('usuario', 'libro').order_by('-fecha')
    
    # Paginación: 15 reseñas por página
    paginator = Paginator(reseñas_feed, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'biblioteca/feed_personalizado.html', {
        'reseñas': page_obj,
        'page_obj': page_obj,
        'total_siguiendo': len(usuarios_seguidos)
    })


@login_required
def perfil_usuario_publico(request, usuario_id):
    """H20: Perfil público"""
    usuario_perfil = get_object_or_404(Usuario, id=usuario_id)
    esta_siguiendo = Seguimiento.esta_siguiendo(request.user, usuario_perfil) if request.user.is_authenticated else False
    
    return render(request, 'biblioteca/usuario/perfil_publico.html', {
        'usuario_perfil': usuario_perfil,
        'esta_siguiendo': esta_siguiendo,
        'total_seguidores': usuario_perfil.seguidores.count(),
        'total_siguiendo': usuario_perfil.siguiendo.count(),
        'reseñas': usuario_perfil.reseñas.select_related('libro').order_by('-fecha')[:10],
        'listas': usuario_perfil.listas.prefetch_related('libros')[:5],
        'es_propio': usuario_perfil == request.user
    })


@login_required
def recomendaciones(request):
    """H19: Recomendaciones personalizadas"""
    generos_historial = list(Historial.objects.filter(usuario=request.user).values_list('libro__genero', flat=True))
    generos_listas = list(Lista.objects.filter(usuario=request.user).values_list('libros__genero', flat=True))
    generos_reseñas = list(Reseña.objects.filter(usuario=request.user, calificacion__gte=4).values_list('libro__genero', flat=True))
    
    todos_generos = generos_historial + generos_listas + generos_reseñas
    
    if not todos_generos:
        libros_recomendados = Libro.objects.annotate(
            promedio=Avg('reseñas__calificacion'),
            total=Count('reseñas')
        ).filter(total__gte=1).order_by('-promedio', '-total')
        razon = "Libros mejor valorados"
    else:
        contador_generos = Counter(todos_generos)
        generos_favoritos = [g for g, _ in contador_generos.most_common(3)]
        libros_vistos = set(Historial.objects.filter(usuario=request.user).values_list('libro_id', flat=True))
        
        libros_recomendados = Libro.objects.filter(
            genero__in=generos_favoritos
        ).exclude(id__in=libros_vistos).annotate(
            promedio=Avg('reseñas__calificacion'),
            total=Count('reseñas')
        ).order_by('-promedio', '-total')
        
        razon = f"Basado en: {', '.join([g.replace('_', ' ').title() for g in generos_favoritos])}"
    
    # Paginación para recomendaciones principales: 20 por página
    paginator = Paginator(libros_recomendados, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    usuarios_seguidos = Seguimiento.objects.filter(seguidor=request.user).values_list('seguido_id', flat=True)
    libros_seguidos = Libro.objects.filter(
        reseñas__usuario_id__in=usuarios_seguidos,
        reseñas__calificacion__gte=4
    ).distinct().annotate(promedio=Avg('reseñas__calificacion')).order_by('-promedio')[:6] if usuarios_seguidos else []
    
    return render(request, 'biblioteca/recomendaciones.html', {
        'libros_recomendados': page_obj,
        'page_obj': page_obj,
        'libros_seguidos': libros_seguidos,
        'razon': razon
    })

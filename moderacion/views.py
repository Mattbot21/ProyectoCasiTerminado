from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from .forms import ReporteForm, AccionModeracionForm
from .models import Reporte
from biblioteca.models import Reseña, Comentario


# -----------------------------
# Reportar reseña
# -----------------------------
@login_required
def reportar_reseña(request, reseña_id):
    reseña = get_object_or_404(Reseña, id=reseña_id)
    
    # Evitar que el usuario reporte su propia reseña
    if reseña.usuario == request.user:
        messages.error(request, "No puedes reportar tu propia reseña.")
        return redirect('detalle_libro', reseña.libro.id)
    
    if request.method == 'POST':
        form = ReporteForm(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.usuario = request.user
            reporte.reseña = reseña
            reporte.save()
            messages.success(request, "Reporte enviado correctamente.")
            return redirect('detalle_libro', reseña.libro.id)
    else:
        form = ReporteForm()
    return render(request, 'moderacion/reportar.html', {'form': form, 'reseña': reseña})


# -----------------------------
# Reportar comentario
# -----------------------------
@login_required
def reportar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)
    
    # Evitar que el usuario reporte su propio comentario
    if comentario.usuario == request.user:
        messages.error(request, "No puedes reportar tu propio comentario.")
        return redirect('detalle_libro', comentario.reseña.libro.id)
    
    if request.method == 'POST':
        form = ReporteForm(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.usuario = request.user
            reporte.comentario = comentario
            reporte.save()
            messages.success(request, "Reporte enviado correctamente.")
            return redirect('detalle_libro', comentario.reseña.libro.id)
    else:
        form = ReporteForm()
    return render(request, 'moderacion/reportar.html', {'form': form, 'comentario': comentario})


# -----------------------------
# Panel de moderación (solo admins) - MEJORADO
# -----------------------------
@login_required
def panel_moderacion(request):
    if not request.user.is_admin:
        return redirect('homeGeneral')

    # Filtros
    motivo_filtro = request.GET.get('motivo', '')
    tipo_filtro = request.GET.get('tipo', '')  # reseña o comentario
    
    # Query base
    reportes_pendientes = Reporte.objects.filter(revisado=False)
    reportes_resueltos = Reporte.objects.filter(revisado=True)
    
    # Aplicar filtro de motivo
    if motivo_filtro:
        reportes_pendientes = reportes_pendientes.filter(motivo=motivo_filtro)
        reportes_resueltos = reportes_resueltos.filter(motivo=motivo_filtro)
    
    # Aplicar filtro de tipo
    if tipo_filtro == 'reseña':
        reportes_pendientes = reportes_pendientes.filter(reseña__isnull=False)
        reportes_resueltos = reportes_resueltos.filter(reseña__isnull=False)
    elif tipo_filtro == 'comentario':
        reportes_pendientes = reportes_pendientes.filter(comentario__isnull=False)
        reportes_resueltos = reportes_resueltos.filter(comentario__isnull=False)
    
    # Ordenar
    reportes_pendientes = reportes_pendientes.select_related('usuario', 'reseña', 'comentario').order_by('-fecha')
    reportes_resueltos = reportes_resueltos.select_related('usuario', 'reseña', 'comentario').order_by('-fecha')
    
    # Paginación - PENDIENTES
    paginator_pendientes = Paginator(reportes_pendientes, 20)  # 20 por página
    page_pendientes = request.GET.get('page_pendientes', 1)
    reportes_pendientes_page = paginator_pendientes.get_page(page_pendientes)
    
    # Paginación - RESUELTOS
    paginator_resueltos = Paginator(reportes_resueltos, 15)  # 15 por página
    page_resueltos = request.GET.get('page_resueltos', 1)
    reportes_resueltos_page = paginator_resueltos.get_page(page_resueltos)
    
    # Estadísticas generales
    stats = {
        'total_pendientes': reportes_pendientes.count(),
        'total_resueltos': reportes_resueltos.count(),
        'spam_pendiente': reportes_pendientes.filter(motivo='spam').count(),
        'inapropiado_pendiente': reportes_pendientes.filter(motivo='inapropiado').count(),
        'otro_pendiente': reportes_pendientes.filter(motivo='otro').count(),
        'reseñas_reportadas': Reporte.objects.filter(revisado=False, reseña__isnull=False).count(),
        'comentarios_reportados': Reporte.objects.filter(revisado=False, comentario__isnull=False).count(),
    }

    return render(request, 'moderacion/panel.html', {
        'reportes_pendientes': reportes_pendientes_page,
        'reportes_resueltos': reportes_resueltos_page,
        'stats': stats,
        'motivo_filtro': motivo_filtro,
        'tipo_filtro': tipo_filtro,
    })


# -----------------------------
# Resolver reporte (solo admins)
# -----------------------------
@login_required
def resolver_reporte(request, reporte_id):
    if not request.user.is_admin:
        return redirect('homeGeneral')

    reporte = get_object_or_404(Reporte, id=reporte_id)
    if request.method == 'POST':
        form = AccionModeracionForm(request.POST)
        if form.is_valid():
            # Marcar reporte como revisado PRIMERO
            reporte.revisado = True
            reporte.save()
            
            # Crear la acción de moderación
            accion = form.save(commit=False)
            accion.reporte = reporte
            accion.administrador = request.user
            accion.save()
            
            # Ejecutar la acción seleccionada
            if accion.accion == 'eliminar':
                if reporte.reseña:
                    libro_id = reporte.reseña.libro.id
                    reporte.reseña.delete()
                    messages.success(request, "Reseña eliminada correctamente.")
                elif reporte.comentario:
                    libro_id = reporte.comentario.reseña.libro.id
                    reporte.comentario.delete()
                    messages.success(request, "Comentario eliminado correctamente.")
            elif accion.accion == 'ocultar':
                # Marcar como oculto (necesitarías agregar un campo 'oculto' en los modelos)
                messages.success(request, "Contenido marcado como oculto.")
            elif accion.accion == 'banear':
                # Banear al usuario que creó el contenido
                if reporte.reseña:
                    usuario_a_banear = reporte.reseña.usuario
                elif reporte.comentario:
                    usuario_a_banear = reporte.comentario.usuario
                else:
                    usuario_a_banear = None
                
                if usuario_a_banear:
                    usuario_a_banear.is_active = False
                    usuario_a_banear.save()
                    messages.success(request, f"Usuario {usuario_a_banear.username} baneado correctamente.")
            elif accion.accion == 'ignorar':
                messages.info(request, "Reporte marcado como ignorado. No se tomó ninguna acción.")
            
            return redirect('panel_moderacion')
    else:
        form = AccionModeracionForm()
    return render(request, 'moderacion/resolver.html', {
        'form': form,
        'reporte': reporte
    })

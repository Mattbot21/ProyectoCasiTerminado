from .models import Notificacion

def notificaciones_no_leidas(request):
    """
    Context processor para mostrar el número de notificaciones no leídas
    en toda la aplicación.
    """
    if request.user.is_authenticated:
        count = Notificacion.objects.filter(usuario=request.user, leida=False).count()
        return {'notificaciones_no_leidas': count}
    return {'notificaciones_no_leidas': 0}

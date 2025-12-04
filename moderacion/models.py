from django.db import models
from usuarios.models import Usuario
from biblioteca.models import Reseña, Comentario


# -----------------------------
# Modelo de Reporte
# -----------------------------
class Reporte(models.Model):
    class Motivo(models.TextChoices):
        SPAM = 'spam', 'Spam'
        INAPROPIADO = 'inapropiado', 'Contenido inapropiado'
        OTRO = 'otro', 'Otro'

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="reportes")
    reseña = models.ForeignKey(Reseña, on_delete=models.CASCADE, null=True, blank=True)
    comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE, null=True, blank=True)
    motivo = models.CharField(max_length=20, choices=Motivo.choices)
    fecha = models.DateTimeField(auto_now_add=True)
    revisado = models.BooleanField(default=False)

    def __str__(self):
        return f"Reporte de {self.usuario.username} - {self.motivo}"


# -----------------------------
# Modelo de Acción de Moderación
# -----------------------------
class AccionModeracion(models.Model):
    class Accion(models.TextChoices):
        ELIMINAR = 'eliminar', 'Eliminar contenido'
        OCULTAR = 'ocultar', 'Ocultar contenido'
        BANEAR = 'banear', 'Banear usuario'
        IGNORAR = 'ignorar', 'Ignorar reporte'

    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, related_name="acciones")
    administrador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'admin'}
    )
    accion = models.CharField(max_length=20, choices=Accion.choices)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_accion_display()} por {self.administrador.username}"

from django.db import models
from usuarios.models import Usuario


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, related_name="libros")
    genero = models.CharField(
        max_length=50,
        choices=[
            ("romance", "Romance"),
            ("terror", "Terror"),
            ("policial", "Policial"),
            ("ciencia_ficcion", "Ciencia Ficción"),
            ("fantasia", "Fantasía"),
            ("historia", "Historia"),
        ],
        default="romance"
    )
    fecha_publicacion = models.DateField(blank=True, null=True)
    portada = models.ImageField(upload_to="portadas/", blank=True, null=True)

    def __str__(self):
        return self.titulo
    
    def promedio_calificacion(self):
        """Calcula el promedio de calificaciones de las reseñas del libro"""
        reseñas = self.reseñas.all()
        if reseñas.exists():
            total = sum([r.calificacion for r in reseñas])
            return round(total / reseñas.count(), 1)
        return 0
    
    def total_reseñas(self):
        """Retorna el total de reseñas del libro"""
        return self.reseñas.count()


class Reseña(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="reseñas")
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name="reseñas")
    comentario = models.TextField()
    calificacion = models.PositiveSmallIntegerField(default=1)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.libro.titulo}"
    
    def promedio_valoracion(self):
        """Calcula el promedio de valoraciones de la reseña"""
        valoraciones = self.valoraciones.all()
        if valoraciones.exists():
            total = sum([v.puntuacion for v in valoraciones])
            return round(total / valoraciones.count(), 1)
        return 0
    
    def total_valoraciones(self):
        """Retorna el total de valoraciones recibidas"""
        return self.valoraciones.count()


class Historial(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='historial_libros')
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario.username} consultó {self.libro.titulo}"


class Lista(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='listas')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    libros = models.ManyToManyField(Libro, related_name='listas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} ({self.usuario.username})"


class Comentario(models.Model):
    """
    H16: Modificado para soportar respuestas anidadas
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    reseña = models.ForeignKey(Reseña, on_delete=models.CASCADE, related_name="comentarios")
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    
    # H16: Campo para respuestas anidadas
    padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='respuestas')

    class Meta:
        ordering = ['fecha']

    def __str__(self):
        if self.padre:
            return f"Respuesta de {self.usuario.username} a {self.padre.usuario.username}"
        return f"Comentario de {self.usuario.username} en {self.reseña.libro.titulo}"
    
    def es_respuesta(self):
        """Retorna True si este comentario es una respuesta a otro"""
        return self.padre is not None
    
    def total_respuestas(self):
        """Cuenta las respuestas directas a este comentario"""
        return self.respuestas.count()


class Favorito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="favoritos")
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name="favoritos")
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'libro')

    def __str__(self):
        return f"{self.usuario.username} → {self.libro.titulo}"


class ValoracionReseña(models.Model):
    """
    H9: Como comentador, quiero valorar una reseña con estrellas o puntos,
    para identificar las reseñas más útiles o interesantes.
    """
    PUNTUACIONES = [
        (1, '1 estrella'),
        (2, '2 estrellas'),
        (3, '3 estrellas'),
        (4, '4 estrellas'),
        (5, '5 estrellas'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="valoraciones_reseñas")
    reseña = models.ForeignKey(Reseña, on_delete=models.CASCADE, related_name="valoraciones")
    puntuacion = models.PositiveSmallIntegerField(choices=PUNTUACIONES, default=5)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'reseña')
        ordering = ['-fecha']
        verbose_name = 'Valoración de Reseña'
        verbose_name_plural = 'Valoraciones de Reseñas'

    def __str__(self):
        return f"{self.usuario.username} valoró con {self.puntuacion}★ la reseña de {self.reseña.usuario.username}"


class Notificacion(models.Model):
    """
    H14: Como usuario registrado, quiero recibir una notificación cuando alguien
    comente o responda mi reseña, para mantenerme al tanto de la conversación.
    """
    TIPOS = [
        ('comentario', 'Nuevo comentario en tu reseña'),
        ('valoracion', 'Nueva valoración en tu reseña'),
        ('respuesta', 'Nueva respuesta a tu comentario'),
        ('seguidor', 'Nuevo seguidor'),
        ('reseña', 'Nueva reseña en libro que sigues'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="notificaciones")
    tipo = models.CharField(max_length=20, choices=TIPOS)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)
    
    # Referencias opcionales a objetos relacionados
    comentario = models.ForeignKey('Comentario', on_delete=models.CASCADE, null=True, blank=True)
    reseña = models.ForeignKey('Reseña', on_delete=models.CASCADE, null=True, blank=True)
    libro = models.ForeignKey('Libro', on_delete=models.CASCADE, null=True, blank=True)
    usuario_origen = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True, related_name="notificaciones_enviadas")
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
    
    def __str__(self):
        return f"Notificación para {self.usuario.username}: {self.tipo}"
    
    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        self.leida = True
        self.save()


class Seguimiento(models.Model):
    """
    H20: Como usuario, quiero poder seguir a otros lectores cuyos gustos encuentre
    interesantes, para ver si actividad en un feed personalizado.
    """
    seguidor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='siguiendo')
    seguido = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='seguidores')
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('seguidor', 'seguido')
        ordering = ['-fecha']
        verbose_name = 'Seguimiento'
        verbose_name_plural = 'Seguimientos'
    
    def __str__(self):
        return f"{self.seguidor.username} sigue a {self.seguido.username}"
    
    @classmethod
    def esta_siguiendo(cls, usuario_seguidor, usuario_seguido):
        """Verifica si un usuario sigue a otro"""
        return cls.objects.filter(seguidor=usuario_seguidor, seguido=usuario_seguido).exists()

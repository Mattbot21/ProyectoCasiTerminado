from django.contrib import admin
from .models import Libro, Categoria, ValoracionReseña, Notificacion, Seguimiento


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "genero", "fecha_publicacion")
    search_fields = ("titulo", "autor")
    list_filter = ("genero", "fecha_publicacion")


@admin.register(ValoracionReseña)
class ValoracionReseñaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "reseña", "puntuacion", "fecha")
    list_filter = ("puntuacion", "fecha")
    search_fields = ("usuario__username", "reseña__libro__titulo")
    readonly_fields = ("fecha",)


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "tipo", "mensaje_corto", "leida", "fecha")
    list_filter = ("tipo", "leida", "fecha")
    search_fields = ("usuario__username", "mensaje")
    readonly_fields = ("fecha",)
    actions = ['marcar_como_leidas']
    
    def mensaje_corto(self, obj):
        return obj.mensaje[:50] + "..." if len(obj.mensaje) > 50 else obj.mensaje
    mensaje_corto.short_description = "Mensaje"
    
    def marcar_como_leidas(self, request, queryset):
        queryset.update(leida=True)
    marcar_como_leidas.short_description = "Marcar seleccionadas como leídas"


@admin.register(Seguimiento)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display = ("seguidor", "seguido", "fecha")
    list_filter = ("fecha",)
    search_fields = ("seguidor__username", "seguido__username")
    readonly_fields = ("fecha",)


admin.site.register(Categoria)

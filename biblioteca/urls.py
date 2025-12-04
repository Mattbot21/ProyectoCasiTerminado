from django.urls import path
from .views import (
    home,
    buscar_libros,
    lista_libros,
    detalle_libro,
    crear_libro,
    editar_libro,
    eliminar_libro,
    crear_lista,
    detalle_lista,
    editar_lista,
    eliminar_lista,
    crear_reseña,
    editar_reseña,
    eliminar_reseña,
    agregar_favorito,
    quitar_favorito,
    ver_historial,
    crear_categoria,
    crear_comentario,
    editar_comentario,
    eliminar_comentario,
    valorar_reseña,
    ver_notificaciones,
    marcar_notificacion_leida,
    marcar_todas_leidas,
    eliminar_notificacion,
    responder_comentario,
    seguir_usuario,
    dejar_seguir_usuario,
    lista_siguiendo,
    lista_seguidores,
    feed_personalizado,
    perfil_usuario_publico,
    recomendaciones,
)

urlpatterns = [
    # Home y búsqueda
    path('', home, name='homeGeneral'),
    path('buscar/', buscar_libros, name='buscar_libros'),
    path('libros/', lista_libros, name='lista_libros'),
    path('libro/<int:libro_id>/', detalle_libro, name='detalle_libro'),

    # Libros (solo admin/superuser)
    path('libro/crear/', crear_libro, name='crear_libro'),
    path('libro/<int:libro_id>/editar/', editar_libro, name='editar_libro'),
    path('libro/<int:libro_id>/eliminar/', eliminar_libro, name='eliminar_libro'),

    # Listas de usuario
    path('lista/crear/', crear_lista, name='crear_lista'),
    path('lista/<int:lista_id>/', detalle_lista, name='detalle_lista'),
    path('lista/<int:lista_id>/editar/', editar_lista, name='editar_lista'),
    path('lista/<int:lista_id>/eliminar/', eliminar_lista, name='eliminar_lista'),

    # Reseñas
    path('libro/<int:libro_id>/reseña/', crear_reseña, name='crear_reseña'),
    path('reseña/<int:reseña_id>/editar/', editar_reseña, name='editar_reseña'),
    path('reseña/<int:reseña_id>/eliminar/', eliminar_reseña, name='eliminar_reseña'),

    # Comentarios (H6, H7, H8)
    path('reseña/<int:reseña_id>/comentario/', crear_comentario, name='crear_comentario'),
    path('comentario/<int:comentario_id>/editar/', editar_comentario, name='editar_comentario'),
    path('comentario/<int:comentario_id>/eliminar/', eliminar_comentario, name='eliminar_comentario'),

    # Valoración de reseñas (H9)
    path('reseña/<int:reseña_id>/valorar/', valorar_reseña, name='valorar_reseña'),

    # Notificaciones (H14)
    path('notificaciones/', ver_notificaciones, name='ver_notificaciones'),
    path('notificacion/<int:notificacion_id>/leida/', marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('notificaciones/marcar-todas/', marcar_todas_leidas, name='marcar_todas_leidas'),
    path('notificacion/<int:notificacion_id>/eliminar/', eliminar_notificacion, name='eliminar_notificacion'),

    # Favoritos
    path('favorito/<int:libro_id>/agregar/', agregar_favorito, name='agregar_favorito'),
    path('favorito/<int:libro_id>/quitar/', quitar_favorito, name='quitar_favorito'),

    # Historial
    path('historial/', ver_historial, name='ver_historial'),

    # Categorías (solo admin/superuser)
    path('categoria/crear/', crear_categoria, name='crear_categoria'),

    # Respuestas a comentarios (H16)
    path('comentario/<int:comentario_id>/responder/', responder_comentario, name='responder_comentario'),

    # Sistema de Seguimiento (H20)
    path('usuario/<int:usuario_id>/seguir/', seguir_usuario, name='seguir_usuario'),
    path('usuario/<int:usuario_id>/dejar-seguir/', dejar_seguir_usuario, name='dejar_seguir_usuario'),
    path('siguiendo/', lista_siguiendo, name='lista_siguiendo'),
    path('seguidores/', lista_seguidores, name='lista_seguidores'),
    path('feed/', feed_personalizado, name='feed_personalizado'),
    path('perfil/<int:usuario_id>/', perfil_usuario_publico, name='perfil_usuario_publico'),

    # Recomendaciones (H19)
    path('recomendaciones/', recomendaciones, name='recomendaciones'),
]

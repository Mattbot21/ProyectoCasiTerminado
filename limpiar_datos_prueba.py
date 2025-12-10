"""
Script para eliminar datos de prueba
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibreriaDigital.settings')
django.setup()

from biblioteca.models import (
    Libro, Reseña, Favorito, Historial, Lista, Comentario, Categoria,
    Seguimiento, ValoracionReseña, Notificacion
)
from usuarios.models import Usuario
from moderacion.models import Reporte, AccionModeracion

def limpiar_datos():
    """Eliminar todos los datos de prueba"""
    print("\n" + "="*70)
    print(" LIMPIEZA DE DATOS DE PRUEBA")
    print("="*70)
    
    print("\n Este script eliminará:")
    print("   • Acciones de moderación")
    print("   • Reportes")
    print("   • Notificaciones")
    print("   • Seguimientos")
    print("   • Valoraciones de reseñas")
    print("   • Comentarios (incluye respuestas)")
    print("   • Reseñas")
    print("   • Listas de libros")
    print("   • Favoritos")
    print("   • Historial")
    print("   • Libros (y sus portadas)")
    print("   • Categorías")
    print("   • Usuarios de prueba (opcional)")
    
    respuesta = input("\n⚠️  ¿Está SEGURO de eliminar TODOS los datos? (escriba 'SI' en mayúsculas): ")
    if respuesta != 'SI':
        print("\n❌ Operación cancelada.")
        return
    
    # Confirmación adicional
    confirmacion = input("\n⚠️  Escriba 'ELIMINAR' para confirmar: ")
    if confirmacion != 'ELIMINAR':
        print("\n❌ Operación cancelada.")
        return
    
    print("\nEliminando datos en orden correcto...")
    
    # Fase 1: Moderación (primero, tienen FK a otros modelos)
    print("\n1. Eliminando acciones de moderación...")
    count = AccionModeracion.objects.all().delete()[0]
    print(f"   ✓ {count} acciones eliminadas")
    
    print("\n2. Eliminando reportes...")
    count = Reporte.objects.all().delete()[0]
    print(f"   ✓ {count} reportes eliminados")
    
    # Fase 2: Notificaciones y seguimientos
    print("\n3. Eliminando notificaciones...")
    count = Notificacion.objects.all().delete()[0]
    print(f"   ✓ {count} notificaciones eliminadas")
    
    print("\n4. Eliminando seguimientos...")
    count = Seguimiento.objects.all().delete()[0]
    print(f"   ✓ {count} seguimientos eliminados")
    
    # Fase 3: Valoraciones y comentarios
    print("\n5. Eliminando valoraciones de reseñas...")
    count = ValoracionReseña.objects.all().delete()[0]
    print(f"   ✓ {count} valoraciones eliminadas")
    
    print("\n6. Eliminando comentarios (incluye respuestas)...")
    count = Comentario.objects.all().delete()[0]
    print(f"   ✓ {count} comentarios eliminados")
    
    # Fase 4: Reseñas y relaciones con libros
    print("\n7. Eliminando reseñas...")
    count = Reseña.objects.all().delete()[0]
    print(f"   ✓ {count} reseñas eliminadas")
    
    print("\n8. Eliminando favoritos...")
    count = Favorito.objects.all().delete()[0]
    print(f"   ✓ {count} favoritos eliminados")
    
    print("\n9. Eliminando historial...")
    count = Historial.objects.all().delete()[0]
    print(f"   ✓ {count} entradas de historial eliminadas")
    
    print("\n10. Eliminando listas...")
    count = Lista.objects.all().delete()[0]
    print(f"   ✓ {count} listas eliminadas")
    
    # Fase 5: Libros y categorías
    print("\n11. Eliminando libros (y portadas)...")
    # Obtener todos los libros antes de eliminarlos para borrar archivos
    libros = list(Libro.objects.all())
    portadas_eliminadas = 0
    errores_portadas = 0
    
    for libro in libros:
        if libro.portada:
            try:
                # Verificar si el archivo existe antes de intentar eliminarlo
                ruta_completa = libro.portada.path
                if os.path.exists(ruta_completa):
                    os.remove(ruta_completa)
                    portadas_eliminadas += 1
                    print(f"   🗑️  Portada eliminada: {os.path.basename(ruta_completa)}")
            except Exception as e:
                errores_portadas += 1
                print(f"   ⚠️  Error al eliminar portada de '{libro.titulo}': {e}")
    
    count = Libro.objects.all().delete()[0]
    print(f"   ✓ {count} libros eliminados")
    print(f"   ✓ {portadas_eliminadas} archivos de portadas eliminados")
    if errores_portadas > 0:
        print(f"   ⚠️  {errores_portadas} portadas no se pudieron eliminar")
    
    print("\n12. Eliminando categorías...")
    count = Categoria.objects.all().delete()[0]
    print(f"   ✓ {count} categorías eliminadas")
    
    # Fase 6: Usuarios (opcional)
    respuesta = input("\n¿Eliminar también TODOS los usuarios? (escriba 'SI' para confirmar): ")
    if respuesta == 'SI':
        print("\n13. Eliminando usuarios...")
        count = Usuario.objects.all().delete()[0]
        print(f"   ✓ {count} usuarios eliminados")
    else:
        # Solo eliminar usuarios de prueba (los que tienen username usuarioXXX)
        print("\n13. Eliminando solo usuarios de prueba...")
        count = Usuario.objects.filter(username__startswith='usuario').delete()[0]
        count2 = Usuario.objects.filter(username__startswith='admin').exclude(username='admin').delete()[0]
        print(f"   ✓ {count + count2} usuarios de prueba eliminados")
        print(f"   ℹ  Usuarios reales preservados (incluido 'admin' principal)")
    
    print("\n" + "="*70)
    print(" ✓ LIMPIEZA COMPLETADA")
    print("="*70)
    print("\n Todos los datos de prueba han sido eliminados.")
    print(" La base de datos está lista para nuevas pruebas.")
    print("="*70 + "\n")

if __name__ == "__main__":
    limpiar_datos()

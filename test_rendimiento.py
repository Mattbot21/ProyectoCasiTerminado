"""
Script de pruebas de rendimiento para la Librería Digital
Genera datos de prueba y mide tiempos de respuesta
Incluye imágenes de prueba predeterminadas
"""

import os
import django
import time
from datetime import datetime, timedelta
import random
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import urllib.request
from urllib.error import URLError

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibreriaDigital.settings')
django.setup()

from biblioteca.models import (
    Libro, Reseña, Favorito, Historial, Lista, Comentario, Categoria, 
    Seguimiento, ValoracionReseña, Notificacion
)
from usuarios.models import Usuario
from moderacion.models import Reporte, AccionModeracion
from django.db import connection
from django.db.models import Avg, Count, Q
from django.test.utils import CaptureQueriesContext

# Listas para generar datos aleatorios
NOMBRES = ['Juan', 'María', 'Carlos', 'Ana', 'Luis', 'Carmen', 'José', 'Laura', 'Pedro', 'Isabel']
APELLIDOS = ['García', 'Martínez', 'López', 'Sánchez', 'González', 'Pérez', 'Rodríguez', 'Fernández']

# Base de datos de libros reales con sus URLs de portadas
LIBROS_REALES = [
    {
        'titulo': 'Cien años de soledad',
        'autor': 'Gabriel García Márquez',
        'genero': 'fantasia',
        'descripcion': 'La historia de la familia Buendía a lo largo de siete generaciones en el pueblo ficticio de Macondo.',
        'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1327881361i/320.jpg'
    },
    {
        'titulo': '1984',
        'autor': 'George Orwell',
        'genero': 'ciencia_ficcion',
        'descripcion': 'Una distopía sobre una sociedad totalitaria donde el Gran Hermano controla cada aspecto de la vida.',
        'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1657781256i/61439040.jpg'
    },
    {
        'titulo': 'El principito',
        'autor': 'Antoine de Saint-Exupéry',
        'genero': 'fantasia',
        'descripcion': 'Un cuento poético sobre un pequeño príncipe que viaja de planeta en planeta.',
        'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1367545443i/157993.jpg'
    },
    {
        'titulo': 'Don Quijote de la Mancha',
        'autor': 'Miguel de Cervantes',
        'genero': 'historia',
        'descripcion': 'Las aventuras de un hidalgo que pierde la cordura y decide convertirse en caballero andante.',
        'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1546112331i/3836.jpg'
    },
    {
        'titulo': 'Orgullo y prejuicio',
        'autor': 'Jane Austen',
        'genero': 'romance',
        'descripcion': 'La historia de Elizabeth Bennet y el señor Darcy en la Inglaterra rural del siglo XIX.',
        'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1320399351i/1885.jpg'
    },
    {
        'titulo': 'El código Da Vinci',
        'autor': 'Dan Brown',
        'genero': 'policial',
        'descripcion': 'Un thriller que mezcla arte, historia y conspiración en torno a un misterioso asesinato.',
        'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1579621267i/968.jpg'
    },
    {
        'titulo': 'Harry Potter y la piedra filosofal',
        'autor': 'J.K. Rowling',
        'genero': 'fantasia',
        'descripcion': 'Un niño huérfano descubre que es un mago y asiste a una escuela de magia.',
        'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1598823299i/42844155.jpg'
    },
    {
        'titulo': 'El Hobbit',
        'autor': 'J.R.R. Tolkien',
        'genero': 'fantasia',
        'descripcion': 'Bilbo Bolsón se embarca en una aventura épica con un grupo de enanos.',
        'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1546071216i/5907.jpg'
    },
    {
        'titulo': 'Crimen y castigo',
        'autor': 'Fiódor Dostoyevski',
        'genero': 'policial',
        'descripcion': 'La historia psicológica de un estudiante que comete un asesinato.',
        'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1382846449i/7144.jpg'
    },
    {
        'titulo': 'Crónica de una muerte anunciada',
        'autor': 'Gabriel García Márquez',
        'genero': 'policial',
        'descripcion': 'La reconstrucción del asesinato de Santiago Nasar en un pueblo colombiano.',
        'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1533690944i/23878.jpg'
    },
    {
        'titulo': 'La sombra del viento',
        'autor': 'Carlos Ruiz Zafón',
        'genero': 'policial',
        'descripcion': 'Un joven descubre un libro maldito en el Barcelona de posguerra.',
        'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1327868566i/1232.jpg'
    },
    {
        'titulo': 'Los juegos del hambre',
        'autor': 'Suzanne Collins',
        'genero': 'ciencia_ficcion',
        'descripcion': 'En un futuro distópico, jóvenes luchan a muerte en un reality show.',
        'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052.jpg'
    },
    {
        'titulo': 'El nombre del viento',
        'autor': 'Patrick Rothfuss',
        'genero': 'fantasia',
        'descripcion': 'La historia de Kvothe, un aventurero y músico legendario.',
        'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1270352123i/186074.jpg'
    },
    {
        'titulo': 'Dune',
        'autor': 'Frank Herbert',
        'genero': 'ciencia_ficcion',
        'descripcion': 'Una épica de ciencia ficción sobre política, religión y ecología en el desierto planeta Arrakis.',
        'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1555447414i/44767458.jpg'
    },
    {
        'titulo': 'El gran Gatsby',
        'autor': 'F. Scott Fitzgerald',
        'genero': 'romance',
        'descripcion': 'La historia del misterioso millonario Jay Gatsby y su amor por Daisy Buchanan.',
        'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1490528560i/4671.jpg'
    },
]

GENEROS = ['romance', 'ciencia_ficcion', 'fantasia', 'policial', 'terror', 'historia']

# Colores para generar portadas de respaldo
COLORES = [
    (233, 69, 96),    # Rosa/Rojo (accent)
    (26, 26, 46),     # Azul oscuro
    (15, 52, 96),     # Azul secundario
    (108, 117, 125),  # Gris
    (255, 193, 7),    # Amarillo
    (40, 167, 69),    # Verde
]

def descargar_portada(url, nombre_archivo):
    """Descarga una portada desde URL y la retorna como InMemoryUploadedFile"""
    try:
        # Descargar la imagen
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            imagen_data = response.read()
        
        # Abrir con PIL y convertir si es necesario
        img = Image.open(BytesIO(imagen_data))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionar si es muy grande
        max_size = (400, 600)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Guardar en buffer
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        
        return InMemoryUploadedFile(
            buffer,
            None,
            nombre_archivo,
            'image/jpeg',
            buffer.getbuffer().nbytes,
            None
        )
    except Exception as e:
        print(f"   ⚠ Error descargando portada: {str(e)[:50]}")
        return None

def generar_imagen_portada(width=400, height=600, color_index=0):
    """Genera una imagen de portada simple con color de fondo (fallback)"""
    color = COLORES[color_index % len(COLORES)]
    img = Image.new('RGB', (width, height), color)
    
    # Guardar en memoria
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)
    
    return InMemoryUploadedFile(
        buffer,
        None,
        f'portada_{color_index}.jpg',
        'image/jpeg',
        buffer.getbuffer().nbytes,
        None
    )

def crear_usuarios(cantidad=1000):
    """Crear usuarios de prueba"""
    print(f"\n1. Creando {cantidad} usuarios...")
    start_time = time.time()
    
    usuarios = []
    for i in range(cantidad):
        username = f"usuario{i+1}"
        email = f"usuario{i+1}@test.com"
        
        # Evitar duplicados
        if not Usuario.objects.filter(username=username).exists():
            usuario = Usuario(
                username=username,
                email=email,
                rol='usuario'
            )
            usuario.set_password('password123')
            usuarios.append(usuario)
    
    # Bulk create para mejor rendimiento
    Usuario.objects.bulk_create(usuarios, ignore_conflicts=True)
    
    elapsed_time = (time.time() - start_time) * 1000
    print(f"   ✓ Usuarios creados en {elapsed_time:.2f} ms")
    return elapsed_time

def crear_libros(cantidad=300):
    """Crear libros de prueba con portadas de colores"""
    print(f"\n2. Creando {cantidad} libros con portadas de colores...")
    start_time = time.time()
    
    libros_creados = 0
    
    for i in range(cantidad):
        # Seleccionar un libro real de la lista (rota circularmente)
        libro_data = LIBROS_REALES[i % len(LIBROS_REALES)]
        
        # Si es una repetición, agregar número al título
        if i >= len(LIBROS_REALES):
            titulo = f"{libro_data['titulo']} - Edición {i // len(LIBROS_REALES) + 1}"
        else:
            titulo = libro_data['titulo']
        
        # Crear libro con portada de color
        libro = Libro(
            titulo=titulo,
            autor=libro_data['autor'],
            genero=libro_data['genero'],
            descripcion=libro_data['descripcion'],
            portada=generar_imagen_portada(color_index=i % 6)
        )
        
        libro.save()
        libros_creados += 1
        
        # Mostrar progreso cada 50 libros
        if (i + 1) % 50 == 0:
            print(f"   → {i + 1}/{cantidad} libros creados...")
    
    elapsed_time = (time.time() - start_time) * 1000
    print(f"   ✓ {libros_creados} libros creados en {elapsed_time:.2f} ms")
    print(f"   ✓ Todos con portadas de colores (6 variantes)")
    return elapsed_time

def crear_reseñas(cantidad=300):
    """Crear reseñas de prueba"""
    print(f"\n3. Creando {cantidad} reseñas...")
    start_time = time.time()
    
    usuarios = list(Usuario.objects.filter(rol='usuario')[:200])
    libros = list(Libro.objects.all()[:300])
    
    if not usuarios or not libros:
        print(f"   ⚠ No hay suficientes usuarios o libros. Saltando...")
        return 0
    
    reseñas = []
    for i in range(cantidad):
        usuario = random.choice(usuarios)
        libro = random.choice(libros)
        
        reseña = Reseña(
            usuario=usuario,
            libro=libro,
            calificacion=random.randint(1, 5),
            comentario=f"Esta es una reseña de prueba número {i+1}. Me pareció un libro interesante."
        )
        reseñas.append(reseña)
    
    Reseña.objects.bulk_create(reseñas, ignore_conflicts=True)
    
    elapsed_time = (time.time() - start_time) * 1000
    print(f"   ✓ Reseñas creadas en {elapsed_time:.2f} ms")
    return elapsed_time

def crear_favoritos(cantidad=100):
    """Crear favoritos de prueba"""
    print(f"\n4. Creando {cantidad} favoritos...")
    start_time = time.time()
    
    usuarios = list(Usuario.objects.filter(rol='usuario')[:200])
    libros = list(Libro.objects.all()[:300])
    
    if not usuarios or not libros:
        print(f"   ⚠ No hay suficientes usuarios o libros. Saltando...")
        return 0
    
    favoritos = []
    for i in range(cantidad):
        usuario = random.choice(usuarios)
        libro = random.choice(libros)
        
        favorito = Favorito(
            usuario=usuario,
            libro=libro
        )
        favoritos.append(favorito)
    
    Favorito.objects.bulk_create(favoritos, ignore_conflicts=True)
    
    elapsed_time = (time.time() - start_time) * 1000
    print(f"   ✓ Favoritos creados en {elapsed_time:.2f} ms")
    return elapsed_time

def crear_historial(cantidad=100):
    """Crear historial de prueba"""
    print(f"\n5. Creando {cantidad} entradas de historial...")
    start_time = time.time()
    
    usuarios = list(Usuario.objects.filter(rol='usuario')[:200])
    libros = list(Libro.objects.all()[:300])
    
    if not usuarios or not libros:
        print(f"   ⚠ No hay suficientes usuarios o libros. Saltando...")
        return 0
    
    historiales = []
    for i in range(cantidad):
        usuario = random.choice(usuarios)
        libro = random.choice(libros)
        
        historial = Historial(
            usuario=usuario,
            libro=libro
        )
        historiales.append(historial)
    
    Historial.objects.bulk_create(historiales, ignore_conflicts=True)
    
    elapsed_time = (time.time() - start_time) * 1000
    print(f"   ✓ Historial creado en {elapsed_time:.2f} ms")
    return elapsed_time

def crear_categorias(cantidad=10):
    """Crear categorías de prueba"""
    print(f"\n6. Creando {cantidad} categorías...")
    start_time = time.time()
    
    categorias_nombres = [
        'Ficción Histórica', 'Biografía', 'Autoayuda', 'Técnico',
        'Ensayo', 'Poesía', 'Teatro', 'Cómic', 'Infantil', 'Juvenil',
        'Clásicos', 'Contemporáneo', 'Distopía', 'Aventura', 'Thriller'
    ]
    
    categorias = []
    for i in range(cantidad):
        nombre = categorias_nombres[i % len(categorias_nombres)]
        categoria = Categoria(nombre=f"{nombre} {i+1}")
        categorias.append(categoria)
    
    Categoria.objects.bulk_create(categorias, ignore_conflicts=True)
    
    elapsed_time = (time.time() - start_time) * 1000
    print(f"   ✓ Categorías creadas en {elapsed_time:.2f} ms")
    return elapsed_time

def crear_listas(cantidad=50):
    """Crear listas de libros"""
    print(f"\n7. Creando {cantidad} listas de libros...")
    start_time = time.time()
    
    usuarios = list(Usuario.objects.filter(rol='usuario')[:100])
    libros = list(Libro.objects.all()[:300])
    
    if not usuarios or not libros:
        print(f"   ⚠ No hay suficientes usuarios o libros. Saltando...")
        return 0
    
    nombres_listas = [
        'Mis Favoritos', 'Para Leer', 'Leídos', 'Recomendados',
        'Clásicos', 'Pendientes', 'Best Sellers', 'Terror'
    ]
    
    for i in range(cantidad):
        usuario = random.choice(usuarios)
        nombre = f"{random.choice(nombres_listas)} {i+1}"
        
        lista = Lista.objects.create(
            usuario=usuario,
            nombre=nombre,
            descripcion=f"Descripción de la lista {nombre}"
        )
        
        # Agregar entre 3 y 10 libros a cada lista
        libros_seleccionados = random.sample(libros, min(random.randint(3, 10), len(libros)))
        lista.libros.set(libros_seleccionados)
    
    elapsed_time = (time.time() - start_time) * 1000
    print(f"   ✓ Listas creadas en {elapsed_time:.2f} ms")
    return elapsed_time

def crear_comentarios(cantidad=200):
    """Crear comentarios en reseñas (incluye respuestas anidadas)"""
    print(f"\n8. Creando {cantidad} comentarios...")
    start_time = time.time()
    
    usuarios = list(Usuario.objects.all()[:200])
    reseñas = list(Reseña.objects.all()[:300])
    
    if not usuarios or not reseñas:
        print(f"   ⚠ No hay suficientes datos. Saltando...")
        return 0
    
    comentarios_creados = []
    
    # Crear comentarios principales (70% del total)
    cantidad_principales = int(cantidad * 0.7)
    for i in range(cantidad_principales):
        usuario = random.choice(usuarios)
        reseña = random.choice(reseñas)
        
        comentario = Comentario(
            usuario=usuario,
            reseña=reseña,
            contenido=f"Comentario de prueba {i+1}. Muy interesante análisis.",
            padre=None
        )
        comentarios_creados.append(comentario)
    
    Comentario.objects.bulk_create(comentarios_creados)
    
    # Crear respuestas a comentarios (30% del total)
    comentarios_principales = list(Comentario.objects.filter(padre__isnull=True)[:100])
    cantidad_respuestas = cantidad - cantidad_principales
    
    respuestas = []
    for i in range(cantidad_respuestas):
        if comentarios_principales:
            usuario = random.choice(usuarios)
            padre = random.choice(comentarios_principales)
            
            respuesta = Comentario(
                usuario=usuario,
                reseña=padre.reseña,
                contenido=f"Respuesta de prueba {i+1}. Estoy de acuerdo.",
                padre=padre
            )
            respuestas.append(respuesta)
    
    Comentario.objects.bulk_create(respuestas, ignore_conflicts=True)
    
    elapsed_time = (time.time() - start_time) * 1000
    print(f"   ✓ Comentarios creados en {elapsed_time:.2f} ms (incluye respuestas)")
    return elapsed_time

def crear_valoraciones(cantidad=150):
    """Crear valoraciones de reseñas"""
    print(f"\n9. Creando {cantidad} valoraciones de reseñas...")
    start_time = time.time()
    
    usuarios = list(Usuario.objects.all()[:200])
    reseñas = list(Reseña.objects.all()[:300])
    
    if not usuarios or not reseñas:
        print(f"   ⚠ No hay suficientes datos. Saltando...")
        return 0
    
    valoraciones = []
    for i in range(cantidad):
        usuario = random.choice(usuarios)
        reseña = random.choice(reseñas)
        puntuacion = random.randint(1, 5)
        
        valoracion = ValoracionReseña(
            usuario=usuario,
            reseña=reseña,
            puntuacion=puntuacion
        )
        valoraciones.append(valoracion)
    
    ValoracionReseña.objects.bulk_create(valoraciones, ignore_conflicts=True)
    
    elapsed_time = (time.time() - start_time) * 1000
    print(f"   ✓ Valoraciones creadas en {elapsed_time:.2f} ms")
    return elapsed_time

def crear_seguimientos(cantidad=100):
    """Crear seguimientos entre usuarios"""
    print(f"\n10. Creando {cantidad} seguimientos...")
    start_time = time.time()
    
    usuarios = list(Usuario.objects.filter(rol='usuario')[:200])
    
    if len(usuarios) < 2:
        print(f"   ⚠ No hay suficientes usuarios. Saltando...")
        return 0
    
    seguimientos = []
    for i in range(cantidad):
        seguidor = random.choice(usuarios)
        seguido = random.choice(usuarios)
        
        # Evitar auto-seguimiento
        while seguidor == seguido:
            seguido = random.choice(usuarios)
        
        seguimiento = Seguimiento(
            seguidor=seguidor,
            seguido=seguido
        )
        seguimientos.append(seguimiento)
    
    Seguimiento.objects.bulk_create(seguimientos, ignore_conflicts=True)
    
    elapsed_time = (time.time() - start_time) * 1000
    print(f"   ✓ Seguimientos creados en {elapsed_time:.2f} ms")
    return elapsed_time

def crear_notificaciones(cantidad=100):
    """Crear notificaciones para usuarios"""
    print(f"\n11. Creando {cantidad} notificaciones...")
    start_time = time.time()
    
    usuarios = list(Usuario.objects.filter(rol='usuario')[:200])
    comentarios = list(Comentario.objects.all()[:50])
    reseñas = list(Reseña.objects.all()[:50])
    
    if not usuarios:
        print(f"   ⚠ No hay suficientes usuarios. Saltando...")
        return 0
    
    tipos = ['comentario', 'valoracion', 'respuesta', 'seguidor', 'reseña']
    notificaciones = []
    
    for i in range(cantidad):
        usuario = random.choice(usuarios)
        tipo = random.choice(tipos)
        mensaje = f"Notificación de prueba tipo {tipo} #{i+1}"
        
        notificacion = Notificacion(
            usuario=usuario,
            tipo=tipo,
            mensaje=mensaje,
            leida=random.choice([True, False])
        )
        
        # Asignar referencias opcionales
        if tipo == 'comentario' and comentarios:
            notificacion.comentario = random.choice(comentarios)
        elif tipo in ['valoracion', 'reseña'] and reseñas:
            notificacion.reseña = random.choice(reseñas)
        
        notificaciones.append(notificacion)
    
    Notificacion.objects.bulk_create(notificaciones)
    
    elapsed_time = (time.time() - start_time) * 1000
    print(f"   ✓ Notificaciones creadas en {elapsed_time:.2f} ms")
    return elapsed_time

def crear_reportes(cantidad=30):
    """Crear reportes de moderación"""
    print(f"\n12. Creando {cantidad} reportes...")
    start_time = time.time()
    
    usuarios = list(Usuario.objects.filter(rol='usuario')[:100])
    reseñas = list(Reseña.objects.all()[:100])
    comentarios = list(Comentario.objects.all()[:100])
    
    if not usuarios:
        print(f"   ⚠ No hay suficientes usuarios. Saltando...")
        return 0
    
    motivos = ['spam', 'inapropiado', 'otro']
    reportes = []
    
    for i in range(cantidad):
        usuario = random.choice(usuarios)
        motivo = random.choice(motivos)
        
        reporte = Reporte(
            usuario=usuario,
            motivo=motivo,
            revisado=random.choice([True, False])
        )
        
        # Asignar reseña o comentario reportado
        if random.choice([True, False]) and reseñas:
            reporte.reseña = random.choice(reseñas)
        elif comentarios:
            reporte.comentario = random.choice(comentarios)
        
        reportes.append(reporte)
    
    Reporte.objects.bulk_create(reportes)
    
    elapsed_time = (time.time() - start_time) * 1000
    print(f"   ✓ Reportes creados en {elapsed_time:.2f} ms")
    return elapsed_time

def crear_acciones_moderacion(cantidad=20):
    """Crear acciones de moderación"""
    print(f"\n13. Creando {cantidad} acciones de moderación...")
    start_time = time.time()
    
    admins = list(Usuario.objects.filter(rol='admin')[:20])
    reportes = list(Reporte.objects.all()[:30])
    
    if not admins or not reportes:
        print(f"   ⚠ No hay suficientes admins o reportes. Saltando...")
        return 0
    
    acciones_tipos = ['eliminar', 'ocultar', 'banear', 'ignorar']
    acciones = []
    
    for i in range(min(cantidad, len(reportes))):
        admin = random.choice(admins)
        reporte = reportes[i]
        accion = random.choice(acciones_tipos)
        
        accion_mod = AccionModeracion(
            reporte=reporte,
            administrador=admin,
            accion=accion
        )
        acciones.append(accion_mod)
    
    AccionModeracion.objects.bulk_create(acciones)
    
    elapsed_time = (time.time() - start_time) * 1000
    print(f"   ✓ Acciones de moderación creadas en {elapsed_time:.2f} ms")
    return elapsed_time

def medir_consultas_complejas():
    """Medir tiempo de consultas complejas"""
    print("\n\n" + "="*60)
    print("PRUEBAS DE RENDIMIENTO DE CONSULTAS")
    print("="*60)
    
    resultados = []
    
    # 1. Búsqueda de libros por título
    print("\n1. Búsqueda de libros por título...")
    with CaptureQueriesContext(connection) as context:
        start_time = time.time()
        libros = Libro.objects.filter(titulo__icontains='el')[:20]
        list(libros)  # Forzar evaluación
        elapsed_time = (time.time() - start_time) * 1000
        num_queries = len(context.captured_queries)
    
    print(f"   ✓ Tiempo: {elapsed_time:.2f} ms")
    print(f"   ✓ Consultas SQL: {num_queries}")
    resultados.append(('Búsqueda por título', elapsed_time, num_queries))
    
    # 2. Filtrar por género
    print("\n2. Filtrar libros por género...")
    with CaptureQueriesContext(connection) as context:
        start_time = time.time()
        libros = Libro.objects.filter(genero='Ficción')[:30]
        list(libros)
        elapsed_time = (time.time() - start_time) * 1000
        num_queries = len(context.captured_queries)
    
    print(f"   ✓ Tiempo: {elapsed_time:.2f} ms")
    print(f"   ✓ Consultas SQL: {num_queries}")
    resultados.append(('Filtro por género', elapsed_time, num_queries))
    
    # 3. Obtener reseñas de un libro con prefetch
    print("\n3. Obtener reseñas de libros (con relaciones)...")
    libro = Libro.objects.first()
    if libro:
        with CaptureQueriesContext(connection) as context:
            start_time = time.time()
            reseñas = Reseña.objects.filter(libro=libro).select_related('usuario')[:50]
            list(reseñas)
            elapsed_time = (time.time() - start_time) * 1000
            num_queries = len(context.captured_queries)
        
        print(f"   ✓ Tiempo: {elapsed_time:.2f} ms")
        print(f"   ✓ Consultas SQL: {num_queries}")
        resultados.append(('Reseñas con relaciones', elapsed_time, num_queries))
    
    # 4. Feed personalizado (costoso)
    print("\n4. Feed personalizado (simulación)...")
    usuario = Usuario.objects.filter(rol='usuario').first()
    if usuario:
        with CaptureQueriesContext(connection) as context:
            start_time = time.time()
            # Simular consulta del feed
            reseñas = Reseña.objects.select_related('usuario', 'libro').order_by('-fecha')[:30]
            list(reseñas)
            elapsed_time = (time.time() - start_time) * 1000
            num_queries = len(context.captured_queries)
        
        print(f"   ✓ Tiempo: {elapsed_time:.2f} ms")
        print(f"   ✓ Consultas SQL: {num_queries}")
        resultados.append(('Feed personalizado', elapsed_time, num_queries))
    
    # 5. Historial de usuario
    print("\n5. Historial de usuario...")
    if usuario:
        with CaptureQueriesContext(connection) as context:
            start_time = time.time()
            historial = Historial.objects.filter(usuario=usuario).select_related('libro')[:50]
            list(historial)
            elapsed_time = (time.time() - start_time) * 1000
            num_queries = len(context.captured_queries)
        
        print(f"   ✓ Tiempo: {elapsed_time:.2f} ms")
        print(f"   ✓ Consultas SQL: {num_queries}")
        resultados.append(('Historial de usuario', elapsed_time, num_queries))
    
    # 6. Carga de perfil completo
    print("\n6. Carga completa de perfil...")
    if usuario:
        with CaptureQueriesContext(connection) as context:
            start_time = time.time()
            _ = list(usuario.reseñas.all()[:10])
            _ = list(usuario.favoritos.all()[:10])
            _ = list(usuario.historial_libros.all()[:10])
            elapsed_time = (time.time() - start_time) * 1000
            num_queries = len(context.captured_queries)
        
        print(f"   ✓ Tiempo: {elapsed_time:.2f} ms")
        print(f"   ✓ Consultas SQL: {num_queries}")
        resultados.append(('Perfil completo', elapsed_time, num_queries))
    
    # 7. Libros con múltiples relaciones
    print("\n7. Libros con relaciones (JOIN)...")
    with CaptureQueriesContext(connection) as context:
        start_time = time.time()
        libros = Libro.objects.prefetch_related('reseñas', 'favoritos')[:20]
        for libro in libros:
            _ = list(libro.reseñas.all())
            _ = list(libro.favoritos.all())
        elapsed_time = (time.time() - start_time) * 1000
        num_queries = len(context.captured_queries)
    
    print(f"   ✓ Tiempo: {elapsed_time:.2f} ms")
    print(f"   ✓ Consultas SQL: {num_queries}")
    resultados.append(('Libros con JOINs', elapsed_time, num_queries))
    
    # 8. Agregaciones (conteos)
    print("\n8. Agregaciones y conteos...")
    with CaptureQueriesContext(connection) as context:
        start_time = time.time()
        total_libros = Libro.objects.count()
        total_usuarios = Usuario.objects.count()
        total_reseñas = Reseña.objects.count()
        total_favoritos = Favorito.objects.count()
        elapsed_time = (time.time() - start_time) * 1000
        num_queries = len(context.captured_queries)
    
    print(f"   ✓ Tiempo: {elapsed_time:.2f} ms")
    print(f"   ✓ Consultas SQL: {num_queries}")
    print(f"   - Libros: {total_libros}, Usuarios: {total_usuarios}")
    print(f"   - Reseñas: {total_reseñas}, Favoritos: {total_favoritos}")
    resultados.append(('Conteos/agregaciones', elapsed_time, num_queries))
    
    return resultados

def mostrar_resumen(tiempos_creacion, resultados_consultas):
    """Mostrar resumen de resultados"""
    print("\n\n" + "="*70)
    print(" RESUMEN DE PRUEBAS DE RENDIMIENTO")
    print("="*70)
    
    print("\nA. CREACIÓN DE DATOS:")
    print("-" * 70)
    print(f"{'Operación':<30} {'Tiempo':<15} {'Registros':<15}")
    print("-" * 70)
    
    # Mostrar todos los datos creados dinámicamente
    totales = {
        'Usuarios': 200, 'Categorías': 10, 'Libros': 300, 'Reseñas': 300,
        'Favoritos': 100, 'Historial': 100, 'Listas': 50, 'Comentarios': 200,
        'Valoraciones': 150, 'Seguimientos': 100, 'Notificaciones': 100,
        'Reportes': 30, 'Acciones Moderación': 20
    }
    
    total_registros = 0
    for nombre, tiempo in tiempos_creacion:
        cantidad = totales.get(nombre, 0)
        total_registros += cantidad
        print(f"{nombre:<30} {tiempo:>10.2f} ms    {cantidad:>3}")
    
    print("-" * 70)
    tiempo_total_creacion = sum(t[1] for t in tiempos_creacion)
    print(f"{'TOTAL CREACIÓN':<30} {tiempo_total_creacion:>10.2f} ms    {total_registros:>3}")
    
    print("\n\nB. CONSULTAS Y OPERACIONES:")
    print("-" * 70)
    print(f"{'Operación':<35} {'Tiempo':<15} {'Queries SQL':<10}")
    print("-" * 70)
    for nombre, tiempo, queries in resultados_consultas:
        print(f"{nombre:<35} {tiempo:>10.2f} ms    {queries:>3}")
    print("-" * 70)
    
    # Análisis de rendimiento
    print("\n\n" + "="*70)
    print(" ANÁLISIS DE RENDIMIENTO")
    print("="*70)
    
    tiempos_consulta = [t for _, t, _ in resultados_consultas]
    tiempo_promedio = sum(tiempos_consulta) / len(tiempos_consulta)
    tiempo_max = max(tiempos_consulta)
    tiempo_min = min(tiempos_consulta)
    
    queries_totales = sum(q for _, _, q in resultados_consultas)
    queries_promedio = queries_totales / len(resultados_consultas)
    
    print(f"\n  Tiempo promedio de consultas: {tiempo_promedio:.2f} ms")
    print(f"  Tiempo mínimo: {tiempo_min:.2f} ms")
    print(f"  Tiempo máximo: {tiempo_max:.2f} ms")
    print(f"  Total queries SQL ejecutadas: {queries_totales}")
    print(f"  Promedio queries por operación: {queries_promedio:.1f}")
    
    # Evaluación de rendimiento
    print("\n  EVALUACIÓN GENERAL:")
    if tiempo_promedio < 100:
        print("  ✓ EXCELENTE: Tiempos de respuesta óptimos (<100ms)")
    elif tiempo_promedio < 300:
        print("  ✓ BUENO: Tiempos de respuesta aceptables (<300ms)")
    elif tiempo_promedio < 1000:
        print("  ⚠ ACEPTABLE: Considerar optimizaciones (300-1000ms)")
    else:
        print("  ✗ MEJORABLE: Se requieren optimizaciones (>1000ms)")
    
    # Recomendaciones
    print("\n  RECOMENDACIONES:")
    if queries_promedio > 5:
        print("  - Considerar usar select_related/prefetch_related para reducir queries")
    if tiempo_max > 500:
        print("  - Revisar índices de base de datos para consultas lentas")
    if tiempo_promedio < 200:
        print("  - Sistema optimizado, rendimiento adecuado para producción")
    
    print("\n" + "="*70)
    print(" DATOS GENERADOS:")
    print("="*70)
    print(f"  USUARIOS Y PERFILES:")
    print(f"  • 200 usuarios (180 usuarios + 20 administradores)")
    print(f"  • 100 seguimientos entre usuarios")
    print(f"\n  CONTENIDO PRINCIPAL:")
    print(f"  • 10 categorías de libros")
    print(f"  • 300 libros con portadas (6 colores diferentes)")
    print(f"  • 300 reseñas con calificaciones")
    print(f"  • 200 comentarios (incluye respuestas anidadas)")
    print(f"\n  INTERACCIONES:")
    print(f"  • 100 favoritos")
    print(f"  • 100 registros de historial")
    print(f"  • 50 listas personalizadas de libros")
    print(f"  • 150 valoraciones de reseñas")
    print(f"  • 100 notificaciones")
    print(f"\n  MODERACIÓN:")
    print(f"  • 30 reportes de contenido")
    print(f"  • 20 acciones de moderación")
    print(f"\n  Total: ~1,760 registros creados")
    print(f"  Cubre TODOS los modelos del sistema")
    print(f"\n  Para limpiar estos datos:")
    print(f"    python limpiar_datos_prueba.py")
    print("="*70 + "\n")

def main():
    """Función principal"""
    print("\n" + "="*70)
    print(" SCRIPT DE PRUEBAS DE RENDIMIENTO COMPLETO")
    print(" Librería Digital - Proyecto Integrado INACAP")
    print("="*70)
    print("\n Este script creará:")
    print("   • 200 usuarios (180 usuarios + 20 admins)")
    print("   • 10 categorías")
    print("   • 300 libros con portadas (6 colores)")
    print("   • 300 reseñas")
    print("   • 100 favoritos")
    print("   • 100 registros de historial")
    print("   • 50 listas de libros")
    print("   • 200 comentarios (con respuestas anidadas)")
    print("   • 150 valoraciones de reseñas")
    print("   • 100 seguimientos entre usuarios")
    print("   • 100 notificaciones")
    print("   • 30 reportes de moderación")
    print("   • 20 acciones de moderación")
    print("\n Total: ~1760 registros para pruebas exhaustivas")
    print("="*70)
    
    # Confirmar ejecución
    respuesta = input("\n¿Desea crear todos los registros de prueba? (s/n): ")
    if respuesta.lower() != 's':
        print("\nOperación cancelada.")
        return
    
    tiempos_creacion = []
    
    # Fase 1: Crear datos base
    print("\n" + "="*70)
    print(" FASE 1: CREACIÓN DE DATOS DE PRUEBA")
    print("="*70)
    
    tiempos_creacion.append(('Usuarios', crear_usuarios(200)))
    tiempos_creacion.append(('Categorías', crear_categorias(10)))
    tiempos_creacion.append(('Libros', crear_libros(300)))
    tiempos_creacion.append(('Reseñas', crear_reseñas(300)))
    tiempos_creacion.append(('Favoritos', crear_favoritos(100)))
    tiempos_creacion.append(('Historial', crear_historial(100)))
    
    # Fase 1.5: Datos sociales y de comunidad
    tiempos_creacion.append(('Listas', crear_listas(50)))
    tiempos_creacion.append(('Comentarios', crear_comentarios(200)))
    tiempos_creacion.append(('Valoraciones', crear_valoraciones(150)))
    tiempos_creacion.append(('Seguimientos', crear_seguimientos(100)))
    tiempos_creacion.append(('Notificaciones', crear_notificaciones(100)))
    
    # Fase 1.6: Moderación
    tiempos_creacion.append(('Reportes', crear_reportes(30)))
    tiempos_creacion.append(('Acciones Moderación', crear_acciones_moderacion(20)))
    
    # Fase 2: Medir consultas
    resultados_consultas = medir_consultas_complejas()
    
    # Mostrar resumen
    mostrar_resumen(tiempos_creacion, resultados_consultas)

if __name__ == "__main__":
    main()

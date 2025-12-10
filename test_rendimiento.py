"""
Script de pruebas de rendimiento para la Librería Digital (OPTIMIZADO)
Genera datos de prueba y mide tiempos de respuesta
Versión RÁPIDA: Portadas de colores generadas localmente (sin descargas)

VENTAJAS:
✓ 100 libros con portadas de colores (instantáneo)
✓ Queries optimizadas con select_related/prefetch_related
✓ Progress bar visual
✓ Sin dependencia de conexión a internet
✓ Ideal para pruebas rápidas y repetidas
"""

import os
import django
import time
from datetime import datetime, timedelta
import random
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

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

# Configuración optimizada
CONFIG = {
    'show_progress': True,       # Mostrar barra de progreso
    'bulk_size': 50,             # Tamaño de lotes para bulk_create
}

# Base de datos extendida: 100 LIBROS FAMOSOS (sin URLs - portadas de colores)
LIBROS_REALES = [
    # Literatura Latinoamericana (1-10)
    {'titulo': 'Cien años de soledad', 'autor': 'Gabriel García Márquez', 'genero': 'fantasia', 
     'descripcion': 'La historia de la familia Buendía a lo largo de siete generaciones en Macondo.'},
    {'titulo': 'Rayuela', 'autor': 'Julio Cortázar', 'genero': 'fantasia',
     'descripcion': 'Una novela experimental que puede leerse de múltiples formas.'},
    {'titulo': 'La casa de los espíritus', 'autor': 'Isabel Allende', 'genero': 'fantasia',
     'descripcion': 'Saga familiar que mezcla realismo mágico y política en Chile.'},
    {'titulo': 'Pedro Páramo', 'autor': 'Juan Rulfo', 'genero': 'fantasia',
     'descripcion': 'Un hombre busca a su padre en un pueblo de muertos.'},
    {'titulo': 'Ficciones', 'autor': 'Jorge Luis Borges', 'genero': 'fantasia',
     'descripcion': 'Colección de cuentos metafísicos y laberintos literarios.'},
    {'titulo': 'El amor en los tiempos del cólera', 'autor': 'Gabriel García Márquez', 'genero': 'romance',
     'descripcion': 'Un amor que espera más de cincuenta años.'},
    {'titulo': 'El túnel', 'autor': 'Ernesto Sabato', 'genero': 'policial',
     'descripcion': 'Un pintor obsesionado confiesa un crimen pasional.'},
    {'titulo': 'Crónica de una muerte anunciada', 'autor': 'Gabriel García Márquez', 'genero': 'policial',
     'descripcion': 'La reconstrucción del asesinato de Santiago Nasar.'},
    {'titulo': 'El coronel no tiene quien le escriba', 'autor': 'Gabriel García Márquez', 'genero': 'historia',
     'descripcion': 'Un coronel espera una pensión que nunca llega.'},
    {'titulo': 'Los detectives salvajes', 'autor': 'Roberto Bolaño', 'genero': 'policial',
     'descripcion': 'Búsqueda de una poeta desaparecida en el México de los 70.'},
    
    # Clásicos Universales (11-25)
    {'titulo': 'Don Quijote de la Mancha', 'autor': 'Miguel de Cervantes', 'genero': 'historia',
     'descripcion': 'Las aventuras del ingenioso hidalgo y su escudero Sancho Panza.'},
    {'titulo': 'Orgullo y prejuicio', 'autor': 'Jane Austen', 'genero': 'romance',
     'descripcion': 'Elizabeth Bennet y el señor Darcy en la Inglaterra del siglo XIX.'},
    {'titulo': 'Crimen y castigo', 'autor': 'Fiódor Dostoyevski', 'genero': 'policial',
     'descripcion': 'El tormento psicológico de un estudiante que comete un asesinato.'},
    {'titulo': 'Moby Dick', 'autor': 'Herman Melville', 'genero': 'historia',
     'descripcion': 'La obsesiva búsqueda del capitán Ahab por la ballena blanca.'},
    {'titulo': 'Los Miserables', 'autor': 'Victor Hugo', 'genero': 'historia',
     'descripcion': 'Jean Valjean y su redención en la Francia del siglo XIX.'},
    {'titulo': 'Anna Karenina', 'autor': 'León Tolstói', 'genero': 'romance',
     'descripcion': 'Tragedia de una mujer en la alta sociedad rusa.'},
    {'titulo': 'Guerra y paz', 'autor': 'León Tolstói', 'genero': 'historia',
     'descripcion': 'Épica sobre la invasión napoleónica de Rusia.'},
    {'titulo': 'El gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'genero': 'romance',
     'descripcion': 'Jay Gatsby y su amor imposible por Daisy Buchanan.'},
    {'titulo': 'Matar un ruiseñor', 'autor': 'Harper Lee', 'genero': 'historia',
     'descripcion': 'Racismo y justicia en el sur de Estados Unidos.'},
    {'titulo': 'El guardián entre el centeno', 'autor': 'J.D. Salinger', 'genero': 'romance',
     'descripcion': 'La rebeldía adolescente de Holden Caulfield.'},
    {'titulo': 'El retrato de Dorian Gray', 'autor': 'Oscar Wilde', 'genero': 'fantasia',
     'descripcion': 'Un hombre vende su alma por la eterna juventud.'},
    {'titulo': 'El extranjero', 'autor': 'Albert Camus', 'genero': 'historia',
     'descripcion': 'La absurda existencia de Meursault tras cometer un crimen.'},
    {'titulo': 'La metamorfosis', 'autor': 'Franz Kafka', 'genero': 'fantasia',
     'descripcion': 'Gregor Samsa despierta convertido en un insecto gigante.'},
    {'titulo': 'El proceso', 'autor': 'Franz Kafka', 'genero': 'policial',
     'descripcion': 'Josef K. es arrestado sin saber de qué se le acusa.'},
    {'titulo': 'Lolita', 'autor': 'Vladimir Nabokov', 'genero': 'romance',
     'descripcion': 'Controversia novela sobre obsesión prohibida.'},
    
    # Ciencia Ficción (26-40)
    {'titulo': '1984', 'autor': 'George Orwell', 'genero': 'ciencia_ficcion',
     'descripcion': 'Distopía totalitaria donde el Gran Hermano todo lo ve.'},
    {'titulo': 'Un mundo feliz', 'autor': 'Aldous Huxley', 'genero': 'ciencia_ficcion',
     'descripcion': 'Sociedad futurista controlada por la tecnología y las drogas.'},
    {'titulo': 'Fahrenheit 451', 'autor': 'Ray Bradbury', 'genero': 'ciencia_ficcion',
     'descripcion': 'Un futuro donde los libros están prohibidos y se queman.'},
    {'titulo': 'Dune', 'autor': 'Frank Herbert', 'genero': 'ciencia_ficcion',
     'descripcion': 'Épica espacial sobre política, religión y ecología en Arrakis.'},
    {'titulo': 'Fundación', 'autor': 'Isaac Asimov', 'genero': 'ciencia_ficcion',
     'descripcion': 'La caída del Imperio Galáctico y el plan para preservar el conocimiento.'},
    {'titulo': 'Neuromante', 'autor': 'William Gibson', 'genero': 'ciencia_ficcion',
     'descripcion': 'Pionera del cyberpunk sobre hackers y realidad virtual.'},
    {'titulo': 'La guerra de los mundos', 'autor': 'H.G. Wells', 'genero': 'ciencia_ficcion',
     'descripcion': 'Invasión marciana de la Tierra victoriana.'},
    {'titulo': 'Yo, Robot', 'autor': 'Isaac Asimov', 'genero': 'ciencia_ficcion',
     'descripcion': 'Relatos sobre robots y las tres leyes de la robótica.'},
    {'titulo': 'El marciano', 'autor': 'Andy Weir', 'genero': 'ciencia_ficcion',
     'descripcion': 'Un astronauta abandonado debe sobrevivir en Marte.'},
    {'titulo': 'Los juegos del hambre', 'autor': 'Suzanne Collins', 'genero': 'ciencia_ficcion',
     'descripcion': 'Jóvenes luchan a muerte en un reality show distópico.'},
    {'titulo': 'Divergente', 'autor': 'Veronica Roth', 'genero': 'ciencia_ficcion',
     'descripcion': 'Una sociedad dividida en facciones según virtudes.'},
    {'titulo': 'El cuento de la criada', 'autor': 'Margaret Atwood', 'genero': 'ciencia_ficcion',
     'descripcion': 'Distopía sobre una teocracia totalitaria.'},
    {'titulo': 'La carretera', 'autor': 'Cormac McCarthy', 'genero': 'ciencia_ficcion',
     'descripcion': 'Padre e hijo en un mundo post-apocalíptico.'},
    {'titulo': 'Homo Deus', 'autor': 'Yuval Noah Harari', 'genero': 'ciencia_ficcion',
     'descripcion': 'Breve historia del mañana y el futuro de la humanidad.'},
    {'titulo': 'Solaris', 'autor': 'Stanisław Lem', 'genero': 'ciencia_ficcion',
     'descripcion': 'Encuentro con una inteligencia alien incomprensible.'},
    
    # Fantasía (41-55)
    {'titulo': 'El Señor de los Anillos', 'autor': 'J.R.R. Tolkien', 'genero': 'fantasia',
     'descripcion': 'La épica aventura para destruir el Anillo Único.'},
    {'titulo': 'El Hobbit', 'autor': 'J.R.R. Tolkien', 'genero': 'fantasia',
     'descripcion': 'Bilbo Bolsón se embarca en una aventura inesperada.'},
    {'titulo': 'Harry Potter y la piedra filosofal', 'autor': 'J.K. Rowling', 'genero': 'fantasia',
     'descripcion': 'Un niño descubre que es mago y asiste a Hogwarts.'},
    {'titulo': 'El nombre del viento', 'autor': 'Patrick Rothfuss', 'genero': 'fantasia',
     'descripcion': 'Kvothe narra su vida como aventurero y músico legendario.'},
    {'titulo': 'Canción de hielo y fuego', 'autor': 'George R.R. Martin', 'genero': 'fantasia',
     'descripcion': 'Intrigas políticas y batallas épicas en Poniente.'},
    {'titulo': 'El principito', 'autor': 'Antoine de Saint-Exupéry', 'genero': 'fantasia',
     'descripcion': 'Cuento poético sobre un pequeño príncipe que viaja entre planetas.'},
    {'titulo': 'Alicia en el país de las maravillas', 'autor': 'Lewis Carroll', 'genero': 'fantasia',
     'descripcion': 'Las aventuras surrealistas de Alicia en un mundo fantástico.'},
    {'titulo': 'Las crónicas de Narnia', 'autor': 'C.S. Lewis', 'genero': 'fantasia',
     'descripcion': 'Niños descubren un mundo mágico dentro de un armario.'},
    {'titulo': 'Charlie y la fábrica de chocolate', 'autor': 'Roald Dahl', 'genero': 'fantasia',
     'descripcion': 'Un niño pobre gana un tour por la fábrica de Willy Wonka.'},
    {'titulo': 'Matilda', 'autor': 'Roald Dahl', 'genero': 'fantasia',
     'descripcion': 'Una niña superdotada con poderes telequinéticos.'},
    {'titulo': 'Percy Jackson y el ladrón del rayo', 'autor': 'Rick Riordan', 'genero': 'fantasia',
     'descripcion': 'Un chico descubre que es hijo de un dios griego.'},
    {'titulo': 'Eragon', 'autor': 'Christopher Paolini', 'genero': 'fantasia',
     'descripcion': 'Un joven granjero encuentra un huevo de dragón.'},
    {'titulo': 'La historia interminable', 'autor': 'Michael Ende', 'genero': 'fantasia',
     'descripcion': 'Un niño descubre un libro mágico que cambia la realidad.'},
    {'titulo': 'El león, la bruja y el ropero', 'autor': 'C.S. Lewis', 'genero': 'fantasia',
     'descripcion': 'Cuatro hermanos descubren el mundo de Narnia.'},
    {'titulo': 'Stardust', 'autor': 'Neil Gaiman', 'genero': 'fantasia',
     'descripcion': 'Un joven cruza un muro hacia un reino mágico.'},
    
    # Policial y Misterio (56-70)
    {'titulo': 'El código Da Vinci', 'autor': 'Dan Brown', 'genero': 'policial',
     'descripcion': 'Thriller que mezcla arte, historia y conspiración.'},
    {'titulo': 'La sombra del viento', 'autor': 'Carlos Ruiz Zafón', 'genero': 'policial',
     'descripcion': 'Misterio en el Barcelona de posguerra sobre un libro maldito.'},
    {'titulo': 'Los crímenes de la calle Morgue', 'autor': 'Edgar Allan Poe', 'genero': 'policial',
     'descripcion': 'El primer relato de detectives de la literatura moderna.'},
    {'titulo': 'El sabueso de los Baskerville', 'autor': 'Arthur Conan Doyle', 'genero': 'policial',
     'descripcion': 'Sherlock Holmes investiga una maldición familiar.'},
    {'titulo': 'El nombre de la rosa', 'autor': 'Umberto Eco', 'genero': 'policial',
     'descripcion': 'Misterio medieval en una abadía benedictina.'},
    {'titulo': 'Perfume', 'autor': 'Patrick Süskind', 'genero': 'policial',
     'descripcion': 'Un asesino con sentido del olfato extraordinario.'},
    {'titulo': 'La chica del tren', 'autor': 'Paula Hawkins', 'genero': 'policial',
     'descripcion': 'Thriller psicológico sobre una mujer que presencia algo terrible.'},
    {'titulo': 'Asesinato en el Orient Express', 'autor': 'Agatha Christie', 'genero': 'policial',
     'descripcion': 'Hércules Poirot investiga un asesinato en un tren.'},
    {'titulo': 'La verdad sobre el caso Harry Quebert', 'autor': 'Joël Dicker', 'genero': 'policial',
     'descripcion': 'Un escritor investiga el pasado oscuro de su mentor.'},
    {'titulo': 'El silencio de los corderos', 'autor': 'Thomas Harris', 'genero': 'policial',
     'descripcion': 'Una agente del FBI busca ayuda de un asesino caníbal.'},
    {'titulo': 'Gone Girl', 'autor': 'Gillian Flynn', 'genero': 'policial',
     'descripcion': 'La desaparición de una mujer revela oscuros secretos matrimoniales.'},
    {'titulo': 'El psicoanalista', 'autor': 'John Katzenbach', 'genero': 'policial',
     'descripcion': 'Un psiquiatra debe resolver un acertijo mortal.'},
    {'titulo': 'La niebla y la doncella', 'autor': 'Lorenzo Silva', 'genero': 'policial',
     'descripcion': 'Investigación de un crimen en la España contemporánea.'},
    {'titulo': 'Los hombres que no amaban a las mujeres', 'autor': 'Stieg Larsson', 'genero': 'policial',
     'descripcion': 'Un periodista y una hacker investigan una desaparición.'},
    {'titulo': 'El visitante', 'autor': 'Stephen King', 'genero': 'policial',
     'descripcion': 'Un detective investiga un crimen con elementos sobrenaturales.'},
    
    # Terror (71-80)
    {'titulo': 'It (Eso)', 'autor': 'Stephen King', 'genero': 'terror',
     'descripcion': 'Un payaso demoníaco aterroriza un pueblo de Maine.'},
    {'titulo': 'El resplandor', 'autor': 'Stephen King', 'genero': 'terror',
     'descripcion': 'Una familia atrapada en un hotel embrujado en invierno.'},
    {'titulo': 'Carrie', 'autor': 'Stephen King', 'genero': 'terror',
     'descripcion': 'Una adolescente con poderes telequinéticos se venga.'},
    {'titulo': 'Drácula', 'autor': 'Bram Stoker', 'genero': 'terror',
     'descripcion': 'El conde vampiro más famoso de la literatura.'},
    {'titulo': 'Frankenstein', 'autor': 'Mary Shelley', 'genero': 'terror',
     'descripcion': 'El doctor que crea vida y las consecuencias de jugar a ser Dios.'},
    {'titulo': 'El exorcista', 'autor': 'William Peter Blatty', 'genero': 'terror',
     'descripcion': 'Posesión demoníaca de una niña de 12 años.'},
    {'titulo': 'Entrevista con el vampiro', 'autor': 'Anne Rice', 'genero': 'terror',
     'descripcion': 'Memorias de un vampiro de 200 años.'},
    {'titulo': 'La llamada de Cthulhu', 'autor': 'H.P. Lovecraft', 'genero': 'terror',
     'descripcion': 'Horror cósmico sobre una entidad antigua y terrible.'},
    {'titulo': 'Psicosis', 'autor': 'Robert Bloch', 'genero': 'terror',
     'descripcion': 'Norman Bates y su oscuro motel.'},
    {'titulo': 'La casa infernal', 'autor': 'Richard Matheson', 'genero': 'terror',
     'descripcion': 'Investigación paranormal en una mansión maldita.'},
    
    # Historia y No Ficción (81-90)
    {'titulo': 'Sapiens', 'autor': 'Yuval Noah Harari', 'genero': 'historia',
     'descripcion': 'De animales a dioses: breve historia de la humanidad.'},
    {'titulo': 'El hombre en busca de sentido', 'autor': 'Viktor Frankl', 'genero': 'historia',
     'descripcion': 'Memorias de un psiquiatra en los campos de concentración.'},
    {'titulo': 'El arte de la guerra', 'autor': 'Sun Tzu', 'genero': 'historia',
     'descripcion': 'Tratado militar chino sobre estrategia.'},
    {'titulo': 'El Príncipe', 'autor': 'Nicolás Maquiavelo', 'genero': 'historia',
     'descripcion': 'Tratado político sobre el poder y la moral.'},
    {'titulo': 'La ladrona de libros', 'autor': 'Markus Zusak', 'genero': 'historia',
     'descripcion': 'Una niña en la Alemania nazi roba libros para sobrevivir.'},
    {'titulo': 'El niño del pijama de rayas', 'autor': 'John Boyne', 'genero': 'historia',
     'descripcion': 'Amistad entre dos niños separados por la valla de un campo de concentración.'},
    {'titulo': 'El médico', 'autor': 'Noah Gordon', 'genero': 'historia',
     'descripcion': 'Un joven estudia medicina en la Persia medieval.'},
    {'titulo': 'Los pilares de la Tierra', 'autor': 'Ken Follett', 'genero': 'historia',
     'descripcion': 'Construcción de una catedral en la Inglaterra medieval.'},
    {'titulo': 'La ciudad y los perros', 'autor': 'Mario Vargas Llosa', 'genero': 'historia',
     'descripcion': 'Cadetes en un colegio militar de Lima.'},
    {'titulo': 'Pensar rápido, pensar despacio', 'autor': 'Daniel Kahneman', 'genero': 'historia',
     'descripcion': 'Dos sistemas de pensamiento humano.'},
    
    # Juvenil y Contemporáneo (91-100)
    {'titulo': 'Las ventajas de ser invisible', 'autor': 'Stephen Chbosky', 'genero': 'romance',
     'descripcion': 'Cartas de un adolescente sobre la vida y el amor.'},
    {'titulo': 'Wonder', 'autor': 'R.J. Palacio', 'genero': 'romance',
     'descripcion': 'Un niño con deformidad facial enfrenta su primer día de escuela.'},
    {'titulo': 'Crepúsculo', 'autor': 'Stephenie Meyer', 'genero': 'romance',
     'descripcion': 'Romance entre una humana y un vampiro.'},
    {'titulo': 'Bajo la misma estrella', 'autor': 'John Green', 'genero': 'romance',
     'descripcion': 'Dos adolescentes con cáncer se enamoran.'},
    {'titulo': 'Eleanor & Park', 'autor': 'Rainbow Rowell', 'genero': 'romance',
     'descripcion': 'Romance entre dos adolescentes inadaptados en los 80.'},
    {'titulo': 'Cincuenta sombras de Grey', 'autor': 'E.L. James', 'genero': 'romance',
     'descripcion': 'Romance erótico entre una estudiante y un empresario.'},
    {'titulo': 'Yo antes de ti', 'autor': 'Jojo Moyes', 'genero': 'romance',
     'descripcion': 'Una cuidadora transforma la vida de un hombre tetrapléjico.'},
    {'titulo': 'La insoportable levedad del ser', 'autor': 'Milan Kundera', 'genero': 'romance',
     'descripcion': 'Amor y filosofía en la Checoslovaquia comunista.'},
    {'titulo': 'El tiempo entre costuras', 'autor': 'María Dueñas', 'genero': 'romance',
     'descripcion': 'Una modista española durante la Guerra Civil.'},
    {'titulo': 'Ready Player One', 'autor': 'Ernest Cline', 'genero': 'ciencia_ficcion',
     'descripcion': 'Búsqueda del tesoro en un universo virtual de los 80s.'},
]

GENEROS = ['romance', 'ciencia_ficcion', 'fantasia', 'policial', 'terror', 'historia']

# Colores vibrantes para portadas (paleta ampliada)
COLORES = [
    (233, 69, 96),    # Rosa/Rojo (accent)
    (26, 26, 46),     # Azul oscuro
    (15, 52, 96),     # Azul secundario
    (108, 117, 125),  # Gris
    (255, 193, 7),    # Amarillo
    (40, 167, 69),    # Verde
    (156, 39, 176),   # Púrpura
    (255, 87, 34),    # Naranja
    (0, 150, 136),    # Verde azulado
    (103, 58, 183),   # Índigo
]

def generar_imagen_portada(width=400, height=600, color_index=0):
    """Genera una imagen de portada con color vibrante"""
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

def mostrar_progreso(completados, total, mensaje="Procesando"):
    """Muestra barra de progreso visual"""
    porcentaje = (completados / total) * 100
    barra_length = 40
    bloques_llenos = int((completados / total) * barra_length)
    barra = '█' * bloques_llenos + '░' * (barra_length - bloques_llenos)
    print(f"\r   [{barra}] {porcentaje:.1f}% ({completados}/{total}) {mensaje}", end='', flush=True)

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
def crear_libros(cantidad=100):
    """Crear libros de prueba con portadas de colores (OPTIMIZADO)"""
    print(f"\n2. Creando {cantidad} libros con portadas de colores...")
    print(f"   🎨 Generación LOCAL de portadas (instantáneo)")
    start_time = time.time()
    
    cantidad = min(cantidad, len(LIBROS_REALES))
    libros_creados = 0
    
    for i in range(cantidad):
        libro_data = LIBROS_REALES[i]
        
        # Crear libro con portada de color
        libro = Libro(
            titulo=libro_data['titulo'],
            autor=libro_data['autor'],
            genero=libro_data['genero'],
            descripcion=libro_data['descripcion'],
            portada=generar_imagen_portada(color_index=i % 10)
        )
        
        libro.save()
        libros_creados += 1
        
        # Mostrar progreso
        if CONFIG['show_progress']:
            mostrar_progreso(i + 1, cantidad, "libros creados")
    
    if CONFIG['show_progress']:
        print()  # Nueva línea después de la barra
    
    elapsed_time = (time.time() - start_time) * 1000
    print(f"\n   ✓ {libros_creados} libros creados en {elapsed_time:.2f} ms")
    print(f"   ✓ Todos con portadas de colores (10 variantes)")
    return elapsed_time
        # Mostrar progreso cada 50 libros
        if (i + 1) % 50 == 0:
            print(f"   → {i + 1}/{cantidad} libros creados...")
def crear_reseñas(cantidad=300):
    """Crear reseñas de prueba (OPTIMIZADO)"""
    print(f"\n3. Creando {cantidad} reseñas...")
    start_time = time.time()
    
    usuarios = list(Usuario.objects.filter(rol='usuario').only('id', 'username')[:200])
    libros = list(Libro.objects.only('id', 'titulo').all())
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
        'Usuarios': 200, 'Categorías': 10, 'Libros': 100, 'Reseñas': 300,
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
    print(" DATOS GENERADOS (PORTADAS DE COLORES):")
    print("="*70)
    print(f"  USUARIOS Y PERFILES:")
    print(f"  • 200 usuarios (180 usuarios + 20 administradores)")
    print(f"  • 100 seguimientos entre usuarios")
    print(f"\n  CONTENIDO PRINCIPAL:")
    print(f"  • 10 categorías de libros")
    print(f"  • 100 libros FAMOSOS con portadas de colores (10 variantes)")
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
    print(f"\n  Total: ~1,560 registros creados")
    print(f"  📚 100 libros famosos de la literatura mundial")
    print(f"  🎨 Portadas de 10 colores diferentes")
    print(f"  ⚡ Sin dependencia de internet")
    print(f"  Cubre TODOS los modelos del sistema")
    print("="*70 + "\n")ital - Proyecto Integrado INACAP")
    print("="*70)
    print("\n Este script creará:")
    print("   • 200 usuarios (180 usuarios + 20 admins)")
    print("   • 10 categorías")
    print("   • 100 libros FAMOSOS con portadas de colores")
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
    print("\n Total: ~1,560 registros para pruebas exhaustivas")
    print("\n ⚡ VENTAJAS:")
    print(f"   • Portadas generadas localmente (sin internet)")
    print(f"   • Ejecución RÁPIDA (< 30 segundos)")
    print(f"   • 100 libros famosos de la literatura mundial")
    print(f"   • Queries optimizadas con .only()")
    print(f"   • Progress bar visual")
    print(f"\n   Ideal para: Pruebas rápidas y desarrollo")
    print("="*70)50 valoraciones de reseñas")
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
    
    tiempos_creacion.append(('Usuarios', crear_usuarios(200)))
    tiempos_creacion.append(('Categorías', crear_categorias(10)))
    tiempos_creacion.append(('Libros', crear_libros(100)))
    tiempos_creacion.append(('Reseñas', crear_reseñas(300)))
    
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

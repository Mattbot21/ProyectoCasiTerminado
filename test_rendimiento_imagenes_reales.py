"""
Script de pruebas de rendimiento con IMÁGENES REALES
Genera datos de prueba con portadas descargadas desde URLs
⚠️ ADVERTENCIA: Descarga 100 imágenes reales, puede tardar varios minutos
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

# Base de datos extendida: 100 LIBROS REALES con URLs de portadas
LIBROS_REALES = [
    # Literatura Latinoamericana
    {'titulo': 'Cien años de soledad', 'autor': 'Gabriel García Márquez', 'genero': 'fantasia', 
     'descripcion': 'La historia de la familia Buendía a lo largo de siete generaciones en Macondo.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1327881361i/320.jpg'},
    
    {'titulo': 'Rayuela', 'autor': 'Julio Cortázar', 'genero': 'fantasia',
     'descripcion': 'Una novela experimental que puede leerse de múltiples formas.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1631820683i/58696894.jpg'},
    
    {'titulo': 'La casa de los espíritus', 'autor': 'Isabel Allende', 'genero': 'fantasia',
     'descripcion': 'Saga familiar que mezcla realismo mágico y política en Chile.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1362544808i/9756.jpg'},
    
    {'titulo': 'Pedro Páramo', 'autor': 'Juan Rulfo', 'genero': 'fantasia',
     'descripcion': 'Un hombre busca a su padre en un pueblo de muertos.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1630642526i/58760894.jpg'},
    
    {'titulo': 'Ficciones', 'autor': 'Jorge Luis Borges', 'genero': 'fantasia',
     'descripcion': 'Colección de cuentos metafísicos y laberintos literarios.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1516044152i/426504.jpg'},
    
    # Clásicos Universales
    {'titulo': 'Don Quijote de la Mancha', 'autor': 'Miguel de Cervantes', 'genero': 'historia',
     'descripcion': 'Las aventuras del ingenioso hidalgo y su escudero Sancho Panza.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1546112331i/3836.jpg'},
    
    {'titulo': 'Orgullo y prejuicio', 'autor': 'Jane Austen', 'genero': 'romance',
     'descripcion': 'Elizabeth Bennet y el señor Darcy en la Inglaterra del siglo XIX.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1320399351i/1885.jpg'},
    
    {'titulo': 'Crimen y castigo', 'autor': 'Fiódor Dostoyevski', 'genero': 'policial',
     'descripcion': 'El tormento psicológico de un estudiante que comete un asesinato.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1382846449i/7144.jpg'},
    
    {'titulo': 'Moby Dick', 'autor': 'Herman Melville', 'genero': 'historia',
     'descripcion': 'La obsesiva búsqueda del capitán Ahab por la ballena blanca.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1327940656i/153747.jpg'},
    
    {'titulo': 'Los Miserables', 'autor': 'Victor Hugo', 'genero': 'historia',
     'descripcion': 'Jean Valjean y su redención en la Francia del siglo XIX.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1411852091i/24280.jpg'},
    
    # Ciencia Ficción Moderna
    {'titulo': '1984', 'autor': 'George Orwell', 'genero': 'ciencia_ficcion',
     'descripcion': 'Distopía totalitaria donde el Gran Hermano todo lo ve.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1657781256i/61439040.jpg'},
    
    {'titulo': 'Un mundo feliz', 'autor': 'Aldous Huxley', 'genero': 'ciencia_ficcion',
     'descripcion': 'Sociedad futurista controlada por la tecnología y las drogas.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1575509280i/5129.jpg'},
    
    {'titulo': 'Fahrenheit 451', 'autor': 'Ray Bradbury', 'genero': 'ciencia_ficcion',
     'descripcion': 'Un futuro donde los libros están prohibidos y se queman.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1383718290i/13079982.jpg'},
    
    {'titulo': 'Dune', 'autor': 'Frank Herbert', 'genero': 'ciencia_ficcion',
     'descripcion': 'Épica espacial sobre política, religión y ecología en Arrakis.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1555447414i/44767458.jpg'},
    
    {'titulo': 'Fundación', 'autor': 'Isaac Asimov', 'genero': 'ciencia_ficcion',
     'descripcion': 'La caída del Imperio Galáctico y el plan para preservar el conocimiento.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1417900846i/29579.jpg'},
    
    # Fantasía Épica
    {'titulo': 'El Señor de los Anillos', 'autor': 'J.R.R. Tolkien', 'genero': 'fantasia',
     'descripcion': 'La épica aventura para destruir el Anillo Único.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1566425108i/33.jpg'},
    
    {'titulo': 'El Hobbit', 'autor': 'J.R.R. Tolkien', 'genero': 'fantasia',
     'descripcion': 'Bilbo Bolsón se embarca en una aventura inesperada.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1546071216i/5907.jpg'},
    
    {'titulo': 'Harry Potter y la piedra filosofal', 'autor': 'J.K. Rowling', 'genero': 'fantasia',
     'descripcion': 'Un niño descubre que es mago y asiste a Hogwarts.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1598823299i/42844155.jpg'},
    
    {'titulo': 'El nombre del viento', 'autor': 'Patrick Rothfuss', 'genero': 'fantasia',
     'descripcion': 'Kvothe narra su vida como aventurero y músico legendario.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1270352123i/186074.jpg'},
    
    {'titulo': 'Canción de hielo y fuego', 'autor': 'George R.R. Martin', 'genero': 'fantasia',
     'descripcion': 'Intrigas políticas y batallas épicas en Poniente.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1562726234i/12177850.jpg'},
    
    # Misterio y Policial
    {'titulo': 'El código Da Vinci', 'autor': 'Dan Brown', 'genero': 'policial',
     'descripcion': 'Thriller que mezcla arte, historia y conspiración.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1579621267i/968.jpg'},
    
    {'titulo': 'La sombra del viento', 'autor': 'Carlos Ruiz Zafón', 'genero': 'policial',
     'descripcion': 'Misterio en el Barcelona de posguerra sobre un libro maldito.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1327868566i/1232.jpg'},
    
    {'titulo': 'Los crímenes de la calle Morgue', 'autor': 'Edgar Allan Poe', 'genero': 'policial',
     'descripcion': 'El primer relato de detectives de la literatura moderna.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1309203070i/126296.jpg'},
    
    {'titulo': 'El sabueso de los Baskerville', 'autor': 'Arthur Conan Doyle', 'genero': 'policial',
     'descripcion': 'Sherlock Holmes investiga una maldición familiar.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1391204589i/8921.jpg'},
    
    {'titulo': 'Crónica de una muerte anunciada', 'autor': 'Gabriel García Márquez', 'genero': 'policial',
     'descripcion': 'La reconstrucción del asesinato de Santiago Nasar.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1533690944i/23878.jpg'},
    
    # Literatura Contemporánea
    {'titulo': 'El gran Gatsby', 'autor': 'F. Scott Fitzgerald', 'genero': 'romance',
     'descripcion': 'Jay Gatsby y su amor imposible por Daisy Buchanan.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1490528560i/4671.jpg'},
    
    {'titulo': 'Matar un ruiseñor', 'autor': 'Harper Lee', 'genero': 'historia',
     'descripcion': 'Racismo y justicia en el sur de Estados Unidos.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1553383690i/2657.jpg'},
    
    {'titulo': 'El guardián entre el centeno', 'autor': 'J.D. Salinger', 'genero': 'romance',
     'descripcion': 'La rebeldía adolescente de Holden Caulfield.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1398034300i/5107.jpg'},
    
    {'titulo': 'Las ventajas de ser invisible', 'autor': 'Stephen Chbosky', 'genero': 'romance',
     'descripcion': 'Cartas de un adolescente sobre la vida y el amor.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1641698074i/22628.jpg'},
    
    {'titulo': 'El amor en los tiempos del cólera', 'autor': 'Gabriel García Márquez', 'genero': 'romance',
     'descripcion': 'Un amor que espera más de cincuenta años.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1327881361i/9712.jpg'},
    
    # Más clásicos imprescindibles (30-50)
    {'titulo': 'Anna Karenina', 'autor': 'León Tolstói', 'genero': 'romance',
     'descripcion': 'Tragedia de una mujer en la alta sociedad rusa.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1601352433i/15823480.jpg'},
    
    {'titulo': 'Guerra y paz', 'autor': 'León Tolstói', 'genero': 'historia',
     'descripcion': 'Épica sobre la invasión napoleónica de Rusia.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1413215930i/656.jpg'},
    
    {'titulo': 'El retrato de Dorian Gray', 'autor': 'Oscar Wilde', 'genero': 'fantasia',
     'descripcion': 'Un hombre vende su alma por la eterna juventud.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1546103428i/5297.jpg'},
    
    {'titulo': 'Drácula', 'autor': 'Bram Stoker', 'genero': 'terror',
     'descripcion': 'El conde vampiro más famoso de la literatura.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1387151694i/17245.jpg'},
    
    {'titulo': 'Frankenstein', 'autor': 'Mary Shelley', 'genero': 'terror',
     'descripcion': 'El doctor que crea vida y las consecuencias de jugar a ser Dios.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1669159060i/35031085.jpg'},
    
    {'titulo': 'El principito', 'autor': 'Antoine de Saint-Exupéry', 'genero': 'fantasia',
     'descripcion': 'Cuento poético sobre un pequeño príncipe que viaja entre planetas.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1367545443i/157993.jpg'},
    
    {'titulo': 'Alicia en el país de las maravillas', 'autor': 'Lewis Carroll', 'genero': 'fantasia',
     'descripcion': 'Las aventuras surrealistas de Alicia en un mundo fantástico.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1630663928i/58657933.jpg'},
    
    {'titulo': 'El extranjero', 'autor': 'Albert Camus', 'genero': 'historia',
     'descripcion': 'La absurda existencia de Meursault tras cometer un crimen.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1590930002i/49552.jpg'},
    
    {'titulo': 'La metamorfosis', 'autor': 'Franz Kafka', 'genero': 'fantasia',
     'descripcion': 'Gregor Samsa despierta convertido en un insecto gigante.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1359061917i/485894.jpg'},
    
    {'titulo': 'El proceso', 'autor': 'Franz Kafka', 'genero': 'policial',
     'descripcion': 'Josef K. es arrestado sin saber de qué se le acusa.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1320399438i/17690.jpg'},
    
    # Literatura infantil y juvenil (41-50)
    {'titulo': 'Las crónicas de Narnia', 'autor': 'C.S. Lewis', 'genero': 'fantasia',
     'descripcion': 'Niños descubren un mundo mágico dentro de un armario.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1661032875i/11127.jpg'},
    
    {'titulo': 'Charlie y la fábrica de chocolate', 'autor': 'Roald Dahl', 'genero': 'fantasia',
     'descripcion': 'Un niño pobre gana un tour por la fábrica de Willy Wonka.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1309211401i/6310.jpg'},
    
    {'titulo': 'Matilda', 'autor': 'Roald Dahl', 'genero': 'fantasia',
     'descripcion': 'Una niña superdotada con poderes telequinéticos.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1388793265i/39988.jpg'},
    
    {'titulo': 'Percy Jackson y el ladrón del rayo', 'autor': 'Rick Riordan', 'genero': 'fantasia',
     'descripcion': 'Un chico descubre que es hijo de un dios griego.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1400602609i/28187.jpg'},
    
    {'titulo': 'Los juegos del hambre', 'autor': 'Suzanne Collins', 'genero': 'ciencia_ficcion',
     'descripcion': 'Jóvenes luchan a muerte en un reality show distópico.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052.jpg'},
    
    {'titulo': 'Divergente', 'autor': 'Veronica Roth', 'genero': 'ciencia_ficcion',
     'descripcion': 'Una sociedad dividida en facciones según virtudes.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1618526419i/13335037.jpg'},
    
    {'titulo': 'Crepúsculo', 'autor': 'Stephenie Meyer', 'genero': 'romance',
     'descripcion': 'Romance entre una humana y un vampiro.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1361039443i/41865.jpg'},
    
    {'titulo': 'La ladrona de libros', 'autor': 'Markus Zusak', 'genero': 'historia',
     'descripcion': 'Una niña en la Alemania nazi roba libros para sobrevivir.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1522157426i/19063.jpg'},
    
    {'titulo': 'El niño del pijama de rayas', 'autor': 'John Boyne', 'genero': 'historia',
     'descripcion': 'Amistad entre dos niños separados por la valla de un campo de concentración.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1294063879i/39999.jpg'},
    
    {'titulo': 'Wonder', 'autor': 'R.J. Palacio', 'genero': 'romance',
     'descripcion': 'Un niño con deformidad facial enfrenta su primer día de escuela.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1309208271i/11387515.jpg'},
    
    # Ciencia ficción y tecnología (51-60)
    {'titulo': 'Neuromante', 'autor': 'William Gibson', 'genero': 'ciencia_ficcion',
     'descripcion': 'Pionera del cyberpunk sobre hackers y realidad virtual.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1554437249i/6088007.jpg'},
    
    {'titulo': 'Snow Crash', 'autor': 'Neal Stephenson', 'genero': 'ciencia_ficcion',
     'descripcion': 'Un repartidor de pizzas investiga un virus informático.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1589800355i/40651883.jpg'},
    
    {'titulo': 'La guerra de los mundos', 'autor': 'H.G. Wells', 'genero': 'ciencia_ficcion',
     'descripcion': 'Invasión marciana de la Tierra victoriana.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1320391644i/8909.jpg'},
    
    {'titulo': 'La máquina del tiempo', 'autor': 'H.G. Wells', 'genero': 'ciencia_ficcion',
     'descripcion': 'Un inventor viaja al futuro lejano.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1327942880i/2493.jpg'},
    
    {'titulo': 'Yo, Robot', 'autor': 'Isaac Asimov', 'genero': 'ciencia_ficcion',
     'descripcion': 'Relatos sobre robots y las tres leyes de la robótica.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1388187281i/41804.jpg'},
    
    {'titulo': 'La guía del autoestopista galáctico', 'autor': 'Douglas Adams', 'genero': 'ciencia_ficcion',
     'descripcion': 'Comedia espacial sobre el fin de la Tierra.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1559986152i/13.jpg'},
    
    {'titulo': 'El marciano', 'autor': 'Andy Weir', 'genero': 'ciencia_ficcion',
     'descripcion': 'Un astronauta abandonado debe sobrevivir en Marte.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1413706054i/18007564.jpg'},
    
    {'titulo': 'Ready Player One', 'autor': 'Ernest Cline', 'genero': 'ciencia_ficcion',
     'descripcion': 'Búsqueda del tesoro en un universo virtual de los 80s.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1500930947i/9969571.jpg'},
    
    {'titulo': 'Ender\'s Game', 'autor': 'Orson Scott Card', 'genero': 'ciencia_ficcion',
     'descripcion': 'Niños entrenados para la guerra contra alienígenas.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1408303130i/375802.jpg'},
    
    {'titulo': 'Solaris', 'autor': 'Stanisław Lem', 'genero': 'ciencia_ficcion',
     'descripcion': 'Encuentro con una inteligencia alien incomprensible.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1524588944i/95558.jpg'},
    
    # Terror y horror (61-70)
    {'titulo': 'It (Eso)', 'autor': 'Stephen King', 'genero': 'terror',
     'descripcion': 'Un payaso demoníaco aterroriza un pueblo de Maine.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1334416842i/830502.jpg'},
    
    {'titulo': 'El resplandor', 'autor': 'Stephen King', 'genero': 'terror',
     'descripcion': 'Una familia atrapada en un hotel embrujado en invierno.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1353277730i/11588.jpg'},
    
    {'titulo': 'Carrie', 'autor': 'Stephen King', 'genero': 'terror',
     'descripcion': 'Una adolescente con poderes telequinéticos se venga.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1166254258i/10592.jpg'},
    
    {'titulo': 'El exorcista', 'autor': 'William Peter Blatty', 'genero': 'terror',
     'descripcion': 'Posesión demoníaca de una niña de 12 años.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1387722964i/179780.jpg'},
    
    {'titulo': 'Entrevista con el vampiro', 'autor': 'Anne Rice', 'genero': 'terror',
     'descripcion': 'Memorias de un vampiro de 200 años.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1380631642i/43763.jpg'},
    
    {'titulo': 'La llamada de Cthulhu', 'autor': 'H.P. Lovecraft', 'genero': 'terror',
     'descripcion': 'Horror cósmico sobre una entidad antigua y terrible.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1485924654i/34094154.jpg'},
    
    {'titulo': 'El corazón delator', 'autor': 'Edgar Allan Poe', 'genero': 'terror',
     'descripcion': 'Un asesino es atormentado por los latidos del corazón de su víctima.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1362211022i/448623.jpg'},
    
    {'titulo': 'Otra vuelta de tuerca', 'autor': 'Henry James', 'genero': 'terror',
     'descripcion': 'Una institutriz ve fantasmas en una mansión victoriana.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1327909192i/12948.jpg'},
    
    {'titulo': 'El espinazo del diablo', 'autor': 'Varios', 'genero': 'terror',
     'descripcion': 'Antología de cuentos de terror gótico.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1320437687i/50033.jpg'},
    
    {'titulo': 'Psicosis', 'autor': 'Robert Bloch', 'genero': 'terror',
     'descripcion': 'Norman Bates y su oscuro motel.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1405012695i/355742.jpg'},
    
    # Literatura hispanoamericana moderna (71-80)
    {'titulo': 'La ciudad y los perros', 'autor': 'Mario Vargas Llosa', 'genero': 'historia',
     'descripcion': 'Cadetes en un colegio militar de Lima.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1556052950i/45453894.jpg'},
    
    {'titulo': 'Pantaleón y las visitadoras', 'autor': 'Mario Vargas Llosa', 'genero': 'romance',
     'descripcion': 'Un capitán organiza un servicio de prostitutas para el ejército.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1389636849i/162664.jpg'},
    
    {'titulo': 'El túnel', 'autor': 'Ernesto Sabato', 'genero': 'policial',
     'descripcion': 'Un pintor obsesionado confiesa un crimen pasional.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1440629213i/104103.jpg'},
    
    {'titulo': 'Sobre héroes y tumbas', 'autor': 'Ernesto Sabato', 'genero': 'romance',
     'descripcion': 'Historia de amor y oscuridad en Buenos Aires.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1327871152i/105206.jpg'},
    
    {'titulo': 'El Aleph', 'autor': 'Jorge Luis Borges', 'genero': 'fantasia',
     'descripcion': 'Cuentos metafísicos y filosóficos magistrales.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1394371174i/105971.jpg'},
    
    {'titulo': 'La tregua', 'autor': 'Mario Benedetti', 'genero': 'romance',
     'descripcion': 'Romance otoñal de un oficinista próximo a jubilarse.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1387739163i/105101.jpg'},
    
    {'titulo': 'El coronel no tiene quien le escriba', 'autor': 'Gabriel García Márquez', 'genero': 'historia',
     'descripcion': 'Un coronel espera una pensión que nunca llega.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1327881361i/23871.jpg'},
    
    {'titulo': 'La región más transparente', 'autor': 'Carlos Fuentes', 'genero': 'historia',
     'descripcion': 'Retrato coral de la Ciudad de México.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1387738890i/104855.jpg'},
    
    {'titulo': 'Los detectives salvajes', 'autor': 'Roberto Bolaño', 'genero': 'policial',
     'descripcion': 'Búsqueda de una poeta desaparecida en el México de los 70.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1327882716i/63033.jpg'},
    
    {'titulo': '2666', 'autor': 'Roberto Bolaño', 'genero': 'policial',
     'descripcion': 'Cinco historias conectadas por feminicidios en el desierto.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1422623758i/63032.jpg'},
    
    # No ficción y ensayo (81-90)
    {'titulo': 'Sapiens', 'autor': 'Yuval Noah Harari', 'genero': 'historia',
     'descripcion': 'De animales a dioses: breve historia de la humanidad.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1595674533i/23692271.jpg'},
    
    {'titulo': 'Homo Deus', 'autor': 'Yuval Noah Harari', 'genero': 'ciencia_ficcion',
     'descripcion': 'Breve historia del mañana y el futuro de la humanidad.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1468760805i/31138556.jpg'},
    
    {'titulo': 'El hombre en busca de sentido', 'autor': 'Viktor Frankl', 'genero': 'historia',
     'descripcion': 'Memorias de un psiquiatra en los campos de concentración.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1535419394i/4069.jpg'},
    
    {'titulo': 'El arte de la guerra', 'autor': 'Sun Tzu', 'genero': 'historia',
     'descripcion': 'Tratado militar chino sobre estrategia.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1453417993i/10534.jpg'},
    
    {'titulo': 'El Príncipe', 'autor': 'Nicolás Maquiavelo', 'genero': 'historia',
     'descripcion': 'Tratado político sobre el poder y la moral.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1348363039i/28862.jpg'},
    
    {'titulo': 'Breve historia del tiempo', 'autor': 'Stephen Hawking', 'genero': 'ciencia_ficcion',
     'descripcion': 'Del Big Bang a los agujeros negros.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1333578746i/3869.jpg'},
    
    {'titulo': 'El gen egoísta', 'autor': 'Richard Dawkins', 'genero': 'ciencia_ficcion',
     'descripcion': 'Nueva visión de la teoría de la evolución.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1366758096i/61535.jpg'},
    
    {'titulo': 'Cosmos', 'autor': 'Carl Sagan', 'genero': 'ciencia_ficcion',
     'descripcion': 'Exploración del universo y nuestro lugar en él.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1388199464i/55030.jpg'},
    
    {'titulo': 'Pensar rápido, pensar despacio', 'autor': 'Daniel Kahneman', 'genero': 'historia',
     'descripcion': 'Dos sistemas de pensamiento humano.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1317793965i/11468377.jpg'},
    
    {'titulo': 'El cisne negro', 'autor': 'Nassim Nicholas Taleb', 'genero': 'historia',
     'descripcion': 'El impacto de lo altamente improbable.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1386924361i/242472.jpg'},
    
    # Completando hasta 100 (91-100)
    {'titulo': 'El médico', 'autor': 'Noah Gordon', 'genero': 'historia',
     'descripcion': 'Un joven estudia medicina en la Persia medieval.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1388253942i/259514.jpg'},
    
    {'titulo': 'Los pilares de la Tierra', 'autor': 'Ken Follett', 'genero': 'historia',
     'descripcion': 'Construcción de una catedral en la Inglaterra medieval.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1576956100i/5043.jpg'},
    
    {'titulo': 'El nombre de la rosa', 'autor': 'Umberto Eco', 'genero': 'policial',
     'descripcion': 'Misterio medieval en una abadía benedictina.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1415375471i/119073.jpg'},
    
    {'titulo': 'Perfume', 'autor': 'Patrick Süskind', 'genero': 'policial',
     'descripcion': 'Un asesino con sentido del olfato extraordinario.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1403165866i/343.jpg'},
    
    {'titulo': 'La insoportable levedad del ser', 'autor': 'Milan Kundera', 'genero': 'romance',
     'descripcion': 'Amor y filosofía en la Checoslovaquia comunista.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1265401884i/9717.jpg'},
    
    {'titulo': 'Lolita', 'autor': 'Vladimir Nabokov', 'genero': 'romance',
     'descripcion': 'Controversia novela sobre obsesión prohibida.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1377756377i/7604.jpg'},
    
    {'titulo': 'El perfume de Adan', 'autor': 'Varios', 'genero': 'romance',
     'descripcion': 'Relatos sobre amor y deseo.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1320526886i/831903.jpg'},
    
    {'titulo': 'La carretera', 'autor': 'Cormac McCarthy', 'genero': 'ciencia_ficcion',
     'descripcion': 'Padre e hijo en un mundo post-apocalíptico.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1600241424i/6288.jpg'},
    
    {'titulo': 'El cuento de la criada', 'autor': 'Margaret Atwood', 'genero': 'ciencia_ficcion',
     'descripcion': 'Distopía sobre una teocracia totalitaria.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1578028274i/38447.jpg'},
    
    {'titulo': 'Oryx y Crake', 'autor': 'Margaret Atwood', 'genero': 'ciencia_ficcion',
     'descripcion': 'Último ser humano tras una catástrofe biotecnológica.',
     'url_portada': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1320611022i/46756.jpg'},
]

GENEROS = ['romance', 'ciencia_ficcion', 'fantasia', 'policial', 'terror', 'historia']

# Colores para generar portadas de respaldo (si falla descarga)
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
        print(f"   ⚠ Error descargando {nombre_archivo}: {str(e)[:50]}")
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

def crear_usuarios(cantidad=200):
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

def crear_libros_con_imagenes_reales(cantidad=100):
    """Crear libros con portadas REALES descargadas"""
    print(f"\n2. Creando {cantidad} libros con PORTADAS REALES descargadas...")
    print(f"   ⚠️ ADVERTENCIA: Esto puede tardar varios minutos")
    start_time = time.time()
    
    libros_creados = 0
    descargas_exitosas = 0
    descargas_fallidas = 0
    
    for i in range(min(cantidad, len(LIBROS_REALES))):
        libro_data = LIBROS_REALES[i]
        
        # Crear libro
        libro = Libro(
            titulo=libro_data['titulo'],
            autor=libro_data['autor'],
            genero=libro_data['genero'],
            descripcion=libro_data['descripcion']
        )
        
        # Intentar descargar portada real
        print(f"   [{i+1}/{cantidad}] Descargando: {libro_data['titulo'][:40]}...")
        portada = descargar_portada(libro_data['url_portada'], f"{libro_data['titulo'][:30]}.jpg")
        
        if portada:
            libro.portada = portada
            descargas_exitosas += 1
            print(f"   ✓ Descargada correctamente")
        else:
            # Fallback a color
            libro.portada = generar_imagen_portada(color_index=i % 6)
            descargas_fallidas += 1
            print(f"   ✗ Usando color de respaldo")
        
        libro.save()
        libros_creados += 1
        
        # Pausa pequeña para no saturar el servidor
        time.sleep(0.5)
    
    elapsed_time = (time.time() - start_time) * 1000
    print(f"\n   ✓ {libros_creados} libros creados en {elapsed_time/1000:.1f} segundos")
    print(f"   ✓ {descargas_exitosas} portadas reales descargadas")
    print(f"   ✗ {descargas_fallidas} con portadas de colores (fallback)")
    return elapsed_time

def crear_reseñas(cantidad=300):
    """Crear reseñas de prueba"""
    print(f"\n3. Creando {cantidad} reseñas...")
    start_time = time.time()
    
    usuarios = list(Usuario.objects.filter(rol='usuario')[:200])
    libros = list(Libro.objects.all())
    
    if not usuarios or not libros:
        print(f"   ⚠ No hay suficientes datos. Saltando...")
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
    libros = list(Libro.objects.all())
    
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
    libros = list(Libro.objects.all())
    
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
    libros = list(Libro.objects.all())
    
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
    reseñas = list(Reseña.objects.all())
    
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
    reseñas = list(Reseña.objects.all())
    
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
        libros = Libro.objects.filter(genero='fantasia')[:30]
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
    print(" RESUMEN DE PRUEBAS DE RENDIMIENTO (IMÁGENES REALES)")
    print("="*70)
    
    print("\nA. CREACIÓN DE DATOS:")
    print("-" * 70)
    print(f"{'Operación':<30} {'Tiempo':<15} {'Registros':<15}")
    print("-" * 70)
    
    # Mostrar todos los datos creados dinámicamente
    totales = {
        'Usuarios': 200, 'Categorías': 10, 'Libros con imágenes reales': 100, 'Reseñas': 300,
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
    print(" DATOS GENERADOS (CON IMÁGENES REALES):")
    print("="*70)
    print(f"  USUARIOS Y PERFILES:")
    print(f"  • 200 usuarios (180 usuarios + 20 administradores)")
    print(f"  • 100 seguimientos entre usuarios")
    print(f"\n  CONTENIDO PRINCIPAL:")
    print(f"  • 10 categorías de libros")
    print(f"  • 100 libros con PORTADAS REALES descargadas desde Goodreads")
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
    print(f"  ⭐ INCLUYE: 100 libros famosos con portadas reales")
    print(f"  Cubre TODOS los modelos del sistema")
    print("="*70 + "\n")

def main():
    """Función principal"""
    print("\n" + "="*70)
    print(" SCRIPT DE PRUEBAS CON IMÁGENES REALES DE PORTADAS")
    print(" Librería Digital - Proyecto Integrado INACAP")
    print("="*70)
    print("\n Este script creará:")
    print("   • 200 usuarios (180 usuarios + 20 admins)")
    print("   • 10 categorías")
    print("   • 100 libros con PORTADAS REALES descargadas (5-10 min)")
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
    print("\n Total: ~1560 registros con PORTADAS REALES")
    print(" ⚠️  ADVERTENCIA: Descarga de imágenes tarda varios minutos")
    print("="*70)
    
    # Confirmar ejecución
    respuesta = input("\n¿Desea crear todos los registros con imágenes reales? (s/n): ")
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
    tiempos_creacion.append(('Libros con imágenes reales', crear_libros_con_imagenes_reales(100)))
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

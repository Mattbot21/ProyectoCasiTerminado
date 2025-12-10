from django import forms
from .models import Libro, Reseña, Lista, Categoria, Comentario


class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo', 'autor', 'descripcion', 'categoria', 'genero', 'fecha_publicacion', 'portada']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del libro'
            }),
            'autor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Autor del libro'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción del libro...'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_publicacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Fecha de publicación'
            }),
            'portada': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }


class ReseñaForm(forms.ModelForm):
    """
    H13: Como autor de reseña, quiero poder adjuntar una calificación con estrellas
    a mi reseña, para complementar mi opinión escrita con una valoración rápida.
    """
    
    class Meta:
        model = Reseña
        fields = ['comentario', 'calificacion']
        widgets = {
            'comentario': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Comparte tu opinión sobre este libro...'
            }),
            'calificacion': forms.RadioSelect(
                choices=[
                    (1, '⭐ 1 estrella'),
                    (2, '⭐⭐ 2 estrellas'),
                    (3, '⭐⭐⭐ 3 estrellas'),
                    (4, '⭐⭐⭐⭐ 4 estrellas'),
                    (5, '⭐⭐⭐⭐⭐ 5 estrellas'),
                ],
                attrs={'class': 'star-rating-input'}
            )
        }
        labels = {
            'comentario': 'Tu reseña',
            'calificacion': 'Calificación'
        }
    
    def clean_calificacion(self):
        """Valida que la calificación esté entre 1 y 5"""
        calificacion = self.cleaned_data.get('calificacion')
        try:
            cal_int = int(calificacion)
            if cal_int < 1 or cal_int > 5:
                raise forms.ValidationError("La calificación debe estar entre 1 y 5 estrellas.")
            return cal_int
        except (ValueError, TypeError):
            raise forms.ValidationError("Selecciona una calificación válida.")


class ListaForm(forms.ModelForm):
    class Meta:
        model = Lista
        fields = ['nombre', 'descripcion', 'libros']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Mis libros de fantasía favoritos'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el propósito de esta lista...'
            }),
            'libros': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 10,
                'multiple': 'multiple'
            })
        }
        labels = {
            'nombre': 'Nombre de la lista',
            'descripcion': 'Descripción',
            'libros': 'Selecciona libros'
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
        }


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Escribe tu comentario aquí...'
            }),
        }
        labels = {
            'contenido': 'Comentario'
        }

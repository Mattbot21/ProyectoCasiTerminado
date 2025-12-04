from django import forms
from .models import Libro, Reseña, Lista, Categoria, Comentario


class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo', 'autor', 'descripcion', 'categoria', 'genero', 'fecha_publicacion', 'portada']


class ReseñaForm(forms.ModelForm):
    """
    H13: Como autor de reseña, quiero poder adjuntar una calificación con estrellas
    a mi reseña, para complementar mi opinión escrita con una valoración rápida.
    """
    CALIFICACIONES = [
        (1, '⭐ 1 estrella - Muy malo'),
        (2, '⭐⭐ 2 estrellas - Malo'),
        (3, '⭐⭐⭐ 3 estrellas - Regular'),
        (4, '⭐⭐⭐⭐ 4 estrellas - Bueno'),
        (5, '⭐⭐⭐⭐⭐ 5 estrellas - Excelente'),
    ]
    
    calificacion = forms.ChoiceField(
        choices=CALIFICACIONES,
        widget=forms.RadioSelect(attrs={'class': 'star-radio'}),
        label='Calificación',
        initial=5
    )
    
    class Meta:
        model = Reseña
        fields = ['comentario', 'calificacion']
        widgets = {
            'comentario': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Comparte tu opinión sobre este libro...'
            }),
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

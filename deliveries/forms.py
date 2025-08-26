from django import forms
from .models import Cliente
from django.contrib.contenttypes.models import ContentType
from .models import Avaliacao

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'telefone', 'email', 'endereco']

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['tipo', 'nota', 'comentario', 'anonimo']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nota': forms.NumberInput(attrs={
                'min': 1, 
                'max': 5, 
                'class': 'form-control',
                'id': 'notaInput'
            }),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Compartilhe sua experiência...'
            }),
            'anonimo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'tipo': 'O que você está avaliando?',
            'nota': 'Nota (1-5 estrelas)',
            'comentario': 'Comentário',
            'anonimo': 'Avaliação anônima'
        }

class AvaliacaoFiltroForm(forms.Form):
    TIPO_FILTRO = [
        ('', 'Todos os tipos'),
        ('entregador', 'Entregadores'),
        ('pedido', 'Pedidos'),
        ('cliente', 'Clientes'),
        ('servico', 'Serviço Geral'),
        ('estabelecimento', 'Estabelecimentos'),
    ]
    
    ORDENACAO = [
        ('-data_criacao', 'Mais recentes'),
        ('data_criacao', 'Mais antigas'),
        ('-nota', 'Melhores avaliações'),
        ('nota', 'Piores avaliações'),
    ]
    
    tipo = forms.ChoiceField(choices=TIPO_FILTRO, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    ordenacao = forms.ChoiceField(choices=ORDENACAO, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    min_nota = forms.IntegerField(
        min_value=1, 
        max_value=5, 
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nota mínima'})
    )
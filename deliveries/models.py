from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

# 1. CLASSE CLIENTE
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    endereco = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def historico_pedidos(self):
        return self.pedidos.all()

    def clean(self):
        if len(self.telefone) < 10:
            raise ValidationError("O telefone deve ter pelo menos 10 dígitos.")

    def __str__(self):
        return f"{self.nome} ({self.email})"

# 2. CLASSE ENTREGADOR
class Entregador(models.Model):
    nome = models.CharField(max_length=100)
    veiculo = models.CharField(
        max_length=20,
        choices=[
            ('Moto', 'Moto'),
            ('Bicicleta', 'Bicicleta'),
            ('Carro', 'Carro'),
        ]
    )
    placa = models.CharField(max_length=10, blank=True, null=True)
    disponibilidade = models.BooleanField(default=True)
    localizacao_atual = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Coordenadas GPS (ex: '-23.5505, -46.6333')"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_disponivel(self):
        return self.disponibilidade

    def clean(self):
        if self.placa and not self.placa.isalnum():
            raise ValidationError("A placa deve conter apenas letras e números.")
        if self.veiculo == 'Carro' and not self.placa:
            raise ValidationError("Placa é obrigatória para entregadores de carro.")
        if self.veiculo == 'Bicicleta' and self.placa:
            raise ValidationError("Placa não deve ser informada para entregadores de bicicleta.")
        if self.veiculo == 'Moto' and not self.placa:
            raise ValidationError("Placa é obrigatória para entregadores de moto.")

    def __str__(self):
        return f"{self.nome} ({self.veiculo}) - {'Disponível' if self.disponibilidade else 'Indisponível'}"

# 3. CLASSE PEDIDO
class Pedido(models.Model):
    STATUS_CHOICES = [
        ('P', 'Preparando'),
        ('R', 'Em rota'),
        ('E', 'Entregue'),
    ]
    PRIORIDADE_CHOICES = [
        ('N', 'Normal'),
        ('U', 'Urgente'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    entregador = models.ForeignKey(
    Entregador, 
    on_delete=models.SET_NULL, 
    null=True, 
    related_name='pedidos'
    )

    endereco_entrega = models.TextField()
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='P'
    )
    prioridade = models.CharField(
        max_length=1,
        choices=PRIORIDADE_CHOICES,
        default='N'
    )
    data_hora_pedido = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    produtos = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de produtos no formato JSON. Ex: [{'nome': 'Remédio X', 'quantidade': 2, 'preco': 10.0}]"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_urgente(self):
        return self.prioridade == 'U'

    def calcular_valor_total(self):
        total = 0
        for item in self.produtos:
            total += item.get('preco', 0) * item.get('quantidade', 1)
        self.valor_total = total
        return total

    def clean(self):
        if not self.produtos:
            raise ValidationError("O pedido deve conter pelo menos um produto.")

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nome} ({self.get_status_display()})"

    class Meta:
        ordering = ['-data_hora_pedido']

# 4. CLASSE LOJISTA
class Lojista(models.Model):
    nome_loja = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18, unique=True)
    telefone = models.CharField(max_length=15)
    endereco_loja = models.CharField(max_length=255)
    categoria = models.CharField(max_length=50)  

    def __str__(self):
        return self.nome_loja

# 5. CLASSE PRODUTO
class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    lojista = models.ForeignKey(Lojista, on_delete=models.CASCADE)
    categoria = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.nome

# 6. CLASSE ACOMPANHE PEDIDO
class AcompanhePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    localizacao_atual = models.CharField(max_length=255, blank=True, null=True)
    tempo_estimado_entrega = models.DurationField(blank=True, null=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido {self.pedido.id} - {self.pedido.status}"

# 7. CLASSE AVALIACAO
class Avaliacao(models.Model):
    TIPO_AVALIACAO_CHOICES = [
        ('entregador', 'Entregador'),
        ('pedido', 'Pedido'),
        ('cliente', 'Cliente'),
        ('servico', 'Serviço Geral'),
        ('estabelecimento', 'Estabelecimento'),
    ]
    
    # Campos para relação genérica (pode avaliar qualquer modelo)
    content_type = models.ForeignKey(ContentType, 
    on_delete=models.CASCADE, 
    null=True, 
    blank=True
    )

    object_id = models.PositiveIntegerField(
        null=True, 
        blank=True
    )

    conteudo = GenericForeignKey('content_type', 'object_id')
    
    # Quem está avaliando
    avaliador = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE,
        related_name='avaliacoes_feitas',
        null=True,
        blank=True
    )
    
    # Dados da avaliação
    tipo = models.CharField(max_length=20, 
    choices=TIPO_AVALIACAO_CHOICES,
    null=True,
    blank=True
    )
    nota = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Nota de 1 a 5 estrelas"
    )
    comentario = models.TextField(blank=True, null=True, max_length=500)
    data_criacao = models.DateTimeField(default=timezone.now)
    anonimo = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        avaliador = "Anônimo" if self.anonimo else self.avaliador.get_full_name() or self.avaliador.username
        return f"Avaliação de {self.get_tipo_display()} por {avaliador} - {self.nota} estrelas"
    
    @property
    def estrelas(self):
        return "⭐" * self.nota
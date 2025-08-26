from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Cliente, Entregador, Pedido
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator
from .forms import AvaliacaoForm, AvaliacaoFiltroForm
from .models import Avaliacao, Entregador

# Create your views here.
@login_required
def area_restrita(request):
    return render(request, 'area_restrita.html')

def lista_clientes(request):
    clientes = Cliente.objects.all().order_by('nome')
    return render(request, 'deliveries/lista_clientes.html', {'clientes': clientes})

def home(request):
    return render(request, 'deliveries/home.html')

def sobre(request):
    return render(request, 'deliveries/sobre.html')

def lista_entregadores(request):
    """View para listar todos os entregadores"""
    entregadores = Entregador.objects.all().order_by('nome')
    
    # DEBUG DETALHADO
    print("=" * 50)
    print("DEBUG DA VIEW lista_entregadores")
    print("=" * 50)
    print(f"Total de entregadores: {entregadores.count()}")
    for e in entregadores:
        print(f"Entregador: {e.nome} (ID: {e.id})")
    print("=" * 50)
    
    context = {
        'entregadores': entregadores,
        'debug': True  # Variável extra para debug no template
    }
    
    return render(request, 'deliveries/lista_entregadores.html', context)

def lista_pedidos(request):
    """View para listar todos os pedidos"""
    pedidos = Pedido.objects.all().order_by('-data_hora_pedido')  # Mais recentes primeiro
    return render(request, 'deliveries/lista_pedidos.html', {'pedidos': pedidos})

def detalhes_pedido(request, pedido_id):
    """View para mostrar detalhes de um pedido específico"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # DEBUG
    print(f"DEBUG: Detalhes do pedido {pedido.id} - {pedido.cliente.nome}")
    
    return render(request, 'deliveries/detalhes_pedido.html', {'pedido': pedido})

def detalhes_entregador(request, entregador_id):
    entregador = get_object_or_404(Entregador, id=entregador_id)
    
    # Use 'pedidos' em vez de 'pedido_set'
    pedidos = entregador.pedidos.all()  # ← Alterado para 'pedidos'
    
    context = {
        'entregador': entregador,
        'pedidos': pedidos
    }
    return render(request, 'deliveries/detalhes_entregador.html', context)

@login_required
def criar_avaliacao(request):
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.avaliador = request.user
            
            # Aqui você pode definir content_type e object_id baseado no contexto
            # Por exemplo, se estiver avaliando um entregador específico:
            # entregador_id = request.POST.get('entregador_id')
            # if entregador_id:
            #     entregador = get_object_or_404(Entregador, id=entregador_id)
            #     avaliacao.content_type = ContentType.objects.get_for_model(entregador)
            #     avaliacao.object_id = entregador.id
            
            avaliacao.save()
            messages.success(request, 'Avaliação registrada com sucesso!')
            return redirect('lista_avaliacoes')
    else:
        form = AvaliacaoForm()
    
    return render(request, 'deliveries/criar_avaliacao.html', {
        'form': form,
        'titulo': 'Nova Avaliação'
    })

def lista_avaliacoes(request):
    avaliacoes = Avaliacao.objects.all()
    
    # Aplicar filtros
    tipo = request.GET.get('tipo')
    min_nota = request.GET.get('min_nota')
    ordenacao = request.GET.get('ordenacao', '-data_criacao')
    
    if tipo:
        avaliacoes = avaliacoes.filter(tipo=tipo)
    if min_nota:
        avaliacoes = avaliacoes.filter(nota__gte=min_nota)
    
    avaliacoes = avaliacoes.order_by(ordenacao)
    
    # Estatísticas
    estatisticas = {
        'total': avaliacoes.count(),
        'media_geral': avaliacoes.aggregate(Avg('nota'))['nota__avg'] or 0,
        'por_tipo': avaliacoes.values('tipo').annotate(
            total=Count('id'),
            media=Avg('nota')
        ).order_by('-total')
    }
    
    # Paginação
    paginator = Paginator(avaliacoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'deliveries/lista_avaliacoes.html', {
        'page_obj': page_obj,
        'estatisticas': estatisticas
    })

@login_required
def minhas_avaliacoes(request):
    avaliacoes = Avaliacao.objects.filter(avaliador=request.user).order_by('-data_criacao')
    return render(request, 'deliveries/minhas_avaliacoes.html', {
        'avaliacoes': avaliacoes
    })


from django.urls import path
from .views import home, sobre, lista_clientes, lista_entregadores, lista_pedidos, detalhes_pedido, detalhes_entregador, lista_avaliacoes, criar_avaliacao

urlpatterns = [
    path('', home, name='home'),
    path('sobre/', sobre, name='sobre'),
    path('clientes/', lista_clientes, name='lista_clientes'),
    path('entregadores/', lista_entregadores, name='lista_entregadores'),
    path('pedidos/', lista_pedidos, name='lista_pedidos'),
    path('pedidos/<int:pedido_id>/', detalhes_pedido, name='detalhes_pedido'),
    path('entregadores/<int:entregador_id>/', detalhes_entregador, name='detalhes_entregador'),
    path('avaliacoes/', lista_avaliacoes, name='lista_avaliacoes'),
    path('avaliacoes/criar/', criar_avaliacao, name='criar_avaliacao'),
]
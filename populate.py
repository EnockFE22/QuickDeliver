import os
import django

# Configure o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickdeliver.settings')
django.setup()

from deliveries.models import Cliente, Entregador, Pedido
from django.utils import timezone

def criar_dados_teste():
    """Cria dados de teste automaticamente"""
    
    # Cria clientes
    clientes = [
        {"nome": "Maria Silva", "telefone": "11999999999", "email": "maria@email.com", "endereco": "Rua das Flores, 123"},
        {"nome": "João Santos", "telefone": "11988888888", "email": "joao@email.com", "endereco": "Av. Paulista, 1000"},
        {"nome": "Ana Costa", "telefone": "11977777777", "email": "ana@email.com", "endereco": "Rua Augusta, 500"}
    ]
    
    clientes_obj = []
    for data in clientes:
        cliente = Cliente.objects.create(**data)
        clientes_obj.append(cliente)
        print(f"✅ Cliente criado: {cliente.nome}")
    
    # Cria entregadores
    entregadores = [
        {"nome": "Carlos Motoboy", "veiculo": "Moto", "placa": "MOT1234", "disponibilidade": True},
        {"nome": "Paula Entregadora", "veiculo": "Carro", "placa": "CAR5678", "disponibilidade": True},
        {"nome": "Ricardo Express", "veiculo": "Bicicleta", "placa": "", "disponibilidade": False}
    ]
    
    entregadores_obj = []
    for data in entregadores:
        entregador = Entregador.objects.create(**data)
        entregadores_obj.append(entregador)
        print(f"✅ Entregador criado: {entregador.nome}")
    
    # Cria pedidos automaticamente para cada cliente
    pedidos_data = [
        {"status": "R", "prioridade": "N", "produtos": [{"nome": "Remédio Dor", "quantidade": 2, "preco": 15.90}]},
        {"status": "E", "prioridade": "N", "produtos": [{"nome": "Shampoo", "quantidade": 1, "preco": 22.90}]},
        {"status": "P", "prioridade": "U", "produtos": [{"nome": "Produto Urgente", "quantidade": 1, "preco": 50.00}]}
    ]
    
    for i, cliente in enumerate(clientes_obj):
        for j, pedido_data in enumerate(pedidos_data):
            pedido = Pedido.objects.create(
                cliente=cliente,
                entregador=entregadores_obj[j % len(entregadores_obj)],  # Distribui entregadores
                endereco_entrega=cliente.endereco,
                status=pedido_data["status"],
                prioridade=pedido_data["prioridade"],
                produtos=pedido_data["produtos"],
                valor_total=sum(item["preco"] * item["quantidade"] for item in pedido_data["produtos"])
            )
            
            # ✅ LINHA CORRIGIDA:
            print(f"✅ Pedido {pedido.id} criado para {cliente.nome} com valor total R$ {pedido.valor_total:.2f}")
    
    print("\n🎉 Dados de teste criados com sucesso!")
    print(f"📦 Total: {Pedido.objects.count()} pedidos criados")

if __name__ == "__main__":
    criar_dados_teste()
from gcap_sdk import Gcap

# Inicialize o cliente
gcap = Gcap()

# Faça login
print(" Tentando fazer login...")
login_result = gcap.login()
if login_result['success']:
    print("✅ Login realizado com sucesso!")
    
    # Exemplo: Listar alguns mandados para testar
    print(" Obtendo lista de mandados...")
    mandados = gcap.listar_mandados(page=0, page_size=5)
    if mandados['success']:
        print(f"✅ Encontrados {len(mandados['data']['data'])} mandados")
    else:
        print("❌ Erro ao listar mandados:", mandados['error'])
        
    # Logout quando terminar
    gcap.logout()
    print("✅ Logout realizado com sucesso!")
    
else:
    print("❌ Falha no login:", login_result['error'])
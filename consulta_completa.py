from gcap_sdk import Gcap

# Inicialize o cliente
gcap = Gcap()

# Faça login
print(" Tentando fazer login...")
login_result = gcap.login()
if login_result['success']:
    print("✅ Login realizado com sucesso!")
    
    # Consultar o mandado específico para mostrar todos os campos
    print(" Consultando todos os campos do mandado 0802467962025823001001000123...")
    mandados = gcap.listar_mandados(
        page=0, 
        page_size=100,
        numero_mandado="0802467962025823001001000123"
    )
    
    if mandados['success']:
        data = mandados['data']
        if data and 'data' in data and len(data['data']) > 0:
            mandado = data['data'][0]
            print("✅ Mandado encontrado! Todos os campos:")
            print("-" * 50)
            
            # Mostrar todos os campos do mandado
            for chave, valor in mandado.items():
                print(f"{chave}: {valor}")
                
        else:
            print("❌ Mandado não encontrado na pesquisa")
    else:
        print("❌ Erro ao buscar mandado:", mandados['error'])
        
    # Logout quando terminar
    gcap.logout()
    print("✅ Logout realizado com sucesso!")
    
else:
    print("❌ Falha no login:", login_result['error'])
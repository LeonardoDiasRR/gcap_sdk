from gcap_sdk import Gcap

# Inicialize o cliente
gcap = Gcap()

# Faça login
print(" Tentando fazer login...")
login_result = gcap.login()
if login_result['success']:
    print("✅ Login realizado com sucesso!")
    
    # Pesquisar o mandado específico
    print(" Buscando mandado 0802467962025823001001000123...")
    mandados = gcap.listar_mandados(
        page=0, 
        page_size=100,  # Aumentei para garantir encontrar
        numero_mandado="0802467962025823001001000123"
    )
    
    if mandados['success']:
        data = mandados['data']
        if data and 'data' in data and len(data['data']) > 0:
            mandado_encontrado = data['data'][0]
            print("✅ Mandado encontrado!")
            print(f"ID: {mandado_encontrado.get('id', 'N/A')}")
            print(f"Número do mandado: {mandado_encontrado.get('numero_mandado', 'N/A')}")
            print(f"Data do mandado: {mandado_encontrado.get('data_mandado', 'N/A')}")
            print(f"Data da prisão: {mandado_encontrado.get('data_prisao', 'N/A')}")
            
            # Mostrar dados do procurado
            procurado = mandado_encontrado.get('procurados', {})
            if procurado:
                print(f"Nome do procurado: {procurado.get('nome', 'N/A')}")
                print(f"CPF do procurado: {procurado.get('cpf', 'N/A')}")
                print(f"RJI do procurado: {procurado.get('rji', 'N/A')}")
            
            # Mostrar dados do crime
            crime = mandado_encontrado.get('crimes', {})
            if crime:
                print(f"Crime: {crime.get('nome_crime', 'N/A')}")
                
            # Mostrar dados do serviço
            servico = mandado_encontrado.get('servicos', {})
            if servico:
                print(f"Serviço: {servico.get('nome', 'N/A')}")
                
        else:
            print("❌ Mandado não encontrado na pesquisa")
    else:
        print("❌ Erro ao buscar mandado:", mandados['error'])
        
    # Logout quando terminar
    gcap.logout()
    print("✅ Logout realizado com sucesso!")
    
else:
    print("❌ Falha no login:", login_result['error'])
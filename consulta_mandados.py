#!/usr/bin/env python3

import sys
sys.path.insert(0, '/opt/projetos/gcap_sdk')

from gcap_sdk import Gcap

# Inicializar o cliente GCAP
gcap = Gcap()

try:
    # Fazer login
    print("Fazendo login...")
    login_result = gcap.login()
    if not login_result['success']:
        print(f"Erro ao fazer login: {login_result['error']}")
    else:
        print("Login bem-sucedido!")
        
        # Listar 3 mandados
        print("Buscando 3 mandados...")
        result = gcap.listar_mandados(page=0, page_size=3)
        
        if result['success']:
            data = result['data']
            if data and 'data' in data and len(data['data']) > 0:
                print(f"\nEncontrados {len(data['data'])} mandados:")
                for i, mandado in enumerate(data['data']):
                    procurado = mandado.get('procurados', {})
                    nome_procurado = procurado.get('nome', 'N/A') if procurado else 'N/A'
                    crime = mandado.get('crimes', {})
                    nome_crime = crime.get('nome_crime', 'N/A') if crime else 'N/A'
                    print(f"  {i+1}. Número: {mandado.get('numero_mandado')}")
                    print(f"      Procurado: {nome_procurado}")
                    print(f"      Crime: {nome_crime}")
                    print(f"      Data prisão: {mandado.get('data_prisao')}")
                    print()  # Linha em branco para separar
            else:
                print("Nenhum mandado encontrado")
        else:
            print(f"Erro ao buscar mandados: {result['error']}")
            
finally:
    # Fazer logout
    gcap.logout()
    print("Logout realizado.")
#!/usr/bin/env python3

import sys
sys.path.insert(0, '/opt/projetos/gcap_sdk')

from gcap_sdk import Gcap

# Inicialize o cliente
gcap = Gcap()

try:
    # Faça login
    print(" Fazendo login...")
    login_result = gcap.login()
    if not login_result['success']:
        print(f"Erro ao fazer login: {login_result['error']}")
    else:
        print("✅ Login realizado com sucesso!")
        
        # Listar presos de ontem (09/03/2026)
        data_prisao = "2026-03-09"
        print(f" Buscando presos de {data_prisao}...")
        
        result = gcap.listar_mandados(
            page=0, 
            page_size=100,  # 100 registros
            data_prisao=data_prisao
        )
        
        if result['success']:
            data = result['data']
            if data and 'data' in data and len(data['data']) > 0:
                procurados_encontrados = data['data']
                print(f"\n✅ Encontrados {len(procurados_encontrados)} presos:")
                
                list_presos = []
                for mandado in procurados_encontrados:
                    procurado = mandado.get('procurados', {})
                    nome_procurado = procurado.get('nome', 'N/A') if procurado else 'N/A'
                    cpf_procurado = procurado.get('cpf', 'N/A') if procurado else 'N/A'
                    
                    crime = mandado.get('crimes', {})
                    nome_crime = crime.get('nome_crime', 'N/A') if crime else 'N/A'
                    
                    list_presos.append({
                        'nome': nome_procurado,
                        'cpf': cpf_procurado,
                        'crime': nome_crime
                    })
                
                # Salvar em arquivo JSON
                import json
                with open('/tmp/presos_ontem.json', 'w', encoding='utf-8') as f:
                    json.dump(list_presos, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Lista salva em: /tmp/presos_ontem.json")
                
            else:
                print("❌ Nenhum preso encontrado")
        else:
            print(f"❌ Erro ao buscar presos: {result['error']}")
            
finally:
    # Logout quando terminar
    gcap.logout()
    print("✅ Logout realizado com sucesso!")


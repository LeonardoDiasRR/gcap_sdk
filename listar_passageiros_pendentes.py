#!/usr/bin/env python3
"""
Script para listar todos os passageiros com status 'Pendente' e salvar em CSV
"""

import csv
from datetime import datetime
from gcap_sdk import Gcap


def main():
    # Inicializar SDK
    gcap = Gcap()
    
    # Fazer login
    print("Autenticando...")
    login_result = gcap.login()
    if not login_result['success']:
        print(f"Erro no login: {login_result['error']}")
        return
    
    print("Autenticação bem-sucedida!\n")
    
    # Listar passageiros com status Pendente
    print("Buscando passageiros com status 'Pendente'...")
    search_result = gcap.listar_passageiros(status='Pendente')
    
    if not search_result['success']:
        print(f"Erro na busca: {search_result.get('error', 'Erro desconhecido')}")
        return
    
    # Extrair dados
    passageiros = search_result.get('data', {}).get('data', [])
    
    if not passageiros:
        print("Nenhum passageiro com status 'Pendente' encontrado.")
        return
    
    print(f"Total de passageiros encontrados: {len(passageiros)}\n")
    
    # Criar arquivo CSV com timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = f'\\\\10.95.7.22\\gcap\\passageiros_pendentes\\passageiros_pendentes_{timestamp}.csv'
    
    try:
        # Colunas a serem exportadas
        fieldnames = ['data_embarque', 'nome_passageiro', 'cpf', 'numero_mandado']
        
        # Filtrar apenas as colunas desejadas
        passageiros_filtrados = []
        for passageiro in passageiros:
            passageiro_filtrado = {col: passageiro.get(col, '') for col in fieldnames}
            passageiros_filtrados.append(passageiro_filtrado)
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(passageiros_filtrados)
        
        print(f"✓ CSV salvo com sucesso: {csv_file}")
        print(f"✓ Total de registros: {len(passageiros)}")
        
    except Exception as e:
        print(f"Erro ao salvar CSV: {str(e)}")
        return


if __name__ == '__main__':
    main()

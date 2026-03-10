#!/usr/bin/env python3

import sys
import json
from gcap_sdk import Gcap

def listar_presos(data_prisao):
    """
    Lista os presos presos em uma data específica.
    
    Args:
        data_prisao (str): Data de prisão no formato ISO (YYYY-MM-DD)
    
    Returns:
        dict: JSON com os resultados da busca
    """
    # Instanciar a classe Gcap
    gcap = Gcap()
    
    try:
        # Fazer login
        login_result = gcap.login()
        if not login_result['success']:
            return {
                'success': False,
                'error': f"Erro ao fazer login: {login_result['error']}"
            }
        
        # Pesquisar mandados com a data de prisão no intervalo especificado
        result = gcap.listar_mandados(
            data_prisao_from=data_prisao,
            data_prisao_to=data_prisao
        )
        
        return result
        
    finally:
        # Fazer logout
        gcap.logout()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python listar_presos.py <data_prisao>")
        print("Exemplo: python listar_presos.py 2026-03-09")
        sys.exit(1)
    
    data_prisao = sys.argv[1]
    result = listar_presos(data_prisao)
    
    # Remover objeto Response que não é serializável em JSON
    if 'response' in result:
        del result['response']
    
    # Imprimir o JSON resultante
    print(json.dumps(result, indent=2))

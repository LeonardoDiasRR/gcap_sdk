#!/usr/bin/env python3

import sys
import json
import calendar
from gcap_sdk import Gcap

def parse_date_input(date_str):
    """
    Analisa a entrada de data e retorna data_from e data_to.
    
    Args:
        date_str (str): Data no formato YYYY-MM-DD (data exata) ou YYYY-MM (mês)
    
    Returns:
        tuple: (data_from, data_to) no formato YYYY-MM-DD
    """
    if len(date_str) == 7:  # Formato YYYY-MM (mês)
        year, month = map(int, date_str.split('-'))
        last_day = calendar.monthrange(year, month)[1]
        data_from = f"{year:04d}-{month:02d}-01"
        data_to = f"{year:04d}-{month:02d}-{last_day:02d}"
        return data_from, data_to
    else:  # Formato YYYY-MM-DD (data exata)
        return date_str, date_str

def listar_presos(data_prisao):
    """
    Lista os presos presos em uma data específica ou durante um mês.
    
    Args:
        data_prisao (str): Data de prisão no formato ISO (YYYY-MM-DD) para data exata,
                          ou YYYY-MM para buscar todo um mês
    
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
        
        # Analisar a entrada de data
        data_from, data_to = parse_date_input(data_prisao)
        
        # Pesquisar mandados com a data de prisão no intervalo especificado
        result = gcap.listar_mandados(
            data_prisao_from=data_from,
            data_prisao_to=data_to
        )
        
        return result
        
    finally:
        # Fazer logout
        gcap.logout()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python listar_presos.py <data_prisao>")
        print("Exemplos:")
        print("  python listar_presos.py 2026-03-09        (data exata)")
        print("  python listar_presos.py 2026-01           (mês inteiro)")
        sys.exit(1)
    
    data_prisao = sys.argv[1]
    result = listar_presos(data_prisao)
    
    # Remover objeto Response que não é serializável em JSON
    if 'response' in result:
        del result['response']
    
    # Imprimir o JSON resultante
    print(json.dumps(result, indent=2))

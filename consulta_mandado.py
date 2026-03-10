#!/usr/bin/env python3

import sys
import json
import re
from gcap_sdk import Gcap

def normalizar_numero_mandado(numero_mandado):
    """
    Normaliza o número do mandado removendo formatação.
    Aceita números formatados (com hífens e pontos) ou somente dígitos.
    
    Args:
        numero_mandado (str): Número do mandado formatado ou não
    
    Returns:
        tuple: (bool, str) - (sucesso, número_normalizado ou mensagem_erro)
    """
    # Remover espaços em branco
    numero_mandado = numero_mandado.strip()
    
    # Remover hífens e pontos
    numero_normalizado = re.sub(r'[-.]', '', numero_mandado)
    
    # Verificar se contém apenas dígitos
    if not numero_normalizado.isdigit():
        return False, "Número de mandado deve conter apenas dígitos, hífens e pontos"
    
    # Verificar se tem exatamente 28 dígitos
    if len(numero_normalizado) != 28:
        return False, f"Número de mandado deve ter exatamente 28 dígitos (recebido: {len(numero_normalizado)})"
    
    return True, numero_normalizado

def consulta_mandado(numero_mandado):
    """
    Consulta um mandado específico pelo número.
    
    Args:
        numero_mandado (str): Número do mandado
    
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
        
        # Pesquisar o mandado pelo número
        result = gcap.listar_mandados(
            page=0,
            page_size=1,
            numero_mandado=numero_mandado
        )
        
        return result
        
    finally:
        # Fazer logout
        gcap.logout()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python consulta_mandado.py <numero_mandado>")
        print("Exemplos:")
        print("  - Formatado: python consulta_mandado.py 0841162-22.2025.8.23.0010.01.0001-17")
        print("  - Somente números: python consulta_mandado.py 0841162222025823001001000117")
        sys.exit(1)
    
    numero_mandado = sys.argv[1]
    
    # Normalizar e validar o número do mandado
    valido, numero_ou_erro = normalizar_numero_mandado(numero_mandado)
    if not valido:
        print(json.dumps({
            'success': False,
            'error': numero_ou_erro
        }, indent=2))
        sys.exit(1)
    
    result = consulta_mandado(numero_ou_erro)
    
    # Remover objeto Response que não é serializável em JSON
    if 'response' in result:
        del result['response']
    
    # Imprimir o JSON resultante
    print(json.dumps(result, indent=2))

#!/usr/bin/env python3

import sys
import json
import os
import mimetypes
from gcap_sdk import Gcap

# MIME types para PDF
PDF_MIMETYPES = [
    'application/pdf',
]

# Extensões de arquivo PDF
PDF_EXTENSIONS = ['.pdf']

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB em bytes

def validar_arquivo(caminho_arquivo):
    """
    Valida se o arquivo é um PDF válido.
    
    Args:
        caminho_arquivo (str): Caminho para o arquivo
    
    Returns:
        tuple: (bool, str) - (válido, mensagem_erro ou "OK")
    """
    # Verificar se o arquivo existe
    if not os.path.exists(caminho_arquivo):
        return False, f"Arquivo '{caminho_arquivo}' não encontrado"
    
    # Verificar se é um arquivo (não diretório)
    if not os.path.isfile(caminho_arquivo):
        return False, f"'{caminho_arquivo}' não é um arquivo"
    
    # Verificar tamanho do arquivo
    tamanho_arquivo = os.path.getsize(caminho_arquivo)
    if tamanho_arquivo > MAX_FILE_SIZE:
        tamanho_mb = tamanho_arquivo / (1024 * 1024)
        return False, f"Arquivo muito grande ({tamanho_mb:.2f}MB). Máximo permitido: 5MB"
    
    if tamanho_arquivo == 0:
        return False, "Arquivo vazio"
    
    # Verificar extensão do arquivo
    _, extensao = os.path.splitext(caminho_arquivo)
    if extensao.lower() not in PDF_EXTENSIONS:
        return False, f"Extensão '{extensao}' não é um arquivo PDF. Extensão aceita: .pdf"
    
    # Verificar MIME type
    mime_type, _ = mimetypes.guess_type(caminho_arquivo)
    if mime_type and mime_type not in PDF_MIMETYPES:
        return False, f"Tipo MIME '{mime_type}' não é um PDF válido"
    
    return True, "OK"

def upload_mandado(caminho_arquivo):
    """
    Faz upload de um arquivo de mandado em PDF.
    
    Args:
        caminho_arquivo (str): Caminho para o arquivo PDF
    
    Returns:
        dict: JSON com os resultados do upload
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
        
        # Fazer upload do arquivo
        result = gcap.upload_mandados(caminho_arquivo)
        
        return result
        
    finally:
        # Fazer logout
        gcap.logout()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python upload_mandado.py <arquivo>")
        print("Exemplo: python upload_mandado.py mandado.pdf")
        print("\nRequisitos:")
        print("  - Arquivo deve ser PDF (.pdf)")
        print("  - Tamanho máximo: 5MB")
        sys.exit(1)
    
    caminho_arquivo = sys.argv[1]
    
    # Validar arquivo
    valido, mensagem = validar_arquivo(caminho_arquivo)
    if not valido:
        print(json.dumps({
            'success': False,
            'error': mensagem
        }, indent=2))
        sys.exit(1)
    
    result = upload_mandado(caminho_arquivo)
    
    # Remover objeto Response que não é serializável em JSON
    if 'response' in result:
        del result['response']
    
    # Imprimir o JSON resultante
    print(json.dumps(result, indent=2))

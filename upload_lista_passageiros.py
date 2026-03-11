#!/usr/bin/env python3

import sys
import json
import os
import mimetypes
from gcap_sdk import Gcap

# Mimetypes para Excel
EXCEL_MIMETYPES = [
    'application/vnd.ms-excel',  # .xls
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
    'application/vnd.ms-excel.sheet.macroEnabled.12',  # .xlsm
    'application/vnd.ms-excel.template.macroEnabled.12',  # .xltm
]

# Extensões de arquivo Excel
EXCEL_EXTENSIONS = ['.xls', '.xlsx', '.xlsm', '.xltm', '.xlt']

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB em bytes
MAX_FILES = 50  # Máximo de arquivos por upload

def validar_arquivo(caminho_arquivo):
    """
    Valida se o arquivo é um Excel válido e está dentro do tamanho limite.
    
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
    if extensao.lower() not in EXCEL_EXTENSIONS:
        return False, f"Extensão '{extensao}' não é um formato Excel válido. Extensões aceitas: {', '.join(EXCEL_EXTENSIONS)}"
    
    # Verificar MIME type
    mime_type, _ = mimetypes.guess_type(caminho_arquivo)
    if mime_type and mime_type not in EXCEL_MIMETYPES:
        return False, f"Tipo MIME '{mime_type}' não é um formato Excel válido"
    
    return True, "OK"

def upload_listas_passageiros(caminhos_arquivos):
    """
    Faz upload de múltiplos arquivos de listas de passageiros.
    
    Args:
        caminhos_arquivos (list): Lista de caminhos para os arquivos Excel
    
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
        
        # Fazer upload dos arquivos
        result = gcap.upload_passageiros(caminhos_arquivos)
        
        return result
        
    finally:
        # Fazer logout
        gcap.logout()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python upload_listas_passageiros.py <arquivo1> [arquivo2] ... [arquivo50]")
        print("Exemplo: python upload_listas_passageiros.py passageiros1.xlsx passageiros2.xlsx")
        print("\nRequisitos:")
        print("  - Arquivos devem ser Excel (.xls, .xlsx, .xlsm, .xltm)")
        print("  - Tamanho máximo por arquivo: 5MB")
        print("  - Máximo de arquivos por upload: 50")
        sys.exit(1)
    
    caminhos_arquivos = sys.argv[1:]
    
    # Verificar limite de arquivos
    if len(caminhos_arquivos) > MAX_FILES:
        print(json.dumps({
            'success': False,
            'error': f"Número de arquivos ({len(caminhos_arquivos)}) excede o limite de {MAX_FILES}"
        }, indent=2))
        sys.exit(1)
    
    # Validar todos os arquivos
    arquivos_validos = []
    erros = []
    
    for caminho in caminhos_arquivos:
        valido, mensagem = validar_arquivo(caminho)
        if valido:
            arquivos_validos.append(caminho)
        else:
            erros.append({
                'arquivo': caminho,
                'erro': mensagem
            })
    
    # Se houver erros, retornar e não fazer upload
    if erros:
        print(json.dumps({
            'success': False,
            'error': 'Alguns arquivos falharam na validação',
            'detalhes': erros
        }, indent=2))
        sys.exit(1)
    
    result = upload_listas_passageiros(arquivos_validos)
    
    # Remover objeto Response que não é serializável em JSON
    if 'response' in result:
        del result['response']
    
    # Imprimir o JSON resultante
    print(json.dumps(result, indent=2))

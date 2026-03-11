#!/usr/bin/env python3

import sys
import json
import os
import mimetypes
import argparse
from gcap_sdk import Gcap

# MIME types para PDF
PDF_MIMETYPES = [
    'application/pdf',
]

# Extensões de arquivo PDF
PDF_EXTENSIONS = ['.pdf']

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB em bytes
MAX_FILES = 50  # Máximo de arquivos por upload

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

def upload_certidoes(caminhos_arquivos, nome_servico):
    """
    Faz upload de múltiplos arquivos de certidões em PDF.
    
    Args:
        caminhos_arquivos (list): Lista de caminhos para os arquivos PDF
        nome_servico (str): Nome do serviço
    
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
        
        # Pesquisar o serviço pelo nome
        busca_result = gcap.listar_servicos(page=0, page_size=100, nome=nome_servico)
        
        if not busca_result['success']:
            return {
                'success': False,
                'error': f"Erro ao buscar serviço: {busca_result.get('error', 'Erro desconhecido')}"
            }
        
        # Verificar se encontrou o serviço
        data = busca_result.get('data', {})
        servicos = data.get('data', [])
        
        if not servicos:
            return {
                'success': False,
                'error': f"Serviço '{nome_servico}' não encontrado"
            }
        
        # Obter o ID do serviço (primeiro resultado)
        servico = servicos[0]
        servico_id = servico.get('id')
        
        if not servico_id:
            return {
                'success': False,
                'error': "ID do serviço não encontrado na resposta"
            }
        
        # Fazer upload das certidões
        upload_result = gcap.upload_certidoes(caminhos_arquivos, servico_id)
        
        return upload_result
        
    finally:
        # Fazer logout
        gcap.logout()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Faz upload de certidões em PDF para um serviço específico'
    )
    parser.add_argument(
        '--servico',
        required=True,
        help='Nome do serviço'
    )
    parser.add_argument(
        'arquivos',
        nargs='+',
        help='Caminhos para os arquivos PDF das certidões (até 50 arquivos)'
    )
    
    args = parser.parse_args()
    
    caminhos_arquivos = args.arquivos
    nome_servico = args.servico
    
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
    
    result = upload_certidoes(arquivos_validos, nome_servico)
    
    # Remover objeto Response que não é serializável em JSON
    if 'response' in result:
        del result['response']
    
    # Imprimir o JSON resultante
    print(json.dumps(result, indent=2))

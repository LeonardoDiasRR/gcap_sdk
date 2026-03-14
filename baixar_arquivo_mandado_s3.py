#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para baixar arquivo PDF de Mandado de Prisão ou Certidão do Supabase Storage via REST API.
Recebe como parâmetro um número de mandado de prisão, pesquisa os dados 
do mandado utilizando gcap_sdk e faz download do arquivo de mandado ou certidão com autenticação Bearer.
Use a flag --certidao para baixar a certidão em vez do mandado.
"""

import sys
import json
import os
import re
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    print("Erro: requests não está instalado. Execute: pip install requests")
    sys.exit(1)

from dotenv import load_dotenv
from gcap_sdk import Gcap

# Carregar variáveis de ambiente
load_dotenv()


def _baixar_com_rest_autenticado(url_arquivo, access_token, api_key):
    """
    Baixa arquivo usando requisição REST autenticada com Supabase Storage.
    
    Args:
        url_arquivo (str): URL do arquivo no Supabase Storage
        access_token (str): Access token obtido através de gcap.login()
        api_key (str): API key (Apikey) do Supabase
    
    Returns:
        bytes: Conteúdo do arquivo
    
    Raises:
        requests.exceptions.RequestException: Se houver erro na requisição HTTP
    """
    headers = {
        'Apikey': api_key,
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(url_arquivo, headers=headers, timeout=30)
    response.raise_for_status()
    return response.content


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


def assegurar_diretorio_saida():
    """
    Assegura que o diretório de saída 'arquivos/' existe.
    
    Returns:
        str: Caminho absoluto do diretório de saída
    """
    diretorio_saida = os.path.join(os.path.dirname(__file__), 'arquivos')
    os.makedirs(diretorio_saida, exist_ok=True)
    return diretorio_saida


def gerar_nome_arquivo(numero_mandado, url_arquivo, eh_certidao=False):
    """
    Gera o nome do arquivo com padrão consistente.
    Para certidão: retorna 'certidao_<numero_mandado>.pdf'
    Para mandado: retorna 'mandado_<numero_mandado>.pdf'
    
    Args:
        numero_mandado (str): Número do mandado normalizado
        url_arquivo (str): URL do arquivo no Supabase Storage
        eh_certidao (bool): Se True, gera nome para certidão; se False, gera para mandado
    
    Returns:
        str: Nome do arquivo com extensão
    """
    if eh_certidao:
        return f"certidao_{numero_mandado}.pdf"
    else:
        return f"mandado_{numero_mandado}.pdf"


def baixar_arquivo_mandado(numero_mandado, eh_certidao=False):
    """
    Baixa arquivo PDF de Mandado de Prisão ou Certidão do Supabase Storage via REST API.
    
    Args:
        numero_mandado (str): Número do mandado normalizado
        eh_certidao (bool): Se True, baixa a certidão; se False, baixa o mandado
    
    Returns:
        dict: JSON com os resultados da operação
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
        
        if not result['success']:
            return {
                'success': False,
                'error': f"Erro ao pesquisar mandado: {result.get('error', 'Unknown error')}"
            }
        
        # Verificar se encontrou o mandado
        mandados = result.get('data', {}).get('data', [])
        if not mandados or len(mandados) == 0:
            return {
                'success': False,
                'error': f"Mandado com número {numero_mandado} não encontrado"
            }
        
        mandado = mandados[0]
        
        # Verificar se há arquivo (mandado ou certidão)
        nome_campo = 'arquivo_certidao' if eh_certidao else 'arquivo_mandado'
        tipo_arquivo = 'certidão' if eh_certidao else 'mandado'
        caminho_arquivo = mandado.get(nome_campo)
        if not caminho_arquivo:
            return {
                'success': False,
                'error': f"O mandado não possui arquivo de {tipo_arquivo} (campo '{nome_campo}' vazio)"
            }
        
        # Construir URL completa se necessário
        if caminho_arquivo.startswith('http://') or caminho_arquivo.startswith('https://'):
            url_arquivo = caminho_arquivo
        else:
            # É um caminho relativo, construir URL completa com base URL do Supabase Storage
            base_url = os.getenv('GCAP_BACKEND_URL_BASE', 'https://xkecjoczmynhnyjwbxry.supabase.co')
            bucket_name = os.getenv('S3_BUCKET_NAME', 'gcap')
            url_arquivo = f"{base_url}/storage/v1/object/{bucket_name}/{caminho_arquivo}"
        
        # Fazer download do arquivo
        diretorio_saida = assegurar_diretorio_saida()
        nome_arquivo = gerar_nome_arquivo(numero_mandado, url_arquivo, eh_certidao=eh_certidao)
        caminho_arquivo_local = os.path.join(diretorio_saida, nome_arquivo)
        
        try:
            # Obter API key para autenticação
            api_key = os.getenv('GCAP_BACKEND_API_KEY')
            if not api_key:
                return {
                    'success': False,
                    'error': "GCAP_BACKEND_API_KEY não configurada no .env"
                }
            
            # Usar access token obtido do login para fazer download autenticado
            arquivo_conteudo = _baixar_com_rest_autenticado(
                url_arquivo,
                gcap.access_token,
                api_key
            )
            
            # Salvar arquivo
            with open(caminho_arquivo_local, 'wb') as f:
                f.write(arquivo_conteudo)
            
            return {
                'success': True,
                'message': "Arquivo baixado com sucesso",
                'mandado_numero': mandado.get('numero_mandado'),
                'arquivo_local': caminho_arquivo_local,
                'arquivo_tamanho_bytes': len(arquivo_conteudo),
                'arquivo_url': url_arquivo
            }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Erro ao baixar arquivo: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Erro ao baixar arquivo: {str(e)}"
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    
    finally:
        # Fazer logout
        gcap.logout()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python baixar_arquivo_mandado_s3.py <numero_mandado> [--certidao]")
        print("Exemplos:")
        print("  - Baixar mandado (formatado): python baixar_arquivo_mandado_s3.py 0841162-22.2025.8.23.0010.01.0001-17")
        print("  - Baixar mandado (somente números): python baixar_arquivo_mandado_s3.py 0841162222025823001001000117")
        print("  - Baixar certidão: python baixar_arquivo_mandado_s3.py 0841162-22.2025.8.23.0010.01.0001-17 --certidao")
        sys.exit(1)
    
    numero_mandado = sys.argv[1]
    eh_certidao = '--certidao' in sys.argv
    
    # Normalizar e validar o número do mandado
    valido, numero_ou_erro = normalizar_numero_mandado(numero_mandado)
    if not valido:
        print(json.dumps({
            'success': False,
            'error': numero_ou_erro
        }, indent=2))
        sys.exit(1)
    
    result = baixar_arquivo_mandado(numero_ou_erro, eh_certidao=eh_certidao)
    
    # Remover objeto Response que não é serializável em JSON
    if 'response' in result:
        del result['response']
    
    # Imprimir o JSON resultante
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Retornar código de saída apropriado
    sys.exit(0 if result['success'] else 1)

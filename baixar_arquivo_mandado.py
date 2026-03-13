#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para baixar arquivo PDF de Mandado de Prisão do storage S3.
Recebe como parâmetro um número de mandado de prisão, pesquisa os dados 
do mandado utilizando gcap_sdk e faz download do arquivo PDF.
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

try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

from dotenv import load_dotenv
from gcap_sdk import Gcap

# Carregar variáveis de ambiente
load_dotenv()


def obter_credenciais_s3():
    """
    Obtém credenciais de S3 e URL base do .env.
    
    Returns:
        dict: Dicionário com configurações S3 (pode ter chaves vazias)
    """
    return {
        's3_url': os.getenv('S3_URL', ''),
        's3_access_key': os.getenv('S3_ACCESS_KEY', ''),
        's3_secret_key': os.getenv('S3_SECRET_KEY', ''),
        's3_region': os.getenv('S3_REGION', 'sa-east-1'),
        's3_bucket_name': os.getenv('S3_BUCKET_NAME', 'default')
    }


def _baixar_com_boto3(url_arquivo, credenciais_s3):
    """
    Baixa arquivo usando boto3 com credenciais S3.
    
    Args:
        url_arquivo (str): URL ou caminho do arquivo no S3
        credenciais_s3 (dict): Dicionário com credenciais S3
    
    Returns:
        bytes: Conteúdo do arquivo
    """
    if not HAS_BOTO3:
        raise ImportError("boto3 não está instalado")
    
    # Extrair chave da URL
    # URL pode ser: https://xkecjoczmynhnyjwbxry.storage.supabase.co/storage/v1/s3/bucket/key
    # Ou: s3://bucket/key
    
    if url_arquivo.startswith('s3://'):
        # Formato s3://bucket/key
        partes = url_arquivo[5:].split('/', 1)
        chave = partes[1] if len(partes) > 1 else ''
    else:
        # Formato URL HTTP
        url_base = credenciais_s3['s3_url'].rstrip('/')
        if url_arquivo.startswith(url_base):
            chave = url_arquivo[len(url_base):].lstrip('/')
        else:
            chave = url_arquivo
    
    # Usar bucket configurado no .env
    bucket = credenciais_s3['s3_bucket_name']
    
    # Criar cliente S3
    s3_client = boto3.client(
        's3',
        endpoint_url=credenciais_s3['s3_url'].rsplit('/storage/v1/s3', 1)[0] if '/storage/v1/s3' in credenciais_s3['s3_url'] else None,
        aws_access_key_id=credenciais_s3['s3_access_key'],
        aws_secret_access_key=credenciais_s3['s3_secret_key'],
        region_name=credenciais_s3['s3_region']
    )
    
    # Fazer download
    response = s3_client.get_object(Bucket=bucket, Key=chave)
    return response['Body'].read()


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


def gerar_nome_arquivo(numero_mandado, url_arquivo):
    """
    Gera um nome para o arquivo com base no número do mandado e a URL.
    
    Args:
        numero_mandado (str): Número do mandado normalizado
        url_arquivo (str): URL do arquivo no S3
    
    Returns:
        str: Nome do arquivo com extensão
    """
    # Extrair extensão da URL se houver
    extensao = '.pdf'
    if '.' in url_arquivo.split('/')[-1]:
        nome_url = url_arquivo.split('/')[-1].split('?')[0]
        if '.' in nome_url:
            extensao = '.' + nome_url.split('.')[-1]
    
    # Criar nome formatado: mandado_<numero_normalizado>_<timestamp>
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f"mandado_{numero_mandado}_{timestamp}{extensao}"
    
    return nome_arquivo


def baixar_arquivo_mandado(numero_mandado):
    """
    Baixa arquivo PDF de Mandado de Prisão do S3.
    
    Args:
        numero_mandado (str): Número do mandado normalizado
    
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
        
        # Verificar se há arquivo_mandado
        caminho_arquivo = mandado.get('arquivo_mandado')
        if not caminho_arquivo:
            return {
                'success': False,
                'error': "O mandado não possui arquivo (campo 'arquivo_mandado' vazio)"
            }
        
        # Construir URL completa se necessário
        if caminho_arquivo.startswith('http://') or caminho_arquivo.startswith('https://'):
            url_arquivo = caminho_arquivo
        else:
            # É um caminho relativo, construir URL completa
            credenciais_s3 = obter_credenciais_s3()
            url_arquivo = f"{credenciais_s3['s3_url']}/{credenciais_s3['s3_bucket_name']}/{caminho_arquivo}"
        
        # Fazer download do arquivo
        diretorio_saida = assegurar_diretorio_saida()
        nome_arquivo = gerar_nome_arquivo(numero_mandado, url_arquivo)
        caminho_arquivo_local = os.path.join(diretorio_saida, nome_arquivo)
        
        try:
            # Obter credenciais S3 (se não obteve acima)
            if 'credenciais_s3' not in locals():
                credenciais_s3 = obter_credenciais_s3()
            
            arquivo_conteudo = None
            
            # Tentar baixar usando boto3 se disponível e credenciais configuradas
            if HAS_BOTO3 and credenciais_s3['s3_access_key'] and credenciais_s3['s3_secret_key']:
                try:
                    arquivo_conteudo = _baixar_com_boto3(url_arquivo, credenciais_s3)
                except Exception as e_boto3:
                    # Se boto3 falhar, tentar com requests
                    pass
            
            # Fallback para requests.get() (para presigned URLs ou URLs públicas)
            if arquivo_conteudo is None:
                response = requests.get(url_arquivo, timeout=30)
                response.raise_for_status()
                arquivo_conteudo = response.content
            
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
                'error': f"Erro ao baixar arquivo do S3: {str(e)}"
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
        print("Uso: python baixar_arquivo_mandado.py <numero_mandado>")
        print("Exemplos:")
        print("  - Formatado: python baixar_arquivo_mandado.py 0841162-22.2025.8.23.0010.01.0001-17")
        print("  - Somente números: python baixar_arquivo_mandado.py 0841162222025823001001000117")
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
    
    result = baixar_arquivo_mandado(numero_ou_erro)
    
    # Remover objeto Response que não é serializável em JSON
    if 'response' in result:
        del result['response']
    
    # Imprimir o JSON resultante
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Retornar código de saída apropriado
    sys.exit(0 if result['success'] else 1)

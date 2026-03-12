#!/usr/bin/env python3
"""
Script para tratar passageiros pendentes:
1. Obter números de mandados dos passageiros com status "Pendente"
2. Baixar arquivos PDF dos mandados via BNMP3
3. Fazer upload dos PDFs para o sistema GCAP
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from gcap_sdk import Gcap
from bnmp3 import Bnmp3


# Carregar variáveis de ambiente do arquivo .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=str(env_path))

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def configurar_selenium_driver(download_dir: str):
    """Configura e retorna um WebDriver do Selenium para o BNMP3."""
    chrome_options = Options()
    
    # Maximizar janela para melhor renderização
    chrome_options.add_argument("--start-maximized")
    
    # Desabilitar notificações e outras popup
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    
    # Configurar diretório de download
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.popups": 0,
        "profile.managed_default_content_settings.pdf_viewer_enabled": False,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Usar webdriver-manager para gerenciar o driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver


def obter_mandados_pendentes(gcap: Gcap) -> list:
    """
    Obtém lista de números de mandados de passageiros com status 'Pendente'.
    
    Returns:
        list: Lista de dicts com 'cpf' e 'numero_mandado'
    """
    print("\n[ETAPA 1] Buscando passageiros pendentes...")
    logger.info("Iniciando busca de passageiros com status 'Pendente'")
    
    search_result = gcap.listar_passageiros(status='Pendente')
    
    if not search_result['success']:
        erro_msg = f"Erro na busca: {search_result.get('error', 'Erro desconhecido')}"
        print(f"✗ {erro_msg}")
        logger.error(erro_msg)
        return []
    
    # Extrair dados
    passageiros = search_result.get('data', {}).get('data', [])
    
    if not passageiros:
        print("⚠ Nenhum passageiro com status 'Pendente' encontrado.")
        logger.warning("Nenhum passageiro pendente encontrado")
        return []
    
    print(f"✓ Total de passageiros encontrados: {len(passageiros)}")
    
    # Filtrar passageiros com número de mandado
    mandados_pendentes = []
    for passageiro in passageiros:
        numero_mandado = passageiro.get('numero_mandado', '').strip()
        cpf = passageiro.get('cpf', '').strip()
        
        if numero_mandado and cpf:
            mandados_pendentes.append({
                'cpf': cpf,
                'numero_mandado': numero_mandado,
                'nome': passageiro.get('nome', 'N/A'),
                'passageiro_id': passageiro.get('id')
            })
    
    print(f"✓ Passageiros com mandado a processar: {len(mandados_pendentes)}")
    logger.info(f"Encontrados {len(mandados_pendentes)} passageiros com mandados pendentes")
    
    return mandados_pendentes


def processar_mandados(mandados_pendentes: list, bnmp3: Bnmp3, gcap: Gcap, download_dir: str) -> dict:
    """
    Processa cada mandado: baixa do BNMP3 e faz upload para GCAP.
    
    Returns:
        dict: Relatório com status de cada processamento
    """
    print("\n[ETAPA 2] Processando mandados...")
    logger.info(f"Iniciando processamento de {len(mandados_pendentes)} mandado(s)")
    
    relatorio = {
        'total': len(mandados_pendentes),
        'sucesso': [],
        'erro_download': [],
        'erro_upload': [],
        'erro_geral': []
    }
    
    for idx, mandado_info in enumerate(mandados_pendentes, 1):
        numero_mandado = mandado_info['numero_mandado']
        cpf = mandado_info['cpf']
        nome = mandado_info['nome']
        
        print(f"\n[{idx}/{len(mandados_pendentes)}] Processando: {nome} ({cpf})")
        print(f"  Mandado: {numero_mandado}")
        
        try:
            # ─── PASSO 1: BAIXAR MANDADO DO BNMP3 ───
            print(f"  [*] Baixando mandado do BNMP3...")
            
            try:
                bnmp3.baixar_mandado(numero_mandado)
                
                # Construir o caminho esperado do arquivo baixado
                numero_limpo = ''.join(filter(str.isdigit, numero_mandado))[:28]
                arquivo_mandado = os.path.join(download_dir, f"mandado_{numero_limpo}.pdf")
                
                if not os.path.exists(arquivo_mandado):
                    erro = f"Arquivo de mandado não encontrado após download: {arquivo_mandado}"
                    print(f"  ✗ {erro}")
                    logger.error(f"[{numero_mandado}] {erro}")
                    relatorio['erro_download'].append({
                        'numero_mandado': numero_mandado,
                        'cpf': cpf,
                        'erro': erro
                    })
                    continue
                
                print(f"  ✓ Mandado baixado com sucesso")
                
            except Exception as e:
                erro = f"Erro ao baixar mandado: {str(e)}"
                print(f"  ✗ {erro}")
                logger.error(f"[{numero_mandado}] {erro}")
                relatorio['erro_download'].append({
                    'numero_mandado': numero_mandado,
                    'cpf': cpf,
                    'erro': erro
                })
                continue
            
            # ─── PASSO 2: FAZER UPLOAD PARA GCAP ───
            print(f"  [*] Fazendo upload para GCAP...")
            
            try:
                upload_result = gcap.upload_mandados(arquivo_mandado)
                
                if upload_result['success']:
                    print(f"  ✓ Upload realizado com sucesso")
                    logger.info(f"[{numero_mandado}] Upload concluído com sucesso")
                    
                    relatorio['sucesso'].append({
                        'numero_mandado': numero_mandado,
                        'cpf': cpf,
                        'arquivo': arquivo_mandado
                    })
                else:
                    erro = f"Erro no upload: {upload_result.get('error', 'Erro desconhecido')}"
                    print(f"  ✗ {erro}")
                    logger.error(f"[{numero_mandado}] {erro}")
                    relatorio['erro_upload'].append({
                        'numero_mandado': numero_mandado,
                        'cpf': cpf,
                        'erro': erro
                    })
            
            except Exception as e:
                erro = f"Erro ao fazer upload: {str(e)}"
                print(f"  ✗ {erro}")
                logger.error(f"[{numero_mandado}] {erro}")
                relatorio['erro_upload'].append({
                    'numero_mandado': numero_mandado,
                    'cpf': cpf,
                    'erro': erro
                })
        
        except Exception as e:
            erro = f"Erro geral no processamento: {str(e)}"
            print(f"  ✗ {erro}")
            logger.error(f"[{numero_mandado}] {erro}")
            relatorio['erro_geral'].append({
                'numero_mandado': numero_mandado,
                'cpf': cpf,
                'erro': erro
            })
    
    return relatorio


def exibir_relatorio(relatorio: dict):
    """Exibe um relatório resumido do processamento."""
    print("\n" + "="*70)
    print("RELATÓRIO FINAL")
    print("="*70)
    print(f"Total processado:        {relatorio['total']}")
    print(f"Sucesso:                 {len(relatorio['sucesso'])}")
    print(f"Erro no download:        {len(relatorio['erro_download'])}")
    print(f"Erro no upload:          {len(relatorio['erro_upload'])}")
    print(f"Erro geral:              {len(relatorio['erro_geral'])}")
    print("="*70)
    
    if relatorio['sucesso']:
        print("\n✓ SUCESSOS:")
        for item in relatorio['sucesso']:
            print(f"  - {item['numero_mandado']} ({item['cpf']})")
    
    if relatorio['erro_download']:
        print("\n✗ ERROS NO DOWNLOAD:")
        for item in relatorio['erro_download']:
            print(f"  - {item['numero_mandado']} ({item['cpf']}): {item['erro']}")
    
    if relatorio['erro_upload']:
        print("\n✗ ERROS NO UPLOAD:")
        for item in relatorio['erro_upload']:
            print(f"  - {item['numero_mandado']} ({item['cpf']}): {item['erro']}")
    
    if relatorio['erro_geral']:
        print("\n✗ ERROS GERAIS:")
        for item in relatorio['erro_geral']:
            print(f"  - {item['numero_mandado']} ({item['cpf']}): {item['erro']}")
    
    print("="*70)


def main():
    """Função principal que orquestra o fluxo."""
    # Configurar stdout para UTF-8 (Windows compatibility)
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("\n" + "="*70)
    print("TRATADOR DE PASSAGEIROS PENDENTES")
    print("="*70)
    
    # ─── INICIALIZAÇÕES ───
    
    # Diretório de download temporário
    download_dir = os.path.expanduser("~\\Downloads\\gcap_mandados")
    os.makedirs(download_dir, exist_ok=True)
    print(f"\n[*] Diretório de download: {download_dir}")
    
    # Inicializar GCAP SDK
    print("\n[ETAPA 0] Inicializando sistemas...")
    gcap = Gcap()
    
    print("[*] Autenticando no GCAP...")
    login_result = gcap.login()
    if not login_result['success']:
        print(f"✗ Erro no login GCAP: {login_result['error']}")
        logger.error(f"Erro no login GCAP: {login_result['error']}")
        return
    
    print("✓ Autenticado no GCAP")
    logger.info("Login GCAP realizado com sucesso")
    
    # ─── OBTER MANDADOS PENDENTES ───
    
    mandados_pendentes = obter_mandados_pendentes(gcap)
    
    if not mandados_pendentes:
        print("\n⚠ Nenhum mandado para processar. Abortando.")
        logger.info("Nenhum mandado pendente para processar")
        return
    
    # ─── INICIALIZAR BNMP3 ───
    
    print("\n[*] Inicializando BNMP3...")
    
    # Obter credenciais do BNMP3 das variáveis de ambiente
    usuario_bnmp = os.getenv('BNMP3_USUARIO')
    senha_bnmp = os.getenv('BNMP3_SENHA')
    
    if not usuario_bnmp or not senha_bnmp:
        print("✗ Credenciais BNMP3 não configuradas!")
        print("  Configure as variáveis de ambiente:")
        print("    - BNMP3_USUARIO")
        print("    - BNMP3_SENHA")
        logger.error("Credenciais BNMP3 não encontradas no .env")
        return
    
    try:
        # Configurar Selenium WebDriver
        driver = configurar_selenium_driver(download_dir)
        
        # Criar instância do BNMP3
        bnmp3 = Bnmp3(
            driver=driver,
            download_dir=download_dir,
            logger=logger,
            baixar_certidao=False
        )
        
        # Fazer login no BNMP3
        print("[*] Autenticando no BNMP3...")
        bnmp3.login(usuario_bnmp, senha_bnmp)
        
        print("✓ Autenticado no BNMP3")
        logger.info("Login BNMP3 realizado com sucesso")
        
    except Exception as e:
        print(f"✗ Erro ao inicializar BNMP3: {str(e)}")
        logger.error(f"Erro ao inicializar BNMP3: {str(e)}")
        return
    
    # ─── PROCESSAR MANDADOS ───
    
    try:
        relatorio = processar_mandados(mandados_pendentes, bnmp3, gcap, download_dir)
    finally:
        # Fechar o WebDriver
        driver.quit()
        print("\n[*] WebDriver fechado")
    
    # ─── EXIBIR RELATÓRIO ───
    
    exibir_relatorio(relatorio)
    
    # Log resumido
    logger.info(
        f"Processamento concluído: {len(relatorio['sucesso'])} sucesso, "
        f"{len(relatorio['erro_download'])} erro download, "
        f"{len(relatorio['erro_upload'])} erro upload, "
        f"{len(relatorio['erro_geral'])} erro geral"
    )
    
    print("\n✓ Processamento concluído!")


if __name__ == '__main__':
    main()

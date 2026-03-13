#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BNMP - Download de Mandados de Prisão e Certidões de Cumprimento via Parâmetros CLI
Plataforma Digital do Poder Judiciário (PDPJ)

Script que recebe números de mandados como parâmetros de linha de comando,
realiza login, prepara a página de pesquisa e faz download dos mandados e certidões.

Requisitos:
    pip install selenium webdriver-manager python-dotenv

Uso:
    python baixar_mandados_bnmp.py <numero_mandado_1> <numero_mandado_2> ... <numero_mandado_N>

Exemplos:
    python baixar_mandados_bnmp.py 0000009282012810008501000312
    python baixar_mandados_bnmp.py 0000009282012810008501000312 0000033582016802001401000108 0000034802017802005501000124
"""

import os
import re
import sys
import time
import logging
import argparse
import shutil
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from bnmp3 import Bnmp3

# ─────────────────────────────────────────────────────────────
# Constantes e Configurações
# ─────────────────────────────────────────────────────────────
DOWNLOAD_DIR = "downloads"
ARCHIVE_DIR = r"Z:\Cris\mandados"

# ─────────────────────────────────────────────────────────────
# Configuração de Logging
# ─────────────────────────────────────────────────────────────
def configurar_logger(log_dir: str = "logs") -> logging.Logger:
    """Configura logger com rotação de arquivos."""
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "baixar_mandados_bnmp.log")
    logger = logging.getLogger("BNMP_Downloader_CLI")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    
    handler = RotatingFileHandler(
        log_file,
        maxBytes=2 * 1024 * 1024,
        backupCount=3
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


logger = None

# ─────────────────────────────────────────────────────────────
# Carregamento de Configuração
# ─────────────────────────────────────────────────────────────
def carregar_credenciais() -> dict:
    """
    Carrega credenciais do arquivo .env ou variáveis de ambiente.
    
    Retorna:
        dict com 'usuario' e 'senha'
    """
    # Tenta carregar do arquivo .env
    load_dotenv()
    
    usuario = os.getenv("BNMP3_USUARIO")
    senha = os.getenv("BNMP3_SENHA")
    
    if not usuario or not senha:
        raise ValueError(
            "Credenciais não encontradas. Configure BNMP3_USUARIO e BNMP3_SENHA "
            "no arquivo .env ou nas variáveis de ambiente."
        )
    
    return {"usuario": usuario, "senha": senha}


def resolver_diretorio_download() -> str:
    """Resolve e cria o diretório de download."""
    caminho = Path(DOWNLOAD_DIR).resolve()
    os.makedirs(caminho, exist_ok=True)
    return str(caminho)


# ─────────────────────────────────────────────────────────────
# Inicialização do Driver
# ─────────────────────────────────────────────────────────────
def criar_driver(download_dir: str) -> webdriver.Chrome:
    """Cria e retorna um Chrome WebDriver configurado."""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    
    prefs = {
        "download.default_directory": download_dir,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.pdf_viewer_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver


# ─────────────────────────────────────────────────────────────
# Movimentação de Arquivos
# ─────────────────────────────────────────────────────────────
def mover_para_arquivo(arquivo_origem: str, diretorio_destino: str = ARCHIVE_DIR) -> bool:
    r"""
    Move um arquivo para o diretório de arquivamento centralizado.
    
    Parâmetros:
        arquivo_origem: caminho completo do arquivo a mover
        diretorio_destino: diretório de destino (padrão: Z:\Cris\mandados)
    
    Retorna:
        True se movido com sucesso, False caso contrário
    """
    try:
        # Verifica se o caminho existe
        if not os.path.exists(arquivo_origem):
            print(f"[!] Arquivo não encontrado: {arquivo_origem}")
            if logger:
                logger.warning(f"Arquivo não encontrado ao tentar mover: {arquivo_origem}")
            return False
        
        # Cria diretório de destino se não existir
        os.makedirs(diretorio_destino, exist_ok=True)
        
        # Move o arquivo
        nome_arquivo = os.path.basename(arquivo_origem)
        destino = os.path.join(diretorio_destino, nome_arquivo)
        
        shutil.move(arquivo_origem, destino)
        print(f"[✓] Arquivo movido: {nome_arquivo}")
        if logger:
            logger.info(f"Arquivo movido para: {destino}")
        
        return True
    
    except Exception as e:
        print(f"[!] Erro ao mover arquivo {arquivo_origem}: {e}")
        if logger:
            logger.error(f"Erro ao mover arquivo: {e}")
        return False


# ─────────────────────────────────────────────────────────────
# Fluxo Principal
# ─────────────────────────────────────────────────────────────
def processar_mandado_com_arquivo(bnmp: Bnmp3, numero_mandado: str, download_dir: str, mover: bool = True) -> bool:
    """
    Processa um mandado usando a classe Bnmp3 e opcionalmente move para arquivo.
    
    Parâmetros:
        bnmp: Instância da classe Bnmp3
        numero_mandado: Número do mandado a processar
        download_dir: Diretório onde os arquivos estão
        mover: Se True, move os arquivos para o diretório centralizado
    
    Retorna:
        True se processado com sucesso, False caso contrário
    """
    try:
        # Processa o mandado (faz download)
        bnmp.baixar_mandado(numero_mandado)
        
        # Move arquivos para o arquivo centralizado se solicitado
        if mover:
            numero_limpo = re.sub(r"\D", "", numero_mandado)[:28]
            arquivo_mandado = os.path.join(download_dir, f"mandado_{numero_limpo}.pdf")
            arquivo_certidao = os.path.join(download_dir, f"certidao_{numero_limpo}.pdf")
            
            if os.path.exists(arquivo_mandado):
                mover_para_arquivo(arquivo_mandado)
            
            if os.path.exists(arquivo_certidao):
                mover_para_arquivo(arquivo_certidao)
        
        return True
    
    except Exception as e:
        print(f"[!] Erro ao processar mandado {numero_mandado}: {e}")
        if logger:
            logger.error(f"Erro ao processar mandado {numero_mandado}: {e}")
        return False


def main():
    """Função principal."""
    global logger
    
    # Inicializa logger
    logger = configurar_logger()
    
    # Configura argumentos de linha de comando
    parser = argparse.ArgumentParser(
        description="Baixa mandados de prisão do BNMP3 usando números fornecidos como parâmetros",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python baixar_mandados_bnmp.py 0000009282012810008501000312
  python baixar_mandados_bnmp.py 0000009282012810008501000312 0000033582016802001401000108
  python baixar_mandados_bnmp.py $(cat lista_mandados/mandados.txt)
        """
    )
    
    parser.add_argument(
        "mandados",
        nargs="+",
        help="Números de mandados a serem baixados (pelo menos um)"
    )
    
    parser.add_argument(
        "--no-mover",
        action="store_true",
        help="Não move os arquivos para a pasta centralizada (Z:\\Cris\\mandados)"
    )
    
    parser.add_argument(
        "--download-dir",
        default=DOWNLOAD_DIR,
        help=f"Diretório de download (padrão: {DOWNLOAD_DIR})"
    )
    
    parser.add_argument(
        "--certidao",
        action="store_true",
        help="Baixa a certidão de cumprimento junto com o mandado"
    )
    
    args = parser.parse_args()
    
    mandados = args.mandados
    download_dir = resolver_diretorio_download()
    mover_arquivos = not args.no_mover
    baixar_certidao = args.certidao
    
    print(f"\n{'='*70}")
    print(f"BNMP - Download de Mandados de Prisão (Classe Bnmp3)")
    print(f"{'='*70}")
    print(f"Mandados a processar: {len(mandados)}")
    for mandado in mandados:
        print(f"  - {mandado}")
    print(f"Diretório de download: {download_dir}")
    print(f"Baixar certidão: {'SIM' if baixar_certidao else 'NÃO'}")
    if mover_arquivos:
        print(f"Arquivo centralizado: {ARCHIVE_DIR}")
    else:
        print(f"Movimentação de arquivos: DESATIVADA")
    print(f"{'='*70}\n")
    
    if logger:
        logger.info(f"Iniciando processamento de {len(mandados)} mandado(s)")
    
    # Carrega credenciais
    try:
        credenciais = carregar_credenciais()
    except ValueError as e:
        print(f"[!] Erro: {e}")
        if logger:
            logger.error(str(e))
        sys.exit(1)
    
    # Inicializa driver e classe Bnmp3
    driver = None
    try:
        driver = criar_driver(download_dir)
        
        # Cria instância da classe Bnmp3
        bnmp = Bnmp3(driver, download_dir, logger, baixar_certidao=baixar_certidao)
        
        # Login e preparação da página em uma única etapa
        print("\n[*] Realizando autenticação...")
        if logger:
            logger.info("Iniciando autenticação")
        bnmp.login(credenciais["usuario"], credenciais["senha"])
        
        # Processar cada mandado
        sucesso = 0
        falha = 0
        
        for numero_mandado in mandados:
            numero_mandado = numero_mandado.strip()
            if numero_mandado:
                if processar_mandado_com_arquivo(bnmp, numero_mandado, download_dir, mover_arquivos):
                    sucesso += 1
                else:
                    falha += 1
        
        # Resumo final
        print(f"\n{'='*70}")
        print(f"RESUMO FINAL")
        print(f"{'='*70}")
        print(f"Total de mandados: {len(mandados)}")
        print(f"Sucesso: {sucesso}")
        print(f"Falhas: {falha}")
        if mover_arquivos:
            print(f"Diretório de arquivamento: {ARCHIVE_DIR}")
        print(f"{'='*70}\n")
        
        if logger:
            logger.info(f"Processamento concluído: {sucesso} sucesso, {falha} falhas")
    
    except Exception as e:
        print(f"[!] Erro fatal: {e}")
        if logger:
            logger.error(f"Erro fatal: {e}", exc_info=True)
        sys.exit(1)
    
    finally:
        if driver:
            print("[*] Fechando navegador...")
            driver.quit()


if __name__ == "__main__":
    main()

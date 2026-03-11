#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair dados de um PDF de Certidão de Cumprimento de Mandado.
Retorna um JSON com os dados extraídos.
"""

import sys
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import pdfplumber
except ImportError:
    print("Erro: pdfplumber não está instalado. Execute: pip install pdfplumber")
    sys.exit(1)


# ─── CLASSES E TIPOS ─────────────────────────────────────────────────────

class CertidaoDeMandado:
    """Estrutura de dados para uma Certidão de Cumprimento de Mandado."""
    
    def __init__(self, arquivo: str):
        self.arquivo = arquivo
        self.erro = False
        self.numero_mandado: Optional[str] = None
        self.data_prisao: Optional[str] = None
        self.unidade_cumpridora: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            'arquivo': self.arquivo,
            'erro': self.erro,
            'numero_mandado': self.numero_mandado,
            'data_prisao': self.data_prisao,
            'unidade_cumpridora': self.unidade_cumpridora,
        }


# ─── FUNÇÕES AUXILIARES ──────────────────────────────────────────────────

def normalizar_texto(valor: str) -> str:
    """Normaliza espaços no texto."""
    return re.sub(r'\s+', ' ', valor).strip()


def converter_data_para_iso(data_str: Optional[str]) -> Optional[str]:
    """Converte data para formato ISO."""
    if not data_str:
        return None
    
    limpo = data_str.strip()
    
    # Padrão completo: DD/MM/YYYY HH:MM:SS ou DD.MM.YYYY HH:MM:SS
    completo = re.match(
        r'^(\d{2})[./](\d{2})[./](\d{4})\s+(\d{1,2}):?(\d{2}):?(\d{2})?$',
        limpo
    )
    
    if completo:
        dia, mes, ano, hora, minuto, segundo = completo.groups()
        segundo = segundo or '00'
        return f'{ano}-{mes}-{dia}T{hora.zfill(2)}:{minuto}:{segundo}'
    
    # Padrão simples: DD/MM/YYYY ou DD.MM.YYYY
    simples = re.match(r'^(\d{2})[./](\d{2})[./](\d{4})$', limpo)
    
    if simples:
        dia, mes, ano = simples.groups()
        return f'{ano}-{mes}-{dia}'
    
    return None


def extrair_campo(texto: str, padrao: re.Pattern) -> Optional[str]:
    """Extrai um campo usando regex."""
    match = padrao.search(texto)
    if not match:
        return None
    
    valor = match.group(1)
    return normalizar_texto(valor)


def extrair_numero_mandado(texto: str) -> Optional[str]:
    """Extrai número do mandado da seção 'Mandados alcançados'."""
    # Buscar bloco de "Mandados alcançados"
    bloco_match = re.search(
        r'Mandados\s+alcançados\s*\n.+?\n([\s\S]+?)(?=Observações|$)',
        texto,
        re.IGNORECASE
    )
    
    if not bloco_match:
        return None
    
    bloco = bloco_match.group(1)
    
    # Procurar por um número de mandado (sequência de dígitos com possíveis separadores)
    numero_match = re.search(r'(\d{4,}[\d.\-]{15,})', bloco)
    
    if numero_match:
        return numero_match.group(1).strip()
    
    return None


def extrair_certidao_de_mandado(caminho_pdf: str) -> CertidaoDeMandado:
    """
    Extrai dados de um PDF de Certidão de Cumprimento de Mandado.
    
    Args:
        caminho_pdf: Caminho para o arquivo PDF
        
    Returns:
        CertidaoDeMandado com os dados extraídos
    """
    nome_arquivo = Path(caminho_pdf).name
    resultado = CertidaoDeMandado(nome_arquivo)
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            # Extrair texto de todas as páginas
            textos = []
            for pagina in pdf.pages:
                textos.append(pagina.extract_text() or '')
            
            texto_completo = '\n'.join(textos)
            
            if not texto_completo:
                resultado.erro = True
                return resultado
    
    except Exception as e:
        print(f"Erro ao abrir PDF: {e}", file=sys.stderr)
        resultado.erro = True
        return resultado
    
    # Normalizar quebras de linha
    texto = texto_completo.replace('\r', '\n')
    
    # Verificar se é uma Certidão de Cumprimento de Mandado
    if not re.search(
        r'CERTIDÃO\s+DE\s+CUMPRIMENTO\s+DE\s+MANDADO',
        texto,
        re.IGNORECASE
    ):
        resultado.erro = True
        return resultado
    
    resultado.erro = False
    
    # ─── EXTRAÇÃO DE CAMPOS ──────────────────────────────────────────────
    
    # Número do Mandado
    resultado.numero_mandado = extrair_numero_mandado(texto)
    
    # Data da Prisão
    data_prisao_str = extrair_campo(
        texto,
        re.compile(r'Data\s+da\s+Pris[ãa]o[:\s]+(\d{2}[./]\d{2}[./]\d{4})', re.IGNORECASE)
    )
    resultado.data_prisao = converter_data_para_iso(data_prisao_str)
    
    # Unidade Comunicante (ou Cumpridora)
    unidade_match = re.search(
        r'Unidade\s+Comunicante[:\s]+([^\n]+)',
        texto,
        re.IGNORECASE
    )
    
    if unidade_match:
        resultado.unidade_cumpridora = normalizar_texto(unidade_match.group(1))
    
    return resultado


# ─── MAIN ────────────────────────────────────────────────────────────────

def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print("Uso: python extrair_dados_certidao.py <caminho_do_pdf>")
        print()
        print("Exemplo:")
        print("  python extrair_dados_certidao.py certidao.pdf")
        sys.exit(1)
    
    caminho_pdf = sys.argv[1]
    
    # Verificar se o arquivo existe
    if not Path(caminho_pdf).exists():
        print(f"Erro: Arquivo '{caminho_pdf}' não encontrado.", file=sys.stderr)
        sys.exit(1)
    
    # Extrair dados
    certidao = extrair_certidao_de_mandado(caminho_pdf)
    
    # Retornar como JSON
    print(json.dumps(certidao.to_dict(), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair dados de um PDF de Mandado de Prisão.
Retorna um JSON com os dados extraídos.
"""

import sys
import json
import re
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime

try:
    import pdfplumber
except ImportError:
    print("Erro: pdfplumber não está instalado. Execute: pip install pdfplumber")
    sys.exit(1)


# ─── CLASSES E TIPOS ─────────────────────────────────────────────────────

class MandadoPrisao:
    """Estrutura de dados para um Mandado de Prisão."""
    
    def __init__(self, arquivo: str):
        self.arquivo = arquivo
        self.erro = False
        self.numero_mandado: Optional[str] = None
        self.numero_processo: Optional[str] = None
        self.nome_preso: Optional[str] = None
        self.cpf: Optional[str] = None
        self.rg: Optional[str] = None
        self.rji: Optional[str] = None
        self.data_nascimento: Optional[str] = None
        self.data_validade: Optional[str] = None
        self.especie_prisao: Optional[str] = None
        self.tipificacao_penal: Optional[str] = None
        self.magistrado: Optional[str] = None
        self.orgao_judicial: Optional[str] = None
        self.data_mandado: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            'arquivo': self.arquivo,
            'erro': self.erro,
            'numero_mandado': self.numero_mandado,
            'numero_processo': self.numero_processo,
            'nome_preso': self.nome_preso,
            'cpf': self.cpf,
            'rg': self.rg,
            'rji': self.rji,
            'data_nascimento': self.data_nascimento,
            'data_validade': self.data_validade,
            'especie_prisao': self.especie_prisao,
            'tipificacao_penal': self.tipificacao_penal,
            'magistrado': self.magistrado,
            'orgao_judicial': self.orgao_judicial,
            'data_mandado': self.data_mandado,
        }


# ─── FUNÇÕES AUXILIARES ──────────────────────────────────────────────────

NAO_INFORMADO = re.compile(r'^n[ãa]o\s+informad[oa]\.?$', re.IGNORECASE)


def normalizar_espacos(texto: str) -> str:
    """Normaliza espaços no texto."""
    texto = texto.replace('\r', '\n')
    texto = re.sub(r'[ \t]+', ' ', texto)
    texto = re.sub(r'\n+', '\n', texto)
    return texto.strip()


def limpar(valor: Optional[str]) -> Optional[str]:
    """Limpa e valida um valor."""
    if valor is None:
        return None
    
    valor = re.sub(r'\s+', ' ', valor).strip()
    
    if not valor or NAO_INFORMADO.match(valor):
        return None
    
    return valor


def escape_re(s: str) -> str:
    """Escapa caracteres especiais para regex."""
    return re.escape(s)


def extrair_entre(
    texto: str,
    ini: str | re.Pattern,
    fim: str | re.Pattern
) -> Optional[str]:
    """Extrai texto entre dois padrões."""
    # Converter string para regex se necessário
    if isinstance(ini, str):
        ini_re = re.compile(escape_re(ini), re.IGNORECASE)
    else:
        # Se já é um Pattern, usar diretamente mas garantir que tem IGNORECASE
        flags = ini.flags | re.IGNORECASE if not (ini.flags & re.IGNORECASE) else ini.flags
        ini_re = re.compile(ini.pattern, flags)
    
    if isinstance(fim, str):
        fim_re = re.compile(escape_re(fim), re.IGNORECASE)
    else:
        # Se já é um Pattern, usar diretamente mas garantir que tem IGNORECASE
        flags = fim.flags | re.IGNORECASE if not (fim.flags & re.IGNORECASE) else fim.flags
        fim_re = re.compile(fim.pattern, flags)
    
    # Encontrar início
    m_ini = ini_re.search(texto)
    if not m_ini:
        return None
    
    start = m_ini.end()
    rest = texto[start:]
    
    # Encontrar fim
    m_fim = fim_re.search(rest)
    if not m_fim:
        return None
    
    resultado = rest[:m_fim.start()]
    return limpar(resultado)


def data_iso(valor: Optional[str]) -> Optional[str]:
    """Converte data em formato DD/MM/YYYY ou DD.MM.YYYY para ISO."""
    if not valor:
        return None
    
    valor = valor.strip()
    
    # Padrão: DD/MM/YYYY ou DD.MM.YYYY, opcionalmente com hora
    m = re.match(
        r'^(\d{2})[./](\d{2})[./](\d{4})(?:\s+(\d{2}):(\d{2}):(\d{2}))?$',
        valor
    )
    
    if not m:
        return None
    
    d, mo, a, h, mi, se = m.groups()
    
    if h:
        return f'{a}-{mo}-{d}T{h}:{mi}:{se}'
    else:
        return f'{a}-{mo}-{d}'


def extrair_tipificacao(texto: str) -> Optional[str]:
    """Extrai tipificação penal do texto."""
    m = re.search(
        r'Tipifica[cç][aã]o\s+Penal[:\s]*([\s\S]*?)(?=Teor\s+do\s+Documento|Identifica[cç][aã]o\s+biom[eé]trica|Pena\s+restante|Regime\s+Prisional|Lavrado\s+por|Documento\s+assinado\s+(?:digitalmente|eletronicamente)|Telefones\s*:)',
        texto,
        re.IGNORECASE
    )
    
    if m:
        return limpar(m.group(1))
    
    return None


def extrair_magistrado_e_data_doc(texto: str) -> Tuple[Optional[str], Optional[str]]:
    """Extrai magistrado e data do documento."""
    # Padrão 1: "Documento assinado digitalmente por ... magistrada em DD/MM/YYYY HH:MM:SS"
    m1 = re.search(
        r'Documento\s+assinado\s+digitalmente\s+por\s+([\s\S]*?)\s+magistrad[oa]\s+em\s+(\d{2}\/\d{2}\/\d{4}\s+\d{2}:\d{2}:\d{2})',
        texto,
        re.IGNORECASE
    )
    
    if m1:
        magistrado = limpar(m1.group(1))
        data = m1.group(2)
        return magistrado, data
    
    # Padrão 2: apenas confirmar que foi assinado por magistrado
    m2 = re.search(
        r'Documento\s+assinado\s+digitalmente\s+pel[oa]\s+magistrad[oa]',
        texto,
        re.IGNORECASE
    )
    
    if m2:
        return None, None
    
    return None, None


def extrair_mandado_de_prisao(caminho_pdf: str) -> MandadoPrisao:
    """
    Extrai dados de um PDF de Mandado de Prisão.
    
    Args:
        caminho_pdf: Caminho para o arquivo PDF
        
    Returns:
        MandadoPrisao com os dados extraídos
    """
    nome_arquivo = Path(caminho_pdf).name
    resultado = MandadoPrisao(nome_arquivo)
    
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
    
    # Normalizar espaços
    texto = normalizar_espacos(texto_completo)
    
    # Verificar se é um mandado de prisão
    if not re.search(r'MANDADO\s+DE\s+PRIS[ÃA]O', texto, re.IGNORECASE):
        resultado.erro = True
        return resultado
    
    resultado.erro = False
    
    # ─── EXTRAÇÃO DE CAMPOS ──────────────────────────────────────────────
    
    # Número do Mandado
    resultado.numero_mandado = extrair_entre(
        texto,
        re.compile(r'N[°ºo]\s*do\s*Mandado\s*:', re.IGNORECASE),
        re.compile(r'Data\s*de\s*validade\s*:|A\s*pessoa\s*presa\s*deve\s*ser', re.IGNORECASE)
    )
    
    # Número do Processo
    resultado.numero_processo = extrair_entre(
        texto,
        re.compile(r'N[º°o]\s*(?:do\s*)?processo\s*:', re.IGNORECASE),
        re.compile(r'[ÓO]rg[ãa]o\s*Judicial\s*:', re.IGNORECASE)
    )
    
    # Data de Validade
    bloco_validade = extrair_entre(
        texto,
        re.compile(r'Data\s*de\s*validade\s*:', re.IGNORECASE),
        re.compile(r'Nome\s*da\s*Pessoa\s*:|MANDADO\s*DE\s*PRIS[ÃA]O|A\s*pessoa\s*presa\s*deve\s*ser', re.IGNORECASE)
    )
    
    data_validade_mandado = None
    if bloco_validade:
        m = re.search(r'\d{2}/\d{2}/\d{4}', bloco_validade)
        if m:
            data_validade_mandado = m.group(0)
        else:
            data_validade_mandado = bloco_validade
    
    resultado.data_validade = data_iso(data_validade_mandado)
    
    # Nome da Pessoa
    resultado.nome_preso = extrair_entre(
        texto,
        re.compile(r'Nome\s*(?:da\s*Pessoa\s*)?:', re.IGNORECASE),
        re.compile(r'CPF\s*:|Marcas\s*e\s*sinais\s*:', re.IGNORECASE)
    )
    
    # CPF
    m_cpf = re.search(r'CPF\s*:\s*([0-9.*-]{11,18})', texto, re.IGNORECASE)
    resultado.cpf = limpar(m_cpf.group(1)) if m_cpf else None
    
    # RG
    m_rg = re.search(r'\bRG\s*:\s*([^\n]+)', texto, re.IGNORECASE)
    rg_bruto = limpar(m_rg.group(1)) if m_rg else None
    resultado.rg = None if (rg_bruto and NAO_INFORMADO.match(rg_bruto)) else rg_bruto
    
    # RJI
    m_rji = re.search(r'\bRJI\s*:\s*([^\n]+)', texto, re.IGNORECASE)
    resultado.rji = limpar(m_rji.group(1)) if m_rji else None
    
    # Data de Nascimento
    m_data_nasc = re.search(
        r'Data\s*de\s*[Nn]asc(?:imento)?\s*\.?\s*:\s*(\d{2}[.\/]\d{2}[.\/]\d{4})',
        texto,
        re.IGNORECASE
    )
    resultado.data_nascimento = data_iso(m_data_nasc.group(1)) if m_data_nasc else None
    
    # Espécie de Prisão
    especie_1 = extrair_entre(
        texto,
        re.compile(r'Esp[ée]cie\s*de\s*pris[ãa]o\s*:', re.IGNORECASE),
        re.compile(r'Tipifica[cç][aã]o\s*Penal\s*:', re.IGNORECASE)
    )
    
    if not especie_1:
        m_especie = re.search(
            r'Esp[ée]cie\s+de\s+pris[ãa]o\s*:\s*([^\n]+)',
            texto,
            re.IGNORECASE
        )
        especie_1 = limpar(m_especie.group(1)) if m_especie else None
    
    resultado.especie_prisao = especie_1
    
    # Tipificação Penal
    resultado.tipificacao_penal = extrair_tipificacao(texto)
    
    # Órgão Judicial
    resultado.orgao_judicial = extrair_entre(
        texto,
        re.compile(r'[ÓO]rg[ãa]o\s*Judicial\s*:', re.IGNORECASE),
        re.compile(r'Esp[ée]cie\s*de\s*pris[ãa]o\s*:', re.IGNORECASE)
    )
    
    # Magistrado e Data do Documento
    magistrado, data_doc_assinatura = extrair_magistrado_e_data_doc(texto)
    resultado.magistrado = magistrado
    
    # Data do Mandado
    trecho_data_mandado = extrair_entre(
        texto,
        re.compile(r'\sem\s', re.IGNORECASE),
        re.compile(r'Para\s+confirmar\s+a\s+autenticidade', re.IGNORECASE)
    )
    
    data_doc_br = None
    if data_doc_assinatura:
        m = re.search(r'\d{2}/\d{2}/\d{4}', data_doc_assinatura)
        if m:
            data_doc_br = m.group(0)
    
    if not data_doc_br and trecho_data_mandado:
        m = re.search(r'\d{2}/\d{2}/\d{4}', trecho_data_mandado)
        if m:
            data_doc_br = m.group(0)
    
    resultado.data_mandado = data_iso(data_doc_br)
    
    return resultado


# ─── MAIN ────────────────────────────────────────────────────────────────

def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print("Uso: python extrair_dados_mandado.py <caminho_do_pdf>")
        print()
        print("Exemplo:")
        print("  python extrair_dados_mandado.py mandado.pdf")
        sys.exit(1)
    
    caminho_pdf = sys.argv[1]
    
    # Verificar se o arquivo existe
    if not Path(caminho_pdf).exists():
        print(f"Erro: Arquivo '{caminho_pdf}' não encontrado.", file=sys.stderr)
        sys.exit(1)
    
    # Extrair dados
    mandado = extrair_mandado_de_prisao(caminho_pdf)
    
    # Retornar como JSON
    print(json.dumps(mandado.to_dict(), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

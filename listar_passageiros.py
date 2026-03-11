#!/usr/bin/env python3

import sys
import json
import calendar
from datetime import datetime, timedelta, timezone
from gcap_sdk import Gcap

def parse_date_input(date_str):
    """
    Analisa a entrada de data e retorna data_from e data_to.
    
    Args:
        date_str (str): Data no formato YYYY-MM-DD (data exata) ou YYYY-MM (mês)
    
    Returns:
        tuple: (data_from, data_to) no formato YYYY-MM-DD
    """
    if len(date_str) == 7:  # Formato YYYY-MM (mês)
        year, month = map(int, date_str.split('-'))
        last_day = calendar.monthrange(year, month)[1]
        data_from = f"{year:04d}-{month:02d}-01"
        data_to = f"{year:04d}-{month:02d}-{last_day:02d}"
        return data_from, data_to
    else:  # Formato YYYY-MM-DD (data exata)
        return date_str, date_str

def validate_status(status_str):
    """
    Valida e normaliza o valor de status.
    
    Args:
        status_str (str): Status fornecido pelo usuário
    
    Returns:
        tuple: (is_valid, normalized_status, error_message)
    """
    if not status_str:
        return False, None, "Status não pode estar vazio"
    
    # Valores aceitos (case-insensitive)
    valid_statuses = {
        'pendente': 'Pendente',
        'em atendimento': 'Em Atendimento',
        'finalizado': 'Finalizado'
    }
    
    status_lower = status_str.lower().strip()
    
    if status_lower in valid_statuses:
        return True, valid_statuses[status_lower], None
    
    valid_values = ', '.join([f'"{v}"' for v in valid_statuses.keys()])
    error_msg = f'Status inválido: "{status_str}". Valores aceitos: {valid_values}'
    return False, None, error_msg

def formatar_data_zona_horaria(data_from_str, data_to_str):
    """
    Recebe datas no formato ISO (YYYY-MM-DD) e retorna as datas
    com timezone, adicionando 3 horas.
    
    Args:
        data_from_str (str): Data inicial no formato ISO (ex: '2026-03-10')
        data_to_str (str): Data final no formato ISO (ex: '2026-03-31')
    
    Returns:
        tuple: (data_from, data_to) formatadas como strings ISO com 3 horas adicionadas
               data_from = 2026-03-10T03:00:00.000000
               data_to = 2026-03-31T02:59:59.999999
    """
    try:
        # Parse da data inicial
        data_from = datetime.fromisoformat(data_from_str).replace(tzinfo=timezone.utc)
        
        # Parse da data final
        data_to = datetime.fromisoformat(data_to_str).replace(tzinfo=timezone.utc)
        
        # Adicionar 3 horas na data inicial
        data_from_adjusted = data_from + timedelta(hours=3)
        
        # data_to é o dia final + 3 horas - 1 microsegundo
        data_to_adjusted = (data_to + timedelta(days=1) + timedelta(hours=3)) - timedelta(microseconds=1)
        
        # Formatar como strings ISO com o padrão correto
        data_from_formatted = f"{data_from_adjusted.strftime('%Y-%m-%dT%H:%M:%S')}.000000"
        data_to_formatted = f"{data_to_adjusted.strftime('%Y-%m-%dT%H:%M:%S')}.999999"
        
        return data_from_formatted, data_to_formatted
    
    except ValueError as e:
        return None, f"Erro ao fazer parse da data: {str(e)}"

def listar_passageiros(data_embarque, preso=False, status=None):
    """
    Lista passageiros com datas de embarque dentro do período especificado.
    
    Args:
        data_embarque (str): Data no formato ISO (YYYY-MM-DD) para data exata,
                            ou YYYY-MM para buscar todo um mês
        preso (bool): Se True, filtra apenas passageiros presos. Padrão: False
        status (str): Status do passageiro (Pendente, Em Atendimento, Finalizado). Padrão: None
    
    Returns:
        dict: JSON com os resultados da busca
    """
    # Fazer parse da data de entrada
    data_from_str, data_to_str = parse_date_input(data_embarque)
    
    # Formatar as datas com timezone
    data_from, data_to = formatar_data_zona_horaria(data_from_str, data_to_str)
    
    if data_from is None:
        return {
            'success': False,
            'error': data_to
        }
    
    # Instanciar a classe Gcap
    gcap = Gcap()
    
    try:
        # Fazer login
        login_result = gcap.login()
        
        if not login_result['success']:
            return {
                'success': False,
                'error': f'Falha no login: {login_result["error"]}'
            }
        
        print(f"✅ Login realizado com sucesso!")
        print(f"📅 Pesquisando passageiros entre {data_from} e {data_to}")
        
        # Buscar passageiros com filtros de data
        filtros = {
            'data_embarque_from': data_from,
            'data_embarque_to': data_to
        }
        
        # Adicionar filtro de preso se informado
        if preso:
            filtros['preso'] = True
        
        # Adicionar filtro de status se informado
        if status:
            filtros['status'] = status
        
        resultado = gcap.listar_passageiros(**filtros)
        
        # Fazer logout
        gcap.logout()
        
        if resultado['success']:
            resposta_json = resultado['data']
            
            # Filtrar por data_prisao se preso=True
            if preso:
                passageiros = resposta_json.get('data', [])
                passageiros_presos = [
                    p for p in passageiros 
                    if p.get('mandados') and p['mandados'].get('data_prisao') is not None
                ]
                resposta_json['data'] = passageiros_presos
            
            total_passageiros = len(resposta_json.get('data', []))
            print(f"✅ Encontrados {total_passageiros} passageiros")
            
            # Exibir resultados formatados
            print("\n" + "="*80)
            print("RESULTADO DA BUSCA")
            print("="*80)
            print(json.dumps(resposta_json, indent=2, ensure_ascii=False))
            
            return {
                'success': True,
                'data': resposta_json,
                'total': total_passageiros
            }
        else:
            return {
                'success': False,
                'error': f'Erro ao listar passageiros: {resultado.get("error", "Erro desconhecido")}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro na busca: {str(e)}'
        }

def main():
    """
    Função principal que processa argumentos de linha de comando.
    """
    if len(sys.argv) < 2:
        print("Uso: python listar_passageiros.py <data> [--preso] [--status=<status>]")
        print("Exemplos:")
        print("  python listar_passageiros.py 2026-03-10        (data exata)")
        print("  python listar_passageiros.py 2026-03           (mês inteiro)")
        print("  python listar_passageiros.py 2026-03-10 --preso")
        print("  python listar_passageiros.py 2026-03-10 --status='Pendente'")
        print("  python listar_passageiros.py 2026-03-10 --preso --status='Em Atendimento'")
        print("\nValores de status aceitos: 'Pendente', 'Em Atendimento', 'Finalizado'")
        sys.exit(1)
    
    data_embarque = sys.argv[1]
    preso = '--preso' in sys.argv
    
    # Parsear parâmetro --status
    status = None
    for arg in sys.argv[2:]:
        if arg.startswith('--status='):
            status = arg.replace('--status=', '').strip()
            # Remove aspas se presentes
            if (status.startswith('"') and status.endswith('"')) or (status.startswith("'") and status.endswith("'")):
                status = status[1:-1]
            break
    
    # Validar status se fornecido
    if status:
        is_valid, normalized_status, error_msg = validate_status(status)
        if not is_valid:
            print(f"❌ Erro: {error_msg}", file=sys.stderr)
            sys.exit(1)
        status = normalized_status
    
    resultado = listar_passageiros(data_embarque, preso=preso, status=status)
    
    if not resultado['success']:
        print(f"❌ Erro: {resultado['error']}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0)

if __name__ == '__main__':
    main()

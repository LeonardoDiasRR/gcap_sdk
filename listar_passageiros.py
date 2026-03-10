#!/usr/bin/env python3

import sys
import json
from datetime import datetime, timedelta, timezone
from gcap_sdk import Gcap

def formatar_data_zona_horaria(data_str):
    """
    Recebe uma data no formato ISO (YYYY-MM-DD) e retorna as datas
    com timezone, adicionando 3 horas.
    
    Args:
        data_str (str): Data no formato ISO (ex: '2026-03-10')
    
    Returns:
        tuple: (data_from, data_to) formatadas como strings ISO com 3 horas adicionadas
               data_from = 2026-03-10T03:00:00.000000
               data_to = 2026-03-11T02:59:59.999999
    """
    try:
        # Parse da data recebida
        data = datetime.fromisoformat(data_str).replace(tzinfo=timezone.utc)
        
        # Adicionar 3 horas
        data_from = data + timedelta(hours=3)
        
        # data_to é o próximo dia + 3 horas - 1 microsegundo
        data_to = (data + timedelta(days=1) + timedelta(hours=3)) - timedelta(microseconds=1)
        
        # Formatar como strings ISO com o padrão correto
        data_from_str = f"{data_from.strftime('%Y-%m-%dT%H:%M:%S')}.000000"
        data_to_str = f"{data_to.strftime('%Y-%m-%dT%H:%M:%S')}.999999"
        
        return data_from_str, data_to_str
    
    except ValueError as e:
        return None, f"Erro ao fazer parse da data: {str(e)}"

def listar_passageiros(data_embarque, preso=False):
    """
    Lista passageiros com datas de embarque dentro do período especificado.
    
    Args:
        data_embarque (str): Data no formato ISO (YYYY-MM-DD)
        preso (bool): Se True, filtra apenas passageiros presos. Padrão: False
    
    Returns:
        dict: JSON com os resultados da busca
    """
    # Formatar as datas
    data_from, data_to = formatar_data_zona_horaria(data_embarque)
    
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
        print("Uso: python listar_passageiros.py <data> [--preso]")
        print("Exemplo: python listar_passageiros.py 2026-03-10")
        print("Exemplo com filtro de preso: python listar_passageiros.py 2026-03-10 --preso")
        sys.exit(1)
    
    data_embarque = sys.argv[1]
    preso = '--preso' in sys.argv
    
    resultado = listar_passageiros(data_embarque, preso=preso)
    
    if not resultado['success']:
        print(f"❌ Erro: {resultado['error']}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Script para atualizar números de mandado dos passageiros a partir de arquivo CSV
"""

import csv
from gcap_sdk import Gcap


def main():
    # Inicializar SDK
    gcap = Gcap()
    
    # Fazer login
    print("Autenticando...")
    login_result = gcap.login()
    if not login_result['success']:
        print(f"Erro no login: {login_result['error']}")
        return
    
    print("Autenticação bem-sucedida!\n")
    
    # Caminho do arquivo CSV
    csv_file = 'arquivos/cpf_mandados.csv'
    
    # Estatísticas
    total = 0
    encontrados = 0
    atualizados = 0
    erros = 0
    nao_encontrados = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            
            for row in csv_reader:
                total += 1
                cpf = row['cpf'].strip()
                # Remover formatação do CPF (pontos e hífens)
                cpf = cpf.replace('.', '').replace('-', '')
                numero_mandado = row['numero_mandado'].strip()
                
                print(f"[{total}] Processando CPF: {cpf}")
                
                # Pesquisar passageiro pelo CPF
                search_result = gcap.listar_passageiros(cpf=cpf)
                
                if not search_result['success']:
                    print(f"  ❌ Erro na busca: {search_result.get('error', 'Erro desconhecido')}")
                    erros += 1
                    continue
                
                # Extrair dados da resposta
                passageiros = search_result.get('data', {}).get('data', [])
                
                if not passageiros:
                    print(f"  ⚠️  Passageiro não encontrado")
                    nao_encontrados += 1
                    continue
                
                encontrados += 1
                
                # Pegar o primeiro passageiro encontrado
                passageiro = passageiros[0]
                passageiro_id = passageiro.get('id')
                
                print(f"  ✓ Passageiro encontrado: {passageiro.get('nome', 'N/A')} (ID: {passageiro_id})")
                
                # Atualizar mandado
                update_result = gcap.atualizar_passageiro(
                    passageiro_id,
                    numero_mandado=numero_mandado
                )
                
                if update_result['success']:
                    print(f"  ✓ Mandado atualizado para: {numero_mandado}")
                    atualizados += 1
                else:
                    print(f"  ❌ Erro ao atualizar: {update_result.get('error', 'Erro desconhecido')}")
                    erros += 1
                
                print()
        
    except FileNotFoundError:
        print(f"Erro: Arquivo {csv_file} não encontrado")
        return
    except Exception as e:
        print(f"Erro ao processar arquivo CSV: {str(e)}")
        return
    
    # Resumo final
    print("\n" + "="*50)
    print("RESUMO DA EXECUÇÃO")
    print("="*50)
    print(f"Total de registros:      {total}")
    print(f"Passageiros encontrados: {encontrados}")
    print(f"Mandados atualizados:    {atualizados}")
    print(f"Passageiros não encontrados: {nao_encontrados}")
    print(f"Erros:                   {erros}")
    print("="*50)


if __name__ == '__main__':
    main()

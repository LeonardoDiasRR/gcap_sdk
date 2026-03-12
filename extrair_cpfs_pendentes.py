#!/usr/bin/env python3
"""
Script para extrair CPFs do arquivo CSV de passageiros pendentes e salvar em .txt
"""

import csv


def main():
    csv_file = 'arquivos/passageiros_pendentes_20260311_225553.csv'
    txt_file = 'arquivos/cpfs_pendentes.txt'
    
    try:
        cpfs = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            
            for row in csv_reader:
                cpf = row['cpf'].strip()
                if cpf:  # Apenas adicionar CPFs não vazios
                    cpfs.append(cpf)
        
        if not cpfs:
            print("Nenhum CPF encontrado no arquivo CSV")
            return
        
        # Salvar em arquivo .txt
        with open(txt_file, 'w', encoding='utf-8') as f:
            for cpf in cpfs:
                f.write(cpf + '\n')
        
        print(f"✓ Arquivo salvo com sucesso: {txt_file}")
        print(f"✓ Total de CPFs extraídos: {len(cpfs)}")
        
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado - {e}")
    except Exception as e:
        print(f"Erro ao processar arquivo: {str(e)}")


if __name__ == '__main__':
    main()

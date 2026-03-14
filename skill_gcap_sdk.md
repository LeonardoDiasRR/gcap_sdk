<<<<<<< HEAD
=======
---
name: gcap-sdk
description: "Operações GCAP SDK (mandados, prisões, certidões, uploads e consultas) a partir de scripts Python localizados em /opt/projetos/gcap_sdk/ (Linux) ou em C:\\Users\\leona\\Documents\\projetos\\gcap_sdk\\ (Windows). Use quando precisar invocar os scripts listados para automações confirmadas da Operação Mitra."
---

>>>>>>> 318e99f69cd7e08b6d95ad6e1c5edefd3cf33c51
# Skill GCAP SDK

## Descrição

Skill para operar com o GCAP SDK, permitindo agentes executarem scripts para:
- Consultar e atualizar mandados de prisão
- Extrair dados de PDFs de mandados e certidões
- Listar presos e passageiros
<<<<<<< HEAD
=======
- Baixar arquivos de mandados e certidões já vinculados no GCAP
>>>>>>> 318e99f69cd7e08b6d95ad6e1c5edefd3cf33c51
- Fazer upload de arquivos (mandados, certidões e listas de passageiros)

## Localização dos Scripts

Os scripts estão localizados em:
<<<<<<< HEAD
- **Windows**: `C:\Users\leona\Documents\projetos\gcap_sdk\`
=======
- **Windows**: `C:\Users\leona\Documents\projetos\gcap_sdk/`
>>>>>>> 318e99f69cd7e08b6d95ad6e1c5edefd3cf33c51
- **Linux**: `/opt/projetos/gcap_sdk/`

## Pré-requisitos

- Ambiente Python com venv ativado: `venv\Scripts\Activate.ps1` (Windows) ou `source venv/bin/activate` (Linux)
- Arquivo `.env` configurado com credenciais GCAP
<<<<<<< HEAD
- Dependências instaladas: `pip install -r requirements.txt`
=======
- Credenciais de autenticação REST: `GCAP_BACKEND_API_KEY` no .env
- Dependências instaladas: `pip install -r requirements.txt`
- Preferir executar com o Python do venv do projeto
>>>>>>> 318e99f69cd7e08b6d95ad6e1c5edefd3cf33c51

## Executando os Scripts

### Windows
Use o caminho completo do Python do ambiente virtual:
```bash
C:\Users\leona\Documents\projetos\gcap_sdk\venv\Scripts\python.exe C:\Users\leona\Documents\projetos\gcap_sdk\listar_passageiros.py --data 2026-03-09
<<<<<<< HEAD
```

**Exemplos de comando completo no Windows**:
```bash
=======

Exemplos de comando completo no Windows:

>>>>>>> 318e99f69cd7e08b6d95ad6e1c5edefd3cf33c51
# Listar presos
C:\Users\leona\Documents\projetos\gcap_sdk\venv\Scripts\python.exe C:\Users\leona\Documents\projetos\gcap_sdk\listar_presos.py 2026-03-09

# Consultar mandado
C:\Users\leona\Documents\projetos\gcap_sdk\venv\Scripts\python.exe C:\Users\leona\Documents\projetos\gcap_sdk\consulta_mandado.py 1234567890123456789012345678

# Extrair dados de PDF
C:\Users\leona\Documents\projetos\gcap_sdk\venv\Scripts\python.exe C:\Users\leona\Documents\projetos\gcap_sdk\extrair_dados_mandado.py "C:\Users\leona\Documents\projetos\gcap_sdk\arquivos\mandado.pdf"

# Upload de arquivo
C:\Users\leona\Documents\projetos\gcap_sdk\venv\Scripts\python.exe C:\Users\leona\Documents\projetos\gcap_sdk\upload_mandados.py "C:\Users\leona\Documents\projetos\gcap_sdk\arquivos\mandado.pdf"
<<<<<<< HEAD
```

### Linux
Use o caminho completo do Python do ambiente virtual para garantir que esteja usando as dependências instaladas no projeto:
```bash
/opt/projetos/gcap_sdk/venv/bin/python /opt/projetos/gcap_sdk/listar_passageiros.py --data 2026-03-09
```

**Exemplos de comando completo no Linux**:
```bash
=======

# Baixar PDF de mandado vinculado ao número
C:\Users\leona\Documents\projetos\gcap_sdk\venv\Scripts\python.exe C:\Users\leona\Documents\projetos\gcap_sdk\baixar_arquivo_mandado_s3.py 0841162-22.2025.8.23.0010.01.0001-17

# Baixar PDF de certidão vinculado ao número
C:\Users\leona\Documents\projetos\gcap_sdk\venv\Scripts\python.exe C:\Users\leona\Documents\projetos\gcap_sdk\baixar_arquivo_mandado_s3.py 0841162-22.2025.8.23.0010.01.0001-17 --certidao

Linux

Use o caminho completo do Python do ambiente virtual para garantir que esteja usando as dependências instaladas no projeto:

/opt/projetos/gcap_sdk/venv/bin/python /opt/projetos/gcap_sdk/listar_passageiros.py --data 2026-03-09

Exemplos de comando completo no Linux:

>>>>>>> 318e99f69cd7e08b6d95ad6e1c5edefd3cf33c51
# Listar presos
/opt/projetos/gcap_sdk/venv/bin/python /opt/projetos/gcap_sdk/listar_presos.py 2026-03-09

# Consultar mandado
/opt/projetos/gcap_sdk/venv/bin/python /opt/projetos/gcap_sdk/consulta_mandado.py 1234567890123456789012345678

# Extrair dados de PDF
/opt/projetos/gcap_sdk/venv/bin/python /opt/projetos/gcap_sdk/extrair_dados_mandado.py "/opt/projetos/gcap_sdk/arquivos/mandado.pdf"

# Upload de arquivo
/opt/projetos/gcap_sdk/venv/bin/python /opt/projetos/gcap_sdk/upload_mandados.py "/opt/projetos/gcap_sdk/arquivos/mandado.pdf"
<<<<<<< HEAD
```

## Scripts Disponíveis

### 1. listar_presos.py
**Descrição**: Lista presos presos em uma data específica ou durante um mês inteiro.

**Uso**:
```bash
python listar_presos.py <data_prisao>
```

**Argumentos**:
- `<data_prisao>`: Data no formato YYYY-MM-DD (data exata) ou YYYY-MM (mês inteiro)

**Exemplos**:
```bash
=======

# Baixar PDF de mandado vinculado ao número
/opt/projetos/gcap_sdk/venv/bin/python /opt/projetos/gcap_sdk/baixar_arquivo_mandado_s3.py 0841162-22.2025.8.23.0010.01.0001-17

# Baixar PDF de certidão vinculado ao número
/opt/projetos/gcap_sdk/venv/bin/python /opt/projetos/gcap_sdk/baixar_arquivo_mandado_s3.py 0841162-22.2025.8.23.0010.01.0001-17 --certidao

Scripts Disponíveis

1. listar_presos.py

Descrição: Lista presos presos em uma data específica ou durante um mês inteiro.

Uso:

python listar_presos.py <data_prisao>

Argumentos:

• <data_prisao>: Data no formato YYYY-MM-DD (data exata) ou YYYY-MM (mês inteiro)

Exemplos:

>>>>>>> 318e99f69cd7e08b6d95ad6e1c5edefd3cf33c51
# Data exata
python listar_presos.py 2026-03-09

# Mês inteiro
python listar_presos.py 2026-01
<<<<<<< HEAD
```

**Saída**: JSON com lista de mandados presos na data/período especificado

**Retorno esperado**:
```json
{
  "success": true,
  "data": {
    "data": [
      {
        "id": "uuid",
        "numero_mandado": "1234567890123456789012345678",
        "data_prisao": "2026-03-09",
        ...
      }
    ],
    "count": 5
  }
}
```

---

### 2. consulta_mandado.py
**Descrição**: Consulta um mandado específico pelo número.

**Uso**:
```bash
python consulta_mandado.py <numero_mandado>
```

**Argumentos**:
- `<numero_mandado>`: Número do mandado (28 dígitos, com ou sem formatação)

**Exemplos**:
```bash
=======

Saída: JSON com lista de mandados presos na data/período especificado

Retorno esperado:

{
"success": true,
"data": {
"data": [
{
"id": "uuid",
"numero_mandado": "1234567890123456789012345678",
"data_prisao": "2026-03-09",
...
}
],
"count": 5
}
}

───

2. consulta_mandado.py

Descrição: Consulta um mandado específico pelo número.

Uso:

python consulta_mandado.py <numero_mandado>

Argumentos:

• <numero_mandado>: Número do mandado (28 dígitos, com ou sem formatação)

Exemplos:

>>>>>>> 318e99f69cd7e08b6d95ad6e1c5edefd3cf33c51
# Com formatação
python consulta_mandado.py 1234567.89.0123.4.567.899-01

# Sem formatação
python consulta_mandado.py 12345678901234567890123456789
<<<<<<< HEAD
```

**Saída**: JSON com detalhes do mandado consultado

**Retorno esperado**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_mandado": "1234567890123456789012345678",
    "numero_processo": "0001234-56.2026.1.02.0001",
    "nome_preso": "JOÃO DA SILVA",
    "cpf": "01666016403",
    "data_prisao": "2026-03-09",
    ...
  }
}
```

**Validações**:
- Número deve ter exatamente 28 dígitos
- Aceita números com hífens, pontos ou sem formatação
- Remove automaticamente hífens e pontos para normalização

---

### 3. atualiza_data_prisao.py
**Descrição**: Atualiza a data de prisão de um mandado específico.

**Uso**:
```bash
python atualiza_data_prisao.py <numero_mandado> <data_prisao>
```

**Argumentos**:
- `<numero_mandado>`: Número do mandado (28 dígitos)
- `<data_prisao>`: Data de prisão no formato YYYY-MM-DD

**Exemplos**:
```bash
python atualiza_data_prisao.py 1234567890123456789012345678 2026-03-09
```

**Saída**: JSON com resultado da atualização

**Retorno esperado**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_mandado": "1234567890123456789012345678",
    "data_prisao": "2026-03-09"
  }
}
```

---

### 4. extrair_dados_mandado.py
**Descrição**: Extrai dados de um PDF de Mandado de Prisão.

**Uso**:
```bash
python extrair_dados_mandado.py <caminho_pdf>
```

**Argumentos**:
- `<caminho_pdf>`: Caminho para o arquivo PDF do mandado

**Exemplos**:
```bash
python extrair_dados_mandado.py "arquivos/mandado_20260309.pdf"
python extrair_dados_mandado.py "C:\Users\leona\Downloads\mandado.pdf"
```

**Saída**: JSON com dados extraídos do PDF

**Retorno esperado**:
```json
{
  "arquivo": "arquivos/mandado.pdf",
  "erro": false,
  "numero_mandado": "1234567890123456789012345678",
  "numero_processo": "0001234-56.2026.1.02.0001",
  "nome_preso": "JOÃO DA SILVA",
  "cpf": "01666016403",
  "rg": "1234567",
  "rji": "123456",
  "data_nascimento": "1990-05-15",
  "data_validade": "2030-03-09",
  "especie_prisao": "Prisão preventiva",
  "tipificacao_penal": "Art. 121 do CP",
  "magistrado": "Juiz de Direito",
  "orgao_judicial": "Tribunal de Justiça",
  "data_mandado": "2026-03-09"
}
```

**Campos extraídos**:
- `numero_mandado`: Número único do mandado
- `numero_processo`: Número do processo judicial
- `nome_preso`: Nome completo do preso
- `cpf`: CPF do preso
- `rg`: RG do preso
- `rji`: Registro Judicial do preso
- `data_nascimento`: Data de nascimento
- `data_validade`: Data de validade do mandado
- `especie_prisao`: Tipo de prisão
- `tipificacao_penal`: Artigo penal aplicável
- `magistrado`: Nome do magistrado
- `orgao_judicial`: Órgão que emitiu o mandado
- `data_mandado`: Data de emissão do mandado

---

### 5. extrair_dados_certidao.py
**Descrição**: Extrai dados de um PDF de Certidão de Cumprimento de Mandado.

**Uso**:
```bash
python extrair_dados_certidao.py <caminho_pdf>
```

**Argumentos**:
- `<caminho_pdf>`: Caminho para o arquivo PDF da certidão

**Exemplos**:
```bash
python extrair_dados_certidao.py "arquivos/certidao_20260309.pdf"
```

**Saída**: JSON com dados extraídos do PDF

**Retorno esperado**:
```json
{
  "arquivo": "arquivos/certidao.pdf",
  "erro": false,
  "numero_mandado": "1234567890123456789012345678",
  "data_prisao": "2026-03-09",
  "unidade_cumpridora": "Polícia Federal - Superintendência de SP"
}
```

**Campos extraídos**:
- `numero_mandado`: Número do mandado cumprido
- `data_prisao`: Data em que a prisão foi realizada
- `unidade_cumpridora`: Unidade responsável pelo cumprimento

---

### 6. listar_passageiros.py
**Descrição**: Lista passageiros com suporte a filtros por CPF e/ou data de registro.

**Uso**:
```bash
python listar_passageiros.py --cpf <cpf> | --data <data>
```

**Argumentos**:
- `--cpf <cpf>`: CPF do passageiro (com ou sem formatação)
- `--data <data>`: Data de registro (YYYY-MM-DD para data exata ou YYYY-MM para mês)

**Exemplos**:
```bash
=======

Saída: JSON com detalhes do mandado consultado

Retorno esperado:

{
"success": true,
"data": {
"id": "uuid",
"numero_mandado": "1234567890123456789012345678",
"numero_processo": "0001234-56.2026.1.02.0001",
"nome_preso": "JOÃO DA SILVA",
"cpf": "01666016403",
"data_prisao": "2026-03-09",
...
}
}

Validações:

• Número deve ter exatamente 28 dígitos
• Aceita números com hífens, pontos ou sem formatação
• Remove automaticamente hífens e pontos para normalização

───

3. atualiza_data_prisao.py

Descrição: Atualiza a data de prisão de um mandado específico.

Uso:

python atualiza_data_prisao.py <numero_mandado> <data_prisao>

Argumentos:

• <numero_mandado>: Número do mandado (28 dígitos)
• <data_prisao>: Data de prisão no formato YYYY-MM-DD

Exemplos:

python atualiza_data_prisao.py 1234567890123456789012345678 2026-03-09

Saída: JSON com resultado da atualização

Retorno esperado:

{
"success": true,
"data": {
"id": "uuid",
"numero_mandado": "1234567890123456789012345678",
"data_prisao": "2026-03-09"
}
}

───

4. extrair_dados_mandado.py

Descrição: Extrai dados de um PDF de Mandado de Prisão.

Uso:

python extrair_dados_mandado.py <caminho_pdf>

Argumentos:

• <caminho_pdf>: Caminho para o arquivo PDF do mandado

Exemplos:

python extrair_dados_mandado.py "arquivos/mandado_20260309.pdf"
python extrair_dados_mandado.py "C:\Users\leona\Downloads\mandado.pdf"

Saída: JSON com dados extraídos do PDF

Retorno esperado:

{
"arquivo": "arquivos/mandado.pdf",
"erro": false,
"numero_mandado": "1234567890123456789012345678",
"numero_processo": "0001234-56.2026.1.02.0001",
"nome_preso": "JOÃO DA SILVA",
"cpf": "01666016403",
"rg": "1234567",
"rji": "123456",
"data_nascimento": "1990-05-15",
"data_validade": "2030-03-09",
"especie_prisao": "Prisão preventiva",
"tipificacao_penal": "Art. 121 do CP",
"magistrado": "Juiz de Direito",
"orgao_judicial": "Tribunal de Justiça",
"data_mandado": "2026-03-09"
}

Campos extraídos:

• numero_mandado: Número único do mandado
• numero_processo: Número do processo judicial
• nome_preso: Nome completo do preso
• cpf: CPF do preso
• rg: RG do preso
• rji: Registro Judicial do preso
• data_nascimento: Data de nascimento
• data_validade: Data de validade do mandado
• especie_prisao: Tipo de prisão
• tipificacao_penal: Artigo penal aplicável
• magistrado: Nome do magistrado
• orgao_judicial: Órgão que emitiu o mandado
• data_mandado: Data de emissão do mandado

───

5. extrair_dados_certidao.py

Descrição: Extrai dados de um PDF de Certidão de Cumprimento de Mandado.

Uso:

python extrair_dados_certidao.py <caminho_pdf>

Argumentos:

• <caminho_pdf>: Caminho para o arquivo PDF da certidão

Exemplos:

python extrair_dados_certidao.py "arquivos/certidao_20260309.pdf"

Saída: JSON com dados extraídos do PDF

Retorno esperado:

{
"arquivo": "arquivos/certidao.pdf",
"erro": false,
"numero_mandado": "1234567890123456789012345678",
"data_prisao": "2026-03-09",
"unidade_cumpridora": "Polícia Federal - Superintendência de SP"
}

Campos extraídos:

• numero_mandado: Número do mandado cumprido
• data_prisao: Data em que a prisão foi realizada
• unidade_cumpridora: Unidade responsável pelo cumprimento

───

6. listar_passageiros.py

Descrição: Lista passageiros com suporte a filtros por CPF e/ou data de registro.

Uso:

python listar_passageiros.py --cpf <cpf> | --data <data>

Argumentos:

• --cpf <cpf>: CPF do passageiro (com ou sem formatação)
• --data <data>: Data de registro (YYYY-MM-DD para data exata ou YYYY-MM para mês)

Exemplos:

>>>>>>> 318e99f69cd7e08b6d95ad6e1c5edefd3cf33c51
# Buscar por CPF
python listar_passageiros.py --cpf 01666016403
python listar_passageiros.py --cpf "016.660.164-03"

# Buscar por data
python listar_passageiros.py --data 2026-03-09
python listar_passageiros.py --data 2026-03

# Combinar filtros
python listar_passageiros.py --cpf 01666016403 --data 2026-03
<<<<<<< HEAD
```

**Saída**: JSON com lista de passageiros

**Retorno esperado**:
```json
{
  "success": true,
  "data": {
    "data": [
      {
        "id": "uuid",
        "cpf": "01666016403",
        "nome": "JOÃO DA SILVA",
        "data_registro": "2026-03-09",
        ...
      }
    ],
    "count": 5,
    "page": 0,
    "page_size": 10
  }
}

---

### 7. upload_mandados.py
**Descrição**: Faz upload de PDFs de mandados para o servidor GCAP.

**Uso**:
bash

```
python upload_mandados.py <arquivo_pdf> [<arquivo_pdf2> ...]
```

**Argumentos**:
- `<arquivo_pdf>`: Caminho para arquivo(s) PDF de mandado

**Exemplos**:
```bash
=======

Saída: JSON com lista de passageiros

Retorno esperado:

{
"success": true,
"data": {
"data": [
{
"id": "uuid",
"cpf": "01666016403",
"nome": "JOÃO DA SILVA",
"data_registro": "2026-03-09",
...
}
],
"count": 5,
"page": 0,
"page_size": 10
}
}

───

7. upload_mandados.py

Descrição: Faz upload de PDFs de mandados para o servidor GCAP.

Uso:

python upload_mandados.py <arquivo_pdf> [<arquivo_pdf2> ...]

Argumentos:

• <arquivo_pdf>: Caminho para arquivo(s) PDF de mandado

Exemplos:

>>>>>>> 318e99f69cd7e08b6d95ad6e1c5edefd3cf33c51
# Upload de um arquivo
python upload_mandados.py "arquivos/mandado.pdf"

# Upload de múltiplos arquivos
python upload_mandados.py "arquivos/mandado1.pdf" "arquivos/mandado2.pdf" "arquivos/mandado3.pdf"

# Upload com caminho absoluto
python upload_mandados.py "C:\Users\leona\Downloads\mandados\mandado.pdf"
<<<<<<< HEAD
```

**Limitações**:
- Máximo 50 arquivos por upload
- Tamanho máximo: 5MB por arquivo
- Apenas arquivos PDF (.pdf)

**Saída**: JSON com resultado do upload

**Retorno esperado**:
```json
{
  "success": true,
  "uploaded_files": 1,
  "results": [
    {
      "file": "mandado.pdf",
      "success": true,
      "message": "Arquivo enviado com sucesso"
    }
  ]
}
```

**Validações automáticas**:
- Verifica existência do arquivo
- Valida extensão (.pdf)
- Verifica tamanho (máx 5MB)
- Detecta arquivo vazio
- Remove arquivo Response antes de retornar JSON

---

### 8. upload_certidao.py
**Descrição**: Faz upload de PDFs de Certidão de Cumprimento para o servidor GCAP.

**Uso**:
```bash
python upload_certidao.py <arquivo_pdf> [<arquivo_pdf2> ...]
```

**Argumentos**:
- `<arquivo_pdf>`: Caminho para arquivo(s) PDF de certidão

**Exemplos**:
```bash
=======

Limitações:

• Máximo 50 arquivos por upload
• Tamanho máximo: 5MB por arquivo
• Apenas arquivos PDF (.pdf)

Saída: JSON com resultado do upload

Retorno esperado:

{
"success": true,
"uploaded_files": 1,
"results": [
{
"file": "mandado.pdf",
"success": true,
"message": "Arquivo enviado com sucesso"
}
]
}

Validações automáticas:

• Verifica existência do arquivo
• Valida extensão (.pdf)
• Verifica tamanho (máx 5MB)
• Detecta arquivo vazio
• Remove arquivo Response antes de retornar JSON

───

8. upload_certidao.py

Descrição: Faz upload de PDFs de Certidão de Cumprimento para o servidor GCAP.

Uso:

python upload_certidao.py <arquivo_pdf> [<arquivo_pdf2> ...]

Argumentos:

• <arquivo_pdf>: Caminho para arquivo(s) PDF de certidão

Exemplos:

>>>>>>> 318e99f69cd7e08b6d95ad6e1c5edefd3cf33c51
# Upload de um arquivo
python upload_certidao.py "arquivos/certidao.pdf"

# Upload de múltiplos arquivos
python upload_certidao.py "arquivos/certidao1.pdf" "arquivos/certidao2.pdf"
<<<<<<< HEAD
```

**Limitações**:
- Máximo 50 arquivos por upload
- Tamanho máximo: 5MB por arquivo
- Apenas arquivos PDF (.pdf)

**Saída**: JSON com resultado do upload

**Retorno esperado**:
```json
{
  "success": true,
  "uploaded_files": 1,
  "results": [
    {
      "file": "certidao.pdf",
      "success": true,
      "message": "Arquivo enviado com sucesso"
    }
  ]
}
```

---

### 9. upload_lista_passageiros.py
**Descrição**: Faz upload de listas de passageiros em formato Excel para o servidor GCAP.

**Uso**:
```bash
python upload_lista_passageiros.py <arquivo_excel> [<arquivo_excel2> ...]
```

**Argumentos**:
- `<arquivo_excel>`: Caminho para arquivo(s) Excel com lista de passageiros

**Exemplos**:
```bash
=======

Limitações:

• Máximo 50 arquivos por upload
• Tamanho máximo: 5MB por arquivo
• Apenas arquivos PDF (.pdf)

Saída: JSON com resultado do upload

Retorno esperado:

{
"success": true,
"uploaded_files": 1,
"results": [
{
"file": "certidao.pdf",
"success": true,
"message": "Arquivo enviado com sucesso"
}
]
}

───

9. baixar_arquivo_mandado_s3.py

Descrição: Baixa do Supabase Storage o arquivo de mandado ou certidão vinculado a um número de mandado já existente no GCAP. Usa autenticação REST (Bearer token).

Uso:

python baixar_arquivo_mandado_s3.py <numero_mandado> [--certidao]

Argumentos:

• <numero_mandado>: Número do mandado com 28 dígitos, com ou sem formatação
• --certidao (opcional): Baixa a certidão em vez do mandado

Exemplos:

# Baixar mandado (com formatação)
python baixar_arquivo_mandado_s3.py 0841162-22.2025.8.23.0010.01.0001-17

# Baixar mandado (somente números)
python baixar_arquivo_mandado_s3.py 0841162222025823001001000117

# Baixar certidão
python baixar_arquivo_mandado_s3.py 0841162-22.2025.8.23.0010.01.0001-17 --certidao

Comportamento:

• Faz login no GCAP para obter access_token
• Consulta o mandado via listar_mandados(page=0, page_size=1, numero_mandado=...)
• Lê o campo arquivo_mandado ou arquivo_certidao conforme parâmetro
• Baixa o arquivo via requisição REST autenticada com Bearer token
• Renomeia o arquivo para padrão consistente:
  - Mandados: mandado_<numero_mandado>.pdf
  - Certidões: certidao_<numero_mandado>.pdf
• Salva o arquivo em arquivos/ no diretório do projeto

Saída: JSON com caminho local, tamanho do arquivo e URL usada no download

Retorno esperado para mandado:

{
"success": true,
"message": "Arquivo baixado com sucesso",
"mandado_numero": "0841162222025823001001000117",
"arquivo_local": "C:\\Users\\leona\\Documents\\projetos\\gcap_sdk\\arquivos\\mandado_0841162222025823001001000117.pdf",
"arquivo_tamanho_bytes": 231342,
"arquivo_url": "https://xkecjoczmynhnyjwbxry.supabase.co/storage/v1/object/gcap/mandados/2026/03/12/48cabd27-mp_.pdf"
}

Retorno esperado para certidão:

{
"success": true,
"message": "Arquivo baixado com sucesso",
"mandado_numero": "0841162222025823001001000117",
"arquivo_local": "C:\\Users\\leona\\Documents\\projetos\\gcap_sdk\\arquivos\\certidao_0841162222025823001001000117.pdf",
"arquivo_tamanho_bytes": 98765,
"arquivo_url": "https://xkecjoczmynhnyjwbxry.supabase.co/storage/v1/object/gcap/certidoes/2026/03/12/cert_123.pdf"
}

Validações e falhas comuns:

• Rejeita números com tamanho diferente de 28 dígitos
• Retorna erro se o mandado não existir
• Retorna erro se arquivo_mandado ou arquivo_certidao estiver vazio
• Cria automaticamente o diretório arquivos/ se ele não existir
• Requer GCAP_BACKEND_API_KEY configurada no .env para autenticação

Autenticação:

• Usa access_token obtido via gcap.login()
• Inclui headers de autenticação: Apikey e Authorization: Bearer {access_token}
• Token é obtido automaticamente durante execução

───

10. upload_lista_passageiros.py

Descrição: Faz upload de listas de passageiros em formato Excel para o servidor GCAP.

Uso:

python upload_lista_passageiros.py <arquivo_excel> [<arquivo_excel2> ...]

Argumentos:

• <arquivo_excel>: Caminho para arquivo(s) Excel com lista de passageiros

Exemplos:

>>>>>>> 318e99f69cd7e08b6d95ad6e1c5edefd3cf33c51
# Upload de um arquivo
python upload_lista_passageiros.py "arquivos/passageiros.xlsx"

# Upload de múltiplos arquivos
python upload_lista_passageiros.py "arquivos/passageiros1.xlsx" "arquivos/passageiros2.xls"
<<<<<<< HEAD
```

**Formatos aceitos**:
- `.xls` (Excel 97-2003)
- `.xlsx` (Excel 2007+)
- `.xlsm` (Excel com macros)
- `.xltm` (Excel template)
- `.xlt` (Excel template)

**Limitações**:
- Máximo 50 arquivos por upload
- Tamanho máximo: 5MB por arquivo

**Saída**: JSON com resultado do upload

**Retorno esperado**:
```json
{
  "success": true,
  "uploaded_files": 1,
  "results": [
    {
      "file": "passageiros.xlsx",
      "success": true,
      "message": "Arquivo enviado com sucesso"
    }
  ]
}
```

---

## Fluxos Comuns

### Fluxo 1: Processar e Subir Mandados
1. Extrair dados do PDF: `python extrair_dados_mandado.py "mandado.pdf"`
2. Fazer upload do arquivo: `python upload_mandados.py "mandado.pdf"`
3. Atualizar data de prisão se necessário: `python atualiza_data_prisao.py <numero> <data>`
4. Consultar mandado para validar: `python consulta_mandado.py <numero>`

### Fluxo 2: Processar Certidão e Atualizar
1. Extrair dados da certidão: `python extrair_dados_certidao.py "certidao.pdf"`
2. Fazer upload da certidão: `python upload_certidao.py "certidao.pdf"`
3. Atualizar mandado com data de prisão: `python atualiza_data_prisao.py <numero> <data_da_certidao>`

### Fluxo 3: Listar e Filtrar Presos
1. Listar presos de uma data: `python listar_presos.py 2026-03-09`
2. Para cada preso, consultar mandado: `python consulta_mandado.py <numero>`
3. Atualizar informações conforme necessário

### Fluxo 4: Upload de Lista de Passageiros
1. Preparar arquivo Excel com dados de passageiros
2. Fazer upload: `python upload_lista_passageiros.py "lista.xlsx"`
3. Validar com: `python listar_passageiros.py --cpf <cpf>` ou `python listar_passageiros.py --data <data>`

---

## Tratamento de Erros

### Erros Comuns

**CPF Inválido**:
- Certificar-se que possui 11 dígitos
- Remover automaticamente pontos e hífens se houver pontuação

**Número de Mandado Inválido**:
- Deve ter exatamente 28 dígitos
- Script normaliza automaticamente removendo hífens e pontos

**Arquivo PDF Inválido**:
- Verificar se o arquivo existe no caminho especificado
- Confirmar que é arquivo PDF válido
- Tamanho máximo: 5MB

**Arquivo Excel Inválido**:
- Deve ter extensão .xls, .xlsx, .xlsm, .xlt ou .xltm
- Tamanho máximo: 5MB

**Erro de Login**:
- Verificar credenciais no arquivo `.env`
- Confirmar que GCAP_BACKEND_URL_BASE está correto
- Verificar acesso à internet

---

## Notas para Agentes

- Todos os scripts retornam JSON na saída padrão
- Use `json.loads()` para parsear a saída em Python
- Scripts fazem login e logout automaticamente
- Erros de autorização geralmente indicam credenciais inválidas no `.env`
- Para uploads em lote, é mais eficiente passar múltiplos arquivos em um comando do que fazer múltiplos uploads
- Extrações de PDF usam pdfplumber e podem falhar em PDFs altamente complexos ou mal formatados
=======

Formatos aceitos:

• .xls (Excel 97-2003)
• .xlsx (Excel 2007+)
• .xlsm (Excel com macros)
• .xltm (Excel template)
• .xlt (Excel template)

Limitações:

• Máximo 50 arquivos por upload
• Tamanho máximo: 5MB por arquivo

Saída: JSON com resultado do upload

Retorno esperado:

{
"success": true,
"uploaded_files": 1,
"results": [
{
"file": "passageiros.xlsx",
"success": true,
"message": "Arquivo enviado com sucesso"
}
]
}

───

Fluxos Comuns

Fluxo 1: Processar e Subir Mandados

1. Extrair dados do PDF: python extrair_dados_mandado.py "mandado.pdf"
2. Fazer upload do arquivo: python upload_mandados.py "mandado.pdf"
3. Atualizar data de prisão se necessário: python atualiza_data_prisao.py <numero> <data>
4. Consultar mandado para validar: python consulta_mandado.py <numero>

Fluxo 2: Processar Certidão e Atualizar

1. Extrair dados da certidão: python extrair_dados_certidao.py "certidao.pdf"
2. Fazer upload da certidão: python upload_certidao.py "certidao.pdf"
3. Atualizar mandado com data de prisão: python atualiza_data_prisao.py <numero> <data_da_certidao>

Fluxo 3: Baixar arquivo já vinculado no GCAP

1. Validar o número: python consulta_mandado.py <numero>
2. Baixar o PDF do mandado: python baixar_arquivo_mandado_s3.py <numero>
3. Baixar o PDF da certidão: python baixar_arquivo_mandado_s3.py <numero> --certidao
4. Processar localmente com extrair_dados_mandado.py ou extrair_dados_certidao.py se necessário

Fluxo 4: Listar e Filtrar Presos

1. Listar presos de uma data: python listar_presos.py 2026-03-09
2. Para cada preso, consultar mandado: python consulta_mandado.py <numero>
3. Atualizar informações conforme necessário

Fluxo 5: Upload de Lista de Passageiros

1. Preparar arquivo Excel com dados de passageiros
2. Fazer upload: python upload_lista_passageiros.py "lista.xlsx"
3. Validar com: python listar_passageiros.py --cpf <cpf> ou python listar_passageiros.py --data <data>

───

Tratamento de Erros

Erros Comuns

CPF Inválido:

• Certificar-se que possui 11 dígitos
• Remover automaticamente pontos e hífens se houver pontuação

Número de Mandado Inválido:

• Deve ter exatamente 28 dígitos
• Script normaliza automaticamente removendo hífens e pontos

Arquivo PDF Inválido:

• Verificar se o arquivo existe no caminho especificado
• Confirmar que é arquivo PDF válido
• Tamanho máximo: 5MB

Arquivo Excel Inválido:

• Deve ter extensão .xls, .xlsx, .xlsm, .xlt ou .xltm
• Tamanho máximo: 5MB

Erro de Login:

• Verificar credenciais no arquivo .env
• Confirmar que GCAP_BACKEND_URL_BASE está correto
• Verificar acesso à internet

───

Notas para Agentes

• Todos os scripts retornam JSON na saída padrão
• Use json.loads() para parsear a saída em Python
• Scripts fazem login e logout automaticamente
• Erros de autorização geralmente indicam credenciais inválidas no .env
• Scripts de download salvam os arquivos em arquivos/ com prefixo mandado_ ou certidao_ seguido do número do mandado
• Autenticação de download usa Bearer token via GCAP_BACKEND_API_KEY
• Para downloads em lote, pode ser mais eficiente usar scripts de listagem combinados com loops
• Extrações de PDF usam pdfplumber e podem falhar em PDFs altamente complexos ou mal formatados
>>>>>>> 318e99f69cd7e08b6d95ad6e1c5edefd3cf33c51

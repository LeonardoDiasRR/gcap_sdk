# GCAP SDK

SDK para acesso ao backend do projeto GCAP, permitindo integração com todos os endpoints da API.

## Estrutura do Projeto

- `gcap_sdk.py`: Módulo principal com a classe `Gcap`
- `.env`: Arquivo de variáveis de ambiente
- `requirements.txt`: Dependências necessárias
- `.gitignore`: Ignorar arquivos desnecessários

## Instalação

1. Ative o ambiente virtual:
   ```bash
   source venv/bin/activate
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

```python
from gcap_sdk import Gcap

# Inicialize o cliente
gcap = Gcap()

# Faça login
login_result = gcap.login()
if login_result['success']:
    print("Login realizado com sucesso!")
    
    # Exemplo: Listar mandados
    mandados = gcap.listar_mandados(page=0, page_size=10)
    if mandados['success']:
        print("Mandados encontrados:", len(mandados['data']['data']))
    
    # Exemplo: Atualizar um mandado
    update_result = gcap.atualizar_mandado(
        mandado_id="uuid-do-mandado",
        numero_mandado="1234567890",
        data_mandado="2026-03-09"
    )
    if update_result['success']:
        print("Mandado atualizado com sucesso!")
        
else:
    print("Falha no login:", login_result['error'])

# Logout quando terminar
gcap.logout()
```

## Métodos Disponíveis

- `login()`: Realiza o login e obtém access token
- `logout()`: Inativa o access token
- `listar_mandados(page=0, page_size=10, **filters)`: Lista mandados com filtros
- `atualizar_mandado(mandado_id, **data)`: Atualiza um mandado
- `listar_passageiros(page=0, page_size=10, **filters)`: Lista passageiros
- `listar_procurados(page=0, page_size=10, **filters)`: Lista procurados
- `listar_contatos(page=0, page_size=10, **filters)`: Lista contatos
- `listar_servicos(page=0, page_size=10, **filters)`: Lista serviços
- `listar_instituicoes(page=0, page_size=10, **filters)`: Lista instituições
- `upload_passageiros(file_path)`: Upload em lote de passageiros
- `obter_unidades()`: Obter unidades do usuário (opcional)

## Variáveis de Ambiente

O arquivo `.env` deve conter:
```
GCAP_BACKEND_URL_BASE=https://xkecjoczmynhnyjwbxry.supabase.co
GCAP_BACKEND_UNIDADE_ID=c6639716-14e9-4856-a43d-24d282b8bab2
GCAP_BACKEND_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhrZWNqb2N6bXluaG55andieHJ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE4NzU1MTEsImV4cCI6MjA4NzQ1MTUxMX0.MKcpTgvWimX55LVXHuIESKURP-cR0YkVhWYe9-FKceA
GCAP_BACKEND_PASSWORD=Sauron_PF
GCAP_BACKEND_USER=mitra.srrr@pf.gov.br
```

## Requisitos

- Python 3.6+
- requests
- python-dotenv
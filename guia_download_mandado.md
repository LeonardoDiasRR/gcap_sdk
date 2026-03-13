# Guia de Download de Mandado e Certidão de Cumprimento - BNMP3

**Objetivo**: Baixar um mandado de prisão e sua certidão de cumprimento da plataforma BNMP3 (Banco Nacional de Mandados de Prisão).

**Diretório de Destino**: `Z:\Cris\mandados`

---

## Fase 1: Autenticação

### Passo 1.1: Acessar a página de login
- Abra o navegador e acesse a URL: `https://sso.cloud.pje.jus.br/auth/realms/pje/protocol/openid-connect/auth?client_id=bnmp&redirect_uri=https://bnmp.pdpj.jus.br/v2/api/login&response_type=code&state=MclSaa`
- Aguarde o carregamento completo da página de login (máximo 4 segundos)

### Passo 1.2: Preencher credenciais de login
- Localize o campo de entrada com placeholder "000.000.000-00"
- Digite seu CPF ou CNPJ neste campo
- Localize o campo de entrada com placeholder "Digite sua senha"
- Digite sua senha neste campo

### Passo 1.3: Clicar no botão "Entrar"
- Localize e clique no botão "Entrar" (é do tipo submit)
- Aguarde o carregamento da página seguinte (máximo 5 segundos)
- O navegador será redirecionado automaticamente para a página inicial ou para a página de peças

---

## Fase 2: Preparação da Página de Pesquisa

### Passo 2.1: Navegar para a página de peças
- Acesse a URL: `https://bnmp.pdpj.jus.br/pecas`
- Aguarde o carregamento completo (máximo 10 segundos)

### Passo 2.2: Preparar a página de pesquisa
- Localize e clique no botão **[Limpar]** para limpar todos os filtros previamente aplicados
- Aguarde 3 segundos para que a página recarregue
- Localize o checkbox com label **"Pessoas Ativas"**
- Clique no checkbox para selecioná-lo
- Aguarde a atualização da página (máximo 2 segundos)

---

## Fase 3: Busca do Mandado

### Passo 3.1: Acessar o campo de busca por número da peça
- Localize o campo de entrada com atributo `name="numeroPeca"` ou com placeholder contendo "número"
- Este é o campo onde você digitará o número do mandado

### Passo 3.2: Inserir número do mandado
- No campo de entrada de "Número da Peça", digite o **número completo do mandado**
- Exemplo: `0001240-18.2000.8.11.0042.01.0004-09`
- O número pode estar com ou sem formatação (com ou sem hífens e pontos)

### Passo 3.3: Executar a busca
- Localize e clique no botão **"Buscar"** ou **"Pesquisar"** (classe CSS: `btn-buscar`)
- Aguarde os resultados da busca carregarem (máximo 5 segundos)

### Passo 3.4: Obter o RJI (Registro de Judicial do Integrado)
- Na página de resultados, localize a linha ou card correspondente ao mandado pesquisado
- Identifique o **Registro RJI** exibido na página
- Anote ou copie este número (será usado posteriormente para a certidão)

---

## Fase 4: Download do Mandado de Prisão

### Passo 4.1: Abrir detalhes do mandado
- Na página de resultados, clique no **número do mandado** ou no link correspondente
- Aguarde o carregamento dos detalhes (máximo 5 segundos)

### Passo 4.2: Localizar e clicar no botão de download
- Na página de detalhes, procure por um **botão de download** ou **ícone de download** (geralmente representado por uma seta apontando para baixo)
- Clique no botão de download do **Mandado de Prisão**
- O arquivo será salvo em seu diretório de downloads padrão (o navegador salvará como `.pdf`)

### Passo 4.3: Mover arquivo para o destino
- O arquivo será baixado com um nome como `mandado_XXXXXXXXXXXXXXXXXXXXXXXXXX.pdf`
- Localize o arquivo no seu diretório de downloads
- Mova o arquivo para `Z:\Cris\mandados\`

---

## Fase 5: Download da Certidão de Cumprimento

### Passo 5.1: Retornar à página de peças se necessário
- Se você saiu da página anterior, acesse novamente: `https://bnmp.pdpj.jus.br/pecas`
- Aguarde o carregamento (máximo 10 segundos)

### Passo 5.2: Buscar pelo RJI
- Localize o campo de entrada com atributo `name="rji"` ou com placeholder contendo "RJI"
- Digite o **número RJI** que você obteve no Passo 3.4
- Exemplo de RJI: `0000001234567890`

### Passo 5.3: Executar a busca por RJI
- Localize e clique no botão **"Buscar"** ou **"Pesquisar"**
- Aguarde os resultados carregarem (máximo 5 segundos)

### Passo 5.4: Abrir detalhes da certidão
- Na página de resultados, localize a linha ou card correspondente à **Certidão de Cumprimento**
- Clique no **número da certidão** ou no link correspondente
- Aguarde o carregamento dos detalhes (máximo 5 segundos)

### Passo 5.5: Baixar a certidão
- Na página de detalhes, procure pelo **botão de download** ou **ícone de download**
- Clique no botão de download da **Certidão de Cumprimento**
- O arquivo será salvo em seu diretório de downloads padrão (como `.pdf`)

### Passo 5.6: Mover arquivo para o destino
- O arquivo será baixado com um nome como `certidao_XXXXXXXXXXXXXXXXXXXXXXXXXX.pdf`
- Localize o arquivo no seu diretório de downloads
- Mova o arquivo para `Z:\Cris\mandados\`

---

## Observações Importantes

1. **Timeout**: Se a página demore mais do que especificado em cada passo, recarregue a página e tente novamente
2. **Autenticação**: A sessão pode expirar após inatividade. Se receber mensagem de "sessão expirada", retorne ao Passo 1.1
3. **Filtros Automáticos**: Alguns filtros podem ser aplicados automaticamente. Remova-os conforme instruído no Passo 2.2
4. **Nomenclatura de Arquivos**: Os arquivos devem ser renomeados para um padrão consistente:
   - Mandado: `mandado_[NUMERO_LIMPIDO].pdf`
   - Certidão: `certidao_[NUMERO_LIMPIDO].pdf`
   - Onde `[NUMERO_LIMPIDO]` é o número com apenas dígitos, primeiros 28 caracteres

5. **Diretório de Destino**: Certifique-se de que o diretório `Z:\Cris\mandados\` existe e tem permissões de escrita

---

## Fluxo Resumido

```
Autenticação (SSO) → Página de Peças → 
Busca por Número → Download Mandado → 
Mover para Z:\Cris\mandados → 
Busca por RJI → Download Certidão → 
Mover para Z:\Cris\mandados
```

---

## Tratamento de Erros Comuns

| Erro | Solução |
|------|---------|
| Campo CPF não encontrado | Verifique se a página carregou completamente. Aguarde 5 segundos e tente novamente. |
| Botão Entrar não respondeu | Clique em uma área vazia da página primeiro e depois clique no botão novamente. |
| Página de peças não carregou | Verifique sua conexão com a internet. Recarregue a página. |
| Mandado não encontrado na busca | Verifique se o número foi digitado corretamente (com ou sem formatação). |
| Botão de download não visível | Role para baixo na página de detalhes. O botão pode estar abaixo do conteúdo principal. |
| Arquivo não foi baixado | Verifique as configurações de download do navegador e as permissões do diretório de destino. |

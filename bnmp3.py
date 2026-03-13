"""
Módulo BNMP3 - Classe para obtenção automatizada de mandados de prisão
Encapsula a lógica de autenticação e download de mandados da plataforma BNMP
"""
import time
import re
import os
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# ─────────────────────────────────────────────────────────────
# Configuração
# ─────────────────────────────────────────────────────────────
LOGIN_URL = (
    "https://sso.cloud.pje.jus.br/auth/realms/pje/protocol/openid-connect/auth"
    "?client_id=bnmp"
    "&redirect_uri=https://bnmp.pdpj.jus.br/v2/api/login"
    "&response_type=code"
    "&state=MclSaa"
)
BNMP_PECAS_URL = "https://bnmp.pdpj.jus.br/pecas"
WAIT_TIMEOUT = 20  # segundos para esperas explícitas

# Seletores CSS Estáveis
SEL_NUMERO_PECA = "input[name='numeroPeca']"
SEL_RJI = "input[name='rji']"
SEL_BTN_BUSCAR = "button.btn-buscar"


# ─────────────────────────────────────────────────────────────
# Gerenciador de Filtros (Chips) - Remoção via JavaScript
# ─────────────────────────────────────────────────────────────
class ChipFilter:
    """Gerenciador de chips de filtro usando JavaScript"""
    
    def __init__(self, driver: webdriver.Chrome, wait_timeout: int = 10, logger: logging.Logger = None):
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_timeout)
        self.timeout = wait_timeout
        self.logger = logger
    
    def remover_chip(self, chip_text: str, esperar_remocao: bool = True) -> dict:
        """
        Remove um chip de filtro usando JavaScript
        
        Args:
            chip_text: Texto do chip a remover
            esperar_remocao: Se True, aguarda o chip desaparecer
        
        Returns:
            dict com status e mensagem
        """
        try:
            # Encontra o chip pelo texto
            xpath_chip = f"//mat-chip[contains(., '{chip_text}')]"
            chips = self.driver.find_elements(By.XPATH, xpath_chip)
            
            if not chips:
                if self.logger:
                    self.logger.debug(f"Chip '{chip_text}' não encontrado")
                return {'sucesso': False, 'chip': chip_text, 'erro': 'Chip não encontrado'}
            
            chip = chips[0]
            
            # Tenta múltiplas formas de localizar e clicar no botão de remoção
            btn_remover = None
            
            # Tenta 1: button com aria-label='remove'
            try:
                btn_remover = chip.find_element(By.XPATH, ".//button[@aria-label='remove']")
                print(f"[*] Botão de remoção encontrado via aria-label")
            except:
                pass
            
            # Tenta 2: button direto dentro do chip
            if not btn_remover:
                try:
                    btn_remover = chip.find_element(By.TAG_NAME, "button")
                    print(f"[*] Botão de remoção encontrado via TAG_NAME")
                except:
                    pass
            
            # Tenta 3: mat-icon dentro do chip
            if not btn_remover:
                try:
                    btn_remover = chip.find_element(By.XPATH, ".//mat-icon/following-sibling::button")
                    print(f"[*] Botão de remoção encontrado via mat-icon")
                except:
                    pass
            
            if not btn_remover:
                raise Exception(f"Botão de remoção não encontrado para o chip '{chip_text}'")
            
            # Scroll para o elemento (se necessário)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chip)
            time.sleep(0.3)
            
            # Remove via JavaScript (mais confiável)
            print(f"[*] Removendo chip '{chip_text}' via JavaScript...")
            self.driver.execute_script("arguments[0].click();", btn_remover)
            time.sleep(1)
            
            print(f"[✓] Chip '{chip_text}' removido")
            if self.logger:
                self.logger.info(f"Chip removido: {chip_text}")
            
            return {'sucesso': True, 'chip': chip_text}
        
        except Exception as e:
            erro_msg = f"Erro ao remover chip '{chip_text}': {str(e)}"
            print(f"[!] {erro_msg}")
            if self.logger:
                self.logger.error(erro_msg)
            return {'sucesso': False, 'chip': chip_text, 'erro': str(e)}
    
    def remover_multiplos_chips(self, chips_list: list, esperar_remocao: bool = True) -> dict:
        """Remove múltiplos chips e retorna relatório"""
        if self.logger:
            self.logger.info(f"Removendo {len(chips_list)} chip(s)")
        resultados = {
            'sucesso': [],
            'erro': [],
            'total': len(chips_list)
        }
        for chip_text in chips_list:
            resultado = self.remover_chip(chip_text, esperar_remocao)
            if resultado['sucesso']:
                resultados['sucesso'].append(chip_text)
            else:
                resultados['erro'].append(resultado)
        
        if self.logger:
            self.logger.info(f"Chips removidos: {len(resultados['sucesso'])}/{resultados['total']}")
        return resultados


# ─────────────────────────────────────────────────────────────
# Classe BNMP3
# ─────────────────────────────────────────────────────────────
class Bnmp3:
    """
    Classe para automatizar download de mandados de prisão do BNMP3.
    Encapsula operações de login, busca e download de documentos.
    """
    
    def __init__(self, driver: webdriver.Chrome = None, download_dir: str = None, logger: logging.Logger = None, baixar_certidao: bool = False):
        """
        Inicializa a classe BNMP3.
        
        Parâmetros:
            driver: WebDriver do Selenium (opcional, será criado se não fornecido)
            download_dir: Diretório para salvar arquivos (padrão: ~/Downloads)
            logger: Logger para registrar operações (opcional)
            baixar_certidao: Se True, baixa a Certidão de Cumprimento; se False, apenas o Mandado (padrão: False)
        """
        self.driver = driver
        self.download_dir = download_dir or os.path.expanduser("~/Downloads")
        self.logger = logger
        self.baixar_certidao = baixar_certidao
        os.makedirs(self.download_dir, exist_ok=True)
    
    def login(self, usuario: str, senha: str):
        """
        Realiza login no BNMP3 e prepara a página de pesquisa.
        
        Parâmetros:
            usuario: CPF/CNPJ do usuário
            senha: Senha da conta
        
        Exceções:
            Levanta exceção se login ou preparação falharem
        """
        print("\n[ETAPA 1] Realizando login...")
        if self.logger:
            self.logger.info("=== INICIANDO LOGIN ===")
        
        try:
            self._fazer_login(usuario, senha)
            print("[✓] Login e preparação realizados com sucesso!\n")
            
            if self.logger:
                self.logger.info("=== LOGIN E PREPARAÇÃO CONCLUÍDOS COM SUCESSO ===")
        
        except Exception as e:
            erro_msg = f"Erro durante login/preparação: {e}"
            print(f"[!] ERRO FATAL: {erro_msg}")
            if self.logger:
                self.logger.error(erro_msg)
            raise
    
    def baixar_mandado(self, numero_bruto: str):
        """
        Executa o fluxo completo para um único número de mandado.
        Busca e baixa o Mandado de Prisão. Opcionalmente baixa a Certidão de Cumprimento.
        
        Parâmetros:
            numero_bruto: Número do mandado (com ou sem formatação)
        
        Exceções:
            Levanta exceção se operação falhar
        
        Nota:
            O download da Certidão é controlado pelo parâmetro 'baixar_certidao'
            passado no construtor da classe.
        """
        numero_formatado = self._formatar_numero_peca(numero_bruto)
        print(f"\n{'='*70}")
        print(f"  Processando mandado: {numero_formatado}")
        print(f"{'='*70}")
        if self.logger:
            self.logger.info(f"Iniciando processamento do mandado: {numero_formatado}")
        
        try:
            # Verifica cedo se os arquivos já existem
            if self._verificar_arquivos_existem(numero_formatado):
                print(f"[✓] Arquivos já existem - pulando processamento.")
                if self.logger:
                    self.logger.info(f"Mandado {numero_formatado} já processado - arquivos existem")
                return
            
            # Navega para a tela de peças
            if "bnmp.pdpj.jus.br/pecas" not in self.driver.current_url:
                self.driver.get(BNMP_PECAS_URL)
                time.sleep(2)
            
            # Passo 1: busca pelo número da peça e obtém o RJI
            rji = self._buscar_por_numero_peca(numero_formatado)
            
            # Passo 2: baixa o Mandado de Prisão
            self._baixar_mandado(numero_formatado)
            
            # Passo 3: busca pelo RJI e baixa a Certidão de Cumprimento (se habilitado)
            if self.baixar_certidao:
                self._buscar_e_baixar_certidao(rji, numero_formatado)
            else:
                print(f"\n[*] Download de Certidão desativado (configure 'baixar_certidao=True' para habilitar)")
                if self.logger:
                    self.logger.debug("Download de Certidão desativado")
            
            print(f"\n[✓] Processamento concluído para {numero_formatado}")
            if self.logger:
                self.logger.info(f"Processamento concluído com sucesso para: {numero_formatado}")
        
        except Exception as e:
            aviso_msg = f"Não foi possível processar o mandado {numero_formatado}: {str(e)}"
            print(f"\n[!] {aviso_msg}")
            if self.logger:
                self.logger.warning(aviso_msg)
            raise
    
    # ─────────────────────────────────────────────────────────────
    # Métodos Privados - Login e Preparação
    # ─────────────────────────────────────────────────────────────
    
    def _fazer_login(self, usuario: str, senha: str):
        """Realiza login no BNMP3 e prepara a página de pesquisa (remove chips de filtro)."""
        print("[*] Acessando página de login...")
        if self.logger:
            self.logger.info("Acessando página de login")
        
        self.driver.get(LOGIN_URL)
        print("[*] Aguardando carregamento da página de login...")
        time.sleep(4)
        
        print("[*] Preenchendo credenciais...")
        
        try:
            # Tenta múltiplos seletores para o campo CPF
            xpath_cpf_list = [
                '//*[@placeholder="000.000.000-00"]',
                '//input[@placeholder="000.000.000-00"]',
                '//input[contains(@placeholder, "000")]',
                'input:first-of-type',
            ]
            
            campo_cpf = None
            for xpath in xpath_cpf_list:
                try:
                    campo_cpf = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    print(f"[✓] Campo CPF encontrado")
                    break
                except:
                    continue
            
            if not campo_cpf:
                raise Exception("Campo CPF não encontrado")
            
            campo_cpf.send_keys(usuario)
            time.sleep(0.5)
            
            # Tenta múltiplos seletores para o campo senha
            xpath_senha_list = [
                '//*[@placeholder="Digite sua senha"]',
                '//input[@placeholder="Digite sua senha"]',
                '//input[@type="password"]',
                'input:last-of-type',
            ]
            
            campo_senha = None
            for xpath in xpath_senha_list:
                try:
                    campo_senha = self.driver.find_element(By.XPATH, xpath)
                    print(f"[✓] Campo senha encontrado")
                    break
                except:
                    continue
            
            if not campo_senha:
                raise Exception("Campo senha não encontrado")
            
            campo_senha.send_keys(senha)
            time.sleep(0.5)
            
            # Tenta múltiplos seletores para o botão Entrar
            xpath_entrar_list = [
                '//button[@type="submit" and contains(text(), "Entrar")]',
                '//form//button[@type="submit"]',
                '//button[contains(text(), "Entrar")]',
                '//button[contains(., "Entrar")]',
                '//*[@type="submit"]',
                'button[type="submit"]',
            ]
            
            botao_entrar = None
            for xpath in xpath_entrar_list:
                try:
                    botao_entrar = self.driver.find_element(By.XPATH, xpath)
                    print(f"[✓] Botão Entrar encontrado")
                    break
                except:
                    continue
            
            if not botao_entrar:
                raise Exception("Botão Entrar não encontrado")
            
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_entrar)
            time.sleep(0.3)
            self.driver.execute_script("arguments[0].click();", botao_entrar)
            
            print("[*] Aguardando carregamento após login...")
            time.sleep(5)
            
            # Verifica se o login foi bem-sucedido
            if "pagina-inicial" in self.driver.current_url or "pecas" in self.driver.current_url:
                print("[✓] Login realizado com sucesso!")
                if self.logger:
                    self.logger.info("Login realizado com sucesso")
            else:
                print(f"[!] Aviso: URL após login é {self.driver.current_url}")
                if self.logger:
                    self.logger.warning(f"URL após login é {self.driver.current_url}")
            
            # ─── PREPARAÇÃO DA PÁGINA (REMOÇÃO DE CHIPS) ───
            print("\n[ETAPA 2] Preparando página de pesquisa...")
            self._preparar_pagina_pesquisa()
        
        except Exception as e:
            print(f"[!] Erro durante login/preparação: {e}")
            if self.logger:
                self.logger.error(f"Erro durante login/preparação: {e}")
            raise
    
    def _preparar_pagina_pesquisa(self):
        """Prepara a página de peças removendo filtros padrão (chips)."""
        max_tentativas = 3
        
        for tentativa in range(1, max_tentativas + 1):
            print(f"\n[*] Tentativa {tentativa}/{max_tentativas}: Acessando página de peças...")
            if self.logger:
                self.logger.info(f"Tentativa {tentativa}/{max_tentativas}: Acessando página de peças")
            
            try:
                self.driver.get(BNMP_PECAS_URL)
                print("[*] Aguardando carregamento da página de peças (10s)...")
                time.sleep(10)
                
                # Verifica se realmente está na página correta
                if "/pecas" in self.driver.current_url:
                    print(f"[✓] Página de peças carregada com sucesso!")
                    if self.logger:
                        self.logger.info("Página de peças carregada com sucesso")
                    break
                else:
                    print(f"[!] Tentativa {tentativa} falhou: Página verificação falhou")
                    if self.logger:
                        self.logger.warning(f"Tentativa {tentativa}/{max_tentativas}: Verificação da página falhou")
            
            except Exception as e:
                print(f"[!] Tentativa {tentativa} falhou: {e}")
                if self.logger:
                    self.logger.warning(f"Tentativa {tentativa}/{max_tentativas} falhou: {e}")
            
            if tentativa < max_tentativas:
                print(f"[*] Aguardando 2 segundos antes de tentar novamente...")
                time.sleep(2)
        else:
            erro_msg = "Não foi possível acessar a página de peças após 3 tentativas. Abortando."
            print(f"\n[!] ERRO FATAL: {erro_msg}")
            if self.logger:
                self.logger.error(erro_msg)
            raise Exception(erro_msg)
        
        print("\n[✓] Página de peças carregada com sucesso!")
        
        # Passo 1: Expandir filtros
        print("[*] Expandindo menu de filtros...")
        if self.logger:
            self.logger.info("Expandindo menu de filtros")
        
        try:
            xpath_mais_filtros = "//button[contains(., 'Mais Filtros')]"
            btn_mais_filtros = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, xpath_mais_filtros))
            )
            self.driver.execute_script("arguments[0].click();", btn_mais_filtros)
            time.sleep(1)
            print("[✓] Menu de filtros expandido")
        except Exception as e:
            print(f"[!] Aviso: Botão 'Mais Filtros' não encontrado: {e}")
            if self.logger:
                self.logger.warning(f"Botão 'Mais Filtros' não encontrado: {e}")
        
        # Passo 2: Remover chip filters
        print("[*] Removendo chip filters...")
        if self.logger:
            self.logger.info("Removendo chip filters")
        
        try:
            # Clica no botão "Limpar"
            btn_limpar = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Limpar']"))
            )
            self.driver.execute_script("arguments[0].click();", btn_limpar)
            print("[✓] Botão 'Limpar' clicado")
            time.sleep(1)
        except Exception as e:
            print(f"[!] Aviso: Botão 'Limpar' não encontrado: {e}")
            if self.logger:
                self.logger.warning(f"Botão 'Limpar' não encontrado: {e}")
        
        try:
            # Marca o checkbox "Pessoas Ativas"
            time.sleep(2)
            checkbox_pessoas_ativas = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox' and @aria-label='Pessoas Ativas']"))
            )
            if not checkbox_pessoas_ativas.is_selected():
                self.driver.execute_script("arguments[0].click();", checkbox_pessoas_ativas)
                print("[✓] Checkbox 'Pessoas Ativas' marcado")
            else:
                print("[*] Checkbox 'Pessoas Ativas' já estava marcado")
            if self.logger:
                self.logger.info("Checkbox 'Pessoas Ativas' marcado")
            time.sleep(1)
        except Exception as e:
            print(f"[!] Aviso: Checkbox 'Pessoas Ativas' não encontrado: {e}")
            if self.logger:
                self.logger.warning(f"Checkbox 'Pessoas Ativas' não encontrado: {e}")
        
        print("[✓] Página preparada para pesquisa!")
        if self.logger:
            self.logger.info("Página preparada com sucesso")
    
    # ─────────────────────────────────────────────────────────────
    # Métodos Privados - Busca e Download
    # ─────────────────────────────────────────────────────────────
    
    def _formatar_numero_peca(self, numero_bruto: str) -> str:
        """Converte número sem formatação para o padrão BNMP."""
        n = re.sub(r"\D", "", numero_bruto)
        if len(n) == 28:
            return (
                f"{n[0:7]}-{n[7:9]}.{n[9:13]}.{n[13]}.{n[14:16]}"
                f".{n[16:20]}.{n[20:22]}.{n[22:26]}-{n[26:28]}"
            )
        return numero_bruto
    
    def _verificar_arquivos_existem(self, numero_mandado: str) -> bool:
        """Verifica se os arquivos de mandado e certidão já existem."""
        numero_limpo = re.sub(r"\D", "", numero_mandado)[:28]
        arquivo_mandado = os.path.join(self.download_dir, f"mandado_{numero_limpo}.pdf")
        arquivo_certidao = os.path.join(self.download_dir, f"certidao_{numero_limpo}.pdf")
        ambos_existem = os.path.exists(arquivo_mandado) and os.path.exists(arquivo_certidao)
        if ambos_existem:
            print(f"[!] Arquivos já existem para este mandado:")
            print(f"    - {os.path.basename(arquivo_mandado)}")
            print(f"    - {os.path.basename(arquivo_certidao)}")
            if self.logger:
                self.logger.debug(f"Arquivos já existem: {arquivo_mandado}, {arquivo_certidao}")
            return True
        return False
    
    def _preencher_campo(self, css_selector: str, valor: str, timeout=WAIT_TIMEOUT):
        """Preenche um campo com suporte a múltiplos seletores."""
        time.sleep(1)
        
        seletores = [
            css_selector,
            "input[name='numeroPeca']",
            "input[name='rji']",
            "#mat-input-3",
            "input[id*='numeroPeca']",
            "mat-form-field input[matinput]",
            "input[matinput]",
        ]
        
        campo = None
        for seletor_atual in seletores:
            try:
                campo = WebDriverWait(self.driver, timeout=5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, seletor_atual))
                )
                break
            except:
                continue
        
        if campo is None:
            raise TimeoutException(f"Campo não encontrado com nenhum dos seletores")
        
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", campo)
        time.sleep(0.3)
        self.driver.execute_script("arguments[0].focus();", campo)
        time.sleep(0.2)
        self.driver.execute_script("arguments[0].value = '';", campo)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", campo)
        
        campo.send_keys(valor)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", campo)
        time.sleep(0.5)
        return campo
    
    def _limpar_campo(self, css_selector: str):
        """Limpa um campo via JavaScript."""
        try:
            campo = self.driver.find_element(By.CSS_SELECTOR, css_selector)
            self.driver.execute_script("arguments[0].value = '';", campo)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", campo)
            time.sleep(0.3)
        except:
            pass
    
    def _clicarbuscar(self):
        """Clica no botão Buscar."""
        time.sleep(0.5)
        btn = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SEL_BTN_BUSCAR))
        )
        print("[*] Clicando no botão Buscar via JavaScript...")
        if self.logger:
            self.logger.debug("Clicando no botão Buscar")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.3)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(2)
    
    def _extrairrji_da_grid(self) -> str | None:
        """Extrai o valor da coluna RJI da primeira linha da grid."""
        try:
            WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
            )
            linhas = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            if not linhas:
                return None
            celulas = linhas[0].find_elements(By.TAG_NAME, "td")
            if 8 < len(celulas):
                rji = celulas[8].text.strip()
                if rji:
                    return rji
        except Exception as e:
            print(f"[!] Erro ao extrair RJI: {e}")
            if self.logger:
                self.logger.error(f"Erro ao extrair RJI: {e}")
        return None
    
    def _localizarmandado_na_grid(self, numero_mandado: str) -> int | None:
        """Localiza a linha do Mandado de Prisão na grid."""
        try:
            WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
            )
            linhas = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            numero_limpo_pesquisado = re.sub(r"\D", "", numero_mandado)[:28]
            for idx, linha in enumerate(linhas):
                celulas = linha.find_elements(By.TAG_NAME, "td")
                if len(celulas) < 3:
                    continue
                numero_peca = re.sub(r"\D", "", celulas[1].text)[:28]
                tipo_peca = celulas[2].text.upper()
                if "MANDADO" in tipo_peca and "PRISÃO" in tipo_peca and numero_peca == numero_limpo_pesquisado:
                    print(f"[✓] Mandado de Prisão encontrado na linha {idx}")
                    if self.logger:
                        self.logger.debug(f"Mandado encontrado na linha {idx}")
                    return idx
        except Exception as e:
            print(f"[!] Erro ao localizar mandado: {e}")
            if self.logger:
                self.logger.error(f"Erro ao localizar mandado: {e}")
        return None
    
    def _localizarcertidao_na_grid(self, numero_mandado: str) -> int | None:
        """Localiza a linha da Certidão de Cumprimento na grid."""
        try:
            WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
            )
            linhas = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            numero_pesquisado_25chars = numero_mandado[:25]
            
            for idx, linha in enumerate(linhas):
                celulas = linha.find_elements(By.TAG_NAME, "td")
                if len(celulas) < 3:
                    continue
                numero_peca_25chars = celulas[1].text[:25]
                tipo_peca = celulas[2].text.upper()
                
                eh_certidao = (
                    "CERTIDÃO" in tipo_peca
                    and "CUMPRIMENTO" in tipo_peca
                    and "MANDADO" in tipo_peca
                    and "PRISÃO" in tipo_peca
                )
                mesmo_prefixo = numero_peca_25chars == numero_pesquisado_25chars
                
                if eh_certidao and mesmo_prefixo:
                    print(f"[✓] Certidão encontrada na linha {idx}")
                    if self.logger:
                        self.logger.debug(f"Certidão encontrada na linha {idx}")
                    return idx
        except Exception as e:
            print(f"[!] Erro ao localizar certidão: {e}")
            if self.logger:
                self.logger.error(f"Erro ao localizar certidão: {e}")
        return None
    
    def _clicardownload_na_linha(self, indice_linha: int):
        """Clica no download de uma linha específica."""
        time.sleep(0.5)
        WebDriverWait(self.driver, WAIT_TIMEOUT).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr button.btn-menu"))
        )
        botoes_menu = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr button.btn-menu")
        if indice_linha >= len(botoes_menu):
            raise IndexError(f"Linha {indice_linha} não encontrada")
        
        print(f"[*] Clicando no botão de menu da linha {indice_linha}")
        btn = botoes_menu[indice_linha]
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.3)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(1.5)
        
        item_download = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//*[@role='menuitem' and contains(., 'Download')]"))
        )
        print(f"[*] Clicando em Download via JavaScript...")
        time.sleep(0.3)
        self.driver.execute_script("arguments[0].click();", item_download)
        time.sleep(3)
    
    def _renomear_arquivo_download(self, numero_mandado: str, sufixo: str, timeout: int = 60):
        """Aguarda e renomeia arquivo de download."""
        caminho_peca = os.path.join(self.download_dir, "Peça.pdf")
        
        print(f"[*] Aguardando arquivo de download...")
        print(f"[*] Procurando em: {self.download_dir}")
        if self.logger:
            self.logger.info(f"Aguardando arquivo '{sufixo}' em {self.download_dir}")
        
        tempo_limite = time.time() + timeout
        intervalo_verificacao = 2
        tempo_inicial = time.time()
        
        while time.time() < tempo_limite:
            time.sleep(intervalo_verificacao)
            
            # Lista todos os arquivos PDF no diretório
            arquivos_pdf = [f for f in os.listdir(self.download_dir) if f.endswith('.pdf')]
            
            if arquivos_pdf:
                print(f"[*] PDFs encontrados: {arquivos_pdf}")
            
            # Procura pelo arquivo esperado
            if os.path.exists(caminho_peca):
                print(f"[✓] Arquivo detectado: Peça.pdf")
                time.sleep(2)
                
                try:
                    tamanho_antes = os.path.getsize(caminho_peca)
                    time.sleep(2)
                    tamanho_depois = os.path.getsize(caminho_peca)
                    
                    if tamanho_antes != tamanho_depois:
                        print(f"[*] Arquivo ainda está sendo baixado (tamanho mudando)...")
                        continue
                    
                    numero_limpo = re.sub(r"\D", "", numero_mandado)[:28]
                    novo_nome = f"{sufixo}_{numero_limpo}.pdf"
                    caminho_novo = os.path.join(self.download_dir, novo_nome)
                    
                    if os.path.exists(caminho_novo):
                        os.remove(caminho_peca)
                        return novo_nome
                    
                    os.rename(caminho_peca, caminho_novo)
                    print(f"[✓] Arquivo renomeado para: {novo_nome}")
                    if self.logger:
                        self.logger.info(f"Arquivo renomeado: {novo_nome}")
                    return novo_nome
                
                except Exception as e:
                    print(f"[!] Erro ao processar arquivo: {e}")
                    if self.logger:
                        self.logger.error(f"Erro ao processar arquivo: {e}")
                    continue
            else:
                # Se não achou "Peça.pdf", procura por arquivos PDF baixados recentemente
                try:
                    arquivos_dir = os.listdir(self.download_dir)
                    tempo_atual = time.time()
                    
                    # Procura por PDFs criados recentemente (nos últimos 10 segundos)
                    for arquivo in arquivos_dir:
                        if arquivo.endswith('.pdf'):
                            caminho_arquivo = os.path.join(self.download_dir, arquivo)
                            tempo_criacao = os.path.getmtime(caminho_arquivo)
                            
                            if tempo_atual - tempo_criacao < 10:
                                print(f"[*] Arquivo PDF detectado (recente): {arquivo}")
                                
                                # Verifica se o arquivo terminou de fazer download
                                tamanho_antes = os.path.getsize(caminho_arquivo)
                                time.sleep(2)
                                tamanho_depois = os.path.getsize(caminho_arquivo)
                                
                                if tamanho_antes == tamanho_depois:
                                    print(f"[✓] Download concluído: {arquivo}")
                                    
                                    numero_limpo = re.sub(r"\D", "", numero_mandado)[:28]
                                    novo_nome = f"{sufixo}_{numero_limpo}.pdf"
                                    caminho_novo = os.path.join(self.download_dir, novo_nome)
                                    
                                    if arquivo != novo_nome:
                                        os.rename(caminho_arquivo, caminho_novo)
                                        print(f"[✓] Arquivo renomeado para: {novo_nome}")
                                    
                                    if self.logger:
                                        self.logger.info(f"Arquivo renomeado: {novo_nome}")
                                    return novo_nome
                except Exception as e:
                    print(f"[!] Erro ao verificar arquivos: {e}")
        
        # Se chegou aqui, timeout ocorreu
        tempo_decorrido = time.time() - tempo_inicial
        erro_msg = f"Timeout aguardando arquivo após {tempo_decorrido:.1f}s"
        print(f"[!] {erro_msg}")
        print(f"[!] Arquivos no diretório: {os.listdir(self.download_dir)}")
        if self.logger:
            self.logger.error(f"{erro_msg}. Arquivos: {os.listdir(self.download_dir)}")
        raise TimeoutError(erro_msg)
    
    def _buscar_por_numero_peca(self, numero_peca: str) -> str:
        """Busca um mandado e retorna o RJI."""
        print(f"\n[2/5] Buscando mandado: {numero_peca}")
        if self.logger:
            self.logger.info(f"Buscando mandado: {numero_peca}")
        
        max_tentativas = 5
        intervalo_tentativa = 2
        
        for tentativa in range(1, max_tentativas + 1):
            try:
                if "bnmp.pdpj.jus.br/pecas" not in self.driver.current_url:
                    self.driver.get(BNMP_PECAS_URL)
                    time.sleep(3)
                
                print(f"[*] Limpando campos de entrada...")
                self._limpar_campo(SEL_NUMERO_PECA)
                self._limpar_campo(SEL_RJI)
                time.sleep(0.5)
                
                self._preencher_campo(SEL_NUMERO_PECA, numero_peca)
                self._clicarbuscar()
                time.sleep(2)
                
                rji = self._extrairrji_da_grid()
                if rji:
                    print(f"[✓] RJI encontrado: {rji}")
                    if self.logger:
                        self.logger.info(f"RJI encontrado: {rji}")
                    return rji
                else:
                    if tentativa < max_tentativas:
                        print(f"[*] Tentativa {tentativa}/{max_tentativas}: RJI não encontrado. Aguardando...")
                        time.sleep(intervalo_tentativa)
                        continue
            except Exception as e:
                if tentativa < max_tentativas:
                    print(f"[*] Tentativa {tentativa}/{max_tentativas}: Erro: {str(e)}")
                    time.sleep(intervalo_tentativa)
                    continue
                else:
                    raise
        
        raise ValueError(f"Não foi possível encontrar o RJI para o mandado {numero_peca}")
    
    def _baixar_mandado(self, numero_mandado: str):
        """Baixa o Mandado de Prisão."""
        print("\n[3/5] Fazendo download do Mandado de Prisão...")
        if self.logger:
            self.logger.info("Fazendo download do Mandado de Prisão")
        
        indice = self._localizarmandado_na_grid(numero_mandado)
        if indice is None:
            raise ValueError(f"Mandado não encontrado na grid")
        
        self._clicardownload_na_linha(indice)
        self._renomear_arquivo_download(numero_mandado, "mandado")
        print("[✓] Download do Mandado de Prisão concluído.")
        if self.logger:
            self.logger.info("Download do Mandado concluído")
    
    def _buscar_e_baixar_certidao(self, rji: str, numero_mandado: str):
        """Busca e baixa a Certidão de Cumprimento."""
        print(f"\n[4/5] Buscando Certidão de Cumprimento pelo RJI {rji}...")
        if self.logger:
            self.logger.info(f"Buscando Certidão - RJI: {rji}")
        
        print(f"[*] Limpando campos de entrada...")
        self._limpar_campo(SEL_NUMERO_PECA)
        self._limpar_campo(SEL_RJI)
        time.sleep(0.5)
        
        self._preencher_campo(SEL_RJI, rji)
        self._clicarbuscar()
        time.sleep(3)
        
        indice = self._localizarcertidao_na_grid(numero_mandado)
        if indice is None:
            print(f"[!] Certidão não encontrada. Continuando...")
            if self.logger:
                self.logger.warning("Certidão não encontrada")
            return
        
        self._clicardownload_na_linha(indice)
        self._renomear_arquivo_download(numero_mandado, "certidao")
        print("[✓] Download da Certidão de Cumprimento concluído.")
        if self.logger:
            self.logger.info("Download da Certidão concluído")

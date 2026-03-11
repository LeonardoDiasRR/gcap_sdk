import os
import requests
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class Gcap:
    def __init__(self):
        self.base_url = os.getenv('GCAP_BACKEND_URL_BASE')
        self.api_key = os.getenv('GCAP_BACKEND_API_KEY')
        self.unidade_id = os.getenv('GCAP_BACKEND_UNIDADE_ID')
        self.user = os.getenv('GCAP_BACKEND_USER')
        self.password = os.getenv('GCAP_BACKEND_PASSWORD')
        self.access_token = None
        self.headers = {
            'Apikey': self.api_key,
            'Content-Type': 'application/json'
        }

    def login(self):
        """
        Realiza login e obtém um access token
        """
        try:
            auth_url = f"{self.base_url}/auth/v1/token?grant_type=password"
            
            payload = {
                "email": self.user,
                "password": self.password,
                "gotrue_meta_security": {}
            }
            
            response = requests.post(
                auth_url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                
                # Atualizar headers com o token obtido
                self.headers['Authorization'] = f"Bearer {self.access_token}"
                
                return {
                    'success': True,
                    'token': self.access_token,
                    'user_id': data.get('user', {}).get('id')
                }
            else:
                return {
                    'success': False,
                    'error': f'Login failed with status code: {response.status_code}',
                    'response': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def logout(self):
        """
        Inativa o access token
        """
        self.access_token = None
        if 'Authorization' in self.headers:
            del self.headers['Authorization']
        return {'success': True, 'message': 'Logged out successfully'}

    def _make_request(self, method, endpoint, **kwargs):
        """
        Faz requisições HTTP para os endpoints da API.
        Para requisições GET em endpoints de listagem, busca todas as páginas automaticamente.
        """
        url = f"{self.base_url}{endpoint}"
        
        # Adicionar o unidade_id como query parameter se não estiver presente
        params = kwargs.get('params', {})
        if 'unidade_id' not in params:
            params['unidade_id'] = self.unidade_id
        kwargs['params'] = params
        
        # Adicionar headers
        kwargs.setdefault('headers', {}).update(self.headers)
        
        try:
            # Para GET em endpoints de listagem, buscar todas as páginas
            if method == 'GET' and '/functions/v1/' in endpoint:
                all_data = []
                page = params.get('page', 0)
                page_size = params.get('page_size', 100)
                
                while True:
                    params['page'] = page
                    params['page_size'] = page_size
                    kwargs['params'] = params
                    
                    response = requests.request(method, url, **kwargs)
                    
                    if response.status_code != 200:
                        return {
                            'success': False,
                            'status_code': response.status_code,
                            'error': f'HTTP {response.status_code}',
                            'response': response.text
                        }
                    
                    result = response.json() if response.content else {}
                    
                    # Extrair dados da resposta
                    # A API pode retornar {'data': [...]} ou {'data': {'data': [...], 'total': N}}
                    response_data = result.get('data', [])
                    
                    # Se response_data é um dict com chave 'data', extrair a lista
                    if isinstance(response_data, dict) and 'data' in response_data:
                        page_items = response_data.get('data', [])
                    elif isinstance(response_data, list):
                        page_items = response_data
                    else:
                        page_items = []
                    
                    # Adicionar itens à lista total
                    if isinstance(page_items, list):
                        all_data.extend(page_items)
                    else:
                        # Se não é lista, é fim dos dados
                        break
                    
                    # Verificar se há mais páginas
                    # Se recebeu menos itens que o page_size, é a última página
                    if len(page_items) < page_size:
                        break
                    
                    page += 1
                
                return {
                    'success': True,
                    'status_code': 200,
                    'data': {'data': all_data, 'total': len(all_data)},
                    'response': response
                }
            else:
                # Para outros tipos de requisição, fazer como antes
                response = requests.request(method, url, **kwargs)
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'data': response.json() if response.content else None,
                    'response': response
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    # Métodos para cada endpoint da API

    def listar_mandados(self, page=0, page_size=100, **filters):
        """
        Lista mandados
        """
        params = {
            'page': page,
            'page_size': page_size
        }
        # Adicionar filtros
        for key, value in filters.items():
            params[key] = value
            
        return self._make_request('GET', '/functions/v1/mandados', params=params)

    def atualizar_mandado(self, mandado_id, **data):
        """
        Atualiza um mandado
        """
        return self._make_request('PATCH', f'/functions/v1/mandados/{mandado_id}', json=data)

    def atualizar_passageiro(self, passageiro_id, **data):
        """
        Atualiza um passageiro
        """
        return self._make_request('PATCH', f'/functions/v1/passageiros/{passageiro_id}', json=data)

    def listar_passageiros(self, page=0, page_size=100, **filters):
        """
        Lista passageiros
        """
        params = {
            'page': page,
            'page_size': page_size
        }
        # Adicionar filtros
        for key, value in filters.items():
            params[key] = value
            
        return self._make_request('GET', '/functions/v1/passageiros', params=params)

    def listar_procurados(self, page=0, page_size=100, **filters):
        """
        Lista procurados
        """
        params = {
            'page': page,
            'page_size': page_size
        }
        # Adicionar filtros
        for key, value in filters.items():
            params[key] = value
            
        return self._make_request('GET', '/functions/v1/procurados', params=params)

    def listar_contatos(self, page=0, page_size=100, **filters):
        """
        Lista contatos
        """
        params = {
            'page': page,
            'page_size': page_size
        }
        # Adicionar filtros
        for key, value in filters.items():
            params[key] = value
            
        return self._make_request('GET', '/functions/v1/contatos', params=params)

    def listar_servicos(self, page=0, page_size=100, **filters):
        """
        Lista serviços
        """
        params = {
            'page': page,
            'page_size': page_size
        }
        # Adicionar filtros
        for key, value in filters.items():
            params[key] = value
            
        return self._make_request('GET', '/functions/v1/servicos', params=params)

    def listar_instituicoes(self, page=0, page_size=100, **filters):
        """
        Lista instituições
        """
        params = {
            'page': page,
            'page_size': page_size
        }
        # Adicionar filtros
        for key, value in filters.items():
            params[key] = value
            
        return self._make_request('GET', '/functions/v1/instituicoes', params=params)

    def upload_passageiros(self, file_path):
        """
        Faz upload em lote de passageiros
        """
        try:
            url = f"{self.base_url}/functions/v1/bulk-upload-passageiros"
            
            files = {
                'files': open(file_path, 'rb')
            }
            
            data = {
                'unidade_id': self.unidade_id
            }
            
            # Criar headers sem Content-Type para deixar requests
            # definir automaticamente multipart/form-data
            upload_headers = {
                'Apikey': self.headers.get('Apikey'),
            }
            if 'Authorization' in self.headers:
                upload_headers['Authorization'] = self.headers['Authorization']
            
            response = requests.post(
                url,
                headers=upload_headers,
                data=data,
                files=files
            )
            
            files['files'].close()
            
            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.json() if response.content else None,
                'response': response
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def upload_mandados(self, file_paths):
        """
        Faz upload em lote de mandados (múltiplos arquivos PDF)
        
        Args:
            file_paths (str ou list): Caminho do arquivo ou lista de caminhos
        """
        try:
            url = f"{self.base_url}/functions/v1/bulk-upload-mandados"
            
            # Converter string para lista se necessário
            if isinstance(file_paths, str):
                file_paths = [file_paths]
            
            # Criar lista de tuplas com content-type explícito
            # Formato: ('field_name', (filename, file_object, content_type))
            files = []
            file_objects = []
            
            for file_path in file_paths:
                file_obj = open(file_path, 'rb')
                file_objects.append(file_obj)
                filename = file_path.split('\\')[-1] if '\\' in file_path else file_path.split('/')[-1]
                files.append(('files', (filename, file_obj, 'application/pdf')))
            
            data = {
                'unidade_id': self.unidade_id
            }
            
            # Criar headers sem Content-Type para deixar requests
            # definir automaticamente multipart/form-data
            upload_headers = {
                'Apikey': self.headers.get('Apikey'),
            }
            if 'Authorization' in self.headers:
                upload_headers['Authorization'] = self.headers['Authorization']
            
            response = requests.post(
                url,
                headers=upload_headers,
                data=data,
                files=files
            )
            
            # Fechar todos os arquivos abertos
            for file_obj in file_objects:
                file_obj.close()
            
            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.json() if response.content else None,
                'response': response
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def upload_certidoes(self, file_paths, servico_id):
        """
        Faz upload em lote de certidões (múltiplos arquivos PDF)
        
        Args:
            file_paths (str ou list): Caminho do arquivo ou lista de caminhos
            servico_id (str): ID do serviço
        """
        try:
            url = f"{self.base_url}/functions/v1/bulk-upload-certidoes"
            
            # Converter string para lista se necessário
            if isinstance(file_paths, str):
                file_paths = [file_paths]
            
            # Criar lista de tuplas com content-type explícito
            # Formato: ('field_name', (filename, file_object, content_type))
            files = []
            file_objects = []
            
            for file_path in file_paths:
                file_obj = open(file_path, 'rb')
                file_objects.append(file_obj)
                filename = file_path.split('\\')[-1] if '\\' in file_path else file_path.split('/')[-1]
                files.append(('files', (filename, file_obj, 'application/pdf')))
            
            data = {
                'unidade_id': self.unidade_id,
                'servico_id': servico_id
            }
            
            # Criar headers sem Content-Type para deixar requests
            # definir automaticamente multipart/form-data
            upload_headers = {
                'Apikey': self.headers.get('Apikey'),
            }
            if 'Authorization' in self.headers:
                upload_headers['Authorization'] = self.headers['Authorization']
            
            response = requests.post(
                url,
                headers=upload_headers,
                data=data,
                files=files
            )
            
            # Fechar todos os arquivos abertos
            for file_obj in file_objects:
                file_obj.close()
            
            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.json() if response.content else None,
                'response': response
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def obter_unidades(self):
        """
        Obtém as unidades do usuário (opcional, se já tiver unidade_id configurada pode ser ignorado)
        """
        try:
            url = f"{self.base_url}/rest/v1/user_roles?select=*&user_id=eq.{self.user}"
            
            response = requests.get(
                url,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to get units with status code: {response.status_code}',
                    'response': response.text
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Exemplo de uso:
# gcap = Gcap()
# login_result = gcap.login()
# if login_result['success']:
#     # Utilizar métodos da API
#     results = gcap.listar_mandados(page=0, page_size=100)
# else:
#     print("Falha no login:", login_result)
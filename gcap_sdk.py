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
        Faz requisições HTTP para os endpoints da API
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

    def listar_mandados(self, page=0, page_size=10, **filters):
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

    def listar_passageiros(self, page=0, page_size=10, **filters):
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

    def listar_procurados(self, page=0, page_size=10, **filters):
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

    def listar_contatos(self, page=0, page_size=10, **filters):
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

    def listar_servicos(self, page=0, page_size=10, **filters):
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

    def listar_instituicoes(self, page=0, page_size=10, **filters):
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
            
            response = requests.post(
                url,
                headers=self.headers,
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
#     results = gcap.listar_mandados(page=0, page_size=10)
# else:
#     print("Falha no login:", login_result)
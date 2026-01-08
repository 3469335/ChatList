"""
Модуль для логики работы с моделями нейросетей
"""
from typing import List, Dict
import concurrent.futures
from db import get_active_models
from network import send_request, APIError
import logger


class Model:
    """Класс для представления модели нейросети"""
    
    def __init__(self, model_data: Dict):
        self.id = model_data.get('id')
        self.name = model_data.get('name', '')
        self.api_url = model_data.get('api_url', '')
        self.api_id = model_data.get('api_id', '')
        self.is_active = model_data.get('is_active', 0)
        self.model_type = model_data.get('model_type', '')
        self.created_at = model_data.get('created_at', '')
    
    def to_dict(self) -> Dict:
        """Преобразовать модель в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'api_url': self.api_url,
            'api_id': self.api_id,
            'is_active': self.is_active,
            'model_type': self.model_type,
            'created_at': self.created_at
        }
    
    def send_prompt(self, prompt: str) -> Dict:
        """
        Отправить промт модели и получить ответ
        
        Args:
            prompt: Текст промта
        
        Returns:
            Словарь с результатом: {'success': bool, 'response': str, 'error': str}
        """
        try:
            model_dict = self.to_dict()
            response = send_request(model_dict, prompt)
            return {
                'success': True,
                'response': response,
                'error': None
            }
        except APIError as e:
            return {
                'success': False,
                'response': '',
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'response': '',
                'error': f"Unexpected error: {str(e)}"
            }


def get_active_models_list() -> List[Model]:
    """
    Получить список активных моделей
    
    Returns:
        Список объектов Model
    """
    models_data = get_active_models()
    return [Model(model_data) for model_data in models_data]


def send_prompt_to_models(prompt: str, models: List[Model] = None) -> List[Dict]:
    """
    Отправить промт нескольким моделям параллельно
    
    Args:
        prompt: Текст промта
        models: Список моделей (если None, используются активные модели)
    
    Returns:
        Список результатов: [{'model_id': int, 'model_name': str, 'response': str, 'error': str}, ...]
    """
    if models is None:
        models = get_active_models_list()
    
    results = []
    
    # Используем ThreadPoolExecutor для параллельной отправки запросов
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(models)) as executor:
        # Запускаем запросы параллельно
        future_to_model = {
            executor.submit(model.send_prompt, prompt): model 
            for model in models
        }
        
        # Собираем результаты
        for future in concurrent.futures.as_completed(future_to_model):
            model = future_to_model[future]
            try:
                result = future.result()
                results.append({
                    'model_id': model.id,
                    'model_name': model.name,
                    'response': result['response'],
                    'error': result['error'],
                    'success': result['success']
                })
            except Exception as e:
                results.append({
                    'model_id': model.id,
                    'model_name': model.name,
                    'response': '',
                    'error': f"Exception: {str(e)}",
                    'success': False
                })
    
    return results


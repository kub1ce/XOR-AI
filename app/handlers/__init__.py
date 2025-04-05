"""  
Инициализация пакета с роутерами.  

Автоматически собирает все переменные, заканчивающиеся на `Router`  
и имеющие тип `aiogram.Router`, из всех `.py` файлов в папке.  

Пример использования в основном файле бота:  
```python
from aiogram import Dispatcher
from . import routers  # импорт списка роутеров

dp = Dispatcher()  
dp.include_routers(*routers)  
```
"""

import os
import importlib
from aiogram import Router

routers: list[Router] = []

for filename in os.listdir(os.path.dirname(__file__)):
    if filename.endswith('.py') and not filename.startswith('__'):
        module_name = filename[:-3]
        module = importlib.import_module(f'app.handlers.{module_name}', package=__name__)
        
        for name in dir(module):
            if name.endswith('Router') and isinstance(getattr(module, name), Router):
                globals()[name] = getattr(module, name)
                routers.append(getattr(module, name))


__all__ = ["routers"]
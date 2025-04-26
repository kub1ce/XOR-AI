# XOR-AI Telegram Bot

Телеграм-бот для распознавания рукописного текста с использованием Google Docs OCR и LLM.

## Содержание

[XOR-AI Telegram Bot](https://github.com/kub1ce/XOR-AI)

- [Содержание](#содержание)
- [Установка](#установка)
- [Настройка](#настройка)
  - [1. Подготовка Google Drive](#1-подготовка-google-drive)
  - [2. Настройка Telegram бота](#2-настройка-telegram-бота)
  - [3. Настройка io.net](#3-настройка-ionet)
  - [4. Настройка переменных окружения](#4-настройка-переменных-окружения)
- [Использование](#использование)
- [Требования](#требования)
- [Структура проекта](#структура-проекта)
- [Поддержка](#поддержка)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/kub1ce/XOR-AI
cd XOR AI
```

2. **(Опционально)** Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
# Для Windows
venv\Scripts\activate
# Для Linux/Mac
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Настройка

### 1. Подготовка Google Drive

1. Перейдите на [Google Cloud Console](https://console.cloud.google.com)
2. Создайте новый проект
3. Включите Google Drive API:
   - В меню слева выберите "APIs & Services" → "Enable APIs & Services"
   - Найдите "Google Drive API" и нажмите "Enable"
4. Создайте сервисный аккаунт:
   - В меню слева выберите "APIs & Services" → "Google Drive Api" → "Credentials"
   - Нажмите "Create Credentials" → "Service account"
   - Укажите имя
   - Нажмите "Готово"
5. Скачайте ключ сервисного аккаунта:
   - Откройте созданный сервисный аккаунт
   - Перейдите на вкладку "Keys"
   - Нажмите "Add Key" → "Create new key"
   - Выберите формат JSON и скачайте файл
6. Настройте доступ к Google Drive:
   - Откройте [Google Drive](https://drive.google.com)
   - Создайте новую папку для бота
   - Нажмите "Настройки" (шестерёнка) → "Настройки доступа"
   - В поле "Добавить людей и группы" введите email сервисного аккаунта (из скачанного JSON-файла, поле `client_email`)
   - Выберите роль "Редактор" и нажмите "Отправить"

### 2. Настройка Telegram бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания нового бота
4. Скопируйте полученный токен бота

### 3. Настройка io.net

1. Зарегистрируйтесь на [io.net](https://io.net)
2. Получите API ключ в личном кабинете

### 4. Настройка переменных окружения

2. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

2. Откройте файл `.env` и заполните следующие переменные:
- `token` - токен вашего Telegram бота (полученный от @BotFather)
- `jsonId` - имя скачанного JSON-файла с учетными данными Google Cloud
- `folderId` - ID папки на Google Drive (можно получить из URL папки : https://drive.google.com/drive/folders/ID_ВАШЕЙ_ПАПКИ)
- `ioKey` - токен из [io.net](https://io.net)

## Использование

1. Запустите бота:
```bash
python main.py
```

2. В Telegram отправьте боту изображение с рукописным текстом.

3. Бот обработает изображение и вернет распознанный текст.

## Требования

- Python 3.8+
- Telegram Bot Token
- Google Drive API credentials
- io.net API Key
- Установленные зависимости из requirements.txt

## Структура проекта

```
XOR-AI-BOT/
├── app/
│   ├── handlers/     # Обработчики команд и сообщений Telegram
│   ├── services/     # Сервисы для работы с Google Drive и OCR
│   ├── utils/        # Вспомогательные функции и утилиты
│   └── settings.py   # Настройки приложения
├── .env             # Переменные окружения
├── .env.example     # Пример конфигурации
├── main.py          # Точка входа
├── requirements.txt # Зависимости
└── README.md        # Документация
```

## Поддержка

При возникновении проблем или вопросов, создайте issue в репозитории проекта.

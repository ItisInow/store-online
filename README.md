# Интернет-магазин на Flask

Адаптивный интернет-магазин, разработанный с использованием Flask и современных веб-технологий.

## Основные функции

- Просмотр каталога товаров
- Детальная страница товара
- Админ-панель для управления товарами
- Форма заказа с интеграцией Яндекс.Карт
- Адаптивный дизайн для всех устройств

## Технологии

- Backend: Flask, SQLAlchemy
- Frontend: HTML5, CSS3, JavaScript
- База данных: SQLite
- Карты: Яндекс.Карты API

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Запустите приложение:
```bash
python app.py
```

5. Откройте браузер и перейдите по адресу `http://localhost:5000`

## Админ-панель

Для доступа к админ-панели используйте:
- Логин: admin
- Пароль: admin123

## Настройка Яндекс.Карт

1. Получите API-ключ на сайте [Яндекс.Разработчики](https://developer.tech.yandex.ru/)
2. Замените `ваш_API_ключ` в файле `templates/order.html` на полученный ключ

## Структура проекта

```
├── app.py                 # Основной файл приложения
├── requirements.txt       # Зависимости проекта
├── static/               # Статические файлы
│   ├── css/             # CSS стили
│   ├── js/              # JavaScript файлы
│   └── uploads/         # Загруженные изображения
└── templates/           # HTML шаблоны
    ├── admin.html       # Админ-панель
    ├── base.html        # Базовый шаблон
    ├── catalog.html     # Страница каталога
    ├── contact.html     # Контактная форма
    ├── home.html        # Главная страница
    ├── order.html       # Форма заказа
    └── product.html     # Страница товара
```

## Лицензия

MIT 
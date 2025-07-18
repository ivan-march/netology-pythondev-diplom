# Backend социальной сети для обмена фотографиями

> Дипломная работа профессии «Python-разработчик с нуля» Netology
> Реализация API для публикации постов с изображениями, лайками и комментариями.  
> Поддержка нескольких изображений и геолокации поста.

---

## Цель проекта

Разработать **backend** приложения для социальной сети, где пользователи могут:

- ✅ Загружать текстовые публикации с фотографией
- ✅ Комментировать и ставить лайки другим публикациям
- ✅ Редактировать/удалять свои посты
- ✅ Получать детали поста, включая список комментариев и количество лайков
- ✅ Загружать несколько изображений к одному посту *(дополнительное задание)*
- ✅ Указывать локацию при создании поста и получать обратно название места по координатам *(дополнительное задание)*

---

## Технологии

- Python 3.x
- Django + Django REST Framework
- PostgreSQL
- DRF TokenAuthentication
- geopy
- drf-spectacular

---

## Структура проекта

### Модели

#### `Post`
- `author`: Автор поста
- `text`: Текст поста
- `image`: Изображение
- `created_at`: Дата создания
- `location`: Адрес, указанный пользователем
- `latitude`, `longitude`: Координаты, вычисляемые автоматически на основе `location`

#### `Comment`
- `author`: Автор комментария
- `post`: Ссылка на пост
- `text`: Текст комментария
- `created_at`: Дата создания

#### `Like`
- `author`: Кто поставил лайк
- `post`: Какой пост был оценён

#### `PostImage` *(дополнительно)*
- `post`: Связь с постом
- `image`: Фото поста

---

## Установка и настройка

### Требования
- Python 3.8+
- PostgreSQL
- Git
- Виртуальное окружение (рекомендуется)

### Инструкции по установке
1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/ivan-march/netology-pythondev-diplom.git
   cd netology-pythondev-diplom
   ```

2. **Создайте и активируйте виртуальное окружение**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Для Windows: venv\Scripts\activate
   ```

3. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте базу данных PostgreSQL**:
   - Создайте базу данных в PostgreSQL:
   - Настройте параметры подключения в `settings.py`:

5. **Примените миграции**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Создайте суперпользователя (для доступа к админ-панели)**:
   ```bash
   python manage.py createsuperuser
   ```

8. **Запустите сервер**:
   ```bash
   python manage.py runserver
   ```

9. **Проверьте API-документацию**:
   - Документация OpenAPI доступна по адресу: `http://localhost:8000/api/swagger/`
   - Redoc-документация: `http://localhost:8000/api/redoc/`

---

## Структура API

API предоставляет следующие эндпоинты для работы с публикациями, комментариями и лайками:

### Эндпоинты
| Метод | URL                         | Описание |
|-------|------------------------------|----------|
| GET   | `/api/posts/`                | Получить список всех постов |
| POST  | `/api/posts/`                | Создать новый пост (только авторизованный) |
| GET   | `/api/posts/{id}/`           | Получить детали конкретного поста |
| PUT/PATCH | `/api/posts/{id}/`         | Обновить пост (только автор) |
| DELETE | `/api/posts/{id}/`          | Удалить пост (только автор) |
| POST  | `/api/posts/{id}/comment/`   | Оставить комментарий (только авторизованный) |
| POST  | `/api/posts/{id}/like/`      | Поставить или убрать лайк (только авторизованный) |
| POST  | `/api/posts/{id}/images/`    | Загрузить несколько изображений к посту *(доп. задание)* |
| DELETE| `/api/posts/{id}/images/`    | Удалить все изображения поста *(доп. задание)* |

Примеры запросов в `requests-examples.http`

---

## Геоданные

- При создании или обновлении публикации с указанием `location` (например, "Москва") автоматически определяются координаты (`latitude` и `longitude`) с помощью библиотеки `geopy` (метод `geocode`).
- Если поле `location` пустое или `null`, координаты очищаются.
- При получении деталей публикации, если координаты доступны, выполняется обратное геокодирование (метод `reverse`), чтобы вернуть адрес в читаемом виде (например, "Москва, Россия").

---

## Лицензия

MIT License
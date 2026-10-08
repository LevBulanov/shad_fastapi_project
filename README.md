# Book Seller Platform API

Веб-приложение на FastAPI для платформы объявлений о продаже книг. Реализована регистрация и управление продавцами, их книгами, а также JWT-авторизация для защищённых эндпоинтов с проверкой прав доступа по владельцу.

## Стек технологий

- **Python 3.11+**
- **FastAPI** — веб-фреймворк
- **SQLAlchemy** — ORM, работа с БД через асинхронные сессии
- **PostgreSQL** — база данных
- **Alembic** — миграции БД
- **Pydantic** — валидация данных
- **python-jose** — работа с JWT-токенами
- **passlib[bcrypt]** — хеширование паролей
- **pytest / pytest-asyncio** — тестирование
- **Docker / docker-compose** — контейнеризация

## Функциональность

### Основные эндпоинты

#### Книги (Books)
| Метод | Эндпоинт | Авторизация | Описание |
|-------|----------|--------------|----------|
| `POST` | `/api/v1/books/` | требуется | Создание книги |
| `GET` | `/api/v1/books/` | не требуется | Получение списка всех книг |
| `GET` | `/api/v1/books/{book_id}` | не требуется | Получение книги по ID |
| `PUT` | `/api/v1/books/{book_id}` | требуется, только владелец | Обновление книги |
| `DELETE` | `/api/v1/books/{book_id}` | не требуется | Удаление книги |

Поля книги в запросе на **создание** (`POST`):
```json
{
  "title": "Clean Architecture",
  "author": "Robert Martin",
  "count_pages": 300,
  "year": 2025
}
```

Поля книги в **ответе** API:
```json
{
  "title": "Clean Architecture",
  "author": "Robert Martin",
  "pages": 300,
  "year": 2025,
  "id": 1,
  "seller_id": 1
}
```

**Важно:**
- при создании книги поле количества страниц называется `count_pages`, а в ответе API оно возвращается как `pages`
- при обновлении книги (`PUT`) поле называется `pages` (как в ответе)
- указание слишком раннего года (например, `1986`) приводит к ошибке валидации `422 Unprocessable Content`
- редактировать книгу (`PUT`) может только тот продавец, `id` которого совпадает с `seller_id` книги. Если авторизованный пользователь пытается изменить чужую книгу — возвращается `403 Forbidden`
- запрос книги по несуществующему `id` возвращает `404 Not Found`

#### Продавцы (Sellers)
| Метод | Эндпоинт | Авторизация | Описание |
|-------|----------|--------------|----------|
| `POST` | `/api/v1/seller/` | не требуется | Регистрация нового продавца |
| `GET` | `/api/v1/seller/` | не требуется | Список всех продавцов (без паролей) |
| `GET` | `/api/v1/seller/{seller_id}` | требуется | Данные продавца и его книги (без пароля) |
| `PUT` | `/api/v1/seller/{seller_id}` | не требуется | Обновление данных продавца (без изменения пароля и книг) |
| `DELETE` | `/api/v1/seller/{seller_id}` | не требуется | Удаление продавца вместе с его книгами (каскадное удаление) |

Поля продавца при **регистрации** (`POST`):
```json
{
  "first_name": "Ivan",
  "last_name": "Ivanov",
  "email": "ivan@test.com",
  "password": "123456"
}
```

Поля продавца в **ответе** API (`password` никогда не возвращается):
```json
{
  "id": 1,
  "first_name": "Ivan",
  "last_name": "Ivanov",
  "email": "ivan@test.com"
}
```

Ответ эндпоинта `GET /api/v1/seller/{seller_id}` дополнительно включает список книг продавца:
```json
{
  "id": 1,
  "first_name": "Ivan",
  "last_name": "Ivanov",
  "email": "ivan@test.com",
  "books": [
    {
      "id": 1,
      "title": "Book 1",
      "author": "Author 1",
      "year": 2023,
      "pages": 100,
      "seller_id": 1
    }
  ]
}
```

**Важно:**
- запрос без токена к `GET /api/v1/seller/{seller_id}` возвращает `401 Unauthorized`
- при удалении продавца (`DELETE`) все его книги удаляются каскадно
- запрос удаления по несуществующему `id` возвращает `404 Not Found`
- список продавцов (`GET /api/v1/seller/`) возвращается в формате `{"sellers": [...]}`
- список книг (`GET /api/v1/books/`) возвращается в формате `{"books": [...]}`

#### Авторизация
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/api/v1/token/` | Получение JWT-токена по email и паролю (JSON) |

### Модели данных

**Seller**
- `id` — идентификатор
- `first_name` — имя
- `last_name` — фамилия
- `email` — email (уникальный)
- `password` — хеш пароля (не возвращается в ответах API)

**Book**
- `id` — идентификатор
- `title` — название
- `author` — автор
- `year` — год издания (есть нижнее ограничение, иначе `422`)
- `pages` — количество страниц (при создании передаётся как `count_pages`)
- `seller_id` — внешний ключ на продавца (связь **один-ко-многим**: один продавец — много книг)

### Авторизация (JWT)

Защищённые эндпоинты требуют передачи токена в заголовке:

```
Authorization: Bearer <your_jwt_token>
```

Токен выдаётся через `POST /api/v1/token/` при передаче корректных `email` и `password` в формате **JSON**:

```json
{
  "email": "ivan@test.com",
  "password": "123456"
}
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Если email не найден или пароль неверный — возвращается `401 Unauthorized`.

Закрытые токеном эндпоинты:
- `GET /api/v1/seller/{seller_id}`
- `POST /api/v1/books/`
- `PUT /api/v1/books/{book_id}` — дополнительно проверяется, что `seller_id` книги совпадает с `id` авторизованного продавца, иначе `403 Forbidden`

## Установка и запуск

### Вариант 1: через Docker

1. Склонируйте репозиторий:
```bash
git clone <ссылка на репозиторий>
cd <папка проекта>
```

2. Проверьте/создайте `.env` файл со следующим содержимым:
```env
DB_USERNAME=postgres_user
DB_PASSWORD=postgres_pass
DB_HOST=127.0.0.1
DB_PORT=5445
DB_NAME=fastapi_project_db
SECRET_KEY=some-very-long-and-secure-secret-key-1234567890!
ALGORITHM=HS256
```

3. Запустите контейнеры:
```bash
docker-compose up --build
```

4. Приложение будет доступно по адресу: `http://localhost:8000`

5. Документация Swagger: `http://localhost:8000/docs`

### Вариант 2: локальный PostgreSQL (без Docker)

1. Убедитесь, что у вас установлен и запущен PostgreSQL.

2. Создайте две базы данных: одну для приложения (`fastapi_project_db`), вторую — для тестов.

3. В файле `.env` укажите параметры подключения к вашему локальному PostgreSQL:
```env
DB_USERNAME=postgres_user
DB_PASSWORD=postgres_pass
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=fastapi_project_db
SECRET_KEY=some-very-long-and-secure-secret-key-1234567890!
ALGORITHM=HS256
```

4. Установите зависимости:
```bash
python -m venv venv
source venv/bin/activate  # для Windows: venv\Scripts\activate
pip install -r requirements.txt
```

5. Примените миграции:
```bash
alembic upgrade head
```

6. Запустите приложение:
```bash
uvicorn app.main:app --reload
```

## Тестирование

Для запуска тестов используется отдельная тестовая база данных, конфигурация которой настраивается через `settings.database_test_url`.

```bash
pytest -v
```

Тесты покрывают все реализованные эндпоинты:
- Регистрация, получение списка, получение по id, обновление и удаление продавцов
- Создание, получение, обновление и удаление книг
- Проверка, что `password` никогда не возвращается в ответах API
- Получение JWT-токена, включая случаи неверного email и пароля
- Проверка доступа к защищённым эндпоинтам без токена (`401`)
- Проверка, что редактировать книгу может только её владелец (`403` при попытке изменить чужую книгу)
- Проверка каскадного удаления книг при удалении продавца
- Проверка кодов ответа при запросах по несуществующим `id` (`404`)
- Проверка валидации года издания книги (`422`)

## Примеры запросов

#### Регистрация продавца
```bash
POST /api/v1/seller/
Content-Type: application/json

{
  "first_name": "Ivan",
  "last_name": "Ivanov",
  "email": "ivan@test.com",
  "password": "123456"
}
```

#### Получение токена
```bash
POST /api/v1/token/
Content-Type: application/json

{
  "email": "ivan@test.com",
  "password": "123456"
}
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Запрос с авторизацией
```bash
GET /api/v1/seller/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Создание книги
```bash
POST /api/v1/books/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Clean Architecture",
  "author": "Robert Martin",
  "count_pages": 300,
  "year": 2025
}
```

#### Попытка изменить чужую книгу
```bash
PUT /api/v1/books/5
Authorization: Bearer <token продавца, который не является владельцем книги>
Content-Type: application/json

{
  "title": "Новое название",
  "author": "Someone",
  "pages": 200,
  "year": 2024,
  "id": 5,
  "seller_id": 2
}
```

Ответ: `403 Forbidden`

## Автор

Выполнено в рамках ШАД МТС.
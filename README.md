## XML Parser & AI Analyzer Service

### Что делает сервис?
Получает XML-файл с данными о продажах, обрабатывает его, сохраняет данные в базе и генерирует аналитический отчет с помощью LLM.

### Стек технологий
* asyncio
* FastAPI
* PostgreSQL
* Adminer
* Celery
* Flower
* Redis
* Docker
* OpenAI API
* Pytest

### Запуск сервиса

* В файле .env указать в переменной OPENAI_API_KEY API ключ от OpenAI API
* Запустить docker compose
```commandline
docker-compose up --build
```
* Запланировать задачу:
```
curl -d '<sales_data date="2024-01-01">
    <products>
        <product>
            <id>1</id>
            <name>Product A</name>
            <quantity>100</quantity>
            <price>1500.00</price>
            <category>Electronics</category>
        </product>
    </products>
</sales_data>' http://localhost:8001/schedule_task
```
В ответ вернется:
```
{"status":"Task scheduled","task_id":"983b2597-f74e-4019-be90-26f7a46ac25f"}
```
* Проверка статуса задачи:
```
curl http://localhost:8001/result/983b2597-f74e-4019-be90-26f7a46ac25f
```
### Мониторинг
* Для мониторинга за базой есть adminer:
```
http://localhost:8080/
```
Сервер: postgres

Имя пользователя: main_user

Пароль: Bht34@nnfES

База данных: some_db

* Для мониторинга за тасками есть Flower:
```
http://localhost:8002/
```

### Документация api

Доступна по ссылке:
```
http://localhost:8001/docs
```
Или:
```
http://127.0.0.1:8001/redoc
```

### Тесты

Тесты можно запустить в запущенном контейнере:
```
docker-compose exec web_app python -m pytest
```

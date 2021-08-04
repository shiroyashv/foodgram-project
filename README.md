# Foodgram
![example workflow](https://github.com/TheXtreme30/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Проект Foodgram позволяет пользователям публиковать рецепты, добавлять рецепты в избранное и список покупок, подписыватся на других пользователей и скачивать список продуктов.

### Технологии
- Python
- Django
- Docker
- postgresql
- nginx
- gunicorn

### Запуск проекта на сервере
## Для работы сервиса на сервере должны быть установлены [Docker](https://www.docker.com) и [docker-compose](https://docs.docker.com/compose/install/)
- Клонируйте репозиторий командой:
```
git clone https://github.com/TheXtreme30/foodgram-project-react.git
``` 
- Перейдите в каталог командой:
```
cd foodgram-project-react/backend/
``` 
- Выполните команду для запуска контейнера:
```
docker-compose up -d
``` 
- Выполните миграции:
```
docker-compose exec web python manage.py migrate --noinput
``` 
- Команда для сбора статики:
```
- docker-compose exec web python manage.py collectstatic --no-input
``` 
- Команда для создания суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
``` 

### Проект доступен по адрессу:
[Foodgram](http://84.201.155.11/)

### Администратор
- email: admin@gmail.com
- password: admin

### Автор
Сергей. Студент Яндекс.Практикум 

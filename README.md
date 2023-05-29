# FOODGRAM
## Yandex Practicum Python-Backend course Diploma
[![foodgram-app workflow](https://github.com/ratarov/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/ratarov/foodgram-project-react/actions/workflows/main.yml)
### Description
Web-service for sharing cooking recipes with its own API, frontend, PostgreSQL database in Docker containers with set-up CI_CD workflows. Features:
 - register users, follow other users - authors of recipes;
 - create recipes: use standard list of ingredients and add tags;
 - add recipes to favorites;
 - add recipes to carts and download list of ingredients with q-ty required for cooking;
### Tools:
![image](https://img.shields.io/badge/Python%203.9-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![image](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![image](https://img.shields.io/badge/Django%204.2-092E20?style=for-the-badge&logo=django&logoColor=green)
![image](https://img.shields.io/badge/django%20rest%203.14-ff1709?style=for-the-badge&logo=django&logoColor=white)
![image](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![image](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![image](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)
![image](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

### Local deploy via Docker
Clone GIT repository via SSH:
```
git clone git@github.com:ratarov/foodgram-project-react.git
```
Open directory with docker-compose file and start containers:
```
cd foodgram-project-react/infra/
```
Create .env file in infra directory using template: 
```
SECRET_KEY='put_django_secret_key_here'
DEBUG=False
ALLOWED_HOSTS='127.0.0.1, localhost, <server.IP-address.or.hostname>'
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
Start docker-compose
```
docker-compose up -d
```
Collect static, apply migrations, create superuser, import fixtures (if required)
```
docker-compose exec -it backend python manage.py collectstatic --no-input
docker-compose exec -it backend python manage.py migrate
docker-compose exec -it backend python manage.py createsuperuser
docker-compose exec -it backend python manage.py loaddata data/fixtures.json
```
### Endpoints
```
documentation: "http://127.0.0.1/api/docs/",
admin-panel: "http://127.0.0.1/admin/",
"users": "http://127.0.0.1/api/users/",
"ingredients": "http://127.0.0.1/api/ingredients/",
"tags": "http://127.0.0.1/api/tags/",
"recipes": "http://127.0.0.1/api/recipes/"
```

### Author
Bakend - Ruslan Atarov
Frontend - provided by Yandex.Practicum
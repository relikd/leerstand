
.PHONY: help
help:
	@echo "available commands:"
	@echo "  -  start-frontend : start frontend server"
	@echo "  -  start-backend  : start backend server"
	@echo "  -  push-frontend  : push changes to server"
	@echo "  -  push-backend   : push changes to server"

.PHONY: start-backend
start-backend:
	@echo Starting server ... http://127.0.0.1:8000/admin/
	@./backend/manage.py runserver

.PHONY: start-frontend
start-frontend:
	@echo Server started on:  http://127.0.0.1/
	@python -m http.server -b 0.0.0.0 80 -d ./frontend

.PHONY: push-backend
push-backend:
	rsync -av --delete backend/ piko:~/leerstand/ \
		--exclude=/data \
		--exclude=/static \
		--exclude=/db \
		--exclude=__pycache__ \
		--exclude=.DS_Store

.PHONY: push-frontend
push-frontend:
	rsync -av --delete frontend/ piko:/srv/http/leerstand/ \
		--exclude=/data \
		--exclude=/static \
		--exclude=.DS_Store

.PHONY: push
push: push-frontend push-backend

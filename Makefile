run:
	cd nba_dashboard; \
	export DASHBOARD_CONFIG=config.py; \
	export FLASK_APP=dashboard.py; \
	flask run

setup:
	cd nba_dashboard/static; \
	npm i webpack; \
	npm i babel-core babel-loader babel-preset-es2015 babel-preset-react; \
	npm i react react-dom; \
	npm i axios; \
	npm i react-table; \
	npm i react-router-dom; \
	npm run build

build:
	cd nba_dashboard/static; \
	npm run watch;

validate-api:
	export DASHBOARD_CONFIG=config.py; \
	export FLASK_APP=dashboard.py; \
	export FLASK_DEBUG=true; \
	python validate_api_response.py;

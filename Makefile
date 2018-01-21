run:
	cd nba_dashboard; \
	export DASHBOARD_CONFIG=config.py; \
	export FLASK_APP=dashboard.py; \
	flask run

build:
	cd nba_dashboard/static; \
	npm run watch;

validate-api:
	export DASHBOARD_CONFIG=config.py; \
	export FLASK_APP=dashboard.py; \
	export FLASK_DEBUG=true; \
	python validate_api_response.py;

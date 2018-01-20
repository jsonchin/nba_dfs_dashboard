run:
	cd nba_dashboard; \
	export DASHBOARD_CONFIG=config.py; \
	export FLASK_APP=dashboard.py; \
	export FLASK_DEBUG=true; \
	flask run

validate-api:
	export DASHBOARD_CONFIG=config.py; \
	export FLASK_APP=dashboard.py; \
	export FLASK_DEBUG=true; \
	python validate_api_response.py;

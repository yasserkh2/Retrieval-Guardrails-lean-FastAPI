.PHONY: run test fmt clean install

run:
	uvicorn app.main:app --reload --port 8000

test:
	pytest -v

fmt:
	black app/ tests/ || true
	isort app/ tests/ || true

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + || true
	find . -type f -name "*.pyc" -delete || true

install:
	pip install -r requirements.txt

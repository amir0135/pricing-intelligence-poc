run:
	uvicorn api.app:app --reload --port 8080

lint:
	ruff .

test:
	pytest tests/ -v

train:
	cd notebooks && python -c "import subprocess; subprocess.run(['jupyter', 'nbconvert', '--to', 'script', '--execute', '02_win_model.ipynb'])"

docker-build:
	docker build -t pricing-poc-api ./api

docker-run:
	docker run -p 8080:8080 pricing-poc-api

demo:
	@echo "🚀 Starting Pricing Intelligence Demo..."
	@echo "1. Training ML model..."
	@python -c "from agents.winrate_agent import WinRateAgent; WinRateAgent()"
	@echo "2. Starting API server..."
	uvicorn api.app:app --port 8080

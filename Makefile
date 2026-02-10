PACKAGE_NAME = dj_control_room
PYPI_REPO ?= pypi   # can be 'testpypi' or 'pypi'

.PHONY: help clean build publish test install

help:
	@echo "Makefile targets:"
	@echo "  make clean           		Remove build artifacts"
	@echo "  make build           		Build sdist and wheel (in ./dist)"
	@echo "  make install_requirements 	Install all dev dependencies"
	@echo "  make install         		Install dependencies and package in editable mode"
	@echo "  make uninstall       		Uninstall package"
	@echo "  make uninstall_all   		Uninstall all packages"
	@echo "  make test_install    		Check if package can be imported"
	@echo "  make test_docker           Run tests inside Docker dev container"
	@echo "  make test_local            Run tests inside local environment"
	@echo "  make test_coverage   		Run tests with coverage report"
	@echo "  make coverage_html   		Generate HTML coverage report"
	@echo "  make publish         		Publish package to PyPI"
	@echo "  make docs            		Build documentation"
	@echo "  make docs_serve      		Serve documentation locally"
	@echo "  make docs_push       		Deploy documentation to GitHub Pages"
	@echo "  make docker_up       		Start all Docker services (dev, Redis, cluster)"
	@echo "  make docker_down     		Stop all Docker services and clean volumes"
	@echo "  make docker_shell    		Open shell in dev container"

clean:
	rm -rf build dist *.egg-info

build: clean
	python -m build

install_requirements:
	python -m pip install -r requirements.txt

install: install_requirements
	python -m pip install -e .

uninstall:
	python -m pip uninstall -y $(PACKAGE_NAME) || true

uninstall_all:
	python -m pip uninstall -y $(PACKAGE_NAME) || true
	python -m pip uninstall -y -r requirements.txt || true
	@echo "All packages in requirements.txt uninstalled"
	@echo "Note that some dependent packages may still be installed"
	@echo "To uninstall all packages, run 'pip freeze | xargs pip uninstall -y'"
	@echo "Do this at your own risk. Use a python virtual environment always."

test_install: build
	python -m pip uninstall -y $(PACKAGE_NAME) || true
	python -m pip install -e .
	python -c "import dj_control_room; print('✅ Import success!')"

test_local:
	@echo "Running tests in local environment..."
	@python -m pytest tests/ -v
	@echo "✅ Tests completed"

test_docker:
	@echo "Starting Docker services..."
	docker compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 3
	@echo "Running tests in dev container..."
	@docker compose exec dev bash -c "cd /app && REDIS_HOST=redis python -m pytest tests/ -v"
	@echo "✅ Tests completed"

test_coverage:
	@echo "Running tests with coverage"
	@python -m pytest --cov=dj_control_room --cov-report=xml --cov-report=html --cov-report=term-missing tests/
	@echo "✅ Tests with coverage completed"

test_coverage_docker:
	@echo "Running tests with coverage in Docker"
	@docker compose up -d
	@echo "Waiting for containers to initialize..."
	@sleep 3
	@echo "Running all tests in dev container..."
	@docker compose exec dev bash -c "cd /app && REDIS_HOST=redis python -m pytest --cov=dj_control_room --cov-report=xml --cov-report=html --cov-report=term-missing tests/"
	@echo "✅ All tests completed"

coverage_html: test_coverage
	@echo "Coverage report generated in htmlcov/index.html"
	@echo "Open htmlcov/index.html in your browser to view the detailed report"

publish:
	twine upload --repository $(PYPI_REPO) dist/*

docs: install
	mkdocs build

docs_serve:
	mkdocs serve

docs_push: docs
	mkdocs gh-deploy --force

# Docker targets
docker_up:
	@echo "Starting all Docker services..."
	@docker compose up -d
	@echo "Waiting for containers to initialize..."
	@sleep 3
	@echo "✅ All services are running:"
	@echo "   Dev container: dj-control-room-dev-1"
	@echo ""
	@echo "Run 'make docker_shell' to open a shell in the dev container"

docker_down:
	@echo "Stopping all Docker services and cleaning volumes..."
	@docker compose down -v
	@echo "✅ All services stopped and volumes cleaned"

docker_shell:
	@echo "Opening shell in dev container..."
	@docker compose exec dev bash

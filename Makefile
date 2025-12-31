.PHONY: help install check run clean visualize

help:
	@echo "Yerevan Fireworks Safe Zones - Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make check      - Check installation"
	@echo "  make run        - Run analysis with default parameters"
	@echo "  make run-full   - Run analysis with obstacle export"
	@echo "  make visualize  - Open visualization in browser"
	@echo "  make notebook   - Launch Jupyter notebook"
	@echo "  make clean      - Remove generated data"
	@echo "  make help       - Show this help message"

install:
	@echo "Installing dependencies..."
	pip3 install -r requirements.txt

check:
	@echo "Checking setup..."
	python3 check_setup.py

run:
	@echo "Running analysis..."
	python3 -m src.main

run-full:
	@echo "Running analysis with obstacle export..."
	python3 -m src.main --save-obstacles

visualize:
	@echo "Opening visualization..."
	@command -v open >/dev/null 2>&1 && open notebooks/leaflet_map.html || \
	command -v xdg-open >/dev/null 2>&1 && xdg-open notebooks/leaflet_map.html || \
	echo "Please open notebooks/leaflet_map.html in your browser"

notebook:
	@echo "Launching Jupyter notebook..."
	jupyter notebook notebooks/visualize_safe_zones.ipynb

clean:
	@echo "Cleaning generated data..."
	rm -rf data/*.geojson data/*.csv
	@echo "Done"

.DEFAULT_GOAL := help

.PHONY: test clean build
.DEFAULT_GOAL = build

test:
	coverage run -m unittest
	coverage html

clean:
	rm -rf dist/
	rm -rf rucksack.egg-info
	rm -rf htmlcov/
	rm -rf test/__pycache__
	rm -rf rucksack/__pycache__
	rm .coverage
	
build:
	python -m build

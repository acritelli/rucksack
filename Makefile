.PHONY: test clean build
.DEFAULT_GOAL = build

test:
	coverage run -m unittest
	coverage html

clean:
	rm -rf dist/
	rm -rf rucksack.egg-info
	
build:
	python -m build

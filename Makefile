test:
	coverage run -m unittest
	coverage html

.PHONY: test

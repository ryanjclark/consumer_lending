install:
	pip install -r requirements.txt

lint:
	pylint --disable=R,C nlib csvcli

test:
	@cd tests; pytest test_*.py

# test:
# 	python -m pytest 

all:
	install lint test

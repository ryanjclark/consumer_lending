install:
	pip install -r requirements.txt

lint:
	pylint --disable=R,C

# test:
# 	python -m pytest 

all:
	install lint test
install.local:
	pip3 install . --user

install:
	poetry lock && poetry install --with dev

shell:
	poetry shell

format:
	autopep8 . && flake8 .
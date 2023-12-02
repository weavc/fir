install.local:
	pip3 install . --user

install:
	poetry lock && poetry install

shell:
	poetry shell

format.project:
	autopep8 .
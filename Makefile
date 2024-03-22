all: resources build

build:
	pyinstaller --noconsole --name "qdata" --icon=resources/favicons/favicon-dark.ico --add-data "resources/favicons/*:resources/favicons" --add-data "resources/images/*:resources/images" --add-data "resources/styles/*:resources/styles" --contents-directory "." "qdata/__main__.py"

resources:
	pyside6-rcc -o qdata/resources.py resources/resources.qrc

run:
	python -m qdata

lint:
	pylint qdata

test:
	pytest

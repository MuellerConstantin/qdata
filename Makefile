all: resources build

build:
	nuitka --plugin-enable=pyside6 --windows-icon-from-ico=./resources/favicons/favicon-dark.ico --include-data-dir=./resources=resources --disable-console --standalone qdata

resources:
	pyside6-rcc -o qdata/resources.py resources/resources.qrc

run:
	python -m qdata

lint:
	pylint qdata

test:
	pytest

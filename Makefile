all: bootstrap

bootstrap:
	[ -e bin/pip ] || virtualenv .
	./bin/pip install -r requirements.txt


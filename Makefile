bower: src/iot/bower.json
	cd src/iot && bower install

static:
	pipenv run python manage.py collectstatic --no-input -i bower
	pipenv run python manage.py collectstatic --no-input -i "[^(bower)]" --no-post-process

clean:
	rm -Rf static
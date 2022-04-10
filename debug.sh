docker run --rm -ti \
	-v `pwd`/configuration.yaml:/etc/opsdroid/configuration.yaml:ro \
	-v `pwd`/__init__.py:/skills/hasskbot/__init__.py:ro \
	--env-file secrets.env \
	--entrypoint sh \
	opsdroid/opsdroid:v0.25.0

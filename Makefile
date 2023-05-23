openapi-gen:
	docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate \
    -i /local/openapis/naas-openapi.json \
    -g python \
	-c /local/openapis/naas-openapi.config.yaml \
    -o /local/openapis/clients/python/

openapi-gen-help:
	docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli help generate

test_extra=-s
test:
	poetry run python -m pytest tests/ $(test_extra)

run:
	@echo "You should execute: poetry run naas-python"
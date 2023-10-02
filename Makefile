format:
	black .

autopep8:
	autopep8 --in-place --recursive TP1/

# clippy:
# 	flake8

.PHONY: format autopep8

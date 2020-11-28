FROM snicolet/poepy
WORKDIR /root
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry export --without-hashes -f requirements.txt --dev \
	| poetry run pip install -r /dev/stdin \
	&& poetry debug

COPY pool/ ./pool/
COPY loop.py ./
CMD ["python", "loop.py"]


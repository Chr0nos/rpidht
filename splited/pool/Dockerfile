FROM snicolet/poepy
WORKDIR /root
COPY ./poetry.lock ./pyproject.toml ./

#RUN poetry export --without-hashes -f requirements.txt --dev \
	#	| poetry run pip install -r /dev/stdin \
	#	&& poetry debug

RUN poetry install --no-root
COPY pool/ ./pool/
COPY main.py ./
CMD ["huey_consumer", "main.huey"]

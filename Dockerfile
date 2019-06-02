FROM gorialis/discord.py:3.7.3-alpine-pypi-minimal
RUN python -m pip install redis

WORKDIR /usr/src/app
COPY main.py .
COPY ffrrace.py .
COPY races.py .
COPY token.txt .

CMD ["python", "./main.py"]


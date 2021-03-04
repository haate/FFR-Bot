FROM gorialis/discord.py:3.8.6-alpine-pypi-minimal
RUN python -m pip install redis
RUN python -m pip install -U discord.py

WORKDIR /usr/src/app
COPY ffrbot ./ffrbot
COPY token.txt ./ffrbot/token.txt

CMD ["python", "-m", "ffrbot.main.py"]


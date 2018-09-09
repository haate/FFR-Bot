FROM gorialis/discord.py:3.6-alpine-minimal

WORKDIR /usr/src/app
COPY main.py .
COPY token.txt .

CMD ["python", "./main.py"]


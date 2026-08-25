FROM python:3.10
WORKDIR /app
COPY . /app/

# Install ffmpeg using apt
RUN apt update && apt install -y ffmpeg

RUN pip install -r requirements.txt

CMD ["python3", "bot.py"]

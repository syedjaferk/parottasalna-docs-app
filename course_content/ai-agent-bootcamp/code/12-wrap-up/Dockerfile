# Dockerfile - run the support bot in a locked-down container (an example, adapt as needed)
FROM python:3.12-slim

# Do not run as root inside the container
RUN useradd --create-home bot
WORKDIR /home/bot/app

COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r requirements.txt

COPY --chown=bot:bot . .
USER bot

# Secrets are NOT copied into the image. Pass them when you run it:  docker run --env-file .env ...
CMD ["python", "bot.py"]

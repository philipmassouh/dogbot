FROM python:3.12.1

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt ./
#TODO pin this version. pin everything in requirements aswe ll
RUN pip install numpy
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "src/bot.py"]

FROM python:3.12.1

WORKDIR /usr/src/app

COPY requirements.txt ./
#TODO pin this version. pin everything in requirements aswe ll
RUN pip install numpy
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "src/bot.py"]

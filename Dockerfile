FROM python:3.11-slim

# ติดตั้ง ffmpeg และ fonts ภาษาไทย/ภาษาอังกฤษสำหรับระบบ Linux
RUN apt-get update && apt-get install -y ffmpeg fonts-freefont-ttf fonts-thai-tlwg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

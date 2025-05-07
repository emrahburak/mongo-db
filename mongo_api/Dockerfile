# Temel imaj
FROM python:3.9-slim

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

ENV API_KEY ""

# Çalışma dizinini ayarla
WORKDIR /app

# Gerekli bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Flask uygulamasını çalıştır

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

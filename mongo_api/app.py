from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timezone
import os
import logging
from logging.handlers import RotatingFileHandler

# Loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler("app.log", maxBytes=5 * 1024 * 1024,
                            backupCount=3),
        logging.StreamHandler()
    ])
logger = logging.getLogger(__name__)

logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("flask").setLevel(logging.WARNING)

# Flask uygulamasını başlat
app = Flask(__name__)

# MongoDB bağlantısı
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)  # MongoDB adresinizi buraya yazın
db = client["transcription_db"]  # Veritabanı adı
collection = db["transcriptions"]  # Koleksiyon adı

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Önceden tanımlanmış API anahtarı
API_KEY = os.getenv("API_KEY")


@app.before_request
def check_api_key():
    if request.headers.get("X-API-Key") != API_KEY:
        logger.error({"error": "Geçersiz API Anahtarı"})
        return jsonify({"error": "Geçersiz API anahtarı"}), 403  # Forbidden


# Yeni transkripsiyon ekleme endpoint'i
@app.route("/transcriptions", methods=["POST"])
def add_transcription():
    try:
        data = request.json  # İstekten gelen JSON verisi
        data["created_at"] = datetime.now(timezone.utc)  #type: ignore
        result = collection.insert_one(data)  # Veriyi MongoDB'ye ekle
        logger.info({"success": {"message": str(result.inserted_id)}})
        return jsonify({"id": str(result.inserted_id)}), 201

    except Exception as error:
        return jsonify({"error": f"{error}"}), 404


# Tüm transkripsiyonları getirme endpoint'i
@app.route("/transcriptions", methods=["GET"])
def get_transcriptions():
    try:
        transcriptions = list(
            collection.find().limit(100))  # Tüm belgeleri getir
        transcriptions = [{
            **doc, "_id": str(doc["_id"])
        } for doc in transcriptions]

        logger.debug(
            {"success": {
                "message": "Transcriptions retrieved successfully"
            }})
        return jsonify({"succes": {"data": transcriptions}}), 200
    except Exception as error:
        logger.error({"error": f"An erorr occured {str(error)}"})
        return jsonify({"error": "An erorr occured"}), 500


# # Belirli bir transkripsiyonu getirme endpoint'i
# @app.route("/transcriptions/<transcription_id>", methods=["GET"])
# def get_transcription(transcription_id):
#     transcription = collection.find_one({"_id": ObjectId(transcription_id)
#                                          })  # Belgeyi bul
#     if transcription:
#         transcription["_id"] = str(
#             transcription["_id"])  # ObjectId'yi string'e çevir
#         logger.debug({"success": {"message": transcription}})
#         return jsonify(transcription), 200
#     else:
#         logger.debug({"error": "Transcription not found"})
#         return jsonify({"error": "Transcription not found"}), 404
#

@app.route("/transcriptions/count", methods=["GET"])
def get_transcriptions_count():
    try:
        count = collection.count_documents({})
        logger.info({
            "success": {
                "count": count,
                "message": "Transcriptions count retrieved successfully"
            }
        })
        return jsonify(count), 200
    except Exception as error:
        logger.error({
            "error": {
                "message": "An error occurred while retrieving count",
                "details": str(error)
            }
        })
        return jsonify({"error": "An error occurred"}), 500


@app.route("/transcriptions/last", methods=["GET"])
def get_last_transcription():
    try:
        # En son eklenen belgeyi çek
        last_document = collection.find_one(sort=[("_id", -1)])

        if not last_document:
            # Eğer koleksiyon boşsa, uygun bir yanıt döndür
            logger.info({
                "info": {
                    "message": "No transcriptions found in the collection"
                }
            })
            return jsonify({"message": "No transcriptions found"}), 404

        # ObjectId'yi string'e çevir
        last_document["_id"] = str(last_document["_id"])

        # Başarılı loglama
        logger.info({
            "success": {
                "data": last_document,
                "message": "Last transcription retrieved successfully"
            }
        })

        # Başarılı yanıt
        return jsonify({"success": {"data": last_document}}), 200

    except Exception as error:
        # Hata loglama
        logger.error({
            "error": {
                "message":
                "An error occurred while retrieving the last transcription",
                "details": str(error)
            }
        })
        # Hata yanıtı
        return jsonify({"error": "An unexpected error occurred"}), 500


# Uygulamayı çalıştır
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

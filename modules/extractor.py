import os

from dotenv import load_dotenv
from google import genai
from PIL import Image

from modules.schema import Charge, Item, Receipt

load_dotenv()  # baca API key dari file .env

MODEL_NAME = "gemini-3.1-flash-lite"   # ganti kalau namanya beda di akunmu

PROMPT = """Baca struk ini dan ekstrak datanya.
- items: setiap item dengan nama, jumlah (qty), harga satuan, dan total harga item.
- subtotal: jumlah semua item SEBELUM pajak/service/diskon.
- additional_charges: semua biaya tambahan (pajak, service charge, dll).
  Diskon harus ditulis sebagai angka NEGATIF.
- total: total akhir yang harus dibayar.
Semua angka dalam Rupiah, bilangan bulat, tanpa titik atau koma pemisah ribuan."""


def extract_receipt(image: Image.Image) -> Receipt:
    """Terima gambar nota, kembalikan data nota yang terstruktur."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY belum diisi. Cek file .env kamu.")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[image, PROMPT],
        config={
            "response_mime_type": "application/json",
            "response_schema": Receipt,
        },
    )
    if response.parsed is None:
        raise ValueError("AI tidak mengembalikan data yang bisa dibaca. Coba foto yang lebih jelas.")
    return response.parsed


def demo_receipt() -> Receipt:
    """Data contoh untuk uji coba tanpa memanggil AI."""
    return Receipt(
        items=[
            Item(name="Bintang Bremer", qty=1, unit_price=59000, total_price=59000),
            Item(name="Chicken H-H", qty=1, unit_price=190000, total_price=190000),
            Item(name="Ades", qty=1, unit_price=10000, total_price=10000),
        ],
        subtotal=259000,
        additional_charges=[
            Charge(name="Service", amount=9600),
            Charge(name="Tax", amount=52416),
            Charge(name="Discount", amount=-19000),
        ],
        total=302016,
    )
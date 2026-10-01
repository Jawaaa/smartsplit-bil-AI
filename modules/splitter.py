import math

from modules.schema import Item, Receipt


def distribute(amount: int, weights: dict[str, float]) -> dict[str, int]:
    """
    Bagi 'amount' ke beberapa orang sesuai bobot. Hasilnya bilangan bulat
    dan JUMLAHNYA PASTI SAMA dengan amount.
    """
    total_bobot = sum(weights.values())
    if total_bobot == 0:
        return {nama: 0 for nama in weights}

    # 1) hitung porsi mentah (masih ada pecahan)
    mentah = {n: amount * w / total_bobot for n, w in weights.items()}

    # 2) bulatkan ke bawah dulu
    hasil = {n: math.floor(v) for n, v in mentah.items()}

    # 3) sisa rupiah dibagikan satu-satu ke yang pecahannya paling besar
    sisa = amount - sum(hasil.values())
    urutan = sorted(mentah, key=lambda n: mentah[n] - hasil[n], reverse=True)
    for n in urutan[:sisa]:
        hasil[n] += 1

    return hasil


def expand_items(items: list[Item], per_unit: bool) -> list[Item]:
    """
    Kalau per_unit=True, item berjumlah 3 dipecah jadi 3 baris (1/3, 2/3, 3/3)
    supaya tiap porsi bisa dibayar orang yang berbeda.
    """
    if not per_unit:
        return list(items)

    hasil = []
    for item in items:
        if item.qty <= 1:
            hasil.append(item)
            continue
        bagian = distribute(item.total_price, {str(k): 1 for k in range(item.qty)})
        for k, harga in enumerate(bagian.values()):
            hasil.append(
                Item(name=f"{item.name} ({k + 1}/{item.qty})", qty=1,
                     unit_price=harga, total_price=harga)
            )
    return hasil


def calculate_split(
    items: list[Item],
    total: int,
    assignments: dict[int, list[str]],
    participants: list[str],
) -> dict:
    """
    items       : daftar item (hasil expand_items)
    total       : total bill di nota
    assignments : {nomor_item: [nama orang yang bayar]}
    participants: semua nama peserta

    Mengembalikan {nama: {"items": [(nama_item, harga)], "subtotal": ..,
                          "others": .., "total": ..}}
    """
    laporan = {p: {"items": [], "subtotal": 0} for p in participants}

    # A) bagi tiap item ke orang-orang yang memilihnya (rata)
    for idx, item in enumerate(items):
        pembayar = assignments.get(idx, [])
        if not pembayar:
            continue
        bagian = distribute(item.total_price, {p: 1 for p in pembayar})
        for orang, harga in bagian.items():
            laporan[orang]["items"].append((item.name, harga))
            laporan[orang]["subtotal"] += harga

    # B) bagi biaya tambahan (pajak+service-diskon) sesuai porsi belanja masing-masing
    jumlah_item = sum(i.total_price for i in items)
    biaya_tambahan = total - jumlah_item
    porsi = distribute(biaya_tambahan, {n: d["subtotal"] for n, d in laporan.items()})

    # C) total per orang
    for orang, data in laporan.items():
        data["others"] = porsi[orang]
        data["total"] = data["subtotal"] + data["others"]

    return laporan


# ---- Tes cepat: jalankan  python -m modules.splitter ----
if __name__ == "__main__":
    from modules.extractor import demo_receipt

    nota = demo_receipt()
    hasil = calculate_split(
        nota.items, nota.total,
        {0: ["Ana"], 1: ["Ali"], 2: ["Ali"]},
        ["Ana", "Ali"],
    )
    for nama, d in hasil.items():
        print(nama, d["total"])
    print("Jumlah semua:", sum(d["total"] for d in hasil.values()), "| Total nota:", nota.total)
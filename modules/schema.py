from pydantic import BaseModel

from modules.utils import rupiah


class Item(BaseModel):
    name: str
    qty: int
    unit_price: int      # harga satuan (Rupiah)
    total_price: int     # qty x harga satuan


class Charge(BaseModel):
    name: str            # contoh: "Pajak", "Service", "Diskon"
    amount: int          # diskon ditulis NEGATIF


class Receipt(BaseModel):
    items: list[Item]
    subtotal: int
    additional_charges: list[Charge]
    total: int


def validate_receipt(r: Receipt) -> list[str]:
    """Cek apakah angka di nota masuk akal. Mengembalikan daftar peringatan."""
    warnings = []

    for i in r.items:
        if i.qty * i.unit_price != i.total_price:
            warnings.append(
                f"Item '{i.name}': {i.qty} × {rupiah(i.unit_price)} tidak sama dengan {rupiah(i.total_price)}."
            )

    jumlah_item = sum(i.total_price for i in r.items)
    if jumlah_item != r.subtotal:
        warnings.append(
            f"Jumlah semua item ({rupiah(jumlah_item)}) tidak sama dengan subtotal ({rupiah(r.subtotal)})."
        )

    biaya = sum(c.amount for c in r.additional_charges)
    if r.subtotal + biaya != r.total:
        warnings.append(
            f"Subtotal + biaya tambahan ({rupiah(r.subtotal + biaya)}) tidak sama dengan total ({rupiah(r.total)})."
        )
    return warnings
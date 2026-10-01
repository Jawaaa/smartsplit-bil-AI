import io
import time

import pandas as pd
import streamlit as st
from PIL import Image, ImageOps

from modules.extractor import demo_receipt, extract_receipt
from modules.schema import Charge, Item, Receipt, validate_receipt
from modules.utils import go


def _to_int(value, default=0) -> int:
    """Ubah nilai dari tabel jadi angka bulat (kosong -> default)."""
    return int(value) if pd.notna(value) else default


def _build_receipt(items_df, charges_df, subtotal, total) -> Receipt:
    """Ubah isi tabel yang diedit user kembali jadi objek Receipt."""
    items = []
    for _, row in items_df.iterrows():
        name = str(row["name"]).strip() if pd.notna(row["name"]) else ""
        if not name:
            continue  # baris kosong diabaikan
        items.append(Item(
            name=name,
            qty=_to_int(row["qty"], 1),
            unit_price=_to_int(row["unit_price"]),
            total_price=_to_int(row["total_price"]),
        ))

    charges = []
    for _, row in charges_df.iterrows():
        name = str(row["name"]).strip() if pd.notna(row["name"]) else ""
        if not name:
            continue
        charges.append(Charge(name=name, amount=_to_int(row["amount"])))

    return Receipt(items=items, subtotal=int(subtotal),
                   additional_charges=charges, total=int(total))


def _set_receipt(receipt: Receipt, seconds: float) -> None:
    """Simpan nota baru ke 'papan tulis' dan reset pilihan lama."""
    st.session_state.receipt = receipt
    st.session_state.read_seconds = seconds
    st.session_state.read_count += 1
    for key in list(st.session_state.keys()):
        if key.startswith("assign_"):
            del st.session_state[key]


def _read_with_ai() -> None:
    image = Image.open(io.BytesIO(st.session_state.image_bytes))
    image = ImageOps.exif_transpose(image)  # betulkan foto HP yang miring
    with st.spinner("AI sedang membaca nota..."):
        start = time.time()
        try:
            receipt = extract_receipt(image)
        except Exception as e:
            st.error(f"Gagal membaca nota: {e}")
            return
    _set_receipt(receipt, time.time() - start)


def _save_and_next(receipt: Receipt) -> None:
    st.session_state.receipt = receipt
    go("assign")


def _render_editor() -> None:
    receipt = st.session_state.receipt
    if receipt is None:
        st.info("Hasil bacaan AI akan muncul di sini.")
        return

    v = st.session_state.read_count  # dipakai di key supaya tabel ter-reset saat baca ulang
    if st.session_state.read_seconds:
        st.caption(f"⏱️ Waktu baca AI: {st.session_state.read_seconds:.1f} detik")

    st.markdown("**🧾 Item belanja** (bisa diedit, tambah, atau hapus baris)")
    items_df = pd.DataFrame(
        [i.model_dump() for i in receipt.items],
        columns=["name", "qty", "unit_price", "total_price"],
    )
    items_df = st.data_editor(
        items_df, num_rows="dynamic", key=f"items_{v}",
        column_config={
            "name": st.column_config.TextColumn("Nama item"),
            "qty": st.column_config.NumberColumn("Jumlah", min_value=1, step=1),
            "unit_price": st.column_config.NumberColumn("Harga satuan", format="Rp %d"),
            "total_price": st.column_config.NumberColumn("Total harga item", format="Rp %d"),
        },
    )

    st.markdown("**➕ Biaya tambahan** (pajak, service, diskon ditulis negatif)")
    charges_df = pd.DataFrame(
        [c.model_dump() for c in receipt.additional_charges],
        columns=["name", "amount"],
    )
    charges_df = st.data_editor(
        charges_df, num_rows="dynamic", key=f"charges_{v}",
        column_config={
            "name": st.column_config.TextColumn("Nama biaya"),
            "amount": st.column_config.NumberColumn("Jumlah", format="Rp %d"),
        },
    )

    c1, c2 = st.columns(2)
    subtotal = c1.number_input("Subtotal (Rp)", value=int(receipt.subtotal), step=1000, key=f"sub_{v}")
    total = c2.number_input("Total bill (Rp)", value=int(receipt.total), step=1000, key=f"tot_{v}")

    current = _build_receipt(items_df, charges_df, subtotal, total)

    warnings = validate_receipt(current)
    for w in warnings:
        st.warning(w)
    if not warnings:
        st.success("Angka nota konsisten ✅")

    st.button(
        "Lanjut ➡️ Tambah peserta", type="primary",
        disabled=len(current.items) == 0,
        on_click=_save_and_next, args=(current,),
    )


def render() -> None:
    st.subheader("Langkah 1 · Upload nota & cek hasil bacaan AI")

    uploaded = st.file_uploader("Pilih foto nota (JPG / PNG)", type=["jpg", "jpeg", "png"])
    if uploaded is not None:
        st.session_state.image_bytes = uploaded.getvalue()

    col_img, col_data = st.columns([1, 2])

    with col_img:
        if st.session_state.image_bytes:
            st.image(st.session_state.image_bytes, caption="Nota kamu")
            if st.button("🔍 Baca nota dengan AI", type="primary"):
                _read_with_ai()
        else:
            st.info("Upload foto nota dulu.")
        if st.button("🧪 Pakai data contoh (tanpa AI)"):
            _set_receipt(demo_receipt(), 0.0)

    with col_data:
        _render_editor()
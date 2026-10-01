import pandas as pd
import streamlit as st

from modules.splitter import calculate_split, expand_items
from modules.utils import go, rupiah


def _reset() -> None:
    st.session_state.clear()


def _make_csv(laporan: dict) -> bytes:
    rows = []
    for orang, d in laporan.items():
        for nama_item, harga in d["items"]:
            rows.append({"Orang": orang, "Rincian": nama_item, "Jumlah": harga})
        rows.append({"Orang": orang, "Rincian": "Pajak/service/diskon", "Jumlah": d["others"]})
        rows.append({"Orang": orang, "Rincian": "TOTAL", "Jumlah": d["total"]})
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")


def _make_summary(laporan: dict, total: int) -> str:
    baris = ["🧾 Split Bill", ""]
    for orang, d in laporan.items():
        baris.append(f"{orang}: {rupiah(d['total'])}")
        for nama_item, harga in d["items"]:
            baris.append(f"  - {nama_item}: {rupiah(harga)}")
        baris.append(f"  - Pajak/service/diskon: {rupiah(d['others'])}")
        baris.append("")
    baris.append(f"Total bill: {rupiah(total)}")
    return "\n".join(baris)


def render() -> None:
    receipt = st.session_state.receipt
    per_unit = st.session_state.per_unit
    items = expand_items(receipt.items, per_unit)

    # ambil pilihan pembayar dari halaman 2
    assignments = {
        i: st.session_state.get(f"assign_{per_unit}_{i}", [])
        for i in range(len(items))
    }

    st.subheader("Langkah 3 · Laporan per orang")

    if any(not pembayar for pembayar in assignments.values()):
        st.error("Masih ada item yang belum dipilih pembayarnya.")
        st.button("⬅️ Kembali", on_click=go, args=("assign",))
        return

    laporan = calculate_split(items, receipt.total, assignments,
                              st.session_state.participants)

    for orang, d in laporan.items():
        with st.container(border=True):
            kiri, kanan = st.columns([3, 1])
            kiri.markdown(f"### 👤 {orang}")
            kanan.metric("Total", rupiah(d["total"]))
            if d["items"]:
                tabel = pd.DataFrame(
                    [(nama, rupiah(harga)) for nama, harga in d["items"]],
                    columns=["Item", "Harga"],
                )
                st.dataframe(tabel, hide_index=True)
            st.write(f"Subtotal item: **{rupiah(d['subtotal'])}**")
            st.write(f"Pajak / service / diskon (porsi): **{rupiah(d['others'])}**")

    # ---------- Cek: jumlah semua orang = total bill ----------
    jumlah = sum(d["total"] for d in laporan.values())
    if jumlah == receipt.total:
        st.success(f"✅ Jumlah semua orang {rupiah(jumlah)} = total bill {rupiah(receipt.total)}")
    else:
        st.error(f"❌ Jumlah semua orang {rupiah(jumlah)} ≠ total bill {rupiah(receipt.total)}")

    st.divider()
    st.markdown("**📤 Bagikan hasilnya**")
    st.download_button("⬇️ Unduh CSV", _make_csv(laporan),
                       file_name="split_bill.csv", mime="text/csv")
    st.caption("Ringkasan untuk grup chat (klik ikon salin di pojok kanan atas kotak):")
    st.code(_make_summary(laporan, receipt.total), language="text")

    n1, n2 = st.columns(2)
    n1.button("⬅️ Ubah pembagian", on_click=go, args=("assign",))
    n2.button("🔄 Mulai dari awal", on_click=_reset)
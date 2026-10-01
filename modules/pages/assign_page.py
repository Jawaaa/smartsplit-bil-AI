import streamlit as st

from modules.splitter import expand_items
from modules.utils import go, rupiah


def _remove_participant(name: str) -> None:
    st.session_state.participants.remove(name)
    # hapus juga nama itu dari pilihan-pilihan yang sudah dibuat
    for key in list(st.session_state.keys()):
        if key.startswith("assign_"):
            st.session_state[key] = [n for n in st.session_state[key] if n != name]


def _set_all(keys: list[str], names: list[str]) -> None:
    for key in keys:
        st.session_state[key] = list(names)


def render() -> None:
    receipt = st.session_state.receipt
    participants = st.session_state.participants

    st.subheader("Langkah 2 · Peserta & pembagian item")

    # ---------- A. Nama peserta ----------
    st.markdown("**👥 Siapa saja yang ikut patungan?**")
    with st.form("form_tambah", clear_on_submit=True):
        nama_baru = st.text_input("Nama peserta", placeholder="contoh: Ana")
        tambah = st.form_submit_button("➕ Tambah")
    if tambah:
        nama = nama_baru.strip()
        if nama and nama not in participants:
            participants.append(nama)
        elif nama in participants:
            st.warning(f"'{nama}' sudah ada.")

    for nama in list(participants):
        c1, c2 = st.columns([5, 1])
        c1.markdown(f"👤 **{nama}**")
        c2.button("🗑️", key=f"hapus_{nama}", on_click=_remove_participant, args=(nama,))

    if not participants:
        st.info("Tambahkan minimal satu nama untuk lanjut.")
        st.button("⬅️ Kembali", on_click=go, args=("upload",))
        return

    st.divider()

    # ---------- B. Pilih pembayar tiap item ----------
    st.markdown("**🍽️ Siapa yang bayar tiap item?** (boleh lebih dari satu orang = patungan)")
    per_unit = st.toggle(
        "Pisahkan item berjumlah lebih dari 1 per porsi",
        key="per_unit",
        help="Misal 2 minuman: porsi 1 dan 2 bisa dibayar orang yang berbeda.",
    )

    items = expand_items(receipt.items, per_unit)
    keys = [f"assign_{per_unit}_{i}" for i in range(len(items))]

    b1, b2 = st.columns(2)
    b1.button("👥 Semua orang bayar semua item (bagi rata)",
              on_click=_set_all, args=(keys, participants))
    b2.button("🧹 Kosongkan semua pilihan",
              on_click=_set_all, args=(keys, []))

    for item, key in zip(items, keys):
        kiri, kanan = st.columns([2, 3])
        kiri.markdown(f"**{item.name}**  \n{rupiah(item.total_price)}")
        kanan.multiselect(
            "Dibayar oleh", participants, key=key,
            label_visibility="collapsed", placeholder="Pilih siapa yang bayar",
        )

    # ---------- C. Cek sebelum lanjut ----------
    belum = [item.name for item, key in zip(items, keys)
             if not st.session_state.get(key)]
    if belum:
        st.warning("Item yang belum ada pembayarnya: " + ", ".join(belum))

    n1, n2 = st.columns(2)
    n1.button("⬅️ Kembali", on_click=go, args=("upload",))
    n2.button("Lihat laporan ➡️", type="primary",
              disabled=bool(belum), on_click=go, args=("report",))
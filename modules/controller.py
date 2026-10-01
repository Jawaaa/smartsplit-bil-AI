import streamlit as st

from modules.pages import assign_page, report_page, upload_page

STEPS = [
    ("upload", "1. Upload & hasil baca"),
    ("assign", "2. Peserta & pembagian"),
    ("report", "3. Laporan"),
]


def _init_state() -> None:
    """Siapkan 'papan tulis' (session_state) dengan nilai awal."""
    defaults = {
        "page": "upload",
        "receipt": None,
        "image_bytes": None,
        "read_count": 0,
        "read_seconds": 0.0,
        "participants": [],
        "per_unit": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _keep_widget_state() -> None:
    """
    Streamlit menghapus isi widget yang tidak tampil di halaman aktif.
    Trik ini menjaga pilihan pembayar & toggle agar tidak hilang saat pindah halaman.
    """
    for key in list(st.session_state.keys()):
        if key.startswith("assign_") or key == "per_unit":
            st.session_state[key] = st.session_state[key]


def _render_header() -> None:
    st.title("💸 SmartSplit Bill AI")
    st.caption("Upload nota, AI membacanya, lalu bagi tagihan dengan adil.")
    kolom = st.columns(len(STEPS))
    for col, (key, label) in zip(kolom, STEPS):
        if key == st.session_state.page:
            col.markdown(f"**➡️ {label}**")
        else:
            col.caption(label)
    st.divider()


def controller() -> None:
    _init_state()
    _keep_widget_state()
    _render_header()

    page = st.session_state.page
    if page != "upload" and st.session_state.receipt is None:
        page = "upload"  # belum ada nota, balik ke awal

    if page == "upload":
        upload_page.render()
    elif page == "assign":
        assign_page.render()
    elif page == "report":
        report_page.render()
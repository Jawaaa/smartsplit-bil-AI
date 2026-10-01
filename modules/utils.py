import streamlit as st


def rupiah(n) -> str:
    """59000 -> 'Rp 59.000'"""
    return "Rp " + f"{int(n):,}".replace(",", ".")


def go(page: str) -> None:
    """Pindah halaman. Dipakai sebagai on_click tombol."""
    st.session_state.page = page
import streamlit as st

from modules.controller import controller

st.set_page_config(page_title="SmartSplit Bill AI", page_icon="💸", layout="wide")


def main() -> None:
    controller()


if __name__ == "__main__":
    main()
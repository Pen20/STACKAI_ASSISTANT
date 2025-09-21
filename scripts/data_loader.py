"""Utility helpers for loading datasets with caching."""

from __future__ import annotations

import io
from typing import Optional

import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def load_default_dataframe(path: str) -> pd.DataFrame:
    """Read a CSV file from disk with caching enabled."""

    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_uploaded_dataframe(file_bytes: bytes) -> pd.DataFrame:
    """Read a CSV uploaded through Streamlit's file uploader."""

    return pd.read_csv(io.BytesIO(file_bytes))


def resolve_dataframe(
    uploaded_file: Optional["UploadedFile"],
    *,
    default_path: str,
) -> Optional[pd.DataFrame]:
    """Load a dataframe from either an uploaded file or a default path."""

    if uploaded_file is not None:
        return load_uploaded_dataframe(uploaded_file.getvalue())

    return load_default_dataframe(default_path)


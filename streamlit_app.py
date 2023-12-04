import streamlit as st
import pandas as pd
import hashlib


# set default to streamlit wide layout
st.set_page_config(layout="wide")

# Initialize session_state
if "to_hash" not in st.session_state:
    st.session_state.to_hash = []

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame([])

def hash_with_salt(value):
    hashed_value = hashlib.shake_256((str(value) + st.secrets["SALT"]).encode()).hexdigest(8)
    return hashed_value

def hash_df(df, columns):
    df_hashed = df.copy()
    for col in columns:
        df_hashed[col] = df[col].apply(lambda x: hash_with_salt(str(x).lower()))
    
    return df_hashed

def hash():
    df_hashed = hash_df(st.session_state.df, st.session_state.to_hash)
    csv_hashed = df_hashed.to_csv(index=False).encode('utf-8')

    df_comparison = df_hashed[st.session_state.to_hash]
    df_comparison = df_comparison.add_suffix('_hashed')
    df_comparison = df_comparison.merge(st.session_state.df[st.session_state.to_hash], left_index=True, right_index=True)
    csv_comparison = df_comparison.to_csv(index=False).encode('utf-8')

    st.session_state.hashed = csv_hashed
    st.session_state.comparison = csv_comparison


st.title("Anonymize data")
st.write("Anonymize your data using the SHAKE_256 hashing algorithm.")
st.write("Select which columns you wish to hash and then click the 'Hash' button.")
st.write("Two files can be downloaded. A file where the selected columns are replaced by their hashed values and a csv to compare the two.")
st.write("All fully empty rows will be deleted from the dataset and won't be hashed (they were empty anyways).")

df_data = st.file_uploader("Upload data", type={"csv", "txt"})
if df_data is not None:
    df = pd.read_csv(df_data)
    df.dropna(how='all', inplace=True) # Deletes all rows where all columns are empty
    st.session_state.df = df

if "df" in st.session_state and st.session_state.df.shape[0] > 1:
    st.session_state.to_hash = st.multiselect(
        "Choose which columns to hash.",
        st.session_state.df.columns)
    st.dataframe(st.session_state.df)

    st.button("Hash", on_click=hash)

if "hashed" in st.session_state and "comparison" in st.session_state:
    st.write("Hashing done. Click the buttons below to download your hashed data and it's comparison.")
    st.download_button(
        "Download hashed data",
        st.session_state.hashed,
        "input_hashed.csv",
        "text/csv",
        key='download-hashed'
    )

    st.download_button(
        "Download comparison data",
        st.session_state.comparison,
        "comparison.csv",
        "text/csv",
        key='download-comparison'
    )
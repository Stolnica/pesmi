import streamlit as st
from PIL import Image
import docx
import os
from zipfile import ZipFile
from streamlit_option_menu import option_menu
import fitz  # PyMuPDF za delo s PDF datotekami

# --- Uporaba CSS za barvo gumbov ---
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #4CAF50 !important;  /* Svetlo zelena */
        color: white !important;
    }
    div.stButton > button:hover {
        background-color: #45a049 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Določanje izbir ---
izbor1 = "Karizma note"

# Nastavimo vrstni red menija in ikon
mozni_izbori = [izbor1]
ikone = ['music-note-list']


# Funkcija za branje besedila iz Word dokumenta ali txt datoteke
def preberi_opombe(datoteka):
    if not os.path.exists(datoteka):
        return None

    if datoteka.endswith('.docx'):
        doc = docx.Document(datoteka)
        odstavki = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
        return odstavki
    elif datoteka.endswith('.txt'):
        with open(datoteka, 'r', encoding='utf-8') as f:
            vrstice = [line.strip() for line in f.readlines() if line.strip()]
        return vrstice
    return []


# Funkcija za pretvorbo PDF datoteke v slike
def pdf_v_slike(pdf_pot, izhodna_mapa="slike_pdf", resolucija=3):
    if not os.path.exists(pdf_pot):
        return []

    if not os.path.exists(izhodna_mapa):
        os.makedirs(izhodna_mapa)

    slike_poti = []
    pdf_dokument = fitz.open(pdf_pot)

    for stran_num, stran in enumerate(pdf_dokument):
        matrika = fitz.Matrix(resolucija, resolucija)
        pix = stran.get_pixmap(matrix=matrika)
        slika_pot = os.path.join(izhodna_mapa, f"stran_{stran_num + 1}.png")
        pix.save(slika_pot)
        slike_poti.append(slika_pot)

    return slike_poti


# Funkcija za iskanje PDF datotek v mapi na podlagi ključnih besed
def poisci_pdf_datoteke(kljucne_besede, mapa="./"):  #mapa="E:\\Karizma note"):
    if not os.path.exists(mapa):
        return []

    pdf_datoteke = []
    for datoteka in os.listdir(mapa):
        if datoteka.lower().endswith('.pdf'):
            for beseda in kljucne_besede:
                if beseda.lower() in datoteka.lower():
                    pdf_datoteke.append(os.path.join(mapa, datoteka))
                    break
    return pdf_datoteke


# CSS za glavno vsebino
st.markdown("""
<style>
.main-content {
    margin-left: 0;
    padding: 20px;
}
.sidebar-content {
    padding: 10px;
}
img {
    max-width: 100%;
    height: auto;
}
.green-button {
    background-color: #4CAF50 !important; /* Svetlo zelena barva */
    color: white !important;
    padding: 10px 24px !important;
    border: none !important;
    border-radius: 4px !important;
    text-align: center !important;
    text-decoration: none !important;
    display: inline-block !important;
    font-size: 16px !important;
    margin: 4px 2px !important;
    cursor: pointer !important;
}
.green-button:hover {
    background-color: #45a049 !important; /* Temnejša zelena ob prehodu miške */
}
/* Stil za Karizma note ozadje */
div[data-testid="stSidebar"] div:has(> div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stMarkdownContainer"] > p) {
    background-color: #e8f5e9; /* Svetlo zelena barva ozadja */
    padding: 10px;
    border-radius: 5px;
}
/* Stil za gumbe */
div[data-testid="stSidebar"] div:has(> .stButton > button) {
    background-color: #e8f5e9; /* Svetlo zelena barva ozadja */
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
}
/* Stil za vnosna polja - nova koda */
.song-input-container {
    margin-top: 20px;
    background-color: #e8f5e9;
    padding: 10px;
    border-radius: 5px;
}
.song-input {
    margin-bottom: 5px !important;
}
.song-input input {
    height: 30px !important;
    padding: 5px 10px !important;
}
</style>
""", unsafe_allow_html=True)

# --- Glavni meni ---
with st.sidebar:
    choose = option_menu("Stolnica Maribor", mozni_izbori,
                         icons=ikone,
                         menu_icon="list", default_index=0)

    # Gumb "Prikaži note"
    if st.button("Prikaži note iz naloženega seznama", key="prikazi_note", type="primary"):
        st.session_state.show_notes = True
        st.session_state.show_all_notes = False  # Počisti seznam vseh not
        st.session_state.pdf_files_to_display = []  # Počisti prikazane pdf datoteke
        st.session_state.show_input_notes = False  # počisti note iz vnosa

    # Gumb "Seznam vseh not"
    if st.button("Prikaži seznam vseh not", key="seznam_vseh_not", type="primary"):
        st.session_state.show_all_notes = True
        st.session_state.show_notes = False  # počisti note iz seznama
        st.session_state.pdf_files_to_display = []  # počisti prikazane pdf datoteke
        st.session_state.show_input_notes = False  # počisti note iz vnosa

# Nalaganje datoteke
uploaded_file = st.sidebar.file_uploader("Naloži svoj seznam not note.docx", type=["docx"])

# Vnos naslovov pesmi - premaknjeno na dno
with st.sidebar:
    st.markdown("""
    <div class="song-input-container">
        <div style="margin-bottom: 10px;">Vnesi naslove pesmi za prikaz:</div>
    """, unsafe_allow_html=True)

    # Ustvarimo stolpce za boljši razpored vnosnih polj
    cols = st.columns(2)
    vneseni_naslovi = []
    for i in range(10):
        with cols[i % 2]:  # Razporedimo v dve stolpca
            vneseni_naslovi.append(st.text_input(
                f"Pesem {i + 1}",
                key=f"naslov_{i}",
                label_visibility="collapsed"
            ))

    st.markdown("</div>", unsafe_allow_html=True)

    # Gumb "Prikaži note" za vnesene naslove
    if st.button("Prikaži zgoraj vnešene note", key="prikazi_vnesene", type="primary"):
        # Preverimo, da upoštevamo samo ne-prazne naslove
        kljucne_besede = [naslov for naslov in vneseni_naslovi if naslov.strip()]
        if kljucne_besede:
            st.session_state.show_input_notes = True
            st.session_state.show_notes = False
            st.session_state.show_all_notes = False
            st.session_state.pdf_files_to_display = []
        else:
            st.warning("Prosimo, vnesite vsaj en naslov pesmi.")

# prikaz not iz vnesenih naslovov
if 'show_input_notes' in st.session_state and st.session_state.show_input_notes:
    kljucne_besede = [naslov for naslov in vneseni_naslovi if naslov.strip()]
    if kljucne_besede:
        pdf_datoteke = poisci_pdf_datoteke(kljucne_besede)
        pdf_datoteke_urejene = []
        for beseda in kljucne_besede:
            for datoteka in pdf_datoteke:
                if beseda.lower() in os.path.basename(datoteka).lower():
                    pdf_datoteke_urejene.append(datoteka)
        st.session_state.pdf_files_to_display = pdf_datoteke_urejene

# Avtomatsko prikazovanje ob nalaganju strani
if 'show_notes' not in st.session_state:
    st.session_state.show_notes = True
    st.session_state.show_all_notes = False
    st.session_state.show_input_notes = False

# Obdelava prikaza dokumentov (tako za avtomatski prikaz kot za ročni klik)
if st.session_state.show_notes:
    note_path = "./note.docx"
    if os.path.exists(note_path):
        # Preberemo vrstice iz note.docx
        kljucne_besede = preberi_opombe(note_path)

        if kljucne_besede:
            with st.sidebar.expander("Ključne besede iz note.docx"):
                for beseda in kljucne_besede:
                    st.write(f"- {beseda}")

            # Poiščemo ustrezne PDF datoteke
            pdf_datoteke = poisci_pdf_datoteke(kljucne_besede)

            # Urejeno po vrstnem redu ključnih besed
            pdf_datoteke_urejene = []
            for beseda in kljucne_besede:
                for datoteka in pdf_datoteke:
                    if beseda.lower() in os.path.basename(datoteka).lower():
                        pdf_datoteke_urejene.append(datoteka)

            if pdf_datoteke_urejene:
                with st.sidebar.expander("Najdene PDF datoteke"):
                    for pdf_datoteka in pdf_datoteke_urejene:
                        st.write(f"- {os.path.basename(pdf_datoteka)}")

                # Shranimo PDF-je v session state za prikaz v glavnem oknu
                st.session_state.pdf_files_to_display = pdf_datoteke_urejene
            else:
                st.sidebar.warning("Ni bilo mogoče najti PDF datotek, ki ustrezajo ključnim besedam.")
        else:
            st.sidebar.warning("Datoteka note.docx ne vsebuje nobenih ključnih besed.")
    else:
        st.sidebar.warning("Datoteka note.docx ne obstaja v trenutnem direktoriju.")

# Glavna vsebina
if choose == "Karizma note":
    if uploaded_file is not None:
        # Shranimo naloženo datoteko
        temp_file_path = os.path.join("temp", uploaded_file.name)
        os.makedirs("temp", exist_ok=True)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.sidebar.success(f"Datoteka {uploaded_file.name} uspešno naložena!")

        if st.sidebar.button("PRIKAŽI note iz tvojega seznama", key="prikazi_naloženo", type="primary"):
            # Preberemo vrstice iz datoteke
            kljucne_besede = preberi_opombe(temp_file_path)

            if kljucne_besede:
                with st.sidebar.expander("Ključne besede iz datoteke"):
                    for beseda in kljucne_besede:
                        st.write(f"- {beseda}")

                # Poiščemo ustrezne PDF datoteke
                pdf_datoteke = poisci_pdf_datoteke(kljucne_besede)

                # Urejeno po vrstnem redu ključnih besed
                pdf_datoteke_urejene = []
                for beseda in kljucne_besede:
                    for datoteka in pdf_datoteke:
                        if beseda.lower() in os.path.basename(datoteka).lower():
                            pdf_datoteke_urejene.append(datoteka)

                if pdf_datoteke_urejene:
                    with st.sidebar.expander("Najdene PDF datoteke"):
                        for pdf_datoteka in pdf_datoteke_urejene:
                            st.write(f"- {os.path.basename(pdf_datoteka)}")

                    # Shranimo PDF-je v session state za prikaz v glavnem oknu
                    st.session_state.pdf_files_to_display = pdf_datoteke_urejene
                else:
                    st.sidebar.warning("Ni bilo mogoče najti PDF datotek, ki ustrezajo ključnim besedam.")
            else:
                st.sidebar.warning("Datoteka opomb ne vsebuje nobenih ključnih besed.")

# Prikaz PDF datotek v glavnem oknu
if 'pdf_files_to_display' in st.session_state and st.session_state.pdf_files_to_display:
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    for pdf_datoteka in st.session_state.pdf_files_to_display:
        slike = pdf_v_slike(pdf_datoteka, resolucija=4)
        for slika_pot in slike:
            st.image(slika_pot, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Prikaz seznama vseh not v glavnem oknu
if 'show_all_notes' in st.session_state and st.session_state.show_all_notes:
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.header("Seznam vseh not")
    for datoteka in os.listdir("./"):
        if datoteka.lower().endswith('.pdf'):
            st.write(datoteka)
    st.markdown('</div>', unsafe_allow_html=True)
import streamlit as st
from PIL import Image
import docx
import os
from zipfile import ZipFile
from streamlit_option_menu import option_menu
import fitz  # PyMuPDF za delo s PDF datotekami

# --- Določanje izbir ---
izbor1 = "Naloži seznam not"

# Nastavimo vrstni red menija in ikon
mozni_izbori = [izbor1]
ikone = ['upload']


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
def poisci_pdf_datoteke(kljucne_besede, mapa="./"):      # mapa="E:\\Karizma note"):
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
.green-button:hover {
    background-color: #45a049 !important;
}
</style>
""", unsafe_allow_html=True)

# Naložimo sidebar sliko
#sidebarimage = Image.open(r'./cerkev.jpg')

# --- Glavni meni ---
with st.sidebar:
    #st.image(sidebarimage, width=290)
    choose = option_menu("Stolnica Maribor", mozni_izbori,
                         icons=ikone,
                         menu_icon="list", default_index=0)

    # Gumb "Prikaži note"
    if st.button("Prikaži note"):
        note_path = "./note.docx"
        if os.path.exists(note_path):
            # Preberemo vrstice iz note.docx
            kljucne_besede = preberi_opombe(note_path)

            if kljucne_besede:
                with st.expander("Ključne besede iz note.docx"):
                    for beseda in kljucne_besede:
                        st.write(f"- {beseda}")

                # Poiščemo ustrezne PDF datoteke
                pdf_datoteke = poisci_pdf_datoteke(kljucne_besede)

                if pdf_datoteke:
                    with st.expander("Najdene PDF datoteke"):
                        for pdf_datoteka in pdf_datoteke:
                            st.write(f"- {os.path.basename(pdf_datoteka)}")

                    # Shranimo PDF-je v session state za prikaz v glavnem oknu
                    st.session_state.pdf_files_to_display = pdf_datoteke
                else:
                    st.warning("Ni bilo mogoče najti PDF datotek, ki ustrezajo ključnim besedam.")
            else:
                st.warning("Datoteka note.docx ne vsebuje nobenih ključnih besed.")
        else:
            st.warning("Datoteka note.docx ne obstaja v trenutnem direktoriju.")

# Glavna vsebina
if choose == "Naloži seznam not":
    # Nalaganje datoteke
    uploaded_file = st.sidebar.file_uploader("Naloži datoteko opomb (.txt ali .docx)", type=["txt", "docx"])

    if uploaded_file is not None:
        # Shranimo naloženo datoteko
        temp_file_path = os.path.join("temp", uploaded_file.name)
        os.makedirs("temp", exist_ok=True)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.sidebar.success(f"Datoteka {uploaded_file.name} uspešno naložena!")

        if st.sidebar.button("PRIKAŽI"):
            # Preberemo vrstice iz datoteke
            kljucne_besede = preberi_opombe(temp_file_path)

            if kljucne_besede:
                with st.sidebar.expander("Ključne besede iz datoteke"):
                    for beseda in kljucne_besede:
                        st.write(f"- {beseda}")

                # Poiščemo ustrezne PDF datoteke
                pdf_datoteke = poisci_pdf_datoteke(kljucne_besede)

                if pdf_datoteke:
                    with st.sidebar.expander("Najdene PDF datoteke"):
                        for pdf_datoteka in pdf_datoteke:
                            st.write(f"- {os.path.basename(pdf_datoteka)}")

                    # Shranimo PDF-je v session state za prikaz v glavnem oknu
                    st.session_state.pdf_files_to_display = pdf_datoteke
                else:
                    st.sidebar.warning("Ni bilo mogoče najti PDF datotek, ki ustrezajo ključnim besedam.")
            else:
                st.sidebar.warning("Datoteka opomb ne vsebuje nobenih ključnih besed.")

# Prikaz PDF datotek v glavnem oknu
if 'pdf_files_to_display' in st.session_state:
    for pdf_datoteka in st.session_state.pdf_files_to_display:
        slike = pdf_v_slike(pdf_datoteka, resolucija=4)
        for slika_pot in slike:
            st.image(slika_pot, use_container_width=True)
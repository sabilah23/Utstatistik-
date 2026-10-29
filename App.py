import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Pengaturan halaman utama dengan mode wide dan tema dasar cerah/gelap adaptif
st.set_page_config(
    page_title="Statistika Dashboard Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kustomisasi Gaya Antarmuka lewat CSS (Memperindah font, card, dan warna header)
st.markdown("""
    <style>
    .main-title {
        font-size: 40px;
        font-weight: 800;
        color: #1E3A8A;
        text-align: left;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 16px;
        color: #4B5563;
        margin-bottom: 30px;
    }
    .stAlert {
        border-radius: 10px;
    }
    .css-1r6slb0 { /* Memberikan padding halus pada container */
        padding: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Header Aplikasi
st.markdown('<p class="main-title">📊 Analytics Studio: Statistika Deskriptif</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Aplikasi pengolahan data otomatis untuk Ujian Tengah Semester (UTS) — Program Studi Matematika S-1.</p>', unsafe_allow_html=True)

# =========================================================================
# 1. SIDEBAR PANEL CONTROL (Unggah & Pengaturan)
# =========================================================================
with st.sidebar:
    st.markdown("### 📁 Manajemen Data")
    uploaded_file = st.file_uploader("Unggah File Excel (.xlsx, .xls) atau CSV", type=["xlsx", "xls", "csv"])
    st.markdown("---")

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        # Mengelompokkan tipe data kolom secara otomatis
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=[object, 'category']).columns.tolist()

        # Input kontrol dinamis yang hanya muncul setelah file sukses di-upload
        with st.sidebar:
            if len(numeric_cols) > 0:
                st.markdown("### 🎯 Konfigurasi Analisis")
                selected_vars = st.multiselect("Pilih Variabel Numerik:", numeric_cols, default=numeric_cols[:1])
                
                stat_options = ["Jumlah Data (N)", "Minimum", "Maksimum", "Mean", "Median", "Modus", "Varians", "Standar Deviasi", "Kuartil 1 (Q1)", "Kuartil 3 (Q3)"]
                selected_stats = st.multiselect("Pilih Ukuran Statistik:", stat_options, default=stat_options[:6])
                
                st.markdown("---")
                st.markdown("### 🎨 Estetika Visual")
                palette_choice = st.selectbox("Tema Warna Grafik:", ["deep", "muted", "pastel", "coolwarm", "viridis", "magma"])
                sns.set_palette(palette_choice)
                plt.style.use('ggplot') # Memakai gaya background grafik yang bersih

        # =========================================================================
        # INTERFACE UTAMA BERBASIS STRUKTUR TAB (Lebih Rapi & Ringkas)
        # =========================================================================
        tab_data, tab_stats, tab_charts = st.tabs(["📋 Ringkasan & Pembersihan Data", "🔢 Kalkulator Statistik", "🎨 Galeri Visualisasi"])

        # --- TAB 1: RINGKASAN & PRATONTON DATA ---
        with tab_data:
            st.markdown("### 🔍 Eksplorasi Struktur Dataset")
            
            # Statistik kilat berkas yang diunggah dalam bentuk Metrik Card
            m1, m2, m3 = st.columns(3)
            m1.metric(label="Total Baris", value=df.shape[0])
            m2.metric(label="Total Kolom", value=df.shape[1])
            m3.metric(label="Variabel Numerik Terdeteksi", value=len(numeric_cols))
            
            # Penanganan Missing Values Terintegrasi Ekspander
            missing_count = df.isnull().sum().sum()
            if missing_count > 0:
                with st.expander(f"⚠️ Deteksi Data Kosong: Ditemukan {missing_count} sel kosong"):
                    clean_option = st.radio("Metode Aksi Cepat:", ["Biarkan", "Hapus Baris yang Kosong", "Substitusi dengan Rata-Rata (Mean)"])
                    if clean_option == "Hapus Baris yang Kosong":
                        df = df.dropna()
                        st.success("Selesai! Baris kosong berhasil dibersihkan.")
                    elif clean_option == "Substitusi dengan Rata-Rata (Mean)":
                        for col in df.select_dtypes(include=[np.number]).columns:
                            df[col] = df[col].fillna(df[col].mean())
                        st.success("Selesai! Nilai kosong diganti dengan nilai rata-rata.")

            st.write("#### 📄 Tampilan 10 Baris Pertama Data")
            st.dataframe(df.head(10), use_container_width=True)

        # --- TAB 2: HITUNG UKURAN STATISTIK ---
        with tab_stats:
            if not selected_vars or not selected_stats:
                st.warning("⚠️ Harap pilih minimal 1 variabel dan 1 ukuran statistik pada panel menu kiri.")
            else:
                st.markdown("### 🔢 Parameter Deskriptif Otomatis")
                
                # Proses kalkulasi matrik data
                results = {}
                for var in selected_vars:
                    var_data = df[var].dropna()
                    metrics = {}
                    if "Jumlah Data (N)" in selected_stats: metrics["Jumlah Data (N)"] = int(len(var_data))
                    if "Minimum" in selected_stats: metrics["Minimum"] = var_data.min()
                    if "Maksimum" in selected_stats: metrics["Maksimum"] = var_data.max()
                    if "Mean" in selected_stats: metrics["Mean"] = round(var_data.mean(), 3)
                    if "Median" in selected_stats: metrics["Median"] = var_data.median()
                    if "Modus" in selected_stats: metrics["Modus"] = var_data.mode().iloc[0] if not var_data.mode().empty else np.nan
                    if "Varians" in selected_stats: metrics["Varians"] = round(var_data.var(), 3)
                    if "Standar Deviasi" in selected_stats: metrics["Standar Deviasi"] = round(var_data.std(), 3)
                    if "Kuartil 1 (Q1)" in selected_stats: metrics["Kuartil 1 (Q1)"] = var_data.quantile(0.25)
                    if "Kuartil 3 (Q3)" in selected_stats: metrics["Kuartil 3 (Q3)"] = var_data.quantile(0.75)
                    results[var] = metrics

                summary_df = pd.DataFrame(results)
                
                # Menampilkan tabel hasil kustomisasi bergaya Dashboard Pro
                st.dataframe(summary_df.style.highlight_max(axis=1, color='#D1FAE5').highlight_min(axis=1, color='#FEE2E2'), use_container_width=True)
                
                # Desain Tombol Unduh yang Elegan
                csv_data = summary_df.to_csv().encode('utf-8')
                st.download_button(
                    label="📥 Ekspor Ringkasan Tabel ke format CSV",
                    data=csv_data,
                    file_name="summary_statistika.csv",
                    mime="text/csv",
                    help="Klik untuk langsung mengunduh file tabel statistik ke komputer Anda."
                )

        # --- TAB 3: GALERI VISUALISASI INTERAKTIF ---
        with tab_charts:
            if not selected_vars:
                st.warning("⚠️ Pilih variabel numerik terlebih dahulu untuk memunculkan visualisasi grafik.")
            else:
                st.markdown("### 🎨 Ruang Eksplorasi Grafis")
                
                # Pembagian sub-layout untuk memisahkan jenis visualisasi
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.markdown("<div style='background-color:#F9FAFB; padding:15px; border-radius:10px;'><b>1. Sebaran Distribusi (Histogram)</b></div>", unsafe_allow_html=True)
                    bins_slider = st.slider("Atur Kerapatan Batang (Bin Count):", 5, 40, 15, key="bins_slider")
                    
                    fig, ax = plt.subplots(figsize=(6, 3.5))
                    for var in selected_vars:
                        sns.histplot(df[var], kde=True, bins=bins_slider, label=var, alpha=0.5, ax=ax)
                    ax.set_title("Grafik Histogram & Densitas Frekuensi", fontsize=10, weight='bold')
                    ax.legend()
                    st.pyplot(fig)
                    
                    st.markdown("<br><div style='background-color:#F9FAFB; padding:15px; border-radius:10px;'><b>2. Deteksi Nilai Ekstrem (Boxplot)</b></div>", unsafe_allow_html=True)
                    fig, ax = plt.subplots(figsize=(6, 3.5))
                    sns.boxplot(data=df[selected_vars], ax=ax, width=0.5)
                    ax.set_title("Deteksi Outlier Menggunakan Kotak Kuartil Boxplot", fontsize=10, weight='bold')
                    st.pyplot(fig)

                with col_right:
                    st.markdown("<div style='background-color:#F9FAFB; padding:15px; border-radius:10px;'><b>3. Analisis Komposisi Variabel Kategorik</b></div>", unsafe_allow_html=True)
                    if len(categorical_cols) == 0:
                        st.info("ℹ️ Tidak ditemukan kolom teks/kategorik pada berkas untuk membuat Diagram Lingkaran.")
                    else:
                        selected_cat = st.selectbox("Pilih Kolom Label:", categorical_cols)
                        cat_data = df[selected_cat].value_counts()
                        
                        # Menampilkan grafik pie yang bersih
                        fig, ax = plt.subplots(figsize=(6, 3.5))
                        ax.pie(cat_data.values, labels=cat_data.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette(palette_choice, len(cat_data)))
                        ax.axis('equal')

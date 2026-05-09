import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import requests

# -------------------------------
# 1. ΚΑΘΑΡΟ ΛΕΥΚΟ ΦΟΝΤΟ ΓΙΑ ΟΛΗ ΤΗΝ ΕΦΑΡΜΟΓΗ
# -------------------------------
st.set_page_config(page_title="Εκπαιδευτικά Δεδομένα - Αργολίδα & Μεσσηνία", layout="wide")

# CSS για λευκό φόντο σε ολόκληρο το app
st.markdown("""
    <style>
        .stApp {
            background-color: gray;
        }
        /* Προαιρετικά: λευκό και για sidebar */
        .css-1d391kg, .css-163ttbj, .eczjsme11 {
            background-color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Interactive Dashboard: Μαθητές & Εκπαιδευτικοί ΠΔΕ Πελοποννήσου")
st.markdown("")

# -------------------------------
# 2. ΒΟΗΘΗΤΙΚΗ ΣΥΝΑΡΤΗΣΗ ΓΙΑ ΛΕΥΚΟ ΦΟΝΤΟ ΣΕ ΟΛΑ ΤΑ PLOTLY ΔΙΑΓΡΑΜΜΑΤΑ
# -------------------------------
def white_theme(fig):
    """Εφαρμόζει λευκό φόντο σε όλο το γράφημα και στους άξονες."""
    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='black'
    )
    # Κάνει και τους άξονες λευκούς (αν θέλετε γραμμές, μπορείτε να αφήσετε το grid)
    fig.update_xaxes(gridcolor='gray', showgrid=True, gridwidth=0.5)
    fig.update_yaxes(gridcolor='gray', showgrid=True, gridwidth=0.5)
    return fig

# -------------------------------
# (Η υπόλοιπη συνάρτηση load_data και φιλτράρισμα παραμένει ΑΚΡΙΒΩΣ ίδια)
# -------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Query1.xlsx", sheet_name=0)
    except FileNotFoundError:
        uploaded_file = st.file_uploader("Ανεβάστε το Query1.xlsx", type=["xlsx"])
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file, sheet_name=0)
        else:
            st.error("Δεν βρέθηκε το αρχείο Query1.xlsx. Παρακαλώ ανεβάστε το.")
            st.stop()
    
    if "ΑΦΜ" in df.columns:
        df["ΑΦΜ"] = df["ΑΦΜ"].astype(str).str.replace('="', '').str.replace('"', '').str.strip()
    
    numeric_cols = ["Αριθμός Τμημάτων", "Αγόρια", "Κορίτσια", "Σύνολο", 
                    "Υποχρεωτικό Διδακτικό Ωράριο Υπηρέτησης", "Α Ανάθεση Συνολικά", 
                    "Β Ανάθεση Συνολικά", "Γ Ανάθεση Συνολικά", "Προσθ Τμημ Συνολικά", 
                    "Άλλες Αναθέσεις Συνολικά"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df["Περιφερειακή Ενότητα"] = df["Περιφερειακή Ενότητα"].str.upper()
    return df

df = load_data()

# Φίλτρα (ίδια)
st.sidebar.header("Φίλτρα")
with st.sidebar.expander("🏫 Σχολεία", expanded=True):
    perifereies = df["Περιφερειακή Ενότητα"].unique()
    selected_perif = st.multiselect("Περιφερειακή Ενότητα", options=perifereies, default=perifereies, key="perif")
    dimos = df[df["Περιφερειακή Ενότητα"].isin(selected_perif)]["Δήμος"].unique()
    selected_dimos = st.multiselect("Δήμος", options=dimos, default=dimos, key="dimos")
    eidos_sx = df["Είδος Σχολείου"].unique()
    selected_eidos = st.multiselect("Είδος Σχολείου", options=eidos_sx, default=eidos_sx, key="eidos")

with st.sidebar.expander("👩‍🏫 Εκπαιδευτικοί", expanded=True):
    fylo_options = sorted(df["Φύλο"].dropna().unique().tolist())
    selected_fylo = st.multiselect("Φύλο Εκπαιδευτικού", options=fylo_options, default=fylo_options, key="fylo")
    eidikotita_options = sorted(df["Κωδικός Κύριας Ειδικότητας"].dropna().unique().tolist())
    selected_eidikotita = st.multiselect("Ειδικότητα", options=eidikotita_options, default=eidikotita_options, key="eidik")

filtered_df = df[
    (df["Περιφερειακή Ενότητα"].isin(selected_perif)) &
    (df["Δήμος"].isin(selected_dimos)) &
    (df["Είδος Σχολείου"].isin(selected_eidos))
]

filtered_teachers_base = df[
    (df["Περιφερειακή Ενότητα"].isin(selected_perif)) &
    (df["Δήμος"].isin(selected_dimos)) &
    (df["Είδος Σχολείου"].isin(selected_eidos)) &
    (df["Φύλο"].isin(selected_fylo)) &
    (df["Κωδικός Κύριας Ειδικότητας"].isin(selected_eidikotita))
]

school_df = filtered_df.drop_duplicates(subset="Ονομασία Σχολείου")
teachers_df = filtered_teachers_base.drop_duplicates(subset="ΑΦΜ")

tab1, tab2, tab3 = st.tabs(["Μαθητές", "Εκπαιδευτικοί", "Χάρτης & Αναλογίες"])

with tab1:
    st.header("Ανάλυση Μαθητών")
    if school_df.empty:
        st.warning("Δεν υπάρχουν δεδομένα με τα επιλεγμένα φίλτρα.")
    else:
        col1, col2 = st.columns(2)
        with col1:

            
            st.subheader("Σύνολο Μαθητών ανά Δήμο")
            students_by_dimos = school_df.groupby("Δήμος")[["Σύνολο"]].sum().reset_index()
            # Ταξινόμηση φθίνουσα
            students_by_dimos = students_by_dimos.sort_values("Σύνολο", ascending=False)
            # Δημιουργία σύντομης στήλης (π.χ. 15 χαρακτήρες, προσθήκη "..." αν κόβεται)
            students_by_dimos["Δήμος_Σύντομος"] = students_by_dimos["Δήμος"].apply(
                lambda x: x[:15] + "..." if len(x) > 15 else x
            )
            fig1 = px.bar(students_by_dimos, x="Δήμος_Σύντομος", y="Σύνολο", color="Δήμος_Σύντομος", text_auto=True,
              category_orders={"Δήμος_Σύντομος": students_by_dimos["Δήμος_Σύντομος"].tolist()})
            fig1.update_layout(xaxis_tickangle=-45, showlegend=False, bargap=0.05)
            fig1 = white_theme(fig1)
            st.plotly_chart(fig1, use_container_width=True)
            

        with col2:
            st.subheader("Κατανομή Μαθητών ανά φύλο")
            gender_agg = school_df.groupby("Τύπος Σχολείου")[["Αγόρια", "Κορίτσια"]].sum().reset_index()
            gender_melt = gender_agg.melt(id_vars="Τύπος Σχολείου", value_vars=["Αγόρια", "Κορίτσια"],
                                          var_name="Φύλο", value_name="Αριθμός")
            fig2 = px.pie(gender_melt, names="Φύλο", values="Αριθμός", color="Φύλο", hole=0.4,
                          hover_data=["Τύπος Σχολείου"])
            fig2 = white_theme(fig2)
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Μέγεθος Σχολείων: Τμήματα vs Μαθητές")
            school_agg = school_df[["Ονομασία Σχολείου", "Αριθμός Τμημάτων", "Σύνολο", "Δήμος", "Είδος Σχολείου"]]
            fig3 = px.scatter(school_agg, x="Αριθμός Τμημάτων", y="Σύνολο",
                              size="Σύνολο", color="Είδος Σχολείου",
                              hover_name="Ονομασία Σχολείου", hover_data=["Δήμος"])
            fig3 = white_theme(fig3)
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.subheader("Heatmap: Μαθητές ανά Είδος Σχολείου & Δήμο")
            heatmap_data = school_df.pivot_table(values="Σύνολο", index="Είδος Σχολείου",
                                                 columns="Δήμος", aggfunc="sum", fill_value=0)
            fig4 = px.imshow(heatmap_data, text_auto=True, aspect="auto", color_continuous_scale="Blues")
            fig4 = white_theme(fig4)
            st.plotly_chart(fig4, use_container_width=True)

        col5, col6 = st.columns(2)
        with col5:
            st.subheader("Ποσοστό Μαθητών ανά Είδος Σχολείου")
            students_by_eidos = school_df.groupby("Είδος Σχολείου")[["Σύνολο"]].sum().reset_index()
            fig5_students = px.pie(students_by_eidos, names="Είδος Σχολείου", values="Σύνολο", hole=0.4)
            fig5_students.update_traces(textposition="inside", textinfo="percent+label")
            fig5_students = white_theme(fig5_students)
            st.plotly_chart(fig5_students, use_container_width=True)

        with col6:
            st.subheader("Treemap: Κατανομή Μαθητών")
            treemap_students = school_df.groupby(
                ["Περιφερειακή Ενότητα", "Δήμος", "Είδος Σχολείου"]
            ).agg(Αριθμός_Μαθητών=("Σύνολο", "sum")).reset_index()
            fig6_students = px.treemap(
                treemap_students,
                path=["Περιφερειακή Ενότητα", "Δήμος", "Είδος Σχολείου"],
                values="Αριθμός_Μαθητών",
                color="Αριθμός_Μαθητών",
                color_continuous_scale="Blues"
            )
            fig6_students.update_traces(textinfo="label+value+percent root")
            fig6_students = white_theme(fig6_students)
            st.plotly_chart(fig6_students, use_container_width=True)

with tab2:
    st.header("Ανάλυση Εκπαιδευτικών")
    if teachers_df.empty:
        st.warning("Δεν υπάρχουν δεδομένα εκπαιδευτικών με τα επιλεγμένα φίλτρα.")
    else:
        st.subheader("Εκπαιδευτικοί ανά Ειδικότητα & Φύλο (Top 10)")
        spec_total = teachers_df.groupby("Κωδικός Κύριας Ειδικότητας").size().reset_index(name="Σύνολο")
        top10_specs = spec_total.nlargest(10, "Σύνολο")["Κωδικός Κύριας Ειδικότητας"].tolist()
        spec_gender = (
            teachers_df[teachers_df["Κωδικός Κύριας Ειδικότητας"].isin(top10_specs)]
            .groupby(["Κωδικός Κύριας Ειδικότητας", "Φύλο"])
            .size()
            .reset_index(name="Αριθμός")
        )
        spec_gender["sort_key"] = spec_gender.groupby("Κωδικός Κύριας Ειδικότητας")["Αριθμός"].transform("sum")
        spec_gender = spec_gender.sort_values("sort_key", ascending=False)
        ordered_specs = spec_gender["Κωδικός Κύριας Ειδικότητας"].unique().tolist()
        fig5 = px.bar(spec_gender, x="Κωδικός Κύριας Ειδικότητας", y="Αριθμός",
                      color="Φύλο", barmode="group",
                      title="Top 10 Ειδικοτήτων ανά Φύλο",
                      category_orders={"Κωδικός Κύριας Ειδικότητας": ordered_specs})
        fig5.update_layout(xaxis_tickangle=-45)
        fig5 = white_theme(fig5)
        st.plotly_chart(fig5, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Κατανομή Σχέσης Εργασίας")
            def group_employment(val):
                return "Μόνιμοι" if str(val) == "Μόνιμος" else "Μη Μόνιμοι"
            employment_grouped = teachers_df["Σχέση Εργασίας"].apply(group_employment)
            employment_pie = employment_grouped.value_counts().reset_index()
            employment_pie.columns = ["Σχέση Εργασίας", "Αριθμός"]
            fig6 = px.pie(employment_pie, names="Σχέση Εργασίας", values="Αριθμός")
            fig6 = white_theme(fig6)
            st.plotly_chart(fig6, use_container_width=True)

        with col2:
            st.subheader("Κατανομή Φύλου Εκπαιδευτικών")
            gender_teachers_pie = teachers_df["Φύλο"].value_counts().reset_index()
            gender_teachers_pie.columns = ["Φύλο", "Αριθμός"]
            fig_gender_teachers = px.pie(gender_teachers_pie, names="Φύλο", values="Αριθμός",
                                         color="Φύλο",
                                         color_discrete_map={"ΑΝΔΡΑΣ": "#1f77b4", "ΓΥΝΑΙΚΑ": "#e377c2"})
            fig_gender_teachers = white_theme(fig_gender_teachers)
            st.plotly_chart(fig_gender_teachers, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Κατανομή Διδακτικού Ωραρίου")
            fig7 = px.histogram(teachers_df, x="Υποχρεωτικό Διδακτικό Ωράριο Υπηρέτησης",
                                nbins=10, color="Φύλο")
            fig7 = white_theme(fig7)
            st.plotly_chart(fig7, use_container_width=True)

        with col4:
            st.subheader("Treemap: Γεωγραφική Κατανομή Εκπαιδευτικών")
            treemap_data = teachers_df.groupby(["Περιφερειακή Ενότητα", "Δήμος", "Είδος Σχολείου"]).size().reset_index(name="Αριθμός")
            fig8 = px.treemap(treemap_data, path=["Περιφερειακή Ενότητα", "Δήμος", "Είδος Σχολείου"],
                              values="Αριθμός", color="Αριθμός")
            fig8 = white_theme(fig8)
            st.plotly_chart(fig8, use_container_width=True)

with tab3:
    st.header("Χάρτης Πελοποννήσου & Αναλογίες")
    
    @st.cache_data
    def load_geojson():
        geo_url = "https://raw.githubusercontent.com/peterdsp/greece-prefectures-and-units/main/greecePrefecturesUnits.geojson"
        response = requests.get(geo_url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Αποτυχία φόρτωσης GeoJSON.")
            return None
    
    geo_data = load_geojson()
    if geo_data:
        peloponnese_units = ["ΑΡΓΟΛΙΔΑΣ", "ΑΡΚΑΔΙΑΣ", "ΚΟΡΙΝΘΙΑΣ", "ΛΑΚΩΝΙΑΣ", "ΜΕΣΣΗΝΙΑΣ"]
        pel_df = df[df["Περιφερειακή Ενότητα"].isin(peloponnese_units)]
        pel_school_df = pel_df.drop_duplicates(subset="Ονομασία Σχολείου")
        pel_teachers_df = pel_df.drop_duplicates(subset="ΑΦΜ")
        
        map_data = pel_school_df.groupby("Περιφερειακή Ενότητα").agg(
            Αριθμός_Σχολείων=("Ονομασία Σχολείου", "count"),
            Αριθμός_Μαθητών=("Σύνολο", "sum")
        ).reset_index()
        teachers_count = pel_teachers_df.groupby("Περιφερειακή Ενότητα").size().reset_index(name="Αριθμός_Εκπαιδευτικών")
        map_data = map_data.merge(teachers_count, on="Περιφερειακή Ενότητα", how="left").fillna(0)
        map_data["Αναλογία Μαθητών/Εκπαιδευτικό"] = map_data["Αριθμός_Μαθητών"] / map_data["Αριθμός_Εκπαιδευτικών"].replace(0, 1)
        
        name_map = {
            "ΑΡΓΟΛΙΔΑΣ": "ARGOLIDAS",
            "ΑΡΚΑΔΙΑΣ": "ARCADIAS",
            "ΚΟΡΙΝΘΙΑΣ": "CORINTHIAS",
            "ΛΑΚΩΝΙΑΣ": "LAKONIAS",
            "ΜΕΣΣΗΝΙΑΣ": "MESSINIAS"
        }
        map_data["Geo_Name"] = map_data["Περιφερειακή Ενότητα"].map(name_map)
        
        st.subheader("Διαδραστικός Χάρτης Πελοποννήσου")
        color_discrete_map = {
            "ARGOLIDAS": "#FF6B6B",
            "ARCADIAS": "#4ECDC4",
            "CORINTHIAS": "#45B7D1",
            "LAKONIAS": "#FFBE0B",
            "MESSINIAS": "#A05195"
        }
        fig_map = px.choropleth(
            map_data,
            geojson=geo_data,
            locations="Geo_Name",
            featureidkey="properties.name",
            color="Περιφερειακή Ενότητα",
            hover_data=["Αριθμός_Σχολείων", "Αριθμός_Εκπαιδευτικών", "Αναλογία Μαθητών/Εκπαιδευτικό"],
            title="Στοιχεία ανά Περιφερειακή Ενότητα (Mouse over για λεπτομέρειες)",
            color_discrete_map=color_discrete_map
        )
        fig_map.update_geos(visible=False, resolution=50, fitbounds="locations", showcountries=True, countrycolor="RebeccaPurple")
        fig_map.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0}, paper_bgcolor="white", plot_bgcolor="white")
        fig_map = white_theme(fig_map)
        st.plotly_chart(fig_map, use_container_width=True)
        
        total_students = map_data["Αριθμός_Μαθητών"].sum()
        total_teachers = map_data["Αριθμός_Εκπαιδευτικών"].sum()
        overall_ratio = total_students / total_teachers if total_teachers > 0 else 0
        st.metric("Συνολική Αναλογία Μαθητών / Εκπαιδευτικό", f"{overall_ratio:.2f}")

st.markdown("---")
st.info("**")

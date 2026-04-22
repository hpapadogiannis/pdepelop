import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import requests

# Τίτλος εφαρμογής
st.set_page_config(page_title="Εκπαιδευτικά Δεδομένα - Αργολίδα & Μεσσηνία", layout="wide")
st.title("Interactive Dashboard: Μαθητές & Εκπαιδευτικοί")
st.markdown("Ανάλυση δεδομένων από το αρχείο **Query1.xlsx**. Φορτώστε το αρχείο στο ίδιο φάκελο με το script ή επιλέξτε το παρακάτω.")

# Φόρτωση δεδομένων
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
    
    # Καθαρισμός βασικών στηλών (π.χ. ΑΦΜ έχει περίεργη μορφή όπως =""031284480"")
    if "ΑΦΜ" in df.columns:
        df["ΑΦΜ"] = df["ΑΦΜ"].astype(str).str.replace('="', '').str.replace('"', '').str.strip()
    
    # Μετατροπή αριθμητικών στηλών (αν χρειάζεται)
    numeric_cols = ["Αριθμός Τμημάτων", "Αγόρια", "Κορίτσια", "Σύνολο", 
                    "Υποχρεωτικό Διδακτικό Ωράριο Υπηρέτησης", "Α Ανάθεση Συνολικά", 
                    "Β Ανάθεση Συνολικά", "Γ Ανάθεση Συνολικά", "Προσθ Τμημ Συνολικά", 
                    "Άλλες Αναθέσεις Συνολικά"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Normalize names for matching with geojson (upper case, remove accents if needed, but here simple upper)
    df["Περιφερειακή Ενότητα"] = df["Περιφερειακή Ενότητα"].str.upper()
    
    return df

df = load_data()

# Φίλτρα κοινά για όλες τις σελίδες
st.sidebar.header("Φίλτρα")
perifereies = df["Περιφερειακή Ενότητα"].unique()
selected_perif = st.sidebar.multiselect("Περιφερειακή Ενότητα", options=perifereies, default=perifereies)

dimos = df[df["Περιφερειακή Ενότητα"].isin(selected_perif)]["Δήμος"].unique()
selected_dimos = st.sidebar.multiselect("Δήμος", options=dimos, default=dimos)

eidos_sx = df["Είδος Σχολείου"].unique()
selected_eidos = st.sidebar.multiselect("Είδος Σχολείου", options=eidos_sx, default=eidos_sx)

# Φιλτράρισμα DataFrame
filtered_df = df[
    (df["Περιφερειακή Ενότητα"].isin(selected_perif)) &
    (df["Δήμος"].isin(selected_dimos)) &
    (df["Είδος Σχολείου"].isin(selected_eidos))
]

# Μοναδικά σχολεία για μαθητές (χωρίς διπλοεγγραφές)
school_df = filtered_df.drop_duplicates(subset="Ονομασία Σχολείου")

# Μοναδικοί εκπαιδευτικοί
teachers_df = filtered_df.drop_duplicates(subset="ΑΦΜ")

# Tabs για Μαθητές, Εκπαιδευτικοί, Χάρτης
tab1, tab2, tab3 = st.tabs(["Μαθητές", "Εκπαιδευτικοί", "Χάρτης & Αναλογίες"])

with tab1:
    st.header("Ανάλυση Μαθητών")
    
    if school_df.empty:
        st.warning("Δεν υπάρχουν δεδομένα με τα επιλεγμένα φίλτρα.")
    else:
        # 1. Bar Chart: Σύνολο Μαθητών ανά Δήμο
        st.subheader("Σύνολο Μαθητών ανά Δήμο")
        students_by_dimos = school_df.groupby("Δήμος")[["Σύνολο"]].sum().reset_index()
        fig1 = px.bar(students_by_dimos, x="Δήμος", y="Σύνολο", 
                      title="Σύνολο Μαθητών ανά Δήμο",
                      color="Δήμος", text_auto=True)
        fig1.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)
        
        # 2. Pie Chart: Κατανομή Φύλου ανά Τύπο Σχολείου
        st.subheader("Κατανομή Φύλου Μαθητών")
        gender_agg = school_df.groupby("Τύπος Σχολείου")[["Αγόρια", "Κορίτσια"]].sum().reset_index()
        gender_melt = gender_agg.melt(id_vars="Τύπος Σχολείου", value_vars=["Αγόρια", "Κορίτσια"], 
                                      var_name="Φύλο", value_name="Αριθμός")
        fig2 = px.pie(gender_melt, names="Φύλο", values="Αριθμός", 
                      color="Φύλο", hole=0.4, 
                      title="Κατανομή Φύλου ανά Τύπο Σχολείου (συνολικά)",
                      hover_data=["Τύπος Σχολείου"])
        st.plotly_chart(fig2, use_container_width=True)
        
        # 3. Scatter Plot: Τμήματα vs Μαθητές
        st.subheader("Αριθμός Τμημάτων vs Σύνολο Μαθητών ανά Σχολείο")
        school_agg = school_df[["Ονομασία Σχολείου", "Αριθμός Τμημάτων", "Σύνολο", "Δήμος", "Είδος Σχολείου"]]
        fig3 = px.scatter(school_agg, x="Αριθμός Τμημάτων", y="Σύνολο",
                          size="Σύνολο", color="Είδος Σχολείου",
                          hover_name="Ονομασία Σχολείου", hover_data=["Δήμος"],
                          title="Μέγεθος Σχολείων: Τμήματα vs Μαθητές")
        st.plotly_chart(fig3, use_container_width=True)
        
        # 4. Heatmap: Μαθητές ανά Είδος Σχολείου και Δήμο
        st.subheader("Heatmap: Μαθητές ανά Είδος Σχολείου & Δήμο")
        heatmap_data = school_df.pivot_table(values="Σύνολο", index="Είδος Σχολείου", 
                                             columns="Δήμος", aggfunc="sum", fill_value=0)
        fig4 = px.imshow(heatmap_data, text_auto=True, aspect="auto",
                         color_continuous_scale="Blues",
                         title="Πυκνότητα Μαθητών")
        st.plotly_chart(fig4, use_container_width=True)

with tab2:
    st.header("Ανάλυση Εκπαιδευτικών")
    
    if teachers_df.empty:
        st.warning("Δεν υπάρχουν δεδομένα εκπαιδευτικών με τα επιλεγμένα φίλτρα.")
    else:
        # 1. Bar Chart: Εκπαιδευτικοί ανά Ειδικότητα & Φύλο
        st.subheader("Εκπαιδευτικοί ανά Ειδικότητα & Φύλο")
        spec_gender = teachers_df.groupby(["Κωδικός Κύριας Ειδικότητας", "Φύλο"]).size().reset_index(name="Αριθμός")
        fig5 = px.bar(spec_gender, x="Κωδικός Κύριας Ειδικότητας", y="Αριθμός",
                      color="Φύλο", barmode="group",
                      title="Κατανομή Ειδικοτήτων ανά Φύλο")
        fig5.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig5, use_container_width=True)
        
        # 2. Pie Chart: Σχέση Εργασίας
        st.subheader("Κατανομή Σχέσης Εργασίας")
        employment_pie = teachers_df["Σχέση Εργασίας"].value_counts().reset_index()
        employment_pie.columns = ["Σχέση Εργασίας", "Αριθμός"]
        fig6 = px.pie(employment_pie, names="Σχέση Εργασίας", values="Αριθμός",
                      title="Τύποι Σχέσεων Εργασίας (Μόνιμοι, Αναπληρωτές κλπ.)")
        st.plotly_chart(fig6, use_container_width=True)
        # 5. Pie Chart: Κατανομή Φύλου Εκπαιδευτικών
        st.subheader("Κατανομή Φύλου Εκπαιδευτικών")
        gender_teachers_pie = teachers_df["Φύλο"].value_counts().reset_index()
        gender_teachers_pie.columns = ["Φύλο", "Αριθμός"]
        fig_gender_teachers = px.pie(gender_teachers_pie, names="Φύλο", values="Αριθμός",
                             title="Ποσοστό Ανδρών - Γυναικών Εκπαιδευτικών",
                             color="Φύλο",
                             color_discrete_map={"ΑΝΔΡΑΣ": "#1f77b4", "ΓΥΝΑΙΚΑ": "#e377c2"})
        st.plotly_chart(fig_gender_teachers, use_container_width=True)
        # 3. Histogram: Διδακτικό Ωράριο
        st.subheader("Κατανομή Υποχρεωτικού Διδακτικού Ωραρίου")
        fig7 = px.histogram(teachers_df, x="Υποχρεωτικό Διδακτικό Ωράριο Υπηρέτησης",
                            nbins=10, color="Φύλο",
                            title="Ωράριο Υπηρέτησης Εκπαιδευτικών")
        st.plotly_chart(fig7, use_container_width=True)
        
        # 4. Treemap: Εκπαιδευτικοί ανά Περιφέρεια / Δήμο / Είδος Σχολείου
        st.subheader("Treemap: Κατανομή Εκπαιδευτικών")
        treemap_data = teachers_df.groupby(["Περιφερειακή Ενότητα", "Δήμος", "Είδος Σχολείου"]).size().reset_index(name="Αριθμός")
        fig8 = px.treemap(treemap_data, path=["Περιφερειακή Ενότητα", "Δήμος", "Είδος Σχολείου"],
                          values="Αριθμός", color="Αριθμός",
                          title="Γεωγραφική Κατανομή Εκπαιδευτικών")
        st.plotly_chart(fig8, use_container_width=True)

with tab3:
    st.header("Χάρτης Πελοποννήσου & Αναλογίες")
    
    # Φόρτωση GeoJSON
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
        # Περιφέρειες Πελοποννήσου (match upper case)
        peloponnese_units = ["ΑΡΓΟΛΙΔΑΣ", "ΑΡΚΑΔΙΑΣ", "ΚΟΡΙΝΘΙΑΣ", "ΛΑΚΩΝΙΑΣ", "ΜΕΣΣΗΝΙΑΣ"]
        
        # Φιλτράρισμα δεδομένων για Πελοπόννησο
        pel_df = df[df["Περιφερειακή Ενότητα"].isin(peloponnese_units)]
        pel_school_df = pel_df.drop_duplicates(subset="Ονομασία Σχολείου")
        pel_teachers_df = pel_df.drop_duplicates(subset="ΑΦΜ")
        
        # Aggregations ανά Ενότητα
        map_data = pel_school_df.groupby("Περιφερειακή Ενότητα").agg(
            Αριθμός_Σχολείων=("Ονομασία Σχολείου", "count"),
            Αριθμός_Μαθητών=("Σύνολο", "sum")
        ).reset_index()
        
        teachers_count = pel_teachers_df.groupby("Περιφερειακή Ενότητα").size().reset_index(name="Αριθμός_Εκπαιδευτικών")
        map_data = map_data.merge(teachers_count, on="Περιφερειακή Ενότητα", how="left").fillna(0)
        
        # Αναλογία Μαθητών / Εκπαιδευτικό
        map_data["Αναλογία Μαθητών/Εκπαιδευτικό"] = map_data["Αριθμός_Μαθητών"] / map_data["Αριθμός_Εκπαιδευτικών"].replace(0, 1)  # Αποφυγή διαίρεσης με 0
        
        # Normalize names for matching (geojson has "ARGOLIDAS", data has "ΑΡΓΟΛΙΔΑΣ")
        name_map = {
            "ΑΡΓΟΛΙΔΑΣ": "ARGOLIDAS",
            "ΑΡΚΑΔΙΑΣ": "ARCADIAS",
            "ΚΟΡΙΝΘΙΑΣ": "CORINTHIAS",
            "ΛΑΚΩΝΙΑΣ": "LAKONIAS",
            "ΜΕΣΣΗΝΙΑΣ": "MESSINIAS"
        }
        map_data["Geo_Name"] = map_data["Περιφερειακή Ενότητα"].map(name_map)

        # Χάρτης
        st.subheader("Διαδραστικός Χάρτης Πελοποννήσου")
        # Ορισμός μιας διακριτής παλέτας (π.χ. 5 χρώματα για τους 5 νομούς της Πελοποννήσου)
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
            color="Περιφερειακή Ενότητα",  # Χρωματίζει ανά νομό, όχι ανά τιμή
            hover_data=["Αριθμός_Σχολείων", "Αριθμός_Εκπαιδευτικών", "Αναλογία Μαθητών/Εκπαιδευτικό"],
            title="Στοιχεία ανά Περιφερειακή Ενότητα (Mouse over για λεπτομέρειες)",
            color_discrete_map=color_discrete_map   # Χρήση της προσαρμοσμένης παλέτας
        )

        # Βελτιωμένη ρύθμιση γεωγραφικής προβολής
        fig_map.update_geos(
            visible=False, 
            resolution=50,
            fitbounds="locations",
            showcountries=True, 
            countrycolor="RebeccaPurple"
        )
        
        fig_map.update_layout(
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            paper_bgcolor="#f0f0f0"
        )
        st.plotly_chart(fig_map, use_container_width=True)
        # Συνολική Αναλογία
        total_students = map_data["Αριθμός_Μαθητών"].sum()
        total_teachers = map_data["Αριθμός_Εκπαιδευτικών"].sum()
        overall_ratio = total_students / total_teachers if total_teachers > 0 else 0
        st.metric("Συνολική Αναλογία Μαθητών / Εκπαιδευτικό", f"{overall_ratio:.2f}")

st.markdown("---")
st.info("**")
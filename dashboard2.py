import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page config
st.set_page_config(
    page_title="Οπτικοποίηση Σχολικών Δεδομένων",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"] p {
        font-weight: 900 !important;
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    # Load both sheets from the Excel file
    df_students = pd.read_excel("Query1.xlsx", sheet_name="students")
    df_teachers = pd.read_excel("Query1.xlsx", sheet_name="teachers")

    # --- Clean Students Data ---
    # Remove summary/total rows (they contain "Σύνολο:" in numeric columns)
    for col in ['Αριθμός Τμημάτων', 'Αγόρια', 'Κορίτσια', 'Σύνολο']:
        df_students = df_students[~df_students[col].astype(str).str.contains('Σύνολο', na=False)]

    # Convert numeric columns for students
    for col in ['Αριθμός Τμημάτων', 'Αγόρια', 'Κορίτσια', 'Σύνολο']:
        df_students[col] = pd.to_numeric(df_students[col], errors='coerce')

    # Remove rows with missing critical data
    df_students = df_students.dropna(subset=['Ονομασία Σχολείου', 'Είδος Σχολείου'])

    # --- Clean Teachers Data ---
    # Remove header rows repeated inside data
    df_teachers = df_teachers[df_teachers['ΑΦΜ'] != 'ΑΦΜ']

    # Convert numeric columns for teachers
    df_teachers['Υποχρεωτικό Διδακτικό Ωράριο Υπηρέτησης'] = pd.to_numeric(
        df_teachers['Υποχρεωτικό Διδακτικό Ωράριο Υπηρέτησης'], errors='coerce'
    )

    # Remove rows with missing critical data
    df_teachers = df_teachers.dropna(subset=['ΑΦΜ'])

    return df_students, df_teachers

df_students, df_teachers = load_data()

# ==================== ΠΛΕΥΡΙΚΗ ΜΠΑΡΑ (SIDEBAR) ====================
st.sidebar.header("🔍 Φίλτρα Δεδομένων")

# Κοινά φίλτρα που εφαρμόζονται και στους δύο πίνακες
available_directions = sorted(list(set(df_students['Διεύθυνση'].dropna().unique()) | set(df_teachers['Διεύθυνση'].dropna().unique())))
selected_direction = st.sidebar.multiselect(
    "Διεύθυνση",
    options=available_directions,
    default=[]
)

available_regions = sorted(list(set(df_students['Περιφερειακή Ενότητα'].dropna().unique()) | set(df_teachers['Περιφερειακή Ενότητα'].dropna().unique())))
selected_region = st.sidebar.multiselect(
    "Περιφερειακή Ενότητα",
    options=available_regions,
    default=[]
)

available_municipalities = sorted(list(set(df_students['Δήμος'].dropna().unique()) | set(df_teachers['Δήμος'].dropna().unique())))
selected_municipality = st.sidebar.multiselect(
    "Δήμος",
    options=available_municipalities,
    default=[]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎓 Ειδικά Φίλτρα Μαθητών")
selected_school_type = st.sidebar.multiselect(
    "Είδος Σχολείου",
    options=sorted(df_students['Είδος Σχολείου'].dropna().unique()),
    default=[]
)
selected_school_subtype = st.sidebar.multiselect(
    "Τύπος Σχολείου",
    options=sorted(df_students['Τύπος Σχολείου'].dropna().unique()),
    default=[]
)

st.sidebar.markdown("---")
st.sidebar.subheader("👨‍🏫 Ειδικά Φίλτρα Εκπαιδευτικών")
selected_gender = st.sidebar.multiselect(
    "Φύλο Εκπαιδευτικού",
    options=sorted(df_teachers['Φύλο'].dropna().unique()),
    default=[]
)
selected_placement = st.sidebar.multiselect(
    "Σχέση Τοποθέτησης",
    options=sorted(df_teachers['Σχέση Τοποθέτησης'].dropna().unique()),
    default=[]
)
selected_specialty = st.sidebar.multiselect(
    "Κωδ. Ειδικότητας",
    options=sorted(df_teachers['Κωδ. Ειδικότητας'].dropna().unique()),
    default=[]
)

# ==================== ΕΦΑΡΜΟΓΗ ΦΙΛΤΡΩΝ ====================
# Φιλτράρισμα Μαθητών
filtered_students = df_students.copy()
if selected_direction:
    filtered_students = filtered_students[filtered_students['Διεύθυνση'].isin(selected_direction)]
if selected_region:
    filtered_students = filtered_students[filtered_students['Περιφερειακή Ενότητα'].isin(selected_region)]
if selected_municipality:
    filtered_students = filtered_students[filtered_students['Δήμος'].isin(selected_municipality)]
if selected_school_type:
    filtered_students = filtered_students[filtered_students['Είδος Σχολείου'].isin(selected_school_type)]
if selected_school_subtype:
    filtered_students = filtered_students[filtered_students['Τύπος Σχολείου'].isin(selected_school_subtype)]

# Φιλτράρισμα Εκπαιδευτικών
filtered_teachers = df_teachers.copy()
if selected_direction:
    filtered_teachers = filtered_teachers[filtered_teachers['Διεύθυνση'].isin(selected_direction)]
if selected_region:
    filtered_teachers = filtered_teachers[filtered_teachers['Περιφερειακή Ενότητα'].isin(selected_region)]
if selected_municipality:
    filtered_teachers = filtered_teachers[filtered_teachers['Δήμος'].isin(selected_municipality)]
if selected_gender:
    filtered_teachers = filtered_teachers[filtered_teachers['Φύλο'].isin(selected_gender)]
if selected_placement:
    filtered_teachers = filtered_teachers[filtered_placement['Σχέση Τοποθέτησης'].isin(selected_placement)]
if selected_specialty:
    filtered_teachers = filtered_teachers[filtered_teachers['Κωδ. Ειδικότητας'].isin(selected_specialty)]

# ==================== ΚΕΝΤΡΙΚΟ ΠΑΝΕΛ ====================
st.markdown('<div class="main-header">🏫 Οπτικοποίηση Σχολικών Δεδομένων ΠΔΕ ΠΕΛΟΠΟΝΝΗΣΟΥ</div>', unsafe_allow_html=True)

# Υπολογισμός Βασικών Μεγεθών με βάση τα φίλτρα
total_schools = filtered_students['Ονομασία Σχολείου'].nunique()
total_students = int(filtered_students['Σύνολο'].sum())
total_sections = int(filtered_students['Αριθμός Τμημάτων'].sum())
total_teachers = filtered_teachers['ΑΦΜ'].nunique()

st.subheader("📊 Βασικά Μεγέθη")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Σύνολο Σχολείων", f"{total_schools:,}")
with col2:
    st.metric("Σύνολο Μαθητών", f"{total_students:,}")
with col3:
    st.metric("Σύνολο Τμημάτων", f"{total_sections:,}")
with col4:
    st.metric("Σύνολο Εκπαιδευτικών", f"{total_teachers:,}")

st.divider()

# Δημιουργία των δύο κεντρικών Tabs στην οθόνη
main_tab1, main_tab2 = st.tabs(["📚 Στατιστικά Μαθητών & Σχολείων", "👨‍🏫 Στατιστικά Εκπαιδευτικών"])

# ==================== ΚΑΡΤΕΛΑ 1: ΜΑΘΗΤΕΣ ====================
with main_tab1:
    unique_df = filtered_students.copy()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Γενικά Στατιστικά",
        "🏫 Στοιχεία Σχολείων",
        "📚 Μαθητές",
        "🔗 Συσχετίσεις",
        "📋 Πίνακας Δεδομένων"
    ])

    with tab1:
        st.header("Γενικά Στατιστικά")
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.subheader("Κατανομή ανά Είδος Σχολείου")
            school_type_counts = filtered_students['Είδος Σχολείου'].value_counts().reset_index()
            school_type_counts.columns = ['Είδος Σχολείου', 'Πλήθος']
            fig = px.pie(school_type_counts, values='Πλήθος', names='Είδος Σχολείου', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        with row1_col2:
            st.subheader("Κατανομή ανά Περιφερειακή Ενότητα")
            region_counts = filtered_students['Περιφερειακή Ενότητα'].value_counts().reset_index()
            region_counts.columns = ['Περιφερειακή Ενότητα', 'Πλήθος']
            fig = px.bar(region_counts, x='Περιφερειακή Ενότητα', y='Πλήθος', color='Περιφερειακή Ενότητα', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.subheader("Κατανομή ανά Διεύθυνση")
            dir_counts = filtered_students['Διεύθυνση'].value_counts().reset_index()
            dir_counts.columns = ['Διεύθυνση', 'Πλήθος']
            fig = px.bar(dir_counts, x='Διεύθυνση', y='Πλήθος', color='Διεύθυνση', color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        with row2_col2:
            st.subheader("Κατανομή ανά Τύπο Σχολείου (Top 15)")
            type_counts = filtered_students['Τύπος Σχολείου'].value_counts().head(15).reset_index()
            type_counts.columns = ['Τύπος Σχολείου', 'Πλήθος']
            fig = px.bar(type_counts, x='Πλήθος', y='Τύπος Σχολείου', orientation='h', color='Πλήθος', color_continuous_scale='Viridis')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        row3_col1, row3_col2 = st.columns(2)
        with row3_col1:
            st.subheader("Κατανομή ανά Δήμο (Top 15)")
            mun_counts = filtered_students['Δήμος'].value_counts().head(15).reset_index()
            mun_counts.columns = ['Δήμος', 'Πλήθος']
            fig = px.bar(mun_counts, x='Πλήθος', y='Δήμος', orientation='h', color='Πλήθος', color_continuous_scale='Plasma')
            st.plotly_chart(fig, use_container_width=True)
        with row3_col2:
            st.subheader("Μαθητές ανά Είδος Σχολείου")
            students_by_type = unique_df.groupby('Είδος Σχολείου')['Σύνολο'].sum().reset_index()
            fig = px.pie(students_by_type, values='Σύνολο', names='Είδος Σχολείου', color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("Στοιχεία Σχολείων")
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.subheader("Αριθμός Τμημάτων ανά Σχολείο")
            fig = px.histogram(filtered_students, x='Αριθμός Τμημάτων', nbins=30, color='Είδος Σχολείου', barmode='stack', color_discrete_sequence=px.colors.qualitative.Set1)
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)
        with row1_col2:
            st.subheader("Κατανομή Τμημάτων ανά Είδος Σχολείου")
            sections_by_type = filtered_students.groupby('Είδος Σχολείου')['Αριθμός Τμημάτων'].sum().reset_index()
            fig = px.pie(sections_by_type, values='Αριθμός Τμημάτων', names='Είδος Σχολείου', color_discrete_sequence=px.colors.qualitative.Set1)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.subheader("Μέσος Αριθμός Τμημάτων ανά Τύπο Σχολείου")
            avg_sections = filtered_students.groupby('Τύπος Σχολείου')['Αριθμός Τμημάτων'].mean().sort_values(ascending=False).head(15).reset_index()
            avg_sections.columns = ['Τύπος Σχολείου', 'Μέσος Όρος Τμημάτων']
            fig = px.bar(avg_sections, x='Μέσος Όρος Τμημάτων', y='Τύπος Σχολείου', orientation='h', color='Μέσος Όρος Τμημάτων', color_continuous_scale='Inferno')
            st.plotly_chart(fig, use_container_width=True)
        with row2_col2:
            st.subheader("Μέσος Αριθμός Τμημάτων ανά Περιφερειακή Ενότητα")
            avg_sections_region = filtered_students.groupby('Περιφερειακή Ενότητα')['Αριθμός Τμημάτων'].mean().sort_values(ascending=False).reset_index()
            avg_sections_region.columns = ['Περιφερειακή Ενότητα', 'Μέσος Όρος Τμημάτων']
            fig = px.bar(avg_sections_region, x='Περιφερειακή Ενότητα', y='Μέσος Όρος Τμημάτων', color='Περιφερειακή Ενότητα', color_discrete_sequence=px.colors.qualitative.Dark24)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Ανάλυση Σχολείων ανά Περιφερειακή Ενότητα και Είδος")
        pivot_schools = filtered_students.pivot_table(index='Περιφερειακή Ενότητα', columns='Είδος Σχολείου', values='Ονομασία Σχολείου', aggfunc='count').fillna(0)
        fig = px.imshow(pivot_schools, text_auto=True, aspect="auto", color_continuous_scale='Blues')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.header("📚 Στοιχεία Μαθητών")
        row1_col1, row1_col2, row1_col3 = st.columns(3)
        with row1_col1:
            st.subheader("Κατανομή Συνόλου Μαθητών")
            fig = px.histogram(unique_df, x='Σύνολο', nbins=50, color_discrete_sequence=['#3366cc'])
            fig.update_layout(bargap=0.05)
            st.plotly_chart(fig, use_container_width=True)
        with row1_col2:
            st.subheader("Κατανομή Αγοριών")
            fig = px.histogram(unique_df, x='Αγόρια', nbins=50, color_discrete_sequence=['#66b3ff'])
            fig.update_layout(bargap=0.05)
            st.plotly_chart(fig, use_container_width=True)
        with row1_col3:
            st.subheader("Κατανομή Κοριτσιών")
            fig = px.histogram(unique_df, x='Κορίτσια', nbins=50, color_discrete_sequence=['#ff9999'])
            fig.update_layout(bargap=0.05)
            st.plotly_chart(fig, use_container_width=True)

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.subheader("Σύνολο Μαθητών ανά Είδος Σχολείου")
            students_by_type = unique_df.groupby('Είδος Σχολείου')['Σύνολο'].sum().reset_index()
            fig = px.pie(students_by_type, values='Σύνολο', names='Είδος Σχολείου', color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        with row2_col2:
            st.subheader("Σύνολο Μαθητών ανά Περιφερειακή Ενότητα")
            students_by_region = unique_df.groupby('Περιφερειακή Ενότητα')['Σύνολο'].sum().reset_index()
            fig = px.bar(students_by_region, x='Περιφερειακή Ενότητα', y='Σύνολο', color='Περιφερειακή Ενότητα', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        row3_col1, row3_col2 = st.columns(2)
        with row3_col1:
            st.subheader("Αγόρια vs Κορίτσια ανά Είδος Σχολείου")
            gender_students = unique_df.groupby('Είδος Σχολείου')[['Αγόρια', 'Κορίτσια']].sum().reset_index()
            gender_students_melted = gender_students.melt(id_vars='Είδος Σχολείου', var_name='Φύλο Μαθητή', value_name='Πλήθος')
            fig = px.bar(gender_students_melted, x='Είδος Σχολείου', y='Πλήθος', color='Φύλο Μαθητή', barmode='group', color_discrete_map={'Αγόρια': '#66b3ff', 'Κορίτσια': '#ff9999'})
            fig.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)
        with row3_col2:
            st.subheader("Αναλογία Αγοριών/Κοριτσιών ανά Περιφερειακή Ενότητα")
            ratio_df = unique_df.groupby('Περιφερειακή Ενότητα')[['Αγόρια', 'Κορίτσια']].sum().reset_index()
            ratio_df['Αναλογία Αγόρια/Κορίτσια'] = ratio_df['Αγόρια'] / ratio_df['Κορίτσια']
            fig = px.bar(ratio_df, x='Περιφερειακή Ενότητα', y='Αναλογία Αγόρια/Κορίτσια', color='Αναλογία Αγόρια/Κορίτσια', color_continuous_scale='RdBu', color_continuous_midpoint=1)
            fig.add_hline(y=1, line_dash="dash", line_color="black")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Μαθητές ανά Δήμο (Top 15)")
        students_by_mun = unique_df.groupby('Δήμος')[['Αγόρια', 'Κορίτσια', 'Σύνολο']].sum().sort_values('Σύνολο', ascending=False).head(15).reset_index()
        students_by_mun_melted = students_by_mun.melt(id_vars='Δήμος', var_name='Κατηγορία', value_name='Πλήθος')
        fig = px.bar(students_by_mun_melted, x='Δήμος', y='Πλήθος', color='Κατηγορία', barmode='group', color_discrete_map={'Αγόρια': '#66b3ff', 'Κορίτσια': '#ff9999', 'Σύνολο': '#99cc00'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.header("🔗 Συσχετίσεις Μεταβλητών")
        numeric_cols = ['Αριθμός Τμημάτων', 'Αγόρια', 'Κορίτσια', 'Σύνολο']
        corr_matrix = unique_df[numeric_cols].corr()
        st.subheader("Πίνακας Συσχέτισης")
        fig = px.imshow(corr_matrix, text_auto='.2f', aspect="auto", color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.subheader("Αγόρια vs Σύνολο Μαθητών")
            fig = px.scatter(unique_df, x='Αγόρια', y='Σύνολο', color='Είδος Σχολείου', trendline='ols', color_discrete_sequence=px.colors.qualitative.Set1, opacity=0.6)
            st.plotly_chart(fig, use_container_width=True)
        with row1_col2:
            st.subheader("Κορίτσια vs Σύνολο Μαθητών")
            fig = px.scatter(unique_df, x='Κορίτσια', y='Σύνολο', color='Είδος Σχολείου', trendline='ols', color_discrete_sequence=px.colors.qualitative.Set1, opacity=0.6)
            st.plotly_chart(fig, use_container_width=True)

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.subheader("Τμήματα vs Σύνολο Μαθητών")
            fig = px.scatter(unique_df, x='Αριθμός Τμημάτων', y='Σύνολο', color='Είδος Σχολείου', trendline='ols', color_discrete_sequence=px.colors.qualitative.Set1, opacity=0.6)
            st.plotly_chart(fig, use_container_width=True)
        with row2_col2:
            st.subheader("Αγόρια vs Κορίτσια")
            fig = px.scatter(unique_df, x='Αγόρια', y='Κορίτσια', color='Είδος Σχολείου', trendline='ols', color_discrete_sequence=px.colors.qualitative.Set1, opacity=0.6)
            st.plotly_chart(fig, use_container_width=True)

    with tab5:
        st.header("📋 Πίνακας Δεδομένων Μαθητών")
        st.write(f"Εμφανίζονται {len(filtered_students)} εγγραφές")
        all_columns = filtered_students.columns.tolist()
        selected_columns = st.multiselect("Επιλέξτε Στήλες (Μαθητές)", options=all_columns, default=all_columns)
        st.dataframe(filtered_students[selected_columns], use_container_width=True, height=600)

# ==================== ΚΑΡΤΕΛΑ 2: ΕΚΠΑΙΔΕΥΤΙΚΟΙ ====================
with main_tab2:
    unique_df = filtered_teachers.copy()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Γενικά Στατιστικά",
        "👨‍🏫 Ειδικότητες & Ωράρια",
        "🏫 Κατανομή ανά Σχολείο",
        "🔗 Συσχετίσεις",
        "📋 Πίνακας Δεδομένων"
    ])

    with tab1:
        st.header("Γενικά Στατιστικά Εκπαιδευτικών")
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.subheader("Κατανομή ανά Φύλο")
            gender_counts = filtered_teachers['Φύλο'].value_counts().reset_index()
            gender_counts.columns = ['Φύλο', 'Πλήθος']
            gender_map = {'Α': 'Άνδρας', 'Θ': 'Γυναίκα'}
            gender_counts['Φύλο'] = gender_counts['Φύλο'].map(gender_map)
            fig = px.pie(gender_counts, values='Πλήθος', names='Φύλο', hole=0.4, color_discrete_sequence=['#66b3ff', '#ff9999'])
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        with row1_col2:
            st.subheader("Κατανομή ανά Σχέση Τοποθέτησης")
            placement_counts = filtered_teachers['Σχέση Τοποθέτησης'].value_counts().reset_index()
            placement_counts.columns = ['Σχέση Τοποθέτησης', 'Πλήθος']
            fig = px.pie(placement_counts, values='Πλήθος', names='Σχέση Τοποθέτησης', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.subheader("Κατανομή ανά Περιφερειακή Ενότητα")
            region_counts = filtered_teachers['Περιφερειακή Ενότητα'].value_counts().reset_index()
            region_counts.columns = ['Περιφερειακή Ενότητα', 'Πλήθος']
            fig = px.bar(region_counts, x='Περιφερειακή Ενότητα', y='Πλήθος', color='Περιφερειακή Ενότητα', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with row2_col2:
            st.subheader("Κατανομή ανά Διεύθυνση")
            dir_counts = filtered_teachers['Διεύθυνση'].value_counts().reset_index()
            dir_counts.columns = ['Διεύθυνση', 'Πλήθος']
            fig = px.bar(dir_counts, x='Διεύθυνση', y='Πλήθος', color='Διεύθυνση', color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("👨‍🏫 Ειδικότητες και Ωράρια Εκπαιδευτικών")
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.subheader("Κατανομή Ειδικοτήτων (Top 15)")
            specialty_counts = filtered_teachers['Κωδ. Ειδικότητας'].value_counts().head(15).reset_index()
            specialty_counts.columns = ['Κωδ. Ειδικότητας', 'Πλήθος']
            fig = px.bar(specialty_counts, x='Πλήθος', y='Κωδ. Ειδικότητας', orientation='h', color='Πλήθος', color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
        with row1_col2:
            st.subheader("Κατανομή Υποχρεωτικού Ωραρίου")
            fig = px.histogram(filtered_teachers, x='Υποχρεωτικό Διδακτικό Ωράριο Υπηρέτησης', nbins=25, color_discrete_sequence=['#3366cc'])
            fig.update_layout(bargap=0.05)
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.header("🏫 Κατανομή Εκπαιδευτικών ανά Σχολείο")
        st.subheader("Σύνολο Εκπαιδευτικών ανά Περιφερειακή Ενότητα")
        teachers_by_region = filtered_teachers.groupby('Περιφερειακή Ενότητα').size().reset_index(name='Πλήθος')
        fig = px.bar(teachers_by_region, x='Περιφερειακή Ενότητα', y='Πλήθος', color='Περιφερειακή Ενότητα', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.header("🔗 Συσχετίσεις Μεταβλητών")
        st.subheader("Κατανομή Ωραρίου ανά Φύλο και Σχέση Τοποθέτησης")
        fig = px.box(filtered_teachers, x='Σχέση Τοποθέτησης', y='Υποχρεωτικό Διδακτικό Ωράριο Υπηρέτησης', color='Φύλο', color_discrete_map={'Α': '#66b3ff', 'Θ': '#ff9999'})
        fig.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    with tab5:
        st.header("📋 Πίνακας Δεδομένων Εκπαιδευτικών")
        st.write(f"Εμφανίζονται {len(filtered_teachers)} εγγραφές")
        all_columns_t = filtered_teachers.columns.tolist()
        selected_columns_t = st.multiselect("Επιλέξτε Στήλες (Εκπαιδευτικοί)", options=all_columns_t, default=all_columns_t)
        st.dataframe(filtered_teachers[selected_columns_t], use_container_width=True, height=600)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888;">
    <p>🏫 Dashboard Οπτικοποίησης Σχολικών Δεδομένων | PDE PELOPONNESE - Streamlit & Plotly</p>
</div>
""", unsafe_allow_html=True)

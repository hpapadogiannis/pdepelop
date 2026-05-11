
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
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_excel("Query1.xlsx")
    # Clean AFM column
    df['ΑΦΜ'] = df['ΑΦΜ'].astype(str).str.replace('"="', '').str.replace('""', '"').str.strip('"')
    # Fill NaN for numeric assignment columns with 0 for visualization
    for col in ['Α Ανάθεση Συνολικά', 'Β Ανάθεση Συνολικά', 'Γ Ανάθεση Συνολικά', 
                'Προσθ Τμημ Συνολικά', 'Άλλες Αναθέσεις Συνολικά']:
        df[col] = df[col].fillna(0)
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Φίλτρα Δεδομένων")

selected_direction = st.sidebar.multiselect(
    "Διεύθυνση", 
    options=sorted(df['Διεύθυνση'].unique()),
    default=[]
)

selected_school_type = st.sidebar.multiselect(
    "Είδος Σχολείου",
    options=sorted(df['Είδος Σχολείου'].unique()),
    default=[]
)

selected_school_subtype = st.sidebar.multiselect(
    "Τύπος Σχολείου",
    options=sorted(df['Τύπος Σχολείου'].unique()),
    default=[]
)

selected_region = st.sidebar.multiselect(
    "Περιφερειακή Ενότητα",
    options=sorted(df['Περιφερειακή Ενότητα'].unique()),
    default=[]
)

selected_municipality = st.sidebar.multiselect(
    "Δήμος",
    options=sorted(df['Δήμος'].unique()),
    default=[]
)

selected_gender = st.sidebar.multiselect(
    "Φύλο Εκπαιδευτικού",
    options=sorted(df['Φύλο'].unique()),
    default=[]
)

selected_specialty = st.sidebar.multiselect(
    "Κωδικός Κύριας Ειδικότητας",
    options=sorted(df['Κωδικός Κύριας Ειδικότητας'].unique()),
    default=[]
)

selected_employment = st.sidebar.multiselect(
    "Σχέση Εργασίας",
    options=sorted(df['Σχέση Εργασίας'].unique()),
    default=[]
)

selected_placement = st.sidebar.multiselect(
    "Σχέση Τοποθέτησης",
    options=sorted(df['Σχέση Τοποθέτησης'].unique()),
    default=[]
)

# Apply filters
filtered_df = df.copy()
if selected_direction:
    filtered_df = filtered_df[filtered_df['Διεύθυνση'].isin(selected_direction)]
if selected_school_type:
    filtered_df = filtered_df[filtered_df['Είδος Σχολείου'].isin(selected_school_type)]
if selected_school_subtype:
    filtered_df = filtered_df[filtered_df['Τύπος Σχολείου'].isin(selected_school_subtype)]
if selected_region:
    filtered_df = filtered_df[filtered_df['Περιφερειακή Ενότητα'].isin(selected_region)]
if selected_municipality:
    filtered_df = filtered_df[filtered_df['Δήμος'].isin(selected_municipality)]
if selected_gender:
    filtered_df = filtered_df[filtered_df['Φύλο'].isin(selected_gender)]
if selected_specialty:
    filtered_df = filtered_df[filtered_df['Κωδικός Κύριας Ειδικότητας'].isin(selected_specialty)]
if selected_employment:
    filtered_df = filtered_df[filtered_df['Σχέση Εργασίας'].isin(selected_employment)]
if selected_placement:
    filtered_df = filtered_df[filtered_df['Σχέση Τοποθέτησης'].isin(selected_placement)]

# Header
st.markdown('<div class="main-header">🏫 Οπτικοποίηση Σχολικών Δεδομένων</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Πλήρης ανάλυση και οπτικοποίηση όλων των μεταβλητών του αρχείου</div>', unsafe_allow_html=True)

# Metrics row
st.subheader("📊 Βασικά Μεγέθη")
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("Συνολικές Εγγραφές", len(filtered_df))
with col2:
    st.metric("Μοναδικά Σχολεία", filtered_df['Ονομασία Σχολείου'].nunique())
with col3:
    st.metric("Μοναδικοί Εκπαιδευτικοί", filtered_df['ΑΦΜ'].nunique())
with col4:
    st.metric("Σύνολο Μαθητών", int(filtered_df['Σύνολο'].sum()))
with col5:
    st.metric("Σύνολο Αγοριών", int(filtered_df['Αγόρια'].sum()))
with col6:
    st.metric("Σύνολο Κοριτσιών", int(filtered_df['Κορίτσια'].sum()))

st.divider()

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 Γενικά Στατιστικά", 
    "🏫 Στοιχεία Σχολείων", 
    "👨‍🏫 Εκπαιδευτικοί",
    "📚 Μαθητές",
    "⏱️ Ωράριο & Αναθέσεις",
    "🔗 Συσχετίσεις",
    "📋 Πίνακας Δεδομένων"
])

# ==================== TAB 1: Γενικά Στατιστικά ====================
with tab1:
    st.header("Γενικά Στατιστικά")

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("Κατανομή ανά Είδος Σχολείου")
        school_type_counts = filtered_df['Είδος Σχολείου'].value_counts().reset_index()
        school_type_counts.columns = ['Είδος Σχολείου', 'Πλήθος']
        fig = px.pie(school_type_counts, values='Πλήθος', names='Είδος Σχολείου', 
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with row1_col2:
        st.subheader("Κατανομή ανά Περιφερειακή Ενότητα")
        region_counts = filtered_df['Περιφερειακή Ενότητα'].value_counts().reset_index()
        region_counts.columns = ['Περιφερειακή Ενότητα', 'Πλήθος']
        fig = px.bar(region_counts, x='Περιφερειακή Ενότητα', y='Πλήθος', 
                     color='Περιφερειακή Ενότητα', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("Κατανομή ανά Διεύθυνση")
        dir_counts = filtered_df['Διεύθυνση'].value_counts().reset_index()
        dir_counts.columns = ['Διεύθυνση', 'Πλήθος']
        fig = px.bar(dir_counts, x='Διεύθυνση', y='Πλήθος', 
                     color='Διεύθυνση', color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with row2_col2:
        st.subheader("Κατανομή ανά Τύπο Σχολείου (Top 15)")
        type_counts = filtered_df['Τύπος Σχολείου'].value_counts().head(15).reset_index()
        type_counts.columns = ['Τύπος Σχολείου', 'Πλήθος']
        fig = px.bar(type_counts, x='Πλήθος', y='Τύπος Σχολείου', orientation='h',
                     color='Πλήθος', color_continuous_scale='Viridis')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    row3_col1, row3_col2 = st.columns(2)

    with row3_col1:
        st.subheader("Κατανομή ανά Δήμο (Top 15)")
        mun_counts = filtered_df['Δήμος'].value_counts().head(15).reset_index()
        mun_counts.columns = ['Δήμος', 'Πλήθος']
        fig = px.bar(mun_counts, x='Πλήθος', y='Δήμος', orientation='h',
                     color='Πλήθος', color_continuous_scale='Plasma')
        st.plotly_chart(fig, use_container_width=True)

    with row3_col2:
        st.subheader("Σχέση Εργασίας")
        emp_counts = filtered_df['Σχέση Εργασίας'].value_counts().reset_index()
        emp_counts.columns = ['Σχέση Εργασίας', 'Πλήθος']
        fig = px.pie(emp_counts, values='Πλήθος', names='Σχέση Εργασίας',
                     color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 2: Στοιχεία Σχολείων ====================
with tab2:
    st.header("Στοιχεία Σχολείων")

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("Αριθμός Τμημάτων ανά Σχολείο")
        fig = px.histogram(filtered_df, x='Αριθμός Τμημάτων', nbins=30,
                          color='Είδος Σχολείου', barmode='stack',
                          color_discrete_sequence=px.colors.qualitative.Set1)
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig, use_container_width=True)

    with row1_col2:
        st.subheader("Κατανομή Τμημάτων ανά Είδος Σχολείου")
        sections_by_type = filtered_df.groupby('Είδος Σχολείου')['Αριθμός Τμημάτων'].sum().reset_index()
        fig = px.pie(sections_by_type, values='Αριθμός Τμημάτων', names='Είδος Σχολείου',
                     color_discrete_sequence=px.colors.qualitative.Set1)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("Μέσος Αριθμός Τμημάτων ανά Τύπο Σχολείου")
        avg_sections = filtered_df.groupby('Τύπος Σχολείου')['Αριθμός Τμημάτων'].mean().sort_values(ascending=False).head(15).reset_index()
        avg_sections.columns = ['Τύπος Σχολείου', 'Μέσος Όρος Τμημάτων']
        fig = px.bar(avg_sections, x='Μέσος Όρος Τμημάτων', y='Τύπος Σχολείου', orientation='h',
                     color='Μέσος Όρος Τμημάτων', color_continuous_scale='Inferno')
        st.plotly_chart(fig, use_container_width=True)

    with row2_col2:
        st.subheader("Μέσος Αριθμός Τμημάτων ανά Περιφερειακή Ενότητα")
        avg_sections_region = filtered_df.groupby('Περιφερειακή Ενότητα')['Αριθμός Τμημάτων'].mean().sort_values(ascending=False).reset_index()
        avg_sections_region.columns = ['Περιφερειακή Ενότητα', 'Μέσος Όρος Τμημάτων']
        fig = px.bar(avg_sections_region, x='Περιφερειακή Ενότητα', y='Μέσος Όρος Τμημάτων',
                     color='Περιφερειακή Ενότητα', color_discrete_sequence=px.colors.qualitative.Dark24)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Ανάλυση Σχολείων ανά Περιφερειακή Ενότητα και Είδος")
    pivot_schools = filtered_df.pivot_table(
        index='Περιφερειακή Ενότητα', 
        columns='Είδος Σχολείου', 
        values='Ονομασία Σχολείου', 
        aggfunc='nunique'
    ).fillna(0)
    fig = px.imshow(pivot_schools, text_auto=True, aspect="auto",
                    color_continuous_scale='Blues')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 3: Εκπαιδευτικοί ====================
with tab3:
    st.header("👨‍🏫 Στοιχεία Εκπαιδευτικών")

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("Φύλο Εκπαιδευτικών")
        gender_counts = filtered_df['Φύλο'].value_counts().reset_index()
        gender_counts.columns = ['Φύλο', 'Πλήθος']
        colors = {'Θ': '#ff9999', 'Α': '#66b3ff'}
        fig = px.pie(gender_counts, values='Πλήθος', names='Φύλο',
                     color='Φύλο', color_discrete_map=colors)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with row1_col2:
        st.subheader("Κύριες Ειδικότητες (Top 15)")
        spec_counts = filtered_df['Κωδικός Κύριας Ειδικότητας'].value_counts().head(15).reset_index()
        spec_counts.columns = ['Ειδικότητα', 'Πλήθος']
        fig = px.bar(spec_counts, x='Πλήθος', y='Ειδικότητα', orientation='h',
                     color='Πλήθος', color_continuous_scale='Turbo')
        st.plotly_chart(fig, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("Σχέση Τοποθέτησης")
        place_counts = filtered_df['Σχέση Τοποθέτησης'].value_counts().reset_index()
        place_counts.columns = ['Σχέση Τοποθέτησης', 'Πλήθος']
        fig = px.bar(place_counts, x='Σχέση Τοποθέτησης', y='Πλήθος',
                     color='Σχέση Τοποθέτησης', color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    with row2_col2:
        st.subheader("Κατανομή Φύλου ανά Είδος Σχολείου")
        gender_school = filtered_df.groupby(['Είδος Σχολείου', 'Φύλο']).size().reset_index(name='Πλήθος')
        fig = px.bar(gender_school, x='Είδος Σχολείου', y='Πλήθος', color='Φύλο',
                     barmode='group', color_discrete_map=colors)
        fig.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    row3_col1, row3_col2 = st.columns(2)

    with row3_col1:
        st.subheader("Ειδικότητες ανά Είδος Σχολείου (Top 10)")
        spec_school = filtered_df.groupby(['Είδος Σχολείου', 'Κωδικός Κύριας Ειδικότητας']).size().reset_index(name='Πλήθος')
        spec_school = spec_school.sort_values('Πλήθος', ascending=False).head(10)
        fig = px.bar(spec_school, x='Πλήθος', y='Κωδικός Κύριας Ειδικότητας', 
                     color='Είδος Σχολείου', orientation='h',
                     color_discrete_sequence=px.colors.qualitative.Vivid)
        st.plotly_chart(fig, use_container_width=True)

    with row3_col2:
        st.subheader("Σχέση Εργασίας ανά Φύλο")
        emp_gender = filtered_df.groupby(['Σχέση Εργασίας', 'Φύλο']).size().reset_index(name='Πλήθος')
        fig = px.bar(emp_gender, x='Σχέση Εργασίας', y='Πλήθος', color='Φύλο',
                     barmode='group', color_discrete_map=colors)
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Υποχρεωτικό Διδακτικό Ωράριο Υπηρέτησης")
    fig = px.histogram(filtered_df, x='Υποχρεωτικό Διδακτικό Ωράριο Υπηρέτησης',
                      color='Είδος Σχολείου', nbins=20, barmode='stack',
                      color_discrete_sequence=px.colors.qualitative.Safe)
    fig.update_layout(bargap=0.1)
    st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 4: Μαθητές ====================
with tab4:
    st.header("📚 Στοιχεία Μαθητών")

    row1_col1, row1_col2, row1_col3 = st.columns(3)

    with row1_col1:
        st.subheader("Κατανομή Συνόλου Μαθητών")
        fig = px.histogram(filtered_df, x='Σύνολο', nbins=50, 
                          color_discrete_sequence=['#3366cc'])
        fig.update_layout(bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)

    with row1_col2:
        st.subheader("Κατανομή Αγοριών")
        fig = px.histogram(filtered_df, x='Αγόρια', nbins=50,
                          color_discrete_sequence=['#66b3ff'])
        fig.update_layout(bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)

    with row1_col3:
        st.subheader("Κατανομή Κοριτσιών")
        fig = px.histogram(filtered_df, x='Κορίτσια', nbins=50,
                          color_discrete_sequence=['#ff9999'])
        fig.update_layout(bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("Σύνολο Μαθητών ανά Είδος Σχολείου")
        students_by_type = filtered_df.groupby('Είδος Σχολείου')['Σύνολο'].sum().reset_index()
        fig = px.pie(students_by_type, values='Σύνολο', names='Είδος Σχολείου',
                     color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with row2_col2:
        st.subheader("Σύνολο Μαθητών ανά Περιφερειακή Ενότητα")
        students_by_region = filtered_df.groupby('Περιφερειακή Ενότητα')['Σύνολο'].sum().reset_index()
        fig = px.bar(students_by_region, x='Περιφερειακή Ενότητα', y='Σύνολο',
                     color='Περιφερειακή Ενότητα', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    row3_col1, row3_col2 = st.columns(2)

    with row3_col1:
        st.subheader("Αγόρια vs Κορίτσια ανά Είδος Σχολείου")
        gender_students = filtered_df.groupby('Είδος Σχολείου')[['Αγόρια', 'Κορίτσια']].sum().reset_index()
        gender_students_melted = gender_students.melt(id_vars='Είδος Σχολείου', 
                                                       var_name='Φύλο Μαθητή', value_name='Πλήθος')
        fig = px.bar(gender_students_melted, x='Είδος Σχολείου', y='Πλήθος', 
                     color='Φύλο Μαθητή', barmode='group',
                     color_discrete_map={'Αγόρια': '#66b3ff', 'Κορίτσια': '#ff9999'})
        fig.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    with row3_col2:
        st.subheader("Αναλογία Αγοριών/Κοριτσιών ανά Περιφερειακή Ενότητα")
        ratio_df = filtered_df.groupby('Περιφερειακή Ενότητα')[['Αγόρια', 'Κορίτσια']].sum().reset_index()
        ratio_df['Αναλογία Αγόρια/Κορίτσια'] = ratio_df['Αγόρια'] / ratio_df['Κορίτσια']
        fig = px.bar(ratio_df, x='Περιφερειακή Ενότητα', y='Αναλογία Αγόρια/Κορίτσια',
                     color='Αναλογία Αγόρια/Κορίτσια', color_continuous_scale='RdBu',
                     color_continuous_midpoint=1)
        fig.add_hline(y=1, line_dash="dash", line_color="black")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Μαθητές ανά Δήμο (Top 15)")
    students_by_mun = filtered_df.groupby('Δήμος')[['Αγόρια', 'Κορίτσια', 'Σύνολο']].sum().sort_values('Σύνολο', ascending=False).head(15).reset_index()
    students_by_mun_melted = students_by_mun.melt(id_vars='Δήμος', var_name='Κατηγορία', value_name='Πλήθος')
    fig = px.bar(students_by_mun_melted, x='Δήμος', y='Πλήθος', color='Κατηγορία',
                 barmode='group', color_discrete_map={'Αγόρια': '#66b3ff', 'Κορίτσια': '#ff9999', 'Σύνολο': '#99cc00'})
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 5: Ωράριο & Αναθέσεις ====================
with tab5:
    st.header("⏱️ Υποχρεωτικό Ωράριο & Αναθέσεις")

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("Κατανομή Ωραρίου Υπηρέτησης")
        fig = px.box(filtered_df, x='Είδος Σχολείου', y='Υποχρεωτικό Διδακτικό Ωράριο Υπηρέτησης',
                     color='Είδος Σχολείου', color_discrete_sequence=px.colors.qualitative.Set1)
        fig.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    with row1_col2:
        st.subheader("Μέσο Ωράριο ανά Σχέση Εργασίας")
        avg_hours = filtered_df.groupby('Σχέση Εργασίας')['Υποχρεωτικό Διδακτικό Ωράριο Υπηρέτησης'].mean().sort_values(ascending=False).reset_index()
        avg_hours.columns = ['Σχέση Εργασίας', 'Μέσο Ωράριο']
        fig = px.bar(avg_hours, x='Σχέση Εργασίας', y='Μέσο Ωράριο',
                     color='Μέσο Ωράριο', color_continuous_scale='Magma')
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("Α Ανάθεση Συνολικά")
        fig = px.histogram(filtered_df[filtered_df['Α Ανάθεση Συνολικά'] > 0], 
                          x='Α Ανάθεση Συνολικά', nbins=30,
                          color='Είδος Σχολείου', barmode='stack',
                          color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig, use_container_width=True)

    with row2_col2:
        st.subheader("Β Ανάθεση Συνολικά")
        fig = px.histogram(filtered_df[filtered_df['Β Ανάθεση Συνολικά'] > 0], 
                          x='Β Ανάθεση Συνολικά', nbins=20,
                          color='Είδος Σχολείου', barmode='stack',
                          color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig, use_container_width=True)

    row3_col1, row3_col2 = st.columns(2)

    with row3_col1:
        st.subheader("Προσθετικά Τμήματα")
        fig = px.histogram(filtered_df[filtered_df['Προσθ Τμημ Συνολικά'] > 0], 
                          x='Προσθ Τμημ Συνολικά', nbins=20,
                          color='Είδος Σχολείου', barmode='stack',
                          color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig, use_container_width=True)

    with row3_col2:
        st.subheader("Άλλες Αναθέσεις")
        fig = px.histogram(filtered_df[filtered_df['Άλλες Αναθέσεις Συνολικά'] > 0], 
                          x='Άλλες Αναθέσεις Συνολικά', nbins=20,
                          color='Είδος Σχολείου', barmode='stack',
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Συνολικές Αναθέσεις ανά Εκπαιδευτικό (Top 20)")
    assignments = filtered_df.groupby('ΑΦΜ')[['Α Ανάθεση Συνολικά', 'Β Ανάθεση Συνολικά', 
                                               'Γ Ανάθεση Συνολικά', 'Προσθ Τμημ Συνολικά', 
                                               'Άλλες Αναθέσεις Συνολικά']].sum()
    assignments['Σύνολο Αναθέσεων'] = assignments.sum(axis=1)
    top_assignments = assignments.sort_values('Σύνολο Αναθέσεων', ascending=False).head(20).reset_index()
    top_assignments_melted = top_assignments.melt(
        id_vars='ΑΦΜ', 
        value_vars=['Α Ανάθεση Συνολικά', 'Β Ανάθεση Συνολικά', 'Γ Ανάθεση Συνολικά', 
                    'Προσθ Τμημ Συνολικά', 'Άλλες Αναθέσεις Συνολικά'],
        var_name='Τύπος Ανάθεσης', value_name='Ώρες'
    )
    fig = px.bar(top_assignments_melted, x='ΑΦΜ', y='Ώρες', color='Τύπος Ανάθεσης',
                 barmode='stack', color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Συσχέτιση Ωραρίου με Αναθέσεις")
    fig = px.scatter(filtered_df, x='Υποχρεωτικό Διδακτικό Ωράριο Υπηρέτησης', 
                     y='Α Ανάθεση Συνολικά', color='Είδος Σχολείου',
                     size='Σύνολο', hover_data=['Ονομασία Σχολείου'],
                     color_discrete_sequence=px.colors.qualitative.Set1,
                     opacity=0.6)
    st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 6: Συσχετίσεις ====================
with tab6:
    st.header("🔗 Συσχετίσεις Μεταβλητών")

    numeric_cols = ['Αριθμός Τμημάτων', 'Αγόρια', 'Κορίτσια', 'Σύνολο', 
                    'Υποχρεωτικό Διδακτικό Ωράριο Υπηρέτησης',
                    'Α Ανάθεση Συνολικά', 'Β Ανάθεση Συνολικά', 
                    'Προσθ Τμημ Συνολικά', 'Άλλες Αναθέσεις Συνολικά']

    corr_matrix = filtered_df[numeric_cols].corr()

    st.subheader("Πίνακας Συσχέτισης")
    fig = px.imshow(corr_matrix, text_auto='.2f', aspect="auto",
                    color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
    fig.update_layout(height=700)
    st.plotly_chart(fig, use_container_width=True)

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("Αγόρια vs Σύνολο Μαθητών")
        fig = px.scatter(filtered_df, x='Αγόρια', y='Σύνολο', 
                         color='Είδος Σχολείου', trendline='ols',
                         color_discrete_sequence=px.colors.qualitative.Set1,
                         opacity=0.6)
        st.plotly_chart(fig, use_container_width=True)

    with row1_col2:
        st.subheader("Κορίτσια vs Σύνολο Μαθητών")
        fig = px.scatter(filtered_df, x='Κορίτσια', y='Σύνολο', 
                         color='Είδος Σχολείου', trendline='ols',
                         color_discrete_sequence=px.colors.qualitative.Set1,
                         opacity=0.6)
        st.plotly_chart(fig, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("Τμήματα vs Σύνολο Μαθητών")
        fig = px.scatter(filtered_df, x='Αριθμός Τμημάτων', y='Σύνολο', 
                         color='Είδος Σχολείου', trendline='ols',
                         color_discrete_sequence=px.colors.qualitative.Set1,
                         opacity=0.6)
        st.plotly_chart(fig, use_container_width=True)

    with row2_col2:
        st.subheader("Αγόρια vs Κορίτσια")
        fig = px.scatter(filtered_df, x='Αγόρια', y='Κορίτσια', 
                         color='Είδος Σχολείου', trendline='ols',
                         color_discrete_sequence=px.colors.qualitative.Set1,
                         opacity=0.6)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Pair Plot - Βασικές Μετρήσεις")
    pair_cols = ['Αριθμός Τμημάτων', 'Αγόρια', 'Κορίτσια', 'Σύνολο']
    fig = px.scatter_matrix(filtered_df, dimensions=pair_cols, 
                            color='Είδος Σχολείου',
                            color_discrete_sequence=px.colors.qualitative.Set1,
                            opacity=0.5)
    fig.update_layout(height=800)
    st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 7: Πίνακας Δεδομένων ====================
with tab7:
    st.header("📋 Πίνακας Δεδομένων")

    st.write(f"Εμφανίζονται {len(filtered_df)} από {len(df)} εγγραφές")

    # Column selector
    all_columns = filtered_df.columns.tolist()
    selected_columns = st.multiselect("Επιλέξτε Στήλες", options=all_columns, default=all_columns)

    # Show dataframe
    st.dataframe(filtered_df[selected_columns], use_container_width=True, height=600)

    # Download button
    csv = filtered_df[selected_columns].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Λήψη CSV",
        data=csv,
        file_name='filtered_school_data.csv',
        mime='text/csv'
    )

    # Summary statistics
    st.subheader("Στατιστικά Στοιχεία Αριθμητικών Μεταβλητών")
    st.dataframe(filtered_df[selected_columns].describe(), use_container_width=True)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888;">
    <p>🏫 Dashboard Οπτικοποίησης Σχολικών Δεδομένων | Δημιουργήθηκε με Streamlit & Plotly</p>
</div>
""", unsafe_allow_html=True)

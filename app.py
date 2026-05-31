import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Hospital Dashboard",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Hospital Management Dashboard")
st.markdown("Patient analytics, doctor performance, "
            "department insights and disease trends.")
st.markdown("---")

# Generate hospital dataset
@st.cache_data
def generate_data():
    np.random.seed(42)
    n = 1000

    departments = {
        'Cardiology':    {'doctors': 8,  'base_patients': 25},
        'Orthopedics':   {'doctors': 6,  'base_patients': 20},
        'Neurology':     {'doctors': 5,  'base_patients': 15},
        'Pediatrics':    {'doctors': 7,  'base_patients': 30},
        'Gynecology':    {'doctors': 6,  'base_patients': 22},
        'Emergency':     {'doctors': 12, 'base_patients': 50},
        'Oncology':      {'doctors': 4,  'base_patients': 12},
        'Dermatology':   {'doctors': 3,  'base_patients': 18},
        'Ophthalmology': {'doctors': 4,  'base_patients': 15},
        'ENT':           {'doctors': 3,  'base_patients': 12}
    }

    diseases = {
        'Cardiology':  ['Heart Disease', 'Hypertension',
                        'Arrhythmia', 'Heart Failure'],
        'Orthopedics': ['Fracture', 'Arthritis',
                        'Back Pain', 'Joint Replacement'],
        'Neurology':   ['Migraine', 'Epilepsy',
                        'Stroke', 'Parkinson\'s'],
        'Pediatrics':  ['Fever', 'Pneumonia',
                        'Malnutrition', 'Dengue'],
        'Gynecology':  ['PCOS', 'Pregnancy Complications',
                        'Endometriosis', 'Fibroids'],
        'Emergency':   ['Trauma', 'Chest Pain',
                        'Poisoning', 'Burns'],
        'Oncology':    ['Breast Cancer', 'Lung Cancer',
                        'Blood Cancer', 'Cervical Cancer'],
        'Dermatology': ['Psoriasis', 'Eczema',
                        'Acne', 'Fungal Infection'],
        'Ophthalmology':['Cataract', 'Glaucoma',
                         'Diabetic Retinopathy', 'Myopia'],
        'ENT':         ['Sinusitis', 'Tonsillitis',
                        'Hearing Loss', 'Vertigo']
    }

    # Patient records
    start_date = datetime(2023, 1, 1)
    rows       = []

    for i in range(n):
        dept    = np.random.choice(
            list(departments.keys()))
        disease = np.random.choice(
            diseases[dept])
        age     = np.random.randint(1, 85)
        gender  = np.random.choice(
            ['Male', 'Female'])
        days_offset = np.random.randint(0, 365)
        admit_date  = start_date + \
            timedelta(days=days_offset)
        stay_days   = np.random.randint(1, 15)
        discharge   = admit_date + \
            timedelta(days=stay_days)
        bill        = np.random.randint(
            5000, 200000)
        status      = np.random.choice(
            ['Discharged', 'Admitted',
             'Critical', 'Recovered'],
            p=[0.60, 0.20, 0.05, 0.15])
        blood_group = np.random.choice(
            ['A+', 'B+', 'O+', 'AB+',
             'A-', 'B-', 'O-', 'AB-'])
        severity    = np.random.choice(
            ['Mild', 'Moderate', 'Severe'],
            p=[0.45, 0.35, 0.20])
        doctor_no   = np.random.randint(
            1, departments[dept]['doctors'] + 1)
        doctor_name = f"Dr. {dept[:3]}{doctor_no:02d}"

        rows.append({
            'patient_id':  f"P{i+1:04d}",
            'age':         age,
            'gender':      gender,
            'department':  dept,
            'disease':     disease,
            'admit_date':  admit_date,
            'discharge':   discharge,
            'stay_days':   stay_days,
            'bill':        bill,
            'status':      status,
            'blood_group': blood_group,
            'severity':    severity,
            'doctor':      doctor_name,
            'month':       admit_date.month,
            'quarter':     (admit_date.month - 1)
                           // 3 + 1
        })

    return pd.DataFrame(rows)

df = generate_data()

# Sidebar
st.sidebar.header("🔍 Filters")
dept_filter = st.sidebar.multiselect(
    "Department:",
    df['department'].unique(),
    default=df['department'].unique()
)
status_filter = st.sidebar.multiselect(
    "Status:",
    df['status'].unique(),
    default=df['status'].unique()
)
severity_filter = st.sidebar.multiselect(
    "Severity:",
    df['severity'].unique(),
    default=df['severity'].unique()
)

filtered = df[
    (df['department'].isin(dept_filter)) &
    (df['status'].isin(status_filter)) &
    (df['severity'].isin(severity_filter))
].copy()

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🏥 Departments",
    "👨‍⚕️ Doctors",
    "🦠 Diseases",
    "💰 Revenue"
])

# Tab 1 — Overview
with tab1:
    st.markdown("### 📊 Hospital Overview")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Patients",
              f"{len(filtered):,}")
    c2.metric("Admitted",
              len(filtered[
                  filtered['status'] == 'Admitted']))
    c3.metric("Critical",
              len(filtered[
                  filtered['status'] == 'Critical']))
    c4.metric("Avg Stay (days)",
              f"{filtered['stay_days'].mean():.1f}")
    c5.metric("Total Revenue",
              f"₹{filtered['bill'].sum()/1e7:.2f}Cr")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        # Monthly admissions
        monthly = filtered.groupby(
            'month').size().reset_index(
            name='patients')
        month_names = ['Jan', 'Feb', 'Mar',
                       'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep',
                       'Oct', 'Nov', 'Dec']
        monthly['month_name'] = monthly[
            'month'].apply(
            lambda x: month_names[x-1])

        fig = px.area(
            monthly,
            x='month_name',
            y='patients',
            title='Monthly Patient Admissions',
            color_discrete_sequence=['#3498db']
        )
        fig.update_layout(
            height=350,
            template='plotly_white',
            xaxis_title='Month',
            yaxis_title='Patients'
        )
        st.plotly_chart(fig,
                        use_container_width=True)

    with col2:
        # Status distribution
        status_counts = filtered[
            'status'].value_counts()
        status_colors = {
            'Discharged': '#2ecc71',
            'Recovered':  '#27ae60',
            'Admitted':   '#3498db',
            'Critical':   '#e74c3c'
        }
        fig2 = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title='Patient Status Distribution',
            color=status_counts.index,
            color_discrete_map=status_colors
        )
        fig2.update_layout(height=350)
        st.plotly_chart(fig2,
                        use_container_width=True)

    # Age distribution
    col3, col4 = st.columns(2)

    with col3:
        fig3 = px.histogram(
            filtered, x='age',
            nbins=20,
            color='gender',
            title='Patient Age Distribution',
            barmode='overlay',
            color_discrete_map={
                'Male':   '#3498db',
                'Female': '#e91e63'
            }
        )
        fig3.update_layout(
            height=320,
            template='plotly_white'
        )
        st.plotly_chart(fig3,
                        use_container_width=True)

    with col4:
        severity_counts = filtered[
            'severity'].value_counts()
        fig4 = px.pie(
            values=severity_counts.values,
            names=severity_counts.index,
            title='Severity Distribution',
            color=severity_counts.index,
            color_discrete_map={
                'Mild':     '#2ecc71',
                'Moderate': '#f39c12',
                'Severe':   '#e74c3c'
            }
        )
        fig4.update_layout(height=320)
        st.plotly_chart(fig4,
                        use_container_width=True)

# Tab 2 — Departments
with tab2:
    st.markdown("### 🏥 Department Analysis")

    dept_stats = filtered.groupby(
        'department').agg(
        patients=('patient_id', 'count'),
        avg_stay=('stay_days', 'mean'),
        avg_bill=('bill', 'mean'),
        total_revenue=('bill', 'sum')
    ).reset_index().sort_values(
        'patients', ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        fig5 = px.bar(
            dept_stats,
            x='patients',
            y='department',
            orientation='h',
            title='Patients by Department',
            color='patients',
            color_continuous_scale='Blues'
        )
        fig5.update_layout(
            height=450,
            template='plotly_white',
            xaxis_title='Patient Count'
        )
        st.plotly_chart(fig5,
                        use_container_width=True)

    with col2:
        fig6 = px.bar(
            dept_stats,
            x='avg_stay',
            y='department',
            orientation='h',
            title='Avg Stay Days by Department',
            color='avg_stay',
            color_continuous_scale='Oranges'
        )
        fig6.update_layout(
            height=450,
            template='plotly_white',
            xaxis_title='Avg Stay (Days)'
        )
        st.plotly_chart(fig6,
                        use_container_width=True)

    # Dept severity heatmap
    st.markdown("#### 🔥 Severity by Department")
    dept_sev = filtered.groupby(
        ['department', 'severity']
    ).size().unstack(fill_value=0)

    fig7 = px.imshow(
        dept_sev,
        title='Patient Count: Dept × Severity',
        color_continuous_scale='RdYlGn_r',
        labels=dict(color='Patients')
    )
    fig7.update_layout(
        height=400,
        template='plotly_white'
    )
    st.plotly_chart(fig7,
                    use_container_width=True)

    st.markdown("#### 📋 Department Summary")
    dept_display = dept_stats.copy()
    dept_display['avg_stay'] = \
        dept_display['avg_stay'].round(1)
    dept_display['avg_bill'] = \
        dept_display['avg_bill'].apply(
            lambda x: f"₹{x:,.0f}")
    dept_display['total_revenue'] = \
        dept_display['total_revenue'].apply(
            lambda x: f"₹{x/1e5:.1f}L")
    dept_display.columns = [
        'Department', 'Patients',
        'Avg Stay', 'Avg Bill', 'Revenue'
    ]
    st.dataframe(dept_display,
                 use_container_width=True,
                 hide_index=True)

# Tab 3 — Doctors
with tab3:
    st.markdown("### 👨‍⚕️ Doctor Performance")

    doctor_stats = filtered.groupby(
        'doctor').agg(
        patients=('patient_id', 'count'),
        avg_stay=('stay_days', 'mean'),
        avg_bill=('bill', 'mean'),
        dept=('department', 'first')
    ).reset_index().sort_values(
        'patients', ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        top_docs = doctor_stats.head(15)
        fig8     = px.bar(
            top_docs,
            x='patients', y='doctor',
            orientation='h',
            color='dept',
            title='Top 15 Doctors by Patients',
        )
        fig8.update_layout(
            height=500,
            template='plotly_white',
            xaxis_title='Patients Handled'
        )
        st.plotly_chart(fig8,
                        use_container_width=True)

    with col2:
        fig9 = px.scatter(
            doctor_stats,
            x='patients',
            y='avg_bill',
            size='avg_stay',
            color='dept',
            title='Patients vs Avg Bill per Doctor',
            hover_data=['doctor'],
            labels={
                'patients': 'Patients',
                'avg_bill': 'Avg Bill (₹)'
            }
        )
        fig9.update_layout(
            height=500,
            template='plotly_white'
        )
        st.plotly_chart(fig9,
                        use_container_width=True)

# Tab 4 — Diseases
with tab4:
    st.markdown("### 🦠 Disease Analysis")

    col1, col2 = st.columns(2)

    with col1:
        top_diseases = filtered[
            'disease'].value_counts().head(15)
        fig10 = px.bar(
            x=top_diseases.values,
            y=top_diseases.index,
            orientation='h',
            title='Top 15 Diseases',
            color=top_diseases.values,
            color_continuous_scale='Reds'
        )
        fig10.update_layout(
            height=500,
            template='plotly_white',
            xaxis_title='Patient Count'
        )
        st.plotly_chart(fig10,
                        use_container_width=True)

    with col2:
        # Disease by age group
        filtered['age_group'] = pd.cut(
            filtered['age'],
            bins=[0, 18, 35, 50, 65, 85],
            labels=['Child', 'Young Adult',
                    'Adult', 'Senior', 'Elderly']
        )
        age_dept = filtered.groupby(
            ['age_group', 'department'],
            observed=True
        ).size().reset_index(name='count')

        fig11 = px.bar(
            age_dept,
            x='age_group', y='count',
            color='department',
            title='Dept Visits by Age Group',
            barmode='stack'
        )
        fig11.update_layout(
            height=500,
            template='plotly_white',
            xaxis_title='Age Group',
            yaxis_title='Patients'
        )
        st.plotly_chart(fig11,
                        use_container_width=True)

    # Blood group distribution
    st.markdown("#### 🩸 Blood Group Distribution")
    bg_counts = filtered[
        'blood_group'].value_counts()
    fig12 = px.bar(
        x=bg_counts.index,
        y=bg_counts.values,
        title='Patients by Blood Group',
        color=bg_counts.values,
        color_continuous_scale='Reds'
    )
    fig12.update_layout(
        height=300,
        template='plotly_white',
        yaxis_title='Count',
        xaxis_title='Blood Group'
    )
    st.plotly_chart(fig12,
                    use_container_width=True)

# Tab 5 — Revenue
with tab5:
    st.markdown("### 💰 Revenue Analysis")

    col1, col2 = st.columns(2)

    with col1:
        dept_rev = filtered.groupby(
            'department')['bill'].sum()\
            .sort_values(ascending=False) / 1e5

        fig13 = px.bar(
            x=dept_rev.index,
            y=dept_rev.values,
            title='Revenue by Department (₹ Lakhs)',
            color=dept_rev.values,
            color_continuous_scale='Greens'
        )
        fig13.update_layout(
            height=350,
            template='plotly_white',
            yaxis_title='Revenue (₹ Lakhs)',
            xaxis_title='Department'
        )
        fig13.update_xaxes(tickangle=45)
        st.plotly_chart(fig13,
                        use_container_width=True)

    with col2:
        monthly_rev = filtered.groupby(
            'month')['bill'].sum().reset_index()
        monthly_rev['month_name'] = \
            monthly_rev['month'].apply(
                lambda x: month_names[x-1])

        fig14 = px.line(
            monthly_rev,
            x='month_name',
            y='bill',
            title='Monthly Revenue Trend (₹)',
            markers=True,
            color_discrete_sequence=['#2ecc71']
        )
        fig14.update_layout(
            height=350,
            template='plotly_white',
            yaxis_title='Revenue (₹)',
            xaxis_title='Month'
        )
        st.plotly_chart(fig14,
                        use_container_width=True)

    # Revenue metrics
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Revenue",
              f"₹{filtered['bill'].sum()/1e7:.2f} Cr")
    s2.metric("Avg Bill/Patient",
              f"₹{filtered['bill'].mean():,.0f}")
    s3.metric("Highest Bill",
              f"₹{filtered['bill'].max():,}")
    s4.metric("Lowest Bill",
              f"₹{filtered['bill'].min():,}")

    # Revenue by severity
    sev_rev = filtered.groupby(
        'severity')['bill'].mean()
    fig15 = px.bar(
        x=sev_rev.index,
        y=sev_rev.values,
        title='Avg Bill by Severity (₹)',
        color=sev_rev.values,
        color_continuous_scale='RdYlGn_r'
    )
    fig15.update_layout(
        height=300,
        template='plotly_white',
        yaxis_title='Avg Bill (₹)'
    )
    st.plotly_chart(fig15,
                    use_container_width=True)

    # Download
    csv = filtered.to_csv(index=False)
    st.download_button(
        "⬇️ Download Patient Data",
        csv, "hospital_data.csv",
        "text/csv"
    )

st.markdown("---")
st.markdown(
    "Built by **Jyotiraditya** | "
    "Hospital Management Dashboard | "
    "1000 patient records analyzed"
)
# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ======================================================
# Configuration de la page Streamlit
# ======================================================
st.set_page_config(
    page_title="Tableau de bord Workflows",
    layout="wide",                # Utilisation de toute la largeur de la page
    initial_sidebar_state="expanded"  # Sidebar étendue par défaut
)

st.title("Tableau de bord Workflows – Analyse professionnelle")
st.write("Analyse des tâches à partir du fichier work.csv : performance, retards, surcoûts, et distribution par employé, département et priorité.")

# ======================================================
# Lecture du fichier CSV
# ======================================================
df = pd.read_csv("work.csv")  # Chargement direct du fichier CSV nommé work.csv

# ======================================================
# Prétraitement des données et calculs
# ======================================================
# Conversion des colonnes de temps en format datetime
df["Task_Start_Time"] = pd.to_datetime(df["Task_Start_Time"])
df["Task_End_Time"] = pd.to_datetime(df["Task_End_Time"])

# Calcul du temps réel en minutes
df["Actual_Time_Minutes"] = (df["Task_End_Time"] - df["Task_Start_Time"]).dt.total_seconds() / 60

# Calcul du dépassement de temps (réel - estimé)
df["Time_Overrun"] = df["Actual_Time_Minutes"] - df["Estimated_Time_Minutes"]

# Calcul du pourcentage de dépassement
df["Overrun_%"] = df["Time_Overrun"] / df["Estimated_Time_Minutes"] * 100

# Flag pour indiquer si une tâche est en retard (1 = retard)
df["Delay_Flag"] = df["Time_Overrun"].apply(lambda x: 1 if x > 0 else 0)

# Calcul du surcoût lié au retard (ex: 0,75€ par minute de retard)
df["Extra_Cost"] = df["Time_Overrun"].apply(lambda x: max(x, 0) * 0.75)

# ======================================================
# Sidebar - filtres interactifs
# ======================================================
st.sidebar.header("Filtres dynamiques")

# Filtrer par département
dept_filter = st.sidebar.multiselect(
    "Département",
    df["Department"].unique(),
    df["Department"].unique()
)

# Filtrer par employé
emp_filter = st.sidebar.multiselect(
    "Employé",
    df["Assigned_Employee_ID"].unique(),
    df["Assigned_Employee_ID"].unique()
)

# Filtrer par priorité
priority_filter = st.sidebar.multiselect(
    "Priorité",
    df["Priority_Level"].unique(),
    df["Priority_Level"].unique()
)

# Appliquer les filtres
df_filtered = df[
    (df["Department"].isin(dept_filter)) &
    (df["Assigned_Employee_ID"].isin(emp_filter)) &
    (df["Priority_Level"].isin(priority_filter))
]

# ======================================================
# Affichage du DataFrame filtré
# ======================================================
st.subheader("Données filtrées")
st.dataframe(df_filtered, use_container_width=True)

# ======================================================
# KPIs principaux
# ======================================================
st.subheader("Indicateurs clés (KPIs)")

# Création de 5 colonnes pour les KPIs
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Nombre total de tâches", len(df_filtered))
col2.metric("Tâches en retard", df_filtered["Delay_Flag"].sum())
col3.metric("Temps moyen réel (min)", round(df_filtered["Actual_Time_Minutes"].mean(), 2))
col4.metric("Surcoût moyen (€)", round(df_filtered["Extra_Cost"].mean(), 2))
col5.metric("Tâches par employé", df_filtered["Assigned_Employee_ID"].nunique())

# ======================================================
# Graphiques améliorés et colorés
# ======================================================
st.subheader(" Analyse graphique avancée")

# 1️⃣ Retard par département
fig1 = px.bar(
    df_filtered.groupby("Department")["Delay_Flag"].sum().reset_index(),
    x="Department",
    y="Delay_Flag",
    text="Delay_Flag",
    title="Tâches en retard par département",
    color="Delay_Flag",
    color_continuous_scale="Reds"
)
st.plotly_chart(fig1, use_container_width=True)

# 2️⃣ Surcoût vs temps réel (taille = workload, couleur = priorité)
fig2 = px.scatter(
    df_filtered,
    x="Actual_Time_Minutes",
    y="Extra_Cost",
    color="Priority_Level",
    size="Employee_Workload",
    hover_data=["Assigned_Employee_ID", "Task_ID", "Process_Name"],
    title="Surcoût vs Temps Réel par tâche"
)
st.plotly_chart(fig2, use_container_width=True)

# 3️⃣ Distribution des dépassements de temps
fig3 = px.histogram(
    df_filtered,
    x="Time_Overrun",
    nbins=15,
    color="Priority_Level",
    title="Distribution des écarts de temps (Actual - Estimé)",
    marginal="box"
)
st.plotly_chart(fig3, use_container_width=True)

# 4️⃣ Retard par employé
fig4 = px.bar(
    df_filtered.groupby("Assigned_Employee_ID")["Delay_Flag"].sum().reset_index(),
    x="Assigned_Employee_ID",
    y="Delay_Flag",
    text="Delay_Flag",
    color="Delay_Flag",
    color_continuous_scale="Oranges",
    title="Tâches en retard par employé"
)
st.plotly_chart(fig4, use_container_width=True)

# 5️⃣ Temps réel vs temps estimé par tâche
fig5 = px.bar(
    df_filtered,
    x="Task_ID",
    y=["Estimated_Time_Minutes", "Actual_Time_Minutes"],
    title="Temps estimé vs temps réel par tâche",
    barmode="group",
    color_discrete_sequence=["#636EFA", "#EF553B"]
)
st.plotly_chart(fig5, use_container_width=True)

# 6️⃣ Nombre de tâches par priorité
fig6 = px.pie(
    df_filtered,
    names="Priority_Level",
    title="Répartition des tâches par priorité",
    hole=0.4,
    color_discrete_sequence=px.colors.sequential.RdBu
)
st.plotly_chart(fig6, use_container_width=True)

# 7️⃣ Surcoût total par département
fig7 = px.bar(
    df_filtered.groupby("Department")["Extra_Cost"].sum().reset_index(),
    x="Department",
    y="Extra_Cost",
    text="Extra_Cost",
    color="Extra_Cost",
    color_continuous_scale="Viridis",
    title="Surcoût total par département"
)
st.plotly_chart(fig7, use_container_width=True)

# 8️⃣ Nombre de tâches par type de processus
fig8 = px.bar(
    df_filtered.groupby("Task_Type")["Task_ID"].count().reset_index(),
    x="Task_Type",
    y="Task_ID",
    text="Task_ID",
    color="Task_ID",
    color_continuous_scale="Blues",
    title="Nombre de tâches par type de processus"
)
st.plotly_chart(fig8, use_container_width=True)

# 9️⃣ Heatmap des retards par département et employé
heatmap_data = df_filtered.pivot_table(
    index="Department",
    columns="Assigned_Employee_ID",
    values="Delay_Flag",
    aggfunc="sum",
    fill_value=0
)
fig9 = px.imshow(
    heatmap_data,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="Reds",
    title="Heatmap des retards par département et employé"
)
st.plotly_chart(fig9, use_container_width=True)
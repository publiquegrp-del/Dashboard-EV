import streamlit as st
import pandas as pd
import altair as alt
from CONSTANT import *


# Page d'accueil du dashboard Streamlit.

# Rôle :
#    - Présenter le contexte du projet
#    - Expliquer le fonctionnement global
#    - Donner un aperçu visuel des impacts du mix énergétique

# Cette page ne contient pas de calculs, uniquement de l'affichage.


# =============================================================================
# CONFIGURATION DE LA PAGE
# =============================================================================

# Configuration globale (titre, icône, layout)
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=PAGE_LAYOUT
)

# =============================================================================
# CHARGEMENT DU STYLE (CSS PERSONNALISÉ)
# =============================================================================

# Injection du CSS pour personnaliser l'apparence du dashboard
with open(CSS_PATH, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Élément graphique de la barre latérale
st.markdown('<div id="left-bar"></div>', unsafe_allow_html=True)

# =============================================================================
# EN-TÊTE (HERO SECTION)
# =============================================================================

# Titre principal
st.markdown(
    f'<h1 class="hero-title">{HERO_TITLE}</h1>',
    unsafe_allow_html=True
)

# Ligne de séparation stylisée
st.markdown(
    f'<hr class="hr-main" style="background-color:{COULEUR_PRINCIPALE};">',
    unsafe_allow_html=True
)

# =============================================================================
# CONTEXTE DU PROJET
# =============================================================================
st.info("""
**Bienvenue!** Si la voiture électrique est l'avenir, son impact écologique réel dépend de l'électricité qu'elle consomme. 
Ce dashboard calcule pour vous le **mix énergétique optimal** sur 10 ans : le but est de **réduire au maximum les émissions de CO₂**, tout en respectant le budget et l'espace disponibles.
Pour plus d'informations, veuillez visiter les pages sur le coté.
""")

# =============================================================================
# KPIs (INDICATEURS CLÉS)
# =============================================================================

st.write("### Paramètres clés de la simulation")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="Periode", value=f"{ANNEE_FIN-ANNEE_DEBUT+1} ans", delta=f"{ANNEE_DEBUT}-{ANNEE_FIN} (Fin du thermique)", delta_color="normal")
with kpi2:
    st.metric(label="Budget Annuel Max", value=f"{B_MAX:,} M€", delta_color="normal")
with kpi3:
    st.metric(label="Demande Est. 2035", value=f"{DEFAULT_DEMANDE_2035} TWh",  delta_color="normal")
with kpi4:
    st.metric(label="Technologies évaluées", value=f"{TECHNOLOGY_LABEL}", delta=f"{TECHNOLOGY_LIST}",
              delta_color="normal")

st.markdown('<hr class="hr-main" style="border-top-color:var(--secondary-background-color);">', unsafe_allow_html=True)

# =============================================================================
# FONCTIONNEMENT DU MODÈLE
# =============================================================================

col_contexte, col_demo = st.columns([1, 1], gap="large")

with col_contexte:
    st.subheader("Architecture du modèle")
    st.write("L'outil s'appuie sur trois piliers interconnectés :")

    st.markdown("""
    **1. Base de données ACV :** Évalue l'impact environnemental réel des véhicules (Thermique vs Électrique) tout au long de leur cycle de vie.

    **2. Algorithme d'Optimisation :** Détermine le mix énergétique idéal à construire ou fermer chaque année.

    **3. Contraintes Opérationnelles :** Ajuste les choix de l'algorithme pour respecter le budget, l'espace terrestre/maritime et la demande électrique.
    """)

with col_demo:
    st.subheader("Aperçu : L'importance du Mix Énergétique")
    # Données de démonstration illustratives
    data_demo = pd.DataFrame({
        "Scénario": ["Diesel (Référence)", "EV (Mix carboné)", "EV (Mix optimisé)"],
        "Émissions (gCO₂/km)": [150, 110, 35]
    })

    # Graphique en barres
    bars = (
        alt.Chart(data_demo)
        .mark_bar(color=COULEUR_PRINCIPALE)
        .encode(
            x=alt.X(
                "Scénario:N",
                title=""
            ),
            y=alt.Y("Émissions (gCO₂/km):Q",
                    title="Grammes de CO₂ par km")
        )
    )

    # Ajout des labels au-dessus des barres
    text = (
        alt.Chart(data_demo)
        .mark_text(
            align="center",
            baseline="bottom",
            dy=-5  # position au-dessus de la barre
        )
        .encode(
            x="Scénario:N",
            y="Émissions (gCO₂/km):Q",
            text=alt.Text("Émissions (gCO₂/km):Q", format=".0f")
        )
    )

    # Combinaison des deux couches (barres + texte)
    chart = (bars + text).properties(height=320)

    st.altair_chart(chart, use_container_width=True)

# Séparateur visuel
st.markdown('<hr class="hr-main" style="border-top-color:var(--secondary-background-color);">', unsafe_allow_html=True)

# =============================================================================
# SECTION À PROPOS
# =============================================================================

st.subheader("À propos")

st.info("""
**Contexte & Objectif :** Ce tableau de bord a été développé dans le cadre d'un projet académique. Il vise à fournir un outil d'aide à la décision interactif pour comprendre les enjeux croisés de la mobilité électrique et de la production d'énergie à l'horizon 2035. L'approche combine une modélisation mathématique stricte et les principes de l'Analyse du Cycle de Vie (ACV).

**Avertissement & Limites :** Les résultats présentés sont générés par un algorithme d'optimisation linéaire. Ils dépendent des hypothèses formulées dans le modèle (telles que des facteurs d'émission statiques ou une croissance linéaire de la demande). Cet outil a une vocation exploratoire et analytique.

**Développé par :** *[ISLAM Memosha, TAYOU FOTSO Cabrel, MLAKAR Loic, LADEN Thomas et AFAQI Ouways]* — **Institution :** *Université Libre de Bruxelles (Projet TRAN-H201)*
""")

# =============================================================================
# FOOTER
# =============================================================================

# Message dans la sidebar
st.sidebar.info("Bienvenue. Sélectionnez une section ci-dessus pour commencer l'exploration.")

st.markdown("---")

st.caption(f"""
{END_PAGE_NOTE}
""")

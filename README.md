# Dashboard – Outil d’optimisation du mix énergétique pour les voitures électriques

## Description

Ce projet est un tableau de bord développé en Python permettant l'analyse de cycle de vie des voitures électriques versus les voitures diesel mais également la détermination du mix énergétique optimal pour la minimisation des émissions de CO₂.

Il permet de :

- Optimiser le mix énergétique afin d’obtenir une émission de CO₂ minimale
- Rechercher des procédés dans une base de données
- Calculer des résultats LCIA (Life Cycle Impact Assessment)
- Afficher les impacts environnementaux
- Afficher les résultats de l'optimisation
- Explorer les résultats via une interface Streamlit

L’outil se connecte à une base de données via un module backend et effectue les calculs d’impacts selon une méthode LCIA sélectionnée.

### Interface utilisateur

Le projet est accessible via un dashboard Streamlit structuré en plusieurs pages :

1. Page d’accueil  
   - Présentation du projet et des objectifs

2. Impact environnemental  
   - Mix énergétique optimisé  
   - Émissions CO₂  
   - Comparaison ACV EV vs Diesel  

3. Impact économique  
   - Coûts d’investissement  
   - Surface utilisée  
   - Courbe de compromis coût / émissions  

4. Informations complémentaires  
   - Équations du modèle  
   - Hypothèses  
   - Sources de données

## Diagramme d'architecture du projet

![Diagramme](\Site\Pictures\Diagramme.jpg)

Le projet suit une architecture modulaire :

- Backend : calculs ACV et optimisation
- Base de données : stockage des procédés et facteurs d’émission
- Frontend : interface Streamlit
- Module optimisation : résolution du modèle linéaire

## Modules du projet

1. Module ACV
2. Module Optimisation énergétique
3. Module Comparaison EV vs Diesel

## Modèle mathématique de l'optimisation du mix énergétique
### Type de problème

- Programmation linéaire (Linear Programming)
- Variables continues
- Résolution via PuLP
- Solveur utilisé : CBC (Coin-or Branch and Cut)

### Hypothèses du modèle

- Facteurs d’émission constants dans le temps
- Croissance linéaire de la demande
- Absence de stockage énergétique
- Interconnexions simplifiées via des importations d’électricité

#### Technologies considérées
- Éolien
- Solaire
- Nucléaire
- Pétrole
- Gaz
- Biomasse
- Charbon

### Contraintes du projet
- Budget annuel maximal 1,0 × 10<sup>3</sup> M€/an
- Capacité nucléaire additionnelle maximale : 4,0 GW
- Demande électrique en 2025 : 8,0 × 10<sup>1</sup> TWh
- Période d’optimisation : 10 années
- Surface maritime disponible : 3,454 × 10<sup>3</sup> km² 
- Surface terrestre disponible 1,2275 × 10<sup>4</sup> km²

### Contrainte de satisfaction de la demande

∑<sub>i</sub>
( C<sub>i,t</sub><sup>cumul</sup> × f<sub>i</sub> × K<sub>conv</sub> )
≥ D<sub>t</sub> ∀ t

où :
- f<sub>i</sub> : facteur de charge de la technologie i [-]
- K<sub>conv</sub> : facteur de conversion GW → kWh
- D<sub>t</sub> : demande électrique annuelle [kWh]

### Contraintes de domaine

- x<sub>i,t</sub> ≥ 0  
- y<sub>i,t</sub> ≥ 0  
- C<sub>i,t</sub><sup>cumul</sup> ≥ 0

### Variables de décision
x<sub>i,t</sub> : Capacité additionnelle installée de la technologie i en année t [GW]

### Fonction objectif

Le modèle minimise le **coût total du système énergétique**, incluant :

- le coût des importations d’électricité
- le coût des émissions de CO₂ (via un prix carbone)
- les coûts d’investissement dans les technologies

Formulation :

Min Z<sub>t</sub> = p<sub>import</sub> I<sub>t</sub> + P<sub>CO2</sub> × (E<sub>t</sub>/10<sup>6</sup>) + ∑<sub>i∈I</sub> c<sub>i</sub> × x<sub>i,t</sub> 

Le modèle est résolu indépendamment pour chaque année t.

où :
- I : ensemble des technologies
- Z<sub>t</sub> : coût total du système énergétique pour l’année t [€]

- p<sub>import</sub> : prix de l’électricité importée [€/MWh]
- I<sub>t</sub> : quantité d’électricité importée [TWh]

- P<sub>CO2</sub> : prix du carbone [€/tCO₂]
- E<sub>t</sub> : émissions totales du système électrique [tCO₂]

- c<sub>i</sub> : coût d’investissement de la technologie i [M€/GW]
- x<sub>i,t</sub> : capacité installée de la technologie i en année t [GW]

- C<sub>i,t</sub><sup>cumul</sup> : capacité cumulée de la technologie i à l’année t [GW]
> C<sub>i,t</sub><sup>cumul</sup> = C<sub>i,t-1</sub><sup>cumul</sup> + x<sub>i,t</sub> - y<sub>i,t</sub>

- y<sub>i,t</sub> : capacité démantelée de la technologie i en année t [GW]
## Analyse du cycle de vie (ACV)

L’ACV compare deux types de véhicules :

- Véhicule électrique (EV)
- Véhicule diesel (CV)

Trois phases sont considérées :

1. Production  
2. Utilisation  
3. Fin de vie  

Les émissions en phase d’utilisation du véhicule électrique dépendent directement de l’intensité carbone du mix énergétique optimisé.

## Performance

Le projet utilise les mécanismes de cache de Streamlit :

- `st.cache_data` : pour éviter de recalculer les optimisations
- `st.cache_resource` : pour la connexion à la base de données

Cela permet de réduire fortement le temps de calcul lors de l’exploration interactive.

## Installation

### Prérequis
- Python 3.10+
- pip

### Base de données

La base SQLite contient :

- Table processes
- Table impacts
- Table technologies
- Table costs

Celui-ci a été récupéré en utilisant le fichier :

```bash
transfer_to_db.py
```
qui a transféré toutes les données dans la base de données LCA :

```bash
Data.zip
```

Pour obtenir la base de donnée, vous pouvez soit la récupéré en runant le code "transfer_to_db.py" ou en installant directement la base de donnée au bon endroit dans le répertoire.

### Installation des dépendances
```bash
git clone <repo>
cd Projet
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Lancement de l'application

### Structure du fichier du projet

```
Projet/
│
Site/
│
├── backend.py
├── Comparaison_EV.py
├── Optimisation_26_02_19.py
├── DataBase.db
├── (transfer_to_db.py)
├── (Data.zip)
├── 1_Page d'accueil.py
├── assets
│ └── styles.css
├── Pages
│ └── 2_Impact environnemental.py
│ └── 3_Impact économique.py
│ └── 4_Informations complémentaires.py
└── README.md
````

---

Pour le moment, avant le déploiement de l'application, Le projet doit être exécuté dans un environnement virtuel respectant la structure ci-dessus.

Ensuite, ouvrez le terminal de votre système d'opération ou celui de votre environnement virtuel et effectuez ces commandes:

```bash
cd *chemin de votre dossier "Projet"*
.\Scripts\activate
streamlit run "Site\1_Page d'accueil.py"
```
## Résultats attendus

- Mix énergétique optimal/année 
- Émissions totales 
- Coût total
- Investissement/année
- Courbe de compromis coût / CO₂ 
- Comparaison EV vs Diesel

## Améliorations futures
- Déploiement via Streamlit Cloud


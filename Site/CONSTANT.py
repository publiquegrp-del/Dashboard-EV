from pathlib import Path

# ============================================
# CHEMINS D'ACCÈS
# ============================================
BASE_DIR = Path(__file__).parent.absolute()
CSS_PATH = BASE_DIR / "assets" / "styles.css"
DB_PATH = BASE_DIR / "DataBase.db"  # <-- Ajout de la constante pour la BDD
zip_path = "Data.zip" # Chemin vers le fichier ZIP contenant l’ensemble des données brutes.
extracted_d = "extracted_data" # Dossier où les données seront extraites
db_path = "DataBase.db" # Chemin vers la future base SQLite. Si elle n’existe pas, elle sera créée automatiquement.

# ============================================
# CONSTANTES DE TRANSFERT DE DATABASE
# ============================================
DB_COMMIT_INTERVAL = 100
DEFAULT_JSON_ENCODING = "utf-8"
FALLBACK_JSON_ENCODING = "latin-1"
DEFAULT_CONVERSION_FACTOR = 1.0
tables = ['locations', 'actors', 'sources', 'unit_groups', 'units',
              'flow_properties', 'flows', 'processes', 'exchanges', 'product_systems',
              'lcia_methods', 'lcia_categories', 'method_categories', 'impact_factors']
# ============================================
# CONSTANTES GLOBALES DE CONVERSIONS
# ============================================
G_TO_KG = 1000
TWH_TO_KWH = 1e9
G_TO_MT = 1e12
G_TO_TON = 1e6
KG_TO_MT = 1e9

# ============================================
# INTERFACE UTILISATEUR (UI)
# ============================================
COULEUR_PRINCIPALE = "#41b8d5"
budget_min_compromis = 0
budget_max_compromis = 10000
step = 300

# ============================================
# NAVIGATION STREAMLIT
# ============================================
PAGE_ENV = "Pages/2_Impact environnemental.py"
PAGE_ECO = "Pages/3_Impact économique.py"
PAGE_INFO = "Pages/4_Informations complémentaires.py"
PAGE_TITLE ="Accueil - Dashboard EV",
PAGE_ICON="🚗",
PAGE_LAYOUT="wide"
ENV_IMPACT_TITLE = "Impact environnemental"

COULEURS_ENERGIE = {
    "Pétrol": "#1B78A7",
    "Gaz": "#41b8d5",
    "Solaire": "#BFD2FF",
    "Éolien": "#C298DE",
    "Nucléaire": "#F05E72",
    "Biomasse" : "#C34A7A",
    "Charbon" : "#6F3A60"
}

LABELS = {
    "eolien": "Éolien",
    "solaire": "Solaire",
    "nucleaire": "Nucléaire",
    "petrole": "Pétrol",
    "gaz": "Gaz",
    "biomasse": "Biomasse",
    "charbon": "Charbon"
}

mapping_tech_process = {
        'gaz': 'Electricity, natural gas, at power plant',
        'charbon': 'Electricity, bituminous coal, at power plant',
        'nucleaire': 'Electricity, nuclear, at power plant',
        'biomasse': 'Electricity, biomass, at power plant',
        'petrole': 'Electricity, residual fuel oil, at power plant',
        'eolien': 'wind',
        'solaire': 'solar'
    }

tech_surface = ["eolien", "solaire"]


# ============================================
# BASE DE DONNÉES & ACV
# ============================================
method_id = "787c02f1-d1f2-36d6-8e06-2307cc3ebebc"

# ============================================
# FACTEURS pour la comparaison entre EV et CV
# ============================================
material_factors = {
    "Aluminum ingot, production mix, at plant": 14.77,
    "Glass": 1.437,
    "Copper, at regional storage": 5.905, #
    "Rubber": 4.13, #
    "Cotton, at field": 2.65
} #kgCO2/kg de matériaux

cell_literature_factors = {
    "Nitrogen, liquid, at plant": 0.06
}

EOL_SCENARIO = {
    "Iron and steel, production mix": {
        "recycling": 1.0,
        "incineration": 0.0,
        "landfill": 0.0
    },
    "Aluminum ingot, production mix, at plant": {
        "recycling": 1.0,
        "incineration": 0.0,
        "landfill": 0.0
    },
    "Copper, at regional storage": {
        "recycling": 1.0,
        "incineration": 0.0,
        "landfill": 0.0
    },
    "Polypropylene resin, at plant": {
        "recycling": 0.671,
        "incineration": 0.209,
        "landfill": 0.120
    },
    "Polystyrene, high impact, resin, at plant": {
        "recycling": 0.405,
        "incineration": 0.295,
        "landfill": 0.300
    },
    "Polyurethane": {
        "recycling": 0.201,
        "incineration": 0.499,
        "landfill": 0.300
    },
    "Rubber": {
        "recycling": 0.576,
        "incineration": 0.377,
        "landfill": 0.049
    },
    "Glass": {
        "recycling": 0.409,
        "incineration": 0.315,
        "landfill": 0.276
    },
    "Polyethylene terephthalate, resin, at plant": {
        "recycling": 0.405,
        "incineration": 0.295,
        "landfill": 0.300
    },
    "Cotton, at field": {
        "recycling": 0.205,
        "incineration": 0.565,
        "landfill": 0.230
    },
    "Acrylonitrile-butadiene-styrene copolymer, resin, at plant": {
        "recycling": 0.405,
        "incineration": 0.295,
        "landfill": 0.300
    }
}

EOL_TREATMENT_KEYWORDS = {
    "recycling": ["recycle", "recycling", "material recovery"],
    "incineration": ["incineration", "waste to energy", "combustion"],
    "landfill": ["landfill", "disposal", "dump"]
}

lifetime_km = 200000
DEFAULT_OCCUPANCY_RATE = 1.5
taux_emssion_diesel = 181 # g CO2/km
convert_g_to_kg = 10**(-3)

MATERIAL_FR = {
    "Rubber": "Caoutchouc",
    "Aluminum ingot, production mix, at plant": "Aluminium",
    "Iron and steel, production mix": "Acier",
    "Copper, at regional storage": "Cuivre",
    "Glass": "Verre",
    "Cotton, at field": "Coton",
    "Polypropylene resin, at plant": "Polypropylène",
    "Polyurethane": "Polyuréthane",
    "Polystyrene, high impact, resin, at plant": "Polystyrène choc",
    "Polyethylene terephthalate, resin, at plant": "PET",
    "Acrylonitrile-butadiene-styrene copolymer, resin, at plant": "ABS",
    "Magnesium": "Magnésium"
}

ELECTRICITY_KEYWORD = "electricity"
BATTERY_CELL_KEYWORD = "battery cell"
BATTERY_PACK_PROCESS = "Battery pack"
USE_PHASE_KEYWORD = "Use Phase"
DUMMY_DISPOSAL_KEYWORD = "Dummy_Disposal"
EXCLUDED_ORE_KEYWORDS = ["sulfide", "ore", "concentrate"]
VALID_ENERGY_UNITS = ["kWh", "kg"]
WASTE_KEYWORD = "waste"
TREATMENT_KEYWORD = "treatment"

# ============================================
# PARAMÈTRES VÉHICULES
# ============================================
BATTERY_CAPACITY_KWH = 62
BATTERY_EMISSION_FACTOR = 80

# ============================================
# VALEURS MAXIMALES POUR LES INDICATEURS
# ============================================

MAX_ENERGIE = 100
MAX_FABRIC = 100
MAX_DECHET = 100

MAX_BUDGET = 100
MAX_TERRAIN = 100

# ============================================
# PARAMÈTRES D'OPTIMISATION
# ============================================
ANNEE_DEBUT = 2026
ANNEE_FIN = 2035
ANNEES = list(range(ANNEE_DEBUT, ANNEE_FIN + 1))

TECHNOLOGIES = ['eolien', 'solaire', 'nucleaire', 'petrole', 'gaz', 'biomasse', 'charbon']

K_CONV = 8.76  # Conversion capacité [GW] → énergie [TWh]
B_MAX = 1000  # Budget annuel maximal [M€/an]
B_MAX_TOTAL = 10 * B_MAX # Budget total sur 10 ans
X_NUC_MAX_TOTAL = 4  # Capacité nucléaire additionnelle maximale payante [GW]
X_NUC_GRATUIT = 2 # Capacité nucléaire additionnelle maximale gratuite [GW]
D_2025 = 80  # Demande électrique de référence en 2025 [TWh]
DEFAULT_DEMANDE_2035 = 127.5 # Demande électrique de référence en 2035 [TWh]
DELTA_T = 10  # Période d'optimisation [années]
D_MIN_2035 = 115  # Demande 2035 min [TWh]
D_MAX_2035 = 140 # Demande 2035 max [TWh]
DEFICIT_WARNING_THRESHOLD = 0.1

PRIX_IMPORT = 58  # Prix d'importation de l'électricité (M€/TWh) (de base)
EMISSION_IMPORT = 255  # gCO2/kWh
PRIX_CARBONE = 88.3  # Coût des émissions [€/tCO2]
ACCEPT_NUCLEAIR = 1.0 # pourcentage d'acceptation nucléaire par défaut
COUVERT_LOCALE = 0.8 # pourcentage de couverture locale par défaut

FACTEURS_CHARGE = {
    'eolien': 0.26, 'solaire': 0.15, 'nucleaire': 0.72,
    'petrole': 0.40, 'gaz': 0.45, 'charbon': 0.4, 'biomasse': 0.6
}

COUTS_INVESTISSEMENT = {  # [M€/GW]
    'eolien': 1500, 'solaire': 1200, 'nucleaire': 1000,
    'petrole': 900, 'gaz': 1000, 'charbon': 0, 'biomasse': 0
}

SURFACES_NECESSAIRES = {  # [km²/GW]
    'eolien': 150, 'solaire': 15, 'nucleaire': 0,
    'petrole': 0, 'gaz': 0, 'charbon': 0, 'biomasse': 0
}

SURFACES_DISPONIBLES = {  # [km²]
    'eolien': 3454, 'solaire': 12275
}

MAX_CONSTRUCTION_ANNUEL = {
    'eolien': 0.8, 'solaire': 1.0, 'nucleaire': 0.5,
    'petrole': 0.2, 'gaz': 0.2, 'charbon': 0, 'biomasse': 0
}

MAX_DECROISSANCE_ANNUEL = {
    'eolien': 0.0, 'solaire': 0.0, 'nucleaire': 0.0,
    'petrole': 0.2, 'gaz': 0.1, 'charbon': 0.1, 'biomasse': 0.0
}

MIX_ENERGETIQUE_2025 = {
    'charbon': 0.055, 'petrole': 0.404, 'gaz': 0.251, 'nucleaire': 0.172, 'biomasse': 0.076, 'energie verte': 0.042
}

VALEURS_DEFAUT_EMISSION = {
    'eolien': 14.1,
    'solaire': 41.0,
    'petrole': 730,
    'gaz': 490,
    'charbon': 820,
    'nucleaire': 12.0,
    'biomasse': 45.0
}

mix_eolien_2025 = 0.6
mix_solaire_2025 = 0.4

MAX_PARALLEL_WORKERS = 8
BINARY_SEARCH_ITER = 8
CACHE_TTL = 3600
DECISION_EPSILON = 0.001
DEMAND_TOLERANCE = 0.99

# ============================================
# PAGE 1 : ACCUEIL
# ============================================

HERO_TITLE = "Transition Énergétique & Véhicules Électriques"
PAGE_TITLE ="Accueil - Dashboard EV"
PAGE_ICON="🚗"
PAGE_LAYOUT="wide"
TECHNOLOGY_LABEL = "7 Sources"
TECHNOLOGY_LIST = "Pétrol, Gaz, Solaire, Éolien, Nucléaire, Biomasse, Charbon"
END_PAGE_NOTE = """
Projet d'optimisation énergétique et analyse du cycle de vie (BA2-TRAN-Informatique) 

Université Libre de Bruxelles – 2025-2026
"""

# ============================================
# PAGE 2 : IMPACT ENVIRONNEMENTAL
# ============================================

PAGE_ENV_TITLE = "Impact environnemental"

BUDGET_MIN = 0
BUDGET_MAX = 20000
BUDGET_STEP = 500

COUVERTURE_MIN = 50
COUVERTURE_MAX = 100
COUVERTURE_STEP = 5
COUVERTURE_DEFAUT = 80

DEMANDE_MIN = 115.0
DEMANDE_MAX = 140.0
DEMANDE_DEFAULT = 127.5
DEMANDE_STEP = 0.5

ACCEP_NUC_MIN = 0
ACCEP_NUC_MAX = 100
ACCEP_NUC_DEFAUT = 100
ACCEP_NUC_STEP = 5

PRIX_IMPORT_MIN = 20
PRIX_IMPORT_MAX = 200
PRIX_IMPORT_DEFAULT = 58

DEFAULT_BAR_COLOR = "#00ff00"
BAR_WIDTH = 200
BAR_HEIGHT = 15

LIFECYCLE_STAGES = ["Début de vie", "Utilisation", "Fin de vie"]

# ============================================
# PAGE 2 : IMPACT ECONOMIQUE
# ============================================
PAGE_ECO_TITLE = "Impact économique"
PAGE_ECO_ICON = "💰"


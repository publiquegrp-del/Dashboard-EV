from collections import defaultdict
from backend import get_connection, calculate_lcia_results, search_processes_data, get_process_full_data
from CONSTANT import *
import Optimisation_26_02_19 as opti

"""
Ce code sert à faire la comparaisons des cycles de vies des voitures électriques et des voitures au diesel.
"""

# =============================================================================
# CACHE POUR EVITER LE TEMPS DE CHARGEMENT LOURD
# =============================================================================

LCIA_CACHE = {} # résultats ACV par process
CELL_CACHE = {} # impacts calculés des cellules batterie
PROCESS_CACHE = {} # résultats de recherche de process
PROCESS_DATA_CACHE = {} # données complètes des process
EOL_CACHE = {} # impacts des traitements de fin de vie

# =============================================================================
# FONCTIONS DE COMPARAISONS DES CYCLES DE VIES
# =============================================================================

# Priorité des sources :
# 1. Base ACV (si process trouvé)
# 2. Facteurs littérature
# 3. Sinon → marqué comme manquant

def get_db():
    """
        Initialise et retourne une connexion à la base de données.

        Raises:
            RuntimeError: si la connexion échoue
        """
    connect = get_connection()
    if connect is None:
        raise RuntimeError("Database connection failed")
    return connect

EVALUATED_INPUTS = [] # Trace des inputs évalués (debug / analyse)

MISSING_FACTORS = set() # Liste des flux sans facteur ACV ni littérature
def compute_lca(conn, process_id, electricity_factor):
    """
        Calcule l'impact ACV d’un process en parcourant ses inputs.

        Logique:
            - Utilise ACV si disponible
            - Fallback vers littérature sinon
            - Cas spécial batterie traité séparément
            - électricité dépend du mix (paramètre)


        Args:
            process_id (int): identifiant du process
            electricity_factor (float): facteur d’émission de l’électricité (kgCO2/kWh)

        Returns:
            float: impact total (kg CO2-eq)
        """
    data = get_process_full_data(conn, process_id)

    total_impact = 0

    # Parcourt tous les flux entrants du process et cumule leurs impacts
    for exc in data["exchanges"]:

        if exc.get("is_input") != 1:
            continue

        flow = exc["flow_name"]
        amount = exc["amount"]
        EVALUATED_INPUTS.append({
            "function": "compute_lca",
            "flow": flow,
            "amount": amount,
            "process_id": process_id
        })

        # Cas électricité → dépend du mix énergétique
        if ELECTRICITY_KEYWORD in flow.lower():
            impact = electricity_factor * amount

            total_impact += impact

            continue

        # Cas spécial batterie (cellules)
        if BATTERY_CELL_KEYWORD in flow.lower():

            if flow not in PROCESS_CACHE:
                PROCESS_CACHE[flow] = search_processes_data(conn, flow)

            suppliers = PROCESS_CACHE[flow]

            if suppliers:

                supplier = suppliers[0]

                key = f"cell_{supplier['id']}"

                if key not in CELL_CACHE:
                    CELL_CACHE[key] = compute_cell_with_literature(
                        conn,
                        supplier,
                        electricity_factor
                    )

                total_impact += CELL_CACHE[key] * amount

            else:
                MISSING_FACTORS.add(flow)

            continue

        # Cas standard (ACV base de données)
        if flow not in PROCESS_CACHE:
            PROCESS_CACHE[flow] = search_processes_data(conn, flow)

        suppliers = PROCESS_CACHE[flow]

        # CAS 1 : supplier existe
        if suppliers:

            supplier = suppliers[0]

            key = supplier["id"]

            if key not in LCIA_CACHE:
                results = calculate_lcia_results(
                    supplier["id"],
                    supplier["name"],
                    method_id
                )

                LCIA_CACHE[key] = results[0]["total"] if results else 0

            total_impact += LCIA_CACHE[key] * amount

        # CAS 2 : trou dans la base
        else:

            # Fallback littérature
            factor = cell_literature_factors.get(flow) \
                     or material_factors.get(flow)

            if factor:
                print(f"[LITTÉRATURE] compute_lca → {flow} | facteur={factor} | quantité={amount}")
                impact = factor * amount
                total_impact += impact
            else:
                MISSING_FACTORS.add(flow)

    return total_impact

def compute_cell_with_literature(conn, cell_process, electricity_fac):
    """
        Calcule l’impact d’une cellule batterie avec fallback littérature.

        Args:
            cell_process (dict): process batterie
            electricity_fac (float): facteur d’émission électricité

        Returns:
            float: impact total cellule
        """
    pid = cell_process["id"]

    if pid not in PROCESS_DATA_CACHE:
        PROCESS_DATA_CACHE[pid] = get_process_full_data(conn, pid)

    data = PROCESS_DATA_CACHE[pid]
    cell_impact = 0

    for exc in data["exchanges"]:

        if exc.get("is_input") != 1:
            continue

        flow = exc["flow_name"]
        amount = exc["amount"]
        EVALUATED_INPUTS.append({
            "function": "compute_cell",
            "flow": flow,
            "amount": amount,
            "process_id": pid
        })

        # Electricité dépend du mix
        if ELECTRICITY_KEYWORD in flow.lower():
            impact = electricity_fac * amount

            cell_impact += impact

            continue

        # Cas général du process
        if flow not in PROCESS_CACHE:
            PROCESS_CACHE[flow] = search_processes_data(conn, flow)

        suppliers = PROCESS_CACHE[flow]

        # Cas 1 : Trouvé dans la db
        if suppliers:

            supplier = suppliers[0]

            key = supplier["id"]

            if key not in LCIA_CACHE:
                results = calculate_lcia_results(
                    supplier["id"],
                    supplier["name"],
                    method_id
                )

                LCIA_CACHE[key] = results[0]["total"] if results else 0

            cell_impact += LCIA_CACHE[key] * amount

        # Cas 2 : Trous dans la db
        else:

            # Fallback littérature
            factor = cell_literature_factors.get(flow) \
                     or material_factors.get(flow)

            if factor:
                print(f"[LITTÉRATURE] cell → {flow} | facteur={factor} | quantité={amount}")
                impact = factor * amount
                cell_impact += impact
            else:
                MISSING_FACTORS.add(flow)

    return cell_impact
def get_pack_structure_impact(conn, electricity_f):
    """
        Calcule l’impact ACV du pack batterie complet.

        Returns:
            float: impact total batterie
        """
    processes = search_processes_data(conn, BATTERY_PACK_PROCESS)

    pack_process = next(
        (p for p in processes if p["name"] == BATTERY_PACK_PROCESS),
        None
    )

    if not pack_process:
        raise ValueError("Battery pack process not found.")

    impact = compute_lca(conn, pack_process["id"], electricity_f)

    return impact

def get_vehicle_structure_impact(conn, method_id, vehicle_name, literature_factors):
    """
        Calcule l’impact de fabrication d’un véhicule (hors batterie).

        Args:
            vehicle_name (str): nom du process véhicule

        Returns:
            float: impact total (kg CO2-eq)
        """

    processes = search_processes_data(conn, vehicle_name)

    vehicle = next(
        (p for p in processes if p["name"] == vehicle_name),
        None
    )

    if not vehicle:
        raise ValueError(f"{vehicle_name} not found.")

    process_data = get_process_full_data(conn, vehicle["id"])

    total_impact = 0
    fallback_used = []

    for e in process_data["exchanges"]:

        if e.get("is_input") != 1:
            continue

        flow_name = e.get("flow_name")
        amount = e.get("amount")
        unit = e.get("unit_name")
        EVALUATED_INPUTS.append({
            "function": "vehicle_structure",
            "flow": flow_name,
            "amount": amount,
            "process": vehicle_name
        })

        # Filtrage des flux non pertinents
        if unit != "kg":
            continue
        if DUMMY_DISPOSAL_KEYWORD in flow_name:
            continue
        if any(word in flow_name.lower() for word in EXCLUDED_ORE_KEYWORDS):
            continue

        material_processes = search_processes_data(conn, flow_name)

        impact_found = False

        if material_processes:
            mat_process = material_processes[0]

            key = mat_process["id"]

            if key not in LCIA_CACHE:

                results = calculate_lcia_results(
                    mat_process["id"],
                    mat_process["name"],
                    method_id
                )

                if results:
                    LCIA_CACHE[key] = results[0]["total"]
                else:
                    factor = literature_factors.get(flow_name)

                    if factor:
                        print(f"[LITTÉRATURE] vehicle_structure (no LCIA result) → {flow_name} | facteur={factor}")
                        LCIA_CACHE[key] = factor
                    else:
                        LCIA_CACHE[key] = 0

            impact_per_unit = LCIA_CACHE[key]

            total_impact += impact_per_unit * amount
            impact_found = True

        # Fallback littérature
        if not impact_found:

            factor = literature_factors.get(flow_name, None)

            if factor is not None:
                print(f"[LITTÉRATURE] vehicle_structure (no LCIA result) → {flow_name} | facteur={factor}")
                total_impact += factor * amount
                fallback_used.append(flow_name)
            else:
                MISSING_FACTORS.add(flow_name)

    return total_impact

def get_vehicle_energy_per_km(conn, search_term, occupancy_rate=DEFAULT_OCCUPANCY_RATE):
    """
        Récupère la consommation énergétique d’un véhicule par km.

        Returns:
            (float, str): énergie par km, unité
        """
    processes = search_processes_data(conn, search_term)

    # On cherche un process contenant "Use Phase"
    process = None
    for p in processes:
        if USE_PHASE_KEYWORD in p["name"]:
            process = p
            break

    if not process:
        print("\nProcess trouvés :")
        for p in processes:
            print(" -", p["name"])
        raise ValueError("Use phase process not found.")

    data = get_process_full_data(conn, process["id"])

    for e in data["exchanges"]:
        if e.get("is_input") == 1:
            unit = e.get("unit_name")

            if unit in VALID_ENERGY_UNITS:
                amount_per_passenger_km = e.get("amount")
                amount_per_vehicle_km = amount_per_passenger_km * occupancy_rate
                return amount_per_vehicle_km, unit

    raise ValueError("Energy input not found.")
def calculate_use_phase_emissions(energy_per_km, unit, lifetime_km, carbon_intensity):
    """
    Calcule les émissions sur la phase d’usage du véhicule.
    Args:
        carbon_intensity (float): kg CO2 / kWh

    Returns:
        dict:
            - kg_CO2_per_km
            - total_Mt
    """

    kg_per_km = energy_per_km * carbon_intensity
    total_kg = kg_per_km * lifetime_km
    total_Mt = total_kg / KG_TO_MT

    return {"kg_CO2_per_km": kg_per_km, "total_Mt": total_Mt}

def get_diesel_consumption():
    """
        Estime les émissions totales d’un véhicule diesel sur sa durée de vie.
            carbon_intensity (float): kg CO2 / kWh
        """
    return taux_emssion_diesel * convert_g_to_kg * lifetime_km # kg CO2

def get_vehicle_material_masses(conn, vehicle_name):
    """
        Extrait les masses de matériaux d’un véhicule.

        Returns:
            dict: {matériau: masse}
        """
    processes = search_processes_data(conn, vehicle_name)
    vehicle = next((p for p in processes if p["name"] == vehicle_name), None)

    if not vehicle:
        raise ValueError("Vehicle not found.")

    data = get_process_full_data(conn, vehicle["id"])

    materials = {}

    for e in data["exchanges"]:

        if e.get("is_input") != 1:
            continue

        if e.get("unit_name") != "kg":
            continue

        name = e.get("flow_name")

        if DUMMY_DISPOSAL_KEYWORD in name:
            continue
        if any(word in name.lower() for word in EXCLUDED_ORE_KEYWORDS):
            continue

        amount = e.get("amount")

        materials[name] = materials.get(name, 0) + amount

    return materials

def find_process_by_keywords(conn, keywords):
    """
        Recherche un process ACV correspondant à une liste de mots-clés.

        Priorité:
            - process contenant "waste" ou "treatment"
            - sinon premier résultat trouvé

        Args:
            keywords (list[str]): mots-clés de recherche

        Returns:
            dict | None: process trouvé ou None
        """
    for kw in keywords:
        results = search_processes_data(conn, kw)

        if results:
            # privilégier les process "treatment" ou "waste"
            for r in results:
                name = r["name"].lower()
                if WASTE_KEYWORD in name or TREATMENT_KEYWORD in name:
                    return r

            return results[0]

    return None

def calculate_vehicle_eol_lca(conn, vehicle_name):
    """
        Calcule l’impact ACV de fin de vie (End-of-Life).

        Returns:
            float: impact total (kg CO2-eq)
        """
    materials = get_vehicle_material_masses(conn, vehicle_name)
    total_impact = 0

    for material, mass in materials.items():

        # Récupère mode de traitement pour ce matériau
        scenario = EOL_SCENARIO.get(material, {"landfill": 1.0})

        for treatment, fraction in scenario.items():

            # Skip s’il n’y a rien à traiter
            if fraction <= 0:
                continue

            # Trouve le process LCA correspondant
            keywords = EOL_TREATMENT_KEYWORDS.get(treatment, [])

            process = find_process_by_keywords(conn, keywords)

            if not process:
                # Pas trouvé : message ou continuer
                print(f"⚠️ process EOL non trouvé pour {treatment}")
                continue

            key = process["id"]

            if key not in EOL_CACHE:
                results = calculate_lcia_results(
                    process["id"],
                    process["name"],
                    method_id
                )

                if not results:
                    print(f"⚠️ LCIA result missing for {process['name']}")
                    continue

                EOL_CACHE[key] = results[0]["total"]

            impact_per_kg = EOL_CACHE[key]

            # Corrige avec fraction et masse
            treated_mass = mass * fraction
            total_impact += impact_per_kg * treated_mass

    return total_impact

def calculate_waste_breakdown(conn, vehicle_name):
    """
        Répartition des déchets par type de traitement.

        Returns:
            dict: {recycling, incineration, landfill} : recyclage, incinération, décharge
        """
    materials = get_vehicle_material_masses(conn, vehicle_name)

    waste = {"recycling":0, "incineration":0, "landfill":0}

    for material, mass in materials.items():

        scenario = EOL_SCENARIO.get(material, {"landfill":1.0})

        if not scenario:
            waste["landfill"] += mass
            continue

        for treatment, fraction in scenario.items():
            waste[treatment] += mass * fraction

    return waste

def get_vehicle_eol_materials(conn, vehicle_name):
    """
        Génère la liste détaillée des déchets en fin de vie par matériau et traitement.

        Returns:
            list[dict]: [
                {"material": str, "treatment": str, "mass": float}
            ]
        """
    materials = get_vehicle_material_masses(conn, vehicle_name)

    waste = []

    for material, mass in materials.items():

        scenario = EOL_SCENARIO.get(material, {"landfill":1})

        for treatment, fraction in scenario.items():

            waste_mass = mass * fraction

            waste.append({
                "material": material,
                "treatment": treatment,
                "mass": waste_mass
            })

    return waste

def fr_name(material):
    """
        Traduit un nom de matériau EN → FR.

        Returns:
            str: nom traduit ou original si absent
        """
    return MATERIAL_FR.get(material, material)


def to_treatment_material_dict(waste_list):
    """
        Transforme une liste de déchets en dictionnaire structuré.

        Format:
            {treatment: {material: masse}}

        Returns:
            dict
        """
    data = defaultdict(lambda: defaultdict(float))

    for item in waste_list:
        mat_en = item["material"]
        mat = fr_name(mat_en)
        treat = item["treatment"]
        mass = item["mass"]

        data[treat][mat] += mass

    return data


def build_comparison_dict(ev_waste_list, cv_waste_list):
    """
        Construit une structure de comparaison EV vs thermique pour affichage.

        Format:
            {
                treatment: {
                    "EV": [{mat: value}],
                    "CV": [{mat: value}]
                }
            }

        Returns:
            dict
        """
    ev_data = to_treatment_material_dict(ev_waste_list)
    cv_data = to_treatment_material_dict(cv_waste_list)

    treatments = set(ev_data.keys()) | set(cv_data.keys())
    comparison = {}

    for treat in treatments:
        ev_mats = ev_data.get(treat, {})
        cv_mats = cv_data.get(treat, {})
        all_materials = set(ev_mats.keys()) | set(cv_mats.keys())

        comparison[treat] = {
            "EV": [{m: ev_mats.get(m, 0)} for m in all_materials],
            "CV": [{m: cv_mats.get(m, 0)} for m in all_materials],
        }

    return comparison

if __name__ == "__main__":
    conn = get_db()

    results = opti.run_optimisation(127.5)
    carbon_intensity = opti.calcul_intensite_carbone(results)

    vehicle_structure = get_vehicle_structure_impact(conn, method_id,"Car, electrically powered", material_factors)

    battery = get_pack_structure_impact(conn, carbon_intensity)
    ev_production_total = vehicle_structure + battery

    print("\n--- Production EV complète ---")

    print(f"Structure véhicule : {vehicle_structure:.2f} kg CO2-eq")
    print(f"Batterie : {battery:.2f} kg CO2-eq")
    print(f"Total production EV : {ev_production_total:.2f} kg CO2-eq")

    ice_structure = get_vehicle_structure_impact(conn, method_id,"Car, diesel-powered", material_factors)

    print("ICE structure :", ice_structure,"kg CO2 eq")

    # consommation
    ev_energy, ev_unit = get_vehicle_energy_per_km(conn,"Transport person e-car")

    print("EV consommation", ev_energy, ev_unit)

    # émissions
    ev_results = calculate_use_phase_emissions(ev_energy, ev_unit, lifetime_km, carbon_intensity)

    print("\n--- EV ---")
    print(f"EV emissions : {ev_results['kg_CO2_per_km']:.3f} kg CO2/km")
    print(f"Lifetime emissions : {ev_results['total_Mt']:.6f} Mt CO2")

    diesel_kg = get_diesel_consumption()

    total_Mt = diesel_kg / KG_TO_MT

    print("\n--- diesel ---")
    print(diesel_kg, total_Mt)

    print(get_vehicle_material_masses(conn,"Car, electrically powered"))

    ev_eol = calculate_vehicle_eol_lca(conn, "Car, electrically powered")
    ice_eol = calculate_vehicle_eol_lca(conn, "Car, diesel-powered")

    print(ev_eol, ice_eol)

    print("\n--- FACTEURS LITTERATURE MANQUANTS ---")

    for f in sorted(MISSING_FACTORS):
        print(f)

    ev_waste = calculate_waste_breakdown(conn, "Car, electrically powered")
    ice_waste = calculate_waste_breakdown(conn, "Car, diesel-powered")

    print("\n--- Waste EV ---")
    print(ev_waste)

    print("\n--- Waste ICE ---")
    print(ice_waste)

    print("\n--- Waste EV ---")
    ev_waste_materials = get_vehicle_eol_materials(conn, "Car, electrically powered")
    cv_waste_materials = get_vehicle_eol_materials(conn, "Car, diesel-powered")

    waste_comparison = build_comparison_dict(ev_waste_materials, cv_waste_materials)

    print(waste_comparison)


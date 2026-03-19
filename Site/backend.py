import sqlite3
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import List, Dict, Any
from CONSTANT import DB_PATH


# ============================================
# FONCTIONS DE BASE DE DONNÉES
# ============================================

@st.cache_resource
def get_connection(): # Cache la connexion → évite de la recréer
    """Établit la connexion à la base de données."""
    if not DB_PATH.exists(): # Vérifie que la DB existe
        return None # Stop si absente
    try:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row

        # --- Performance pragmas (WAL + 64 MB page cache) ---
        conn.execute("PRAGMA journal_mode=WAL") # Lecture/écriture en parallèle
        conn.execute("PRAGMA cache_size=-64000") # Cache mémoire (~64MB)
        conn.execute("PRAGMA synchronous=NORMAL") # Moins de sécurité mais + rapide
        conn.execute("PRAGMA temp_store=MEMORY") # Données temporaires en RAM
        conn.execute("PRAGMA mmap_size=268435456") # Accès mémoire (256MB)

        _ensure_indexes(conn) # Création des index si nécessaire

        return conn # Retourne la connexion

    except Exception as e:
        st.error(f"Erreur de connexion : {e}") # Affiche erreur dans Streamlit
        return None


def _ensure_indexes(conn):
    """Crée des index s'ils n'existent pas encore (aucun changement de schéma)."""
    index_statements = [
        "CREATE INDEX IF NOT EXISTS idx_exchanges_process_id ON exchanges(process_id)", # Filtrer par process
        "CREATE INDEX IF NOT EXISTS idx_exchanges_flow_id ON exchanges(flow_id)", # Filtrer par flow
        "CREATE INDEX IF NOT EXISTS idx_exchanges_is_input ON exchanges(process_id, is_input)", # Input/output
        "CREATE INDEX IF NOT EXISTS idx_flows_flow_type ON flows(flow_type)", # Type de flux
        "CREATE INDEX IF NOT EXISTS idx_impact_factors_flow_id ON impact_factors(flow_id)",
        "CREATE INDEX IF NOT EXISTS idx_impact_factors_category ON impact_factors(lcia_category_id)", # Facteurs impact
        "CREATE INDEX IF NOT EXISTS idx_method_categories_method ON method_categories(method_id)",  # Méthodes
    ]
    cursor = conn.cursor()  # Curseur pour exécuter SQL
    for stmt in index_statements:
        try:
            cursor.execute(stmt) # Exécute création index
        except Exception:
            pass  # Ignore si erreur (ex: table inexistante)

    conn.commit() # Sauvegarde modifications


def get_lcia_methods(conn) -> List[Dict]:
    """Récupère la liste des méthodes LCIA disponibles."""
    cursor = conn.cursor() # Curseur SQL
    cursor.execute("SELECT id, name, description FROM lcia_methods ORDER BY name") # Récupère les méthodes LCIA
    return [dict(row) for row in cursor.fetchall()] # Convertit chaque ligne en dictionnaire


@st.cache_data(show_spinner=False, ttl=3600) # Cache 1h
def search_processes_data(_conn, search_term: str) -> List[Dict]:
    """Recherche les processus (résultat mis en cache pour la session)."""
    cursor = _conn.cursor()
    cursor.execute("""
        SELECT id, name, description, category, process_type, location_id
        FROM processes
        WHERE name LIKE ? OR description LIKE ?
        LIMIT 50
    """, (f"%{search_term}%", f"%{search_term}%"))
    return [dict(row) for row in cursor.fetchall()] # Résultat en dict


@st.cache_data(show_spinner=False, ttl=3600)
def get_process_full_data(_conn, process_id: str) -> Dict[str, Any]:
    """Récupère les détails complets d'un processus (mis en cache)."""
    cursor = _conn.cursor()

    # Info de base du process
    cursor.execute("""
        SELECT p.*, l.name as location_name, l.code as location_code
        FROM processes p
        LEFT JOIN locations l ON p.location_id = l.id
        WHERE p.id = ?
    """, (process_id,))
    process_row = cursor.fetchone() # Récupère 1 ligne
    if not process_row:
        return None # Process inexistant
    process = dict(process_row) # Convertit en dict

    # Récupération échanges (Inputs/Outputs)
    cursor.execute("""
        SELECT 
            e.*, f.name as flow_name, f.flow_type, f.category as flow_category,
            fp.name as flow_property_name, u.name as unit_name, u.symbol as unit_symbol
        FROM exchanges e
        LEFT JOIN flows f ON e.flow_id = f.id
        LEFT JOIN flow_properties fp ON e.flow_property_id = fp.id
        LEFT JOIN units u ON e.unit_id = u.id
        WHERE e.process_id = ?
        ORDER BY e.is_input DESC, e.internal_id
    """, (process_id,))
    process['exchanges'] = [dict(row) for row in cursor.fetchall()]
    return process


# ============================================
# FONCTIONS DE CALCUL (Moteur LCIA)
# ============================================

def get_elementary_flows(conn, process_id: str):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.amount, e.is_input, f.id as flow_id, f.name as flow_name,
            f.flow_type, u.id as unit_id, u.name as unit_name,
            fp.id as flow_property_id
        FROM exchanges e
        JOIN flows f ON e.flow_id = f.id
        LEFT JOIN units u ON e.unit_id = u.id
        LEFT JOIN flow_properties fp ON e.flow_property_id = fp.id
        WHERE e.process_id = ? AND f.flow_type = 'ELEMENTARY_FLOW'
    """, (process_id,))
    # Récupère uniquement les flux environnementaux
    return [dict(row) for row in cursor.fetchall()]


def get_subprocess_ids_data(conn, process_id: str):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT e.flow_id FROM exchanges e
        JOIN flows f ON e.flow_id = f.id
        WHERE e.process_id = ? AND e.is_input = 1 
        AND f.flow_type IN ('PRODUCT_FLOW', 'WASTE_FLOW')
    """, (process_id,))
    input_flow_ids = [row['flow_id'] for row in cursor.fetchall()]

    if not input_flow_ids: return [] # Aucun sous-process

    placeholders = ','.join('?' * len(input_flow_ids))
    cursor.execute(f"""
        SELECT DISTINCT p.id, p.name FROM exchanges e
        JOIN processes p ON e.process_id = p.id
        WHERE e.flow_id IN ({placeholders}) AND e.is_input = 0 AND p.id != ?
        LIMIT 20
    """, input_flow_ids + [process_id])
    return [dict(row) for row in cursor.fetchall()]


@st.cache_data(show_spinner=False)
def calculate_lcia_results(process_id: str, process_name: str, method_id: str, include_subs: bool = True):
    """
    Calcule les impacts LCIA.
    Optimisé : récupère les flux des sous-processus en une seule requête bulk.
    """
    conn = get_connection() # Connexion DB
    if not conn: return None
    cursor = conn.cursor()

    # Flux principaux
    main_flows = get_elementary_flows(conn, process_id)
    subprocess_flows = []

    # Sous-process
    if include_subs:
        subs = get_subprocess_ids_data(conn, process_id)
        if subs:
            sub_ids = [sub['id'] for sub in subs]

            ph_subs = ','.join('?' * len(sub_ids))

            # Quantité demandée aux sous-process
            cursor.execute(f"""
                SELECT e.process_id AS parent_id, e2.process_id AS sub_id, e.amount
                FROM exchanges e
                JOIN exchanges e2 ON e.flow_id = e2.flow_id
                    AND e2.is_quantitative_reference = 1
                    AND e2.process_id IN ({ph_subs})
                WHERE e.process_id = ? AND e.is_input = 1
            """, sub_ids + [process_id])
            demand_rows = cursor.fetchall()
            demand_map = {}
            for row in demand_rows:
                demand_map[row['sub_id']] = row['amount'] if row['amount'] else 1.0

            # Récupération flux des sous-process
            cursor.execute(f"""
                SELECT e.process_id as sub_process_id,
                    e.amount, e.is_input, f.id as flow_id, f.name as flow_name,
                    f.flow_type, u.id as unit_id, u.name as unit_name,
                    fp.id as flow_property_id
                FROM exchanges e
                JOIN flows f ON e.flow_id = f.id
                LEFT JOIN units u ON e.unit_id = u.id
                LEFT JOIN flow_properties fp ON e.flow_property_id = fp.id
                WHERE e.process_id IN ({ph_subs}) AND f.flow_type = 'ELEMENTARY_FLOW'
            """, sub_ids)
            for row in cursor.fetchall():
                sf = dict(row)
                sub_pid = sf.pop('sub_process_id')
                demand = demand_map.get(sub_pid, 1.0) # Poids du sous-process
                sf['amount'] = (sf['amount'] or 0.0) * demand # Ajustement
                subprocess_flows.append(sf)

    # Fusion des flux
    all_flows = main_flows + subprocess_flows

    # Agrégation par flow_id
    aggregated = {}
    for f in all_flows:
        fid = f['flow_id']
        if fid in aggregated:
            aggregated[fid]['amount'] += (f['amount'] or 0.0)
        else:
            aggregated[fid] = f.copy()

    final_flows = list(aggregated.values())
    if not final_flows: return None

    # Récupération facteurs d’impact
    flow_ids = [f['flow_id'] for f in final_flows]
    if not flow_ids: return None
    placeholders = ','.join('?' * len(flow_ids))

    cursor.execute(f"""
        SELECT if_.flow_id, if_.value, c.id as cat_id, c.name as cat_name, c.ref_unit
        FROM impact_factors if_
        INNER JOIN lcia_categories c ON if_.lcia_category_id = c.id
        INNER JOIN method_categories mc ON c.id = mc.category_id
        WHERE if_.flow_id IN ({placeholders}) AND mc.method_id = ?
        AND if_.value != 0
    """, flow_ids + [method_id])

    factors = [dict(row) for row in cursor.fetchall()]

    # Dictionnaire rapide : flow_id → amount
    amount_by_flow = {f['flow_id']: (f['amount'] or 0.0) for f in final_flows}

    # Organisation par catégorie
    factors_by_cat = {}
    for fact in factors:
        cid = fact['cat_id']
        if cid not in factors_by_cat:
            factors_by_cat[cid] = {'info': fact, 'factors': {}}
        factors_by_cat[cid]['factors'][fact['flow_id']] = fact['value']

    # Calcul final
    results = []
    for cid, data in factors_by_cat.items():
        total_impact = 0.0
        for fid, factor_val in data['factors'].items():
            amt = amount_by_flow.get(fid, 0.0)
            if amt:
                total_impact += amt * factor_val

        if abs(total_impact) > 0:
            results.append({
                'category': data['info']['cat_name'],
                'unit': data['info']['ref_unit'],
                'total': total_impact
            })

    results.sort(key=lambda x: abs(x['total']), reverse=True)
    return results
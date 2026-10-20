"""
UtilPulse Command Centre — Central Configuration
=================================================
All project-wide settings, paths, constants, user accounts, role definitions,
and LLM parameters are defined here.
"""

import os
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Datasets")
CSV_PATH = os.path.join(DATA_DIR, "util_12.csv")
DB_PATH = os.path.join(BASE_DIR, "database", "util_12.db")
KNOWLEDGE_BASE_DIR = os.path.join(BASE_DIR, "knowledge_base", "documents")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
TABLE_NAME = "water_nodes"

# ---------------------------------------------------------------------------
# Valid columns (all 51)
# ---------------------------------------------------------------------------
VALID_COLUMNS = [
    "record_id",
    "node_id",
    "utility_name",
    "city",
    "state",
    "zone_id",
    "node_type",
    "pipe_material",
    "pipe_age_years",
    "pipe_diameter_mm",
    "elevation_m",
    "distance_to_treatment_plant_km",
    "pump_station_nearby",
    "reservoir_fed",
    "num_customer_connections",
    "demand_category",
    "pipe_length_upstream_m",
    "observation_date",
    "day_of_week",
    "is_weekend",
    "month_num",
    "month_name",
    "season",
    "inlet_pressure_bar",
    "outlet_pressure_bar",
    "pressure_differential_bar",
    "min_pressure_bar",
    "max_pressure_bar",
    "pressure_hourly_variance",
    "avg_flow_lps",
    "peak_flow_lps",
    "daily_volume_m3",
    "flow_velocity_m_s",
    "hydraulic_head_loss_m_per_km",
    "ph_value",
    "turbidity_ntu",
    "residual_chlorine_mg_l",
    "total_dissolved_solids_mg_l",
    "conductivity_us_cm",
    "water_temperature_c",
    "water_hardness_mg_l",
    "iron_ppb",
    "nitrate_mg_l",
    "coliform_cfu_100ml",
    "water_age_hours",
    "supply_hours_per_day",
    "leak_detection_events",
    "service_interruptions_count",
    "non_revenue_water_pct",
    "pressure_compliance_flag",
    "chlorine_compliance_flag",
]

# ---------------------------------------------------------------------------
# Categorical value mappings
# ---------------------------------------------------------------------------
CATEGORICAL_VALUES = {
    "utility_name": [
        "MCGM",
        "Delhi Jal Board",
        "BWSSB",
        "HMWSSB",
        "CMWSSB",
        "PMRDA Water",
        "AMC Water",
        "PHED Rajasthan",
        "Jal Nigam UP",
        "KMC Water",
    ],
    "city": [
        "Mumbai",
        "Delhi",
        "Bangalore",
        "Hyderabad",
        "Chennai",
        "Pune",
        "Ahmedabad",
        "Jaipur",
        "Lucknow",
        "Kolkata",
    ],
    "state": [
        "Maharashtra",
        "Delhi",
        "Karnataka",
        "Telangana",
        "Tamil Nadu",
        "Gujarat",
        "Rajasthan",
        "Uttar Pradesh",
        "West Bengal",
    ],
    "zone_id": ["Zone_A", "Zone_B", "Zone_C", "Zone_D", "Zone_E"],
    "node_type": [
        "Pressure_Only",
        "Combined",
        "Flow_Junction",
        "Quality_Only",
    ],
    "pipe_material": [
        "HDPE",
        "Cast_Iron",
        "PVC",
        "Asbestos_Cement",
        "Ductile_Iron",
    ],
    "demand_category": [
        "Residential",
        "Commercial",
        "Industrial",
        "Agricultural",
        "Mixed",
    ],
    "season": ["Winter", "Summer", "Pre_Monsoon"],
    "day_of_week": [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ],
}

# ---------------------------------------------------------------------------
# City ↔ Utility mapping
# ---------------------------------------------------------------------------
CITY_UTILITY_MAP = {
    "Mumbai": "MCGM",
    "Delhi": "Delhi Jal Board",
    "Bangalore": "BWSSB",
    "Hyderabad": "HMWSSB",
    "Chennai": "CMWSSB",
    "Pune": "PMRDA Water",
    "Ahmedabad": "AMC Water",
    "Jaipur": "PHED Rajasthan",
    "Lucknow": "Jal Nigam UP",
    "Kolkata": "KMC Water",
}

# ---------------------------------------------------------------------------
# User accounts  (username → credentials & metadata)
# ---------------------------------------------------------------------------
USERS = {
    "admin": {
        "password": "admin",
        "name": "Admin User",
        "role": "Admin",
        "designation": "System Administrator",
    },
    "operator_mumbai": {
        "password": "oper123",
        "name": "Rajesh Kumar",
        "role": "Zone Operator",
        "designation": "Field Operations Manager",
    },
    "quality_analyst": {
        "password": "qual123",
        "name": "Priya Sharma",
        "role": "Quality Analyst",
        "designation": "Water Quality Specialist",
    },
    "executive": {
        "password": "exec123",
        "name": "Vikram Singh",
        "role": "Executive",
        "designation": "Chief Operations Officer",
    },
}

# ---------------------------------------------------------------------------
# Role-based access control
# ---------------------------------------------------------------------------
ROLES = {
    "Admin": {
        "description": "Full system access with administrative privileges",
        "allowed_cities": "all",
        "allowed_columns": "all",
        "can_see_node_level": True,
    },
    "Zone Operator": {
        "description": "Operational access for field monitoring and zone management",
        "allowed_cities": "all",
        "allowed_columns": "all",
        "can_see_node_level": True,
    },
    "Quality Analyst": {
        "description": "Focused access on water quality parameters and compliance",
        "allowed_cities": "all",
        "allowed_columns": [
            "record_id",
            "node_id",
            "utility_name",
            "city",
            "state",
            "zone_id",
            "node_type",
            "observation_date",
            "ph_value",
            "turbidity_ntu",
            "residual_chlorine_mg_l",
            "total_dissolved_solids_mg_l",
            "conductivity_us_cm",
            "water_temperature_c",
            "water_hardness_mg_l",
            "iron_ppb",
            "nitrate_mg_l",
            "coliform_cfu_100ml",
            "water_age_hours",
            "chlorine_compliance_flag",
        ],
        "can_see_node_level": True,
    },
    "Executive": {
        "description": "High-level strategic overview with aggregated insights",
        "allowed_cities": "all",
        "allowed_columns": "all",
        "can_see_node_level": False,
    },
}

# ---------------------------------------------------------------------------
# LLM settings
# ---------------------------------------------------------------------------
LLM_MODEL = "openai/gpt-oss-120b"
LLM_BACKUP_MODEL = "openai/gpt-oss-20b"
LLM_TEMPERATURE = 0.1
MAX_QUERY_RESULTS = 500

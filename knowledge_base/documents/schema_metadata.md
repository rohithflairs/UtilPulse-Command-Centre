# Schema Metadata — `water_nodes` Table

> **Source**: UtilPulse Command Centre operational dataset
> **Total Records**: 163,904 observations
> **Total Columns**: 51
> **Coverage**: 832 sensor nodes across 10 Indian cities, January – July 2024

This document provides an exhaustive description of every column in the `water_nodes` table. It is the primary reference for any LLM or RAG agent generating SQL queries, dashboards, or analytical commentary about the UtilPulse dataset.

---

## Table of Contents

1. [Identification & Location Columns](#1-identification--location-columns)
2. [Infrastructure & Asset Columns](#2-infrastructure--asset-columns)
3. [Temporal Columns](#3-temporal-columns)
4. [Pressure Metrics](#4-pressure-metrics)
5. [Flow & Hydraulic Metrics](#5-flow--hydraulic-metrics)
6. [Water Quality Parameters](#6-water-quality-parameters)
7. [Operational & Service Metrics](#7-operational--service-metrics)
8. [Compliance Flags](#8-compliance-flags)

---

## 1. Identification & Location Columns

### 1.1 `record_id`

| Property | Value |
|---|---|
| **Data Type** | `TEXT` (string) |
| **Unit** | N/A — unique identifier |
| **Format** | `REC-XXXXXXX` (e.g., `REC-0000001`) |
| **Cardinality** | 163,904 unique values (one per row) |

**Description**: A globally unique identifier for each observation row. Every row in the dataset has a distinct `record_id`. It serves as the primary key and is not analytically meaningful on its own—it exists solely for traceability, audit logging, and join operations when cross-referencing external systems.

**Interpretation**:
- The numeric suffix is zero-padded to 7 digits.
- Record IDs are sequentially assigned but should not be used to infer chronological ordering—use `observation_date` instead.

**Common SQL Usage**:
```sql
-- Count total records
SELECT COUNT(record_id) AS total_records FROM water_nodes;

-- Retrieve a specific observation
SELECT * FROM water_nodes WHERE record_id = 'REC-0000001';

-- Check for duplicates (should return 0)
SELECT record_id, COUNT(*) FROM water_nodes GROUP BY record_id HAVING COUNT(*) > 1;
```

---

### 1.2 `node_id`

| Property | Value |
|---|---|
| **Data Type** | `TEXT` (string) |
| **Unit** | N/A — sensor identifier |
| **Format** | `WN-XXXXX` (e.g., `WN-00001`) |
| **Cardinality** | 832 unique sensor nodes |
| **Avg observations per node** | ~197 |

**Description**: Identifies a specific sensor/monitoring node in the water distribution network. Each node is a physical installation point—typically at a pipe junction, pressure-reduction valve, quality monitoring station, or customer delivery point. A single `node_id` can appear in many rows because observations are recorded across multiple dates.

**Interpretation**:
- **High node coverage** (832 nodes across 10 cities) enables comparative analysis across geographies.
- Each node has a fixed `city`, `state`, `utility_name`, `zone_id`, `node_type`, and infrastructure profile (`pipe_material`, `pipe_age_years`, etc.).
- Time-varying measurements (pressure, flow, quality) change across `observation_date` for the same node.

**Common SQL Usage**:
```sql
-- Count of nodes per city
SELECT city, COUNT(DISTINCT node_id) AS num_nodes FROM water_nodes GROUP BY city;

-- All observations for a specific node
SELECT * FROM water_nodes WHERE node_id = 'WN-00042' ORDER BY observation_date;

-- Average daily volume per node
SELECT node_id, AVG(daily_volume_m3) AS avg_daily_vol FROM water_nodes GROUP BY node_id;
```

---

### 1.3 `utility_name`

| Property | Value |
|---|---|
| **Data Type** | `TEXT` (string) |
| **Unit** | N/A — categorical |
| **Distinct Values** | 10 |

**Valid Values**:
| Utility Name | Full Name | City |
|---|---|---|
| `MCGM` | Municipal Corporation of Greater Mumbai | Mumbai |
| `Delhi Jal Board` | Delhi Jal Board | Delhi |
| `BWSSB` | Bangalore Water Supply & Sewerage Board | Bangalore |
| `HMWSSB` | Hyderabad Metropolitan Water Supply & Sewerage Board | Hyderabad |
| `CMWSSB` | Chennai Metropolitan Water Supply & Sewerage Board | Chennai |
| `PMRDA Water` | Pune Metropolitan Region Development Authority | Pune |
| `AMC Water` | Ahmedabad Municipal Corporation | Ahmedabad |
| `PHED Rajasthan` | Public Health Engineering Dept., Rajasthan | Jaipur |
| `Jal Nigam UP` | Uttar Pradesh Jal Nigam | Lucknow |
| `KMC Water` | Kolkata Municipal Corporation | Kolkata |

**Description**: The water utility or water board responsible for operating the distribution network where the node is located. This is the highest-level organizational grouping in the dataset.

**Interpretation**:
- Each utility serves a distinct city. The `utility_name` ↔ `city` mapping is 1:1.
- Performance benchmarking across utilities reveals governance quality differences.
- Utilities like BWSSB and Delhi Jal Board are known for intermittent supply patterns; MCGM has higher pipe age profiles.

**Common SQL Usage**:
```sql
-- Overall performance by utility
SELECT utility_name,
       AVG(supply_hours_per_day) AS avg_supply_hours,
       AVG(non_revenue_water_pct) AS avg_nrw,
       AVG(pressure_compliance_flag)*100 AS pressure_compliance_pct
FROM water_nodes
GROUP BY utility_name
ORDER BY avg_supply_hours DESC;

-- Compare chlorine compliance across utilities
SELECT utility_name, AVG(chlorine_compliance_flag)*100 AS chlorine_compliance_rate
FROM water_nodes
GROUP BY utility_name;
```

---

### 1.4 `city`

| Property | Value |
|---|---|
| **Data Type** | `TEXT` (string) |
| **Unit** | N/A — categorical |
| **Distinct Values** | 10 |

**Valid Values**: `Mumbai`, `Delhi`, `Bangalore`, `Hyderabad`, `Chennai`, `Pune`, `Ahmedabad`, `Jaipur`, `Lucknow`, `Kolkata`

**Description**: The city in which the monitoring node is physically located. Maps 1:1 with `utility_name`. Useful for geographic filtering, regional analysis, and dashboarding.

**Interpretation**:
- Climate patterns vary significantly across cities (e.g., Chennai vs. Jaipur), which affects water temperature, demand, and seasonal quality patterns.
- Coastal cities (Mumbai, Chennai, Kolkata) may show higher TDS and conductivity.
- Northern cities (Delhi, Jaipur, Lucknow) exhibit wider temperature ranges across seasons.

**Common SQL Usage**:
```sql
-- Average water quality by city
SELECT city,
       AVG(ph_value) AS avg_ph,
       AVG(turbidity_ntu) AS avg_turbidity,
       AVG(residual_chlorine_mg_l) AS avg_chlorine
FROM water_nodes
GROUP BY city;

-- City-level leak frequency
SELECT city, SUM(leak_detection_events) AS total_leaks, COUNT(DISTINCT node_id) AS nodes
FROM water_nodes
GROUP BY city;
```

---

### 1.5 `state`

| Property | Value |
|---|---|
| **Data Type** | `TEXT` (string) |
| **Unit** | N/A — categorical |
| **Distinct Values** | 9 (Maharashtra has 2 cities: Mumbai, Pune) |

**Valid Values**: `Maharashtra`, `Delhi`, `Karnataka`, `Telangana`, `Tamil Nadu`, `Gujarat`, `Rajasthan`, `Uttar Pradesh`, `West Bengal`

**Description**: The Indian state in which the node is located. Note that Maharashtra contains two cities (Mumbai and Pune), so state-level aggregation combines data from both MCGM and PMRDA Water.

**Interpretation**:
- State-level grouping is useful for regulatory compliance reporting, as several regulations are enforced at the state level.
- Delhi is both a city and a state (National Capital Territory).

**Common SQL Usage**:
```sql
-- State-level NRW comparison
SELECT state, AVG(non_revenue_water_pct) AS avg_nrw
FROM water_nodes
GROUP BY state
ORDER BY avg_nrw DESC;

-- Number of nodes per state
SELECT state, COUNT(DISTINCT node_id) AS nodes FROM water_nodes GROUP BY state;
```

---

### 1.6 `zone_id`

| Property | Value |
|---|---|
| **Data Type** | `TEXT` (string) |
| **Unit** | N/A — categorical |
| **Distinct Values** | 5 |

**Valid Values**: `Zone_A`, `Zone_B`, `Zone_C`, `Zone_D`, `Zone_E`

**Description**: A sub-division within each city representing a District Metered Area (DMA) or pressure zone. Zones are defined by the local utility for operational management—they typically correspond to distinct hydraulic pressure zones, each with its own pumping schedule, reservoir, and pipe network.

**Interpretation**:
- The same zone label (e.g., `Zone_A`) in different cities represents different physical areas.
- Always filter by `city` (or `utility_name`) **and** `zone_id` together for meaningful zone-level analysis.
- Zone-level analysis is critical for identifying localized issues: a specific zone might have higher leaks, lower pressure, or worse quality.

**Common SQL Usage**:
```sql
-- Zone-level performance within a city
SELECT zone_id,
       AVG(supply_hours_per_day) AS avg_supply,
       AVG(non_revenue_water_pct) AS avg_nrw,
       SUM(leak_detection_events) AS total_leaks
FROM water_nodes
WHERE city = 'Mumbai'
GROUP BY zone_id;

-- Cross-city zone comparison (always pair with city)
SELECT city, zone_id, AVG(inlet_pressure_bar) AS avg_pressure
FROM water_nodes
GROUP BY city, zone_id
ORDER BY city, zone_id;
```

---

### 1.7 `node_type`

| Property | Value |
|---|---|
| **Data Type** | `TEXT` (string) |
| **Unit** | N/A — categorical |
| **Distinct Values** | 4 |

**Valid Values**:
| Node Type | Description |
|---|---|
| `Pressure_Only` | Monitors only pressure metrics |
| `Combined` | Full instrumentation — pressure, flow, and quality |
| `Flow_Junction` | Monitors flow and hydraulic parameters at pipe junctions |
| `Quality_Only` | Dedicated water quality monitoring station |

**Description**: Classifies the type of sensor instrumentation installed at each node. This determines which measurements are most reliable and primary for that node.

**Interpretation**:
- **Combined** nodes provide the richest data — all metrics are instrumented.
- **Pressure_Only** nodes may still report flow/quality values (estimated or interpolated), but pressure readings are the primary, calibrated measurements.
- **Quality_Only** nodes are typically installed at treatment plant outlets, reservoir inlets, or consumer delivery points where quality monitoring is the priority.
- When analysing quality data, prefer `Quality_Only` or `Combined` nodes for highest accuracy.
- When analysing pressure or flow, prefer `Pressure_Only`, `Flow_Junction`, or `Combined` nodes.

**Common SQL Usage**:
```sql
-- Distribution of node types
SELECT node_type, COUNT(DISTINCT node_id) AS num_nodes FROM water_nodes GROUP BY node_type;

-- Quality analysis using quality-focused nodes
SELECT city, AVG(turbidity_ntu) AS avg_turbidity
FROM water_nodes
WHERE node_type IN ('Quality_Only', 'Combined')
GROUP BY city;
```

---

## 2. Infrastructure & Asset Columns

### 2.1 `pipe_material`

| Property | Value |
|---|---|
| **Data Type** | `TEXT` (string) |
| **Unit** | N/A — categorical |
| **Distinct Values** | 5 |

**Valid Values**:
| Material | Properties | Typical Use |
|---|---|---|
| `HDPE` | High-Density Polyethylene; flexible, corrosion-resistant | Modern installations, replacement programs |
| `Cast_Iron` | Traditional; durable but prone to corrosion and tuberculation | Older networks (pre-1990) |
| `PVC` | Polyvinyl Chloride; lightweight, chemical-resistant | Medium-pressure residential areas |
| `Asbestos_Cement` | Legacy material; being phased out due to health concerns | Very old networks (pre-1980) |
| `Ductile_Iron` | Stronger than cast iron; better fracture resistance | Transmission mains, high-pressure zones |

**Description**: The material of the pipe at or immediately adjacent to the monitoring node. Pipe material significantly influences water quality (iron leaching, turbidity), failure risk, and hydraulic characteristics.

**Interpretation**:
- **Cast_Iron** and **Asbestos_Cement** pipes correlate with higher iron concentrations, turbidity, and leak events.
- **HDPE** and **PVC** typically show lower iron levels and fewer leaks — these are modern materials.
- **Ductile_Iron** is used for high-pressure mains and is more resistant to failure than Cast_Iron but can still corrode.
- Pipe material combined with `pipe_age_years` is the strongest predictor of asset failure risk.

**Common SQL Usage**:
```sql
-- Average iron levels by pipe material
SELECT pipe_material, AVG(iron_ppb) AS avg_iron, AVG(turbidity_ntu) AS avg_turbidity
FROM water_nodes
GROUP BY pipe_material
ORDER BY avg_iron DESC;

-- Leak frequency by material
SELECT pipe_material,
       SUM(leak_detection_events) / COUNT(DISTINCT node_id) AS leaks_per_node
FROM water_nodes
GROUP BY pipe_material;
```

---

### 2.2 `pipe_age_years`

| Property | Value |
|---|---|
| **Data Type** | `INTEGER` |
| **Unit** | Years |
| **Range** | 3 – 55 |
| **Mean** | ~23.6 |
| **Median** | ~24 |

**Description**: The age of the pipe infrastructure at the node location, measured in years from installation. This is a static attribute per node (does not change across observation dates within this dataset window).

**Interpretation**:
- **< 10 years**: New infrastructure; low failure risk; typically HDPE or PVC.
- **10 – 25 years**: Mid-life; routine maintenance phase; condition depends on material.
- **25 – 40 years**: Aging infrastructure; increased leak risk, higher iron levels from corroding pipes.
- **> 40 years**: Critical age; high probability of failure; prioritize for replacement. Cast_Iron and Asbestos_Cement pipes in this range are highest risk.
- Pipe age is a key input to the **Asset Risk Score** KPI.

**Common SQL Usage**:
```sql
-- Average pipe age by city
SELECT city, AVG(pipe_age_years) AS avg_pipe_age FROM water_nodes GROUP BY city ORDER BY avg_pipe_age DESC;

-- Correlation between age and leaks
SELECT
  CASE
    WHEN pipe_age_years < 10 THEN '0-9'
    WHEN pipe_age_years < 20 THEN '10-19'
    WHEN pipe_age_years < 30 THEN '20-29'
    WHEN pipe_age_years < 40 THEN '30-39'
    ELSE '40+'
  END AS age_group,
  AVG(leak_detection_events) AS avg_leaks,
  AVG(iron_ppb) AS avg_iron
FROM water_nodes
GROUP BY age_group
ORDER BY age_group;
```

---

### 2.3 `pipe_diameter_mm`

| Property | Value |
|---|---|
| **Data Type** | `INTEGER` |
| **Unit** | Millimetres (mm) |
| **Range** | 75 – 500 |
| **Mean** | ~189.5 |

**Description**: The internal diameter of the pipe at the node location. Pipe diameter directly affects flow capacity, velocity, and head loss.

**Interpretation**:
- **75 – 100 mm**: Small distribution pipes serving individual streets or small clusters.
- **100 – 200 mm**: Standard distribution mains; most common size.
- **200 – 300 mm**: Sub-transmission mains; serve multiple zones.
- **300 – 500 mm**: Transmission mains; trunk lines from treatment plants or reservoirs.
- Smaller diameters at the same flow rate produce higher velocities and greater head loss.
- Larger diameters provide more buffer capacity and lower pressure fluctuation.

**Common SQL Usage**:
```sql
-- Flow velocity vs diameter
SELECT pipe_diameter_mm, AVG(flow_velocity_m_s) AS avg_velocity, AVG(hydraulic_head_loss_m_per_km) AS avg_head_loss
FROM water_nodes
GROUP BY pipe_diameter_mm
ORDER BY pipe_diameter_mm;

-- Distribution of pipe sizes
SELECT pipe_diameter_mm, COUNT(DISTINCT node_id) AS num_nodes
FROM water_nodes
GROUP BY pipe_diameter_mm
ORDER BY pipe_diameter_mm;
```

---

### 2.4 `elevation_m`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Metres above sea level |
| **Range** | 5.1 – 149.4 |

**Description**: The geographic elevation of the monitoring node. Elevation is critical in gravity-fed water supply systems—higher elevations require more pumping energy to maintain adequate pressure.

**Interpretation**:
- **Low elevation (< 30 m)**: Typically flat terrain; gravity feed easier; common in coastal cities (Mumbai, Chennai, Kolkata).
- **Medium elevation (30 – 80 m)**: Moderate terrain; mixed gravity/pumped supply.
- **High elevation (> 80 m)**: Hilltop areas; often experience lower pressure; may need dedicated booster pumps. Common in Bangalore, Pune, Hyderabad.
- Nodes at higher elevations often show lower `inlet_pressure_bar` and higher `pressure_differential_bar`.

**Common SQL Usage**:
```sql
-- Pressure vs elevation correlation
SELECT
  CASE WHEN elevation_m < 30 THEN 'Low' WHEN elevation_m < 80 THEN 'Medium' ELSE 'High' END AS elevation_band,
  AVG(inlet_pressure_bar) AS avg_inlet_pressure,
  AVG(supply_hours_per_day) AS avg_supply_hours
FROM water_nodes
GROUP BY elevation_band;
```

---

### 2.5 `distance_to_treatment_plant_km`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Kilometres (km) |
| **Range** | 1.0 – 40.0 |

**Description**: The network distance from the node to the nearest water treatment plant (WTP). This affects water age, residual chlorine decay, and pressure at the node.

**Interpretation**:
- **< 5 km**: Close to WTP; expect higher chlorine residual, lower water age, fresher water.
- **5 – 15 km**: Mid-range; standard distribution distance.
- **15 – 30 km**: Distant; chlorine may have decayed below effective levels; water age increases.
- **> 30 km**: Very distant; highest risk of quality degradation; may need rechlorination stations.
- Strong positive correlation with `water_age_hours` and negative correlation with `residual_chlorine_mg_l`.

**Common SQL Usage**:
```sql
-- Chlorine decay with distance
SELECT
  ROUND(distance_to_treatment_plant_km / 5) * 5 AS distance_band_km,
  AVG(residual_chlorine_mg_l) AS avg_chlorine,
  AVG(water_age_hours) AS avg_water_age
FROM water_nodes
GROUP BY distance_band_km
ORDER BY distance_band_km;
```

---

### 2.6 `pump_station_nearby`

| Property | Value |
|---|---|
| **Data Type** | `INTEGER` (binary) |
| **Unit** | Boolean (0 = No, 1 = Yes) |
| **Distribution** | ~47% have a pump station nearby |

**Description**: Indicates whether a pumping station is located in proximity to the node. Pump stations boost pressure in the network and are typically placed at low-pressure zones, elevation transitions, or far-network extremities.

**Interpretation**:
- **1 (Yes)**: Node benefits from boosted pressure; typically shows higher `inlet_pressure_bar` and more stable pressure.
- **0 (No)**: Node relies on gravity or upstream pressure; may be more vulnerable to pressure drops during peak demand.
- Nodes with pump stations nearby tend to have more stable `pressure_hourly_variance`.

**Common SQL Usage**:
```sql
-- Impact of pump station on pressure
SELECT pump_station_nearby,
       AVG(inlet_pressure_bar) AS avg_pressure,
       AVG(pressure_hourly_variance) AS avg_variance,
       AVG(supply_hours_per_day) AS avg_supply
FROM water_nodes
GROUP BY pump_station_nearby;
```

---

### 2.7 `reservoir_fed`

| Property | Value |
|---|---|
| **Data Type** | `INTEGER` (binary) |
| **Unit** | Boolean (0 = No, 1 = Yes) |
| **Distribution** | ~33% are reservoir-fed |

**Description**: Indicates whether the node is supplied from a service reservoir (elevated storage tank or ground-level reservoir). Reservoir-fed nodes benefit from storage buffering, which stabilises pressure and supply continuity.

**Interpretation**:
- **1 (Yes)**: More consistent supply; less sensitive to pump schedule variations; typically higher `supply_hours_per_day`.
- **0 (No)**: Direct pumping supply; supply depends on pump schedule; more vulnerable to interruptions.
- Reservoir-fed nodes often have higher `water_age_hours` because water sits in the reservoir before distribution.

**Common SQL Usage**:
```sql
-- Reservoir-fed vs direct supply comparison
SELECT reservoir_fed,
       AVG(supply_hours_per_day) AS avg_supply,
       AVG(water_age_hours) AS avg_water_age,
       AVG(service_interruptions_count) AS avg_interruptions
FROM water_nodes
GROUP BY reservoir_fed;
```

---

### 2.8 `num_customer_connections`

| Property | Value |
|---|---|
| **Data Type** | `INTEGER` |
| **Unit** | Count of customer connections (households/premises) |
| **Range** | 50 – 598 |
| **Mean** | ~252 |

**Description**: The number of customer connections (household taps, commercial connections, etc.) served downstream of this node. This is a static attribute representing the demand load on the node.

**Interpretation**:
- **< 100**: Low-density area; fewer customers; lower demand.
- **100 – 300**: Typical residential area.
- **300 – 500**: High-density residential or mixed commercial area.
- **> 500**: Very high-density; potential stress point; may need larger pipe or additional supply.
- Combined with `daily_volume_m3`, enables per-capita or per-connection consumption analysis.
- High connection count with low `supply_hours_per_day` indicates under-served areas.

**Common SQL Usage**:
```sql
-- Per-connection daily volume
SELECT node_id,
       AVG(daily_volume_m3) / AVG(num_customer_connections) AS vol_per_connection
FROM water_nodes
GROUP BY node_id
ORDER BY vol_per_connection DESC
LIMIT 10;

-- Connection density by city
SELECT city, AVG(num_customer_connections) AS avg_connections FROM water_nodes GROUP BY city;
```

---

### 2.9 `demand_category`

| Property | Value |
|---|---|
| **Data Type** | `TEXT` (string) |
| **Unit** | N/A — categorical |
| **Distinct Values** | 5 |

**Valid Values**: `Residential`, `Commercial`, `Industrial`, `Agricultural`, `Mixed`

**Description**: Classifies the primary demand type of the area served by the node. Different demand categories have different consumption patterns, peak hours, and quality requirements.

**Interpretation**:
- **Residential**: Peak demand in mornings (6-9 AM) and evenings (6-9 PM); quality standards for drinking water apply.
- **Commercial**: More uniform demand during business hours; moderate volume.
- **Industrial**: High volume, may have specific quality needs (e.g., low hardness); often off-peak bulk consumption.
- **Agricultural**: Seasonal demand; less stringent quality requirements; typically higher volume.
- **Mixed**: Combination of categories; most complex demand pattern.

**Common SQL Usage**:
```sql
-- Demand pattern by category
SELECT demand_category,
       AVG(avg_flow_lps) AS avg_flow,
       AVG(daily_volume_m3) AS avg_daily_vol,
       AVG(peak_flow_lps) / AVG(avg_flow_lps) AS peaking_factor
FROM water_nodes
GROUP BY demand_category;
```

---

### 2.10 `pipe_length_upstream_m`

| Property | Value |
|---|---|
| **Data Type** | `INTEGER` |
| **Unit** | Metres (m) |
| **Range** | 52 – 1,996 |

**Description**: The total length of the pipe network upstream of this node, measured in metres. This represents the distance water has travelled through the distribution network to reach this point.

**Interpretation**:
- **Short upstream length (< 200 m)**: Node is close to a junction or source; less friction loss; better pressure.
- **Long upstream length (> 1,000 m)**: Significant friction loss; more opportunity for quality degradation; higher head loss.
- Correlates with `hydraulic_head_loss_m_per_km` and `water_age_hours`.
- Longer upstream pipe also means more joints and potential leak points.

**Common SQL Usage**:
```sql
-- Head loss vs upstream length
SELECT
  CASE WHEN pipe_length_upstream_m < 500 THEN '<500m'
       WHEN pipe_length_upstream_m < 1000 THEN '500-1000m'
       ELSE '>1000m' END AS upstream_band,
  AVG(hydraulic_head_loss_m_per_km) AS avg_head_loss
FROM water_nodes
GROUP BY upstream_band;
```

---

## 3. Temporal Columns

### 3.1 `observation_date`

| Property | Value |
|---|---|
| **Data Type** | `TEXT` (date string) |
| **Format** | `YYYY-MM-DD` |
| **Range** | `2024-01-01` to `2024-07-15` |
| **Duration** | 197 days (~6.5 months) |

**Description**: The date on which the observation was recorded. Each row represents a single day's aggregated readings for a specific node. The dataset covers the first half of 2024, spanning winter, summer, and pre-monsoon seasons.

**Interpretation**:
- Use for time-series analysis, trend detection, and seasonal comparisons.
- Not every node has an observation on every date (some may have gaps).
- In SQLite, date comparisons work with string format `YYYY-MM-DD`.

**Common SQL Usage**:
```sql
-- Daily system-wide average pressure
SELECT observation_date, AVG(inlet_pressure_bar) AS avg_pressure
FROM water_nodes
GROUP BY observation_date
ORDER BY observation_date;

-- Monthly trend
SELECT month_name, AVG(daily_volume_m3) AS avg_volume
FROM water_nodes
GROUP BY month_num, month_name
ORDER BY month_num;

-- Date range filter
SELECT * FROM water_nodes WHERE observation_date BETWEEN '2024-03-01' AND '2024-03-31';
```

---

### 3.2 `day_of_week`

| Property | Value |
|---|---|
| **Data Type** | `TEXT` (string) |
| **Unit** | N/A — categorical |
| **Distinct Values** | 7 |

**Valid Values**: `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday`

**Description**: The day of the week for the observation date. Useful for analysing weekday vs. weekend demand patterns.

**Common SQL Usage**:
```sql
-- Weekday demand pattern
SELECT day_of_week, AVG(daily_volume_m3) AS avg_volume, AVG(peak_flow_lps) AS avg_peak_flow
FROM water_nodes
GROUP BY day_of_week;
```

---

### 3.3 `is_weekend`

| Property | Value |
|---|---|
| **Data Type** | `INTEGER` (binary) |
| **Unit** | Boolean (0 = Weekday, 1 = Weekend) |

**Description**: Binary flag indicating whether the observation falls on a Saturday or Sunday. Simplifies weekday/weekend comparisons without needing to filter on `day_of_week`.

**Common SQL Usage**:
```sql
-- Weekend vs weekday comparison
SELECT is_weekend, AVG(daily_volume_m3) AS avg_vol, AVG(avg_flow_lps) AS avg_flow
FROM water_nodes
GROUP BY is_weekend;
```

---

### 3.4 `month_num`

| Property | Value |
|---|---|
| **Data Type** | `INTEGER` |
| **Unit** | Month number |
| **Range** | 1 – 7 (January – July) |

**Description**: Numeric month extracted from `observation_date`. Use for `ORDER BY` in temporal queries.

**Common SQL Usage**:
```sql
SELECT month_num, AVG(water_temperature_c) AS avg_temp FROM water_nodes GROUP BY month_num ORDER BY month_num;
```

---

### 3.5 `month_name`

| Property | Value |
|---|---|
| **Data Type** | `TEXT` (string) |
| **Distinct Values** | 7 |

**Valid Values**: `Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`

**Description**: Abbreviated month name. Use for display/labelling in charts and reports. Always order by `month_num` rather than alphabetically.

---

### 3.6 `season`

| Property | Value |
|---|---|
| **Data Type** | `TEXT` (string) |
| **Distinct Values** | 3 |

**Valid Values**:
| Season | Typical Months | Characteristics |
|---|---|---|
| `Winter` | Jan – Feb | Lower temperatures; lower demand; better water quality |
| `Summer` | Mar – May | High temperatures; peak demand; stress on supply systems |
| `Pre_Monsoon` | Jun – Jul | Very high temperatures; highest demand; possible quality degradation before rains |

**Description**: Indian meteorological season classification. Seasonal patterns strongly influence demand, water quality, and infrastructure stress.

**Interpretation**:
- **Winter**: Lower evaporation, lower demand, typically better quality metrics.
- **Summer**: Higher demand (domestic cooling, agriculture); stress on supply hours; higher water temperature promotes bacterial growth.
- **Pre_Monsoon**: Critical period; reservoir levels at lowest; highest water stress; demand peaks.

**Common SQL Usage**:
```sql
-- Seasonal performance comparison
SELECT season,
       AVG(supply_hours_per_day) AS avg_supply,
       AVG(daily_volume_m3) AS avg_volume,
       AVG(water_temperature_c) AS avg_temp,
       AVG(residual_chlorine_mg_l) AS avg_chlorine
FROM water_nodes
GROUP BY season;
```

---

## 4. Pressure Metrics

### 4.1 `inlet_pressure_bar`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Bar (1 bar ≈ 10.2 metres of water head) |
| **Range** | 0.5 – 6.96 |

**Description**: The water pressure measured at the inlet side of the node. This is the pressure of water arriving at the monitoring point from the upstream network.

**Interpretation**:
- **< 1.0 bar**: Critically low pressure; customers may not receive water at upper floors; potential for back-siphonage contamination.
- **1.0 – 2.0 bar**: Low but functional for ground-level connections.
- **2.0 – 4.0 bar**: Normal operating range for most Indian distribution systems.
- **4.0 – 6.0 bar**: High pressure; adequate for multi-storey buildings.
- **> 6.0 bar**: Very high; risk of pipe bursts and fitting failures.
- The CPHEEO guideline recommends a minimum residual pressure of 7 metres (~0.7 bar) at the consumer tap.

**Common SQL Usage**:
```sql
-- Pressure distribution
SELECT city, AVG(inlet_pressure_bar) AS avg_pressure, MIN(inlet_pressure_bar) AS min_pressure
FROM water_nodes
GROUP BY city
ORDER BY avg_pressure;

-- Low-pressure nodes
SELECT node_id, city, AVG(inlet_pressure_bar) AS avg_inlet
FROM water_nodes
GROUP BY node_id, city
HAVING AVG(inlet_pressure_bar) < 1.0;
```

---

### 4.2 `outlet_pressure_bar`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Bar |
| **Range** | 0.2 – 6.67 |

**Description**: The water pressure at the outlet side of the node. This represents the pressure delivered to downstream consumers or the next network segment.

**Interpretation**:
- Always ≤ `inlet_pressure_bar` (pressure drops due to friction, elevation changes, and local consumption).
- The difference (`inlet_pressure_bar - outlet_pressure_bar`) is approximately `pressure_differential_bar`.
- Very low outlet pressure (< 0.5 bar) means downstream customers may not receive adequate supply.

**Common SQL Usage**:
```sql
-- Nodes with significant pressure drop
SELECT node_id, AVG(inlet_pressure_bar) AS avg_inlet, AVG(outlet_pressure_bar) AS avg_outlet,
       AVG(inlet_pressure_bar) - AVG(outlet_pressure_bar) AS avg_drop
FROM water_nodes
GROUP BY node_id
HAVING avg_drop > 1.0
ORDER BY avg_drop DESC;
```

---

### 4.3 `pressure_differential_bar`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Bar |
| **Range** | 0.05 – 1.42 |

**Description**: The pressure drop across the node, calculated as the difference between inlet and outlet pressure. Represents energy lost due to friction, fittings, valves, and consumption at the node.

**Interpretation**:
- **< 0.2 bar**: Minimal loss; good hydraulic condition; large-diameter or short pipe segment.
- **0.2 – 0.5 bar**: Normal differential for distribution nodes.
- **0.5 – 1.0 bar**: Elevated differential; possible partial blockage, undersized pipe, or heavy local demand.
- **> 1.0 bar**: High differential; investigate for valve obstructions, tuberculation in old pipes, or excessive demand.

**Common SQL Usage**:
```sql
-- Nodes with high pressure differential (potential blockage)
SELECT node_id, city, pipe_material, pipe_age_years,
       AVG(pressure_differential_bar) AS avg_diff
FROM water_nodes
GROUP BY node_id, city, pipe_material, pipe_age_years
HAVING AVG(pressure_differential_bar) > 0.8
ORDER BY avg_diff DESC;
```

---

### 4.4 `min_pressure_bar`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Bar |
| **Range** | 0.1 – 6.59 |

**Description**: The minimum pressure recorded at the node during the observation day. Captures the worst-case pressure condition, typically occurring during peak demand hours.

**Interpretation**:
- This is the most critical pressure value for compliance checking — if `min_pressure_bar` falls below the minimum threshold, customers experienced inadequate pressure at some point during the day.
- Values < 0.7 bar indicate potential compliance failure.
- The gap between `min_pressure_bar` and `max_pressure_bar` reveals daily pressure variation.

**Common SQL Usage**:
```sql
-- Days with critically low minimum pressure
SELECT observation_date, COUNT(*) AS low_pressure_nodes
FROM water_nodes
WHERE min_pressure_bar < 0.5
GROUP BY observation_date
ORDER BY low_pressure_nodes DESC;
```

---

### 4.5 `max_pressure_bar`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Bar |
| **Range** | 0.56 – 7.0 |

**Description**: The maximum pressure recorded at the node during the observation day. Captures peak pressure conditions, typically during off-peak hours or when pumps are operating at full capacity.

**Interpretation**:
- Very high values (> 6 bar) may indicate excessive pumping or pressure surges (water hammer).
- The ratio `max_pressure_bar / min_pressure_bar` indicates pressure stability — values close to 1.0 mean stable pressure.
- Large daily pressure swings (high max, low min) indicate intermittent supply patterns.

**Common SQL Usage**:
```sql
-- Pressure range (stability indicator)
SELECT node_id, AVG(max_pressure_bar - min_pressure_bar) AS avg_pressure_range
FROM water_nodes
GROUP BY node_id
ORDER BY avg_pressure_range DESC
LIMIT 20;
```

---

### 4.6 `pressure_hourly_variance`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Bar² (variance of hourly pressure readings) |
| **Range** | 0.0 – 0.76 |

**Description**: The statistical variance of hourly pressure readings within the observation day. Quantifies pressure stability — a key indicator of supply consistency.

**Interpretation**:
- **< 0.05**: Very stable pressure; continuous 24×7 supply or well-regulated zone.
- **0.05 – 0.20**: Moderate variation; normal for intermittent supply systems.
- **0.20 – 0.50**: High variation; significant pressure fluctuations during the day.
- **> 0.50**: Extreme variation; likely intermittent supply with pressure cycling (pump on/off).
- Low variance is desirable — it indicates stable, predictable pressure for consumers.

**Common SQL Usage**:
```sql
-- Most unstable pressure nodes
SELECT node_id, city, AVG(pressure_hourly_variance) AS avg_variance
FROM water_nodes
GROUP BY node_id, city
ORDER BY avg_variance DESC
LIMIT 10;

-- Variance by supply pattern
SELECT reservoir_fed, AVG(pressure_hourly_variance) AS avg_variance
FROM water_nodes
GROUP BY reservoir_fed;
```

---

## 5. Flow & Hydraulic Metrics

### 5.1 `avg_flow_lps`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Litres per second (LPS) |
| **Range** | 0.5 – 114.3 |

**Description**: The average water flow rate through the node during the observation day, measured in litres per second. This is the primary volumetric throughput metric.

**Interpretation**:
- **< 5 LPS**: Low flow; small distribution pipe or low-demand area.
- **5 – 30 LPS**: Moderate flow; typical for residential distribution nodes.
- **30 – 60 LPS**: High flow; trunk mains or commercial/industrial areas.
- **> 60 LPS**: Very high flow; major transmission mains.
- Sudden drops in flow (compared to historical average for the same node) may indicate blockage, valve closure, or upstream disruption.
- Sudden increases may indicate a pipe burst downstream (unmetered flow).

**Common SQL Usage**:
```sql
-- Average flow by demand category
SELECT demand_category, AVG(avg_flow_lps) AS avg_flow FROM water_nodes GROUP BY demand_category;

-- Flow trend for a specific node
SELECT observation_date, avg_flow_lps FROM water_nodes WHERE node_id = 'WN-00100' ORDER BY observation_date;
```

---

### 5.2 `peak_flow_lps`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Litres per second (LPS) |
| **Range** | 0.8 – 180.0 |

**Description**: The maximum instantaneous flow rate recorded during the observation day. Represents peak demand conditions.

**Interpretation**:
- The **peaking factor** = `peak_flow_lps / avg_flow_lps` indicates demand variability.
  - Factor < 1.5: Stable demand (industrial, continuous supply areas).
  - Factor 1.5 – 2.5: Normal residential peaking.
  - Factor > 2.5: Extreme peaking; may indicate intermittent supply where consumers rush to store water when supply is available.
- Peak flow drives pipe sizing requirements — pipes must handle peak without excessive velocity.

**Common SQL Usage**:
```sql
-- Peaking factor analysis
SELECT demand_category,
       AVG(peak_flow_lps / avg_flow_lps) AS avg_peaking_factor
FROM water_nodes
WHERE avg_flow_lps > 0
GROUP BY demand_category;
```

---

### 5.3 `daily_volume_m3`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Cubic metres (m³) |
| **Range** | 5.4 – 8,356 |

**Description**: The total volume of water that passed through the node during the observation day. This is the integral of flow rate over the supply period.

**Interpretation**:
- **Relationship**: `daily_volume_m3 ≈ avg_flow_lps × supply_hours_per_day × 3.6` (conversion factor: 1 LPS × 1 hour = 3.6 m³).
- **< 50 m³/day**: Small distribution point.
- **50 – 500 m³/day**: Typical residential distribution node.
- **500 – 2,000 m³/day**: Large distribution or sub-transmission node.
- **> 2,000 m³/day**: Major transmission main.
- Combined with `num_customer_connections`, derives per-connection demand (the **Demand per Connection** KPI).
- 1 m³ = 1,000 litres.

**Common SQL Usage**:
```sql
-- Total daily volume by city
SELECT city, SUM(daily_volume_m3) AS total_volume, observation_date
FROM water_nodes
GROUP BY city, observation_date
ORDER BY observation_date;

-- Per-connection daily volume
SELECT city, AVG(daily_volume_m3 * 1.0 / num_customer_connections) AS avg_vol_per_conn
FROM water_nodes
GROUP BY city;
```

---

### 5.4 `flow_velocity_m_s`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Metres per second (m/s) |
| **Range** | 0.01 – 5.0 |

**Description**: The velocity of water flow through the pipe at the node. Derived from flow rate and pipe cross-sectional area: `velocity = flow / area`.

**Interpretation**:
- **< 0.3 m/s**: Very low velocity; risk of sediment deposition; stagnant water quality issues.
- **0.3 – 1.0 m/s**: Optimal operating range; balances hydraulic efficiency with minimal erosion.
- **1.0 – 2.0 m/s**: Acceptable; higher friction losses; some noise.
- **2.0 – 3.0 m/s**: High velocity; significant head loss; pipe noise; accelerated wear.
- **> 3.0 m/s**: Excessive; risk of water hammer, pipe erosion, and fitting damage.
- CPHEEO recommends maintaining velocity between 0.6 – 1.2 m/s in distribution mains.

**Common SQL Usage**:
```sql
-- Nodes with excessive velocity
SELECT node_id, city, pipe_diameter_mm, AVG(flow_velocity_m_s) AS avg_velocity
FROM water_nodes
GROUP BY node_id, city, pipe_diameter_mm
HAVING AVG(flow_velocity_m_s) > 2.0
ORDER BY avg_velocity DESC;
```

---

### 5.5 `hydraulic_head_loss_m_per_km`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Metres of head loss per kilometre of pipe (m/km) |
| **Range** | 0.3 – 26.3 |

**Description**: The hydraulic gradient — the rate of energy loss due to friction as water flows through the pipe. Calculated using the Hazen-Williams or Darcy-Weisbach equation based on flow velocity, pipe diameter, and pipe roughness.

**Interpretation**:
- **< 2 m/km**: Low head loss; good hydraulic condition; large or smooth pipe.
- **2 – 5 m/km**: Normal range for distribution mains.
- **5 – 10 m/km**: Elevated; pipe may be undersized, partially blocked, or heavily corroded.
- **> 10 m/km**: Critical; severe hydraulic inefficiency; immediate investigation required.
- High head loss combined with old cast iron pipes strongly suggests internal corrosion and tuberculation.
- This is the key input to the **Hydraulic Efficiency** KPI.

**Common SQL Usage**:
```sql
-- Head loss by pipe material and age
SELECT pipe_material,
  CASE WHEN pipe_age_years < 20 THEN 'Young' ELSE 'Old' END AS age_group,
  AVG(hydraulic_head_loss_m_per_km) AS avg_head_loss
FROM water_nodes
GROUP BY pipe_material, age_group;
```

---

## 6. Water Quality Parameters

### 6.1 `ph_value`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | pH units (dimensionless, logarithmic scale) |
| **Range** | 6.0 – 8.34 |

**Description**: The pH of the water sample at the node. pH measures the hydrogen ion concentration and indicates whether water is acidic (< 7) or alkaline (> 7).

**Interpretation**:
- **< 6.5**: Acidic; below BIS desirable limit; can corrode metallic pipes, leaching lead and copper.
- **6.5 – 7.5**: Slightly acidic to neutral; ideal for drinking water.
- **7.5 – 8.5**: Slightly alkaline; common in Indian groundwater; within BIS permissible limit.
- **> 8.5**: Excessively alkaline; beyond BIS limit; may indicate industrial contamination.
- **BIS IS 10500:2012**: Desirable 6.5 – 8.5.
- pH influences chlorine disinfection effectiveness — chlorine is most effective at pH 6.5 – 7.5.

**Common SQL Usage**:
```sql
-- pH distribution by city
SELECT city, AVG(ph_value) AS avg_ph, MIN(ph_value) AS min_ph, MAX(ph_value) AS max_ph
FROM water_nodes
GROUP BY city;

-- Out-of-range pH observations
SELECT COUNT(*) AS violations FROM water_nodes WHERE ph_value < 6.5 OR ph_value > 8.5;
```

---

### 6.2 `turbidity_ntu`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Nephelometric Turbidity Units (NTU) |
| **Range** | 0.05 – 29.2 |

**Description**: Turbidity measures the cloudiness or haziness of water caused by suspended particles (silt, clay, organic matter, microorganisms). It is the most sensitive indicator of treatment effectiveness and distribution system integrity.

**Interpretation**:
- **< 1 NTU**: Excellent; meets BIS desirable limit; effective disinfection possible.
- **1 – 5 NTU**: Acceptable; within BIS permissible limit; adequate for most uses.
- **5 – 10 NTU**: Elevated; indicates possible contamination, pipe disturbance, or treatment issues.
- **> 10 NTU**: High; unacceptable for drinking; potential health risk; investigate immediately.
- **> 20 NTU**: Critical; water is visibly cloudy; consumers will complain.
- High turbidity reduces chlorine effectiveness (particles shield bacteria from disinfection).
- Sudden turbidity spikes often indicate pipe breaks, construction disturbances, or backflow contamination.

**Common SQL Usage**:
```sql
-- Turbidity violations
SELECT city, COUNT(*) AS high_turbidity_count
FROM water_nodes
WHERE turbidity_ntu > 5
GROUP BY city
ORDER BY high_turbidity_count DESC;

-- Turbidity vs pipe material
SELECT pipe_material, AVG(turbidity_ntu) AS avg_turbidity FROM water_nodes GROUP BY pipe_material;
```

---

### 6.3 `residual_chlorine_mg_l`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Milligrams per litre (mg/L) |
| **Range** | 0.01 – 1.11 |

**Description**: The concentration of free chlorine remaining in the water at the node. Residual chlorine is the primary disinfectant barrier preventing microbial regrowth in the distribution system.

**Interpretation**:
- **< 0.2 mg/L**: Below WHO/BIS recommended minimum; inadequate disinfection; bacterial regrowth risk. This drives `chlorine_compliance_flag = 0`.
- **0.2 – 0.5 mg/L**: Ideal range; effective disinfection with minimal taste/odour impact.
- **0.5 – 1.0 mg/L**: Acceptable; may produce slight chlorine taste; still safe.
- **> 1.0 mg/L**: High but within BIS maximum; consumers may notice strong chlorine taste/odour.
- Chlorine decays with distance from the treatment plant, water age, temperature, and organic matter.
- The 61.8% compliance rate in the dataset indicates that nearly 40% of observations have inadequate chlorine — this is a critical operational issue.

**Common SQL Usage**:
```sql
-- Chlorine compliance by city
SELECT city, AVG(chlorine_compliance_flag) * 100 AS compliance_pct
FROM water_nodes
GROUP BY city
ORDER BY compliance_pct;

-- Chlorine decay with distance
SELECT
  CAST(distance_to_treatment_plant_km / 5 AS INTEGER) * 5 AS distance_band,
  AVG(residual_chlorine_mg_l) AS avg_chlorine
FROM water_nodes
GROUP BY distance_band
ORDER BY distance_band;
```

---

### 6.4 `total_dissolved_solids_mg_l`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Milligrams per litre (mg/L) |
| **Range** | 30 – 975 |

**Description**: Total Dissolved Solids (TDS) measures the combined concentration of all dissolved inorganic salts and organic matter in water, including calcium, magnesium, sodium, potassium, bicarbonate, chloride, and sulphate ions.

**Interpretation**:
- **< 300 mg/L**: Excellent; very pure water.
- **300 – 500 mg/L**: Good; within BIS desirable limit.
- **500 – 1,000 mg/L**: Acceptable but exceeds desirable limit; within BIS permissible limit of 2,000 mg/L.
- **> 1,000 mg/L**: High; may have salty or bitter taste; potential health concerns with long-term consumption.
- High TDS often correlates with high `conductivity_us_cm` and `water_hardness_mg_l`.
- Source-dependent: groundwater sources typically have higher TDS than surface water.

**Common SQL Usage**:
```sql
-- TDS by city
SELECT city, AVG(total_dissolved_solids_mg_l) AS avg_tds FROM water_nodes GROUP BY city ORDER BY avg_tds DESC;

-- TDS vs hardness correlation
SELECT
  CASE WHEN total_dissolved_solids_mg_l < 300 THEN 'Low' WHEN total_dissolved_solids_mg_l < 500 THEN 'Medium' ELSE 'High' END AS tds_band,
  AVG(water_hardness_mg_l) AS avg_hardness,
  AVG(conductivity_us_cm) AS avg_conductivity
FROM water_nodes
GROUP BY tds_band;
```

---

### 6.5 `conductivity_us_cm`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Microsiemens per centimetre (µS/cm) |
| **Range** | 60 – 1,435 |

**Description**: Electrical conductivity of the water, which measures the water's ability to conduct electricity. It is directly proportional to the concentration of dissolved ions (salts, minerals).

**Interpretation**:
- **< 200 µS/cm**: Low mineralisation; very pure water (surface water sources).
- **200 – 800 µS/cm**: Normal for treated municipal water.
- **800 – 1,200 µS/cm**: Elevated; may indicate mixing with groundwater or insufficient treatment.
- **> 1,200 µS/cm**: High; investigate source water quality.
- Rule of thumb: `TDS ≈ conductivity × 0.65` (approximate conversion factor).
- Sudden changes in conductivity can indicate contamination events or source water changes.

**Common SQL Usage**:
```sql
-- Conductivity vs TDS verification
SELECT AVG(total_dissolved_solids_mg_l / conductivity_us_cm) AS tds_to_conductivity_ratio
FROM water_nodes
WHERE conductivity_us_cm > 0;
```

---

### 6.6 `water_temperature_c`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Degrees Celsius (°C) |
| **Range** | 10.0 – 41.3 |

**Description**: The temperature of the water at the node. Water temperature affects treatment process efficiency, microbial growth rates, chlorine decay, and consumer acceptability.

**Interpretation**:
- **< 15°C**: Cold; low microbial growth; slow chlorine decay; winter in northern cities.
- **15 – 25°C**: Moderate; optimal for most treatment processes.
- **25 – 35°C**: Warm; accelerated chlorine decay; increased bacterial growth risk; summer conditions.
- **> 35°C**: Hot; rapid chlorine decay; high bacterial growth; taste/odour complaints; may exceed consumer preference.
- Water temperature increases with ambient temperature and longer distribution distances.
- Higher temperature requires higher initial chlorine dosing to maintain adequate residual at far-network points.

**Common SQL Usage**:
```sql
-- Seasonal temperature variation
SELECT season, city, AVG(water_temperature_c) AS avg_temp
FROM water_nodes
GROUP BY season, city
ORDER BY avg_temp DESC;

-- Temperature effect on chlorine
SELECT
  CASE WHEN water_temperature_c < 20 THEN 'Cool' WHEN water_temperature_c < 30 THEN 'Warm' ELSE 'Hot' END AS temp_band,
  AVG(residual_chlorine_mg_l) AS avg_chlorine
FROM water_nodes
GROUP BY temp_band;
```

---

### 6.7 `water_hardness_mg_l`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Milligrams per litre (mg/L) as CaCO₃ equivalent |
| **Range** | 20 – 556 |

**Description**: Total hardness of the water, expressed as calcium carbonate (CaCO₃) equivalent. Hardness is caused by dissolved calcium and magnesium ions from geological formations.

**Interpretation**:
- **< 60 mg/L**: Soft water; may be aggressive to pipe materials; low mineral content.
- **60 – 120 mg/L**: Moderately hard; optimal range.
- **120 – 200 mg/L**: Hard; within BIS desirable limit; may cause scale buildup.
- **200 – 600 mg/L**: Very hard; exceeds BIS desirable limit (200 mg/L) but within permissible limit (600 mg/L); significant scaling in pipes and appliances.
- **> 600 mg/L**: Excessively hard; beyond BIS permissible limit; requires softening.
- Hard water forms scale deposits (calcium carbonate) inside pipes, reducing effective diameter and increasing head loss over time.

**Common SQL Usage**:
```sql
-- Hardness classification
SELECT city,
  SUM(CASE WHEN water_hardness_mg_l <= 60 THEN 1 ELSE 0 END) AS soft,
  SUM(CASE WHEN water_hardness_mg_l > 60 AND water_hardness_mg_l <= 200 THEN 1 ELSE 0 END) AS moderate,
  SUM(CASE WHEN water_hardness_mg_l > 200 THEN 1 ELSE 0 END) AS hard
FROM water_nodes
GROUP BY city;
```

---

### 6.8 `iron_ppb`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Parts per billion (ppb); 1 ppb = 0.001 mg/L |
| **Range** | 5 – 416 |

**Description**: Iron concentration in the water. Iron typically enters the distribution system through corrosion of cast iron and ductile iron pipes, or from source water.

**Interpretation**:
- **< 100 ppb (0.1 mg/L)**: Low; no aesthetic issues.
- **100 – 300 ppb (0.1 – 0.3 mg/L)**: Moderate; within BIS desirable limit of 300 ppb (0.3 mg/L).
- **> 300 ppb (0.3 mg/L)**: Exceeds BIS desirable limit; water may have rusty colour, metallic taste, staining of laundry/fixtures.
- **> 416 ppb (max in dataset)**: Still within BIS permissible limit of 1,000 ppb (1.0 mg/L) but undesirable.
- Strong correlation with `pipe_material` (Cast_Iron > Ductile_Iron > others) and `pipe_age_years`.
- High iron often accompanies high turbidity (iron particles contribute to cloudiness).

**Common SQL Usage**:
```sql
-- Iron by pipe material
SELECT pipe_material, AVG(iron_ppb) AS avg_iron, MAX(iron_ppb) AS max_iron
FROM water_nodes
GROUP BY pipe_material
ORDER BY avg_iron DESC;

-- BIS violation check (> 300 ppb)
SELECT city, COUNT(*) AS iron_violations
FROM water_nodes
WHERE iron_ppb > 300
GROUP BY city;
```

---

### 6.9 `nitrate_mg_l`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Milligrams per litre (mg/L) as NO₃ |
| **Range** | 0.2 – 72.8 |

**Description**: Nitrate concentration in the water. Nitrate contamination typically originates from agricultural runoff, sewage infiltration, or industrial discharge into source water bodies.

**Interpretation**:
- **< 10 mg/L**: Low; safe for all populations.
- **10 – 45 mg/L**: Moderate; within BIS permissible limit of 45 mg/L.
- **> 45 mg/L**: Exceeds BIS limit; health risk — particularly methemoglobinemia ("blue baby syndrome") in infants.
- **> 60 mg/L**: Critically high; immediate remediation required.
- High nitrate often indicates contamination of source water — this is a source quality issue rather than a distribution issue.
- Nitrate does not decay in the distribution system (unlike chlorine) — what enters at the treatment plant exits at the consumer tap.

**Common SQL Usage**:
```sql
-- Nitrate violations (> 45 mg/L)
SELECT city, COUNT(*) AS violations, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM water_nodes) AS pct
FROM water_nodes
WHERE nitrate_mg_l > 45
GROUP BY city;

-- Nitrate trend over time
SELECT month_name, AVG(nitrate_mg_l) AS avg_nitrate FROM water_nodes GROUP BY month_num, month_name ORDER BY month_num;
```

---

### 6.10 `coliform_cfu_100ml`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Colony Forming Units per 100 millilitres (CFU/100ml) |
| **Range** | 0 – 200 |

**Description**: Total coliform bacteria count. Coliform bacteria are indicator organisms — their presence suggests that the water may be contaminated with fecal matter and potentially harmful pathogens.

**Interpretation**:
- **0 CFU/100ml**: Ideal; no coliform detected; water is microbiologically safe.
- **1 – 10 CFU/100ml**: Low; marginal detection; investigate source.
- **10 – 50 CFU/100ml**: Elevated; indicates disinfection failure or contamination intrusion.
- **50 – 100 CFU/100ml**: High; serious concern; potential health risk.
- **> 100 CFU/100ml**: Critical; unsafe for consumption; boil-water advisory may be warranted.
- **BIS Standard**: 0 CFU/100ml is the target; any presence is technically non-compliant.
- Strong inverse correlation with `residual_chlorine_mg_l` — adequate chlorine kills coliforms.
- Positive correlation with `water_age_hours` and `water_temperature_c` (old, warm water promotes regrowth).

**Common SQL Usage**:
```sql
-- Coliform detection rate by city
SELECT city,
       AVG(CASE WHEN coliform_cfu_100ml > 0 THEN 1.0 ELSE 0.0 END) * 100 AS detection_rate_pct,
       AVG(coliform_cfu_100ml) AS avg_coliform
FROM water_nodes
GROUP BY city;

-- Coliform vs chlorine relationship
SELECT
  CASE WHEN residual_chlorine_mg_l < 0.2 THEN 'Low Cl' WHEN residual_chlorine_mg_l < 0.5 THEN 'Medium Cl' ELSE 'High Cl' END AS chlorine_band,
  AVG(coliform_cfu_100ml) AS avg_coliform
FROM water_nodes
GROUP BY chlorine_band;
```

---

### 6.11 `water_age_hours`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Hours |
| **Range** | 0.5 – 80.9 |

**Description**: The estimated time that water has spent in the distribution system since leaving the treatment plant. Water age is a critical quality parameter — older water has lower chlorine residual, higher bacterial regrowth, and more opportunity for contaminant intrusion.

**Interpretation**:
- **< 8 hours**: Fresh; excellent quality maintenance; close to WTP.
- **8 – 24 hours**: Acceptable; standard for most distribution networks.
- **24 – 48 hours**: Elevated; chlorine likely significantly decayed; quality monitoring important.
- **> 48 hours**: Old water; high risk of quality issues; may need rechlorination.
- **> 72 hours**: Critical; stagnation concerns; discolouration and taste/odour likely.
- Reservoir-fed nodes tend to have higher water age due to storage time.
- Correlates positively with `distance_to_treatment_plant_km`.

**Common SQL Usage**:
```sql
-- Water age distribution
SELECT
  CASE WHEN water_age_hours < 8 THEN '<8h' WHEN water_age_hours < 24 THEN '8-24h'
       WHEN water_age_hours < 48 THEN '24-48h' ELSE '>48h' END AS age_band,
  COUNT(*) AS observations,
  AVG(residual_chlorine_mg_l) AS avg_chlorine,
  AVG(coliform_cfu_100ml) AS avg_coliform
FROM water_nodes
GROUP BY age_band;
```

---

## 7. Operational & Service Metrics

### 7.1 `supply_hours_per_day`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Hours per day |
| **Range** | 3 – 24 |

**Description**: The number of hours during which water was actively supplied to the node during the observation day. This is the most direct measure of service continuity.

**Interpretation**:
- **24 hours**: Continuous (24×7) supply; the gold standard per Smart Cities Mission.
- **18 – 23 hours**: Near-continuous; brief interruptions for maintenance or pressure regulation.
- **12 – 18 hours**: Intermittent; typical for many Indian cities; consumers need storage tanks.
- **6 – 12 hours**: Limited supply; significant hardship; consumers rely on tankers or alternative sources.
- **< 6 hours**: Critical; severe water scarcity or infrastructure failure.
- The national Service Level Benchmark target is 24 hours/day.
- Intermittent supply (< 24 hours) creates negative-pressure events that draw contaminants into pipes through leaks.

**Common SQL Usage**:
```sql
-- Supply hours by city
SELECT city, AVG(supply_hours_per_day) AS avg_supply, MIN(supply_hours_per_day) AS min_supply
FROM water_nodes
GROUP BY city
ORDER BY avg_supply;

-- 24x7 supply achievement
SELECT city,
       SUM(CASE WHEN supply_hours_per_day >= 23 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS pct_continuous
FROM water_nodes
GROUP BY city;
```

---

### 7.2 `leak_detection_events`

| Property | Value |
|---|---|
| **Data Type** | `INTEGER` |
| **Unit** | Count of events |
| **Range** | 0 – 7 |

**Description**: The number of leak detection events recorded at or near the node during the observation day. Events are detected through acoustic sensors, pressure transients, flow anomalies, or manual inspection.

**Interpretation**:
- **0**: No leaks detected; normal operations.
- **1 – 2**: Minor; routine level of leak activity; schedule repair.
- **3 – 4**: Elevated; multiple issues in the vicinity; prioritize repair crew.
- **5 – 7**: High; potential major infrastructure failure; emergency response may be needed.
- Leak events directly contribute to Non-Revenue Water (NRW).
- Correlates with `pipe_age_years`, `pipe_material` (older cast iron pipes leak more), and `non_revenue_water_pct`.

**Common SQL Usage**:
```sql
-- Leak hotspots
SELECT node_id, city, SUM(leak_detection_events) AS total_leaks
FROM water_nodes
GROUP BY node_id, city
ORDER BY total_leaks DESC
LIMIT 10;

-- Leaks by pipe age
SELECT
  CASE WHEN pipe_age_years < 15 THEN 'New' WHEN pipe_age_years < 30 THEN 'Mid' ELSE 'Old' END AS age_group,
  AVG(leak_detection_events) AS avg_leaks
FROM water_nodes
GROUP BY age_group;
```

---

### 7.3 `service_interruptions_count`

| Property | Value |
|---|---|
| **Data Type** | `INTEGER` |
| **Unit** | Count of interruptions |
| **Range** | 0 – 6 |

**Description**: The number of unplanned service interruptions experienced by the node during the observation day. An interruption is any unscheduled cessation of water supply (distinct from planned intermittent supply schedules).

**Interpretation**:
- **0**: No interruptions; reliable service. This is the target.
- **1**: Single interruption; acceptable if brief; investigate cause.
- **2 – 3**: Multiple interruptions; significant customer impact; reliability concern.
- **4 – 6**: Severe; major infrastructure problems; emergency investigation required.
- The **Service Reliability** KPI is calculated as the percentage of observations where `service_interruptions_count = 0`.
- Frequent interruptions at a node suggest chronic infrastructure issues (failing pump, deteriorating pipe).

**Common SQL Usage**:
```sql
-- Service reliability by city
SELECT city,
       SUM(CASE WHEN service_interruptions_count = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS reliability_pct
FROM water_nodes
GROUP BY city
ORDER BY reliability_pct;

-- Nodes with chronic interruptions
SELECT node_id, city, AVG(service_interruptions_count) AS avg_interruptions
FROM water_nodes
GROUP BY node_id, city
HAVING AVG(service_interruptions_count) > 2
ORDER BY avg_interruptions DESC;
```

---

### 7.4 `non_revenue_water_pct`

| Property | Value |
|---|---|
| **Data Type** | `FLOAT` |
| **Unit** | Percentage (%) |
| **Range** | 2 – 70.5 |

**Description**: The percentage of water entering the node's area that is "lost" — i.e., not billed to customers. Non-Revenue Water (NRW) includes physical losses (leaks, pipe bursts), commercial losses (theft, meter inaccuracy), and unbilled authorised consumption (firefighting, flushing).

**Interpretation**:
- **< 15%**: Excellent; meets Smart Cities Mission target; world-class performance.
- **15 – 25%**: Good; typical of well-managed systems in developed countries.
- **25 – 40%**: Average for Indian cities; significant improvement opportunity.
- **40 – 60%**: Poor; major financial and resource loss; urgent intervention needed.
- **> 60%**: Critical; more water is lost than delivered; system is unsustainable.
- NRW is arguably the single most important efficiency metric for a water utility.
- High NRW means the utility incurs treatment and pumping costs for water that never generates revenue.

**Common SQL Usage**:
```sql
-- NRW by city
SELECT city, AVG(non_revenue_water_pct) AS avg_nrw FROM water_nodes GROUP BY city ORDER BY avg_nrw DESC;

-- NRW vs pipe age
SELECT
  CASE WHEN pipe_age_years < 20 THEN 'New' ELSE 'Old' END AS age_group,
  AVG(non_revenue_water_pct) AS avg_nrw
FROM water_nodes
GROUP BY age_group;

-- High NRW nodes
SELECT node_id, city, AVG(non_revenue_water_pct) AS avg_nrw
FROM water_nodes
GROUP BY node_id, city
HAVING AVG(non_revenue_water_pct) > 50
ORDER BY avg_nrw DESC;
```

---

## 8. Compliance Flags

### 8.1 `pressure_compliance_flag`

| Property | Value |
|---|---|
| **Data Type** | `INTEGER` (binary) |
| **Unit** | Boolean (0 = Non-compliant, 1 = Compliant) |
| **Distribution** | ~99.2% compliant (flag = 1) |

**Description**: Binary flag indicating whether the node's pressure readings meet the minimum pressure standard for the observation day. A value of 1 means the minimum pressure stayed above the required threshold (typically 0.7 bar / 7 metres of head per CPHEEO guidelines).

**Interpretation**:
- **1 (Compliant)**: Minimum pressure stayed above threshold throughout the day; adequate service delivery.
- **0 (Non-compliant)**: Pressure dropped below minimum threshold at some point; consumers at this node likely experienced inadequate supply (e.g., no water on upper floors).
- The 99.2% compliance rate means only ~0.8% of observations show pressure failures — pressure compliance is generally well-managed across the network.
- Non-compliance events are rare but significant — they indicate acute infrastructure or demand issues.

**Common SQL Usage**:
```sql
-- Pressure compliance rate by city
SELECT city, AVG(pressure_compliance_flag) * 100 AS compliance_pct
FROM water_nodes
GROUP BY city
ORDER BY compliance_pct;

-- Pressure non-compliance details
SELECT node_id, city, observation_date, min_pressure_bar
FROM water_nodes
WHERE pressure_compliance_flag = 0
ORDER BY min_pressure_bar;
```

---

### 8.2 `chlorine_compliance_flag`

| Property | Value |
|---|---|
| **Data Type** | `INTEGER` (binary) |
| **Unit** | Boolean (0 = Non-compliant, 1 = Compliant) |
| **Distribution** | ~61.8% compliant (flag = 1) |

**Description**: Binary flag indicating whether the node's residual chlorine level meets the minimum disinfection standard (typically ≥ 0.2 mg/L per WHO/BIS guidelines) for the observation day.

**Interpretation**:
- **1 (Compliant)**: Residual chlorine is at or above 0.2 mg/L; adequate disinfection barrier.
- **0 (Non-compliant)**: Chlorine has decayed below 0.2 mg/L; inadequate disinfection; risk of microbial regrowth.
- The 61.8% compliance rate is a **major concern** — nearly 40% of observations have inadequate chlorine. This is the single most critical water quality gap in the dataset.
- Non-compliance is concentrated at nodes that are:
  - Far from treatment plants (high `distance_to_treatment_plant_km`)
  - Old water (high `water_age_hours`)
  - High temperature (high `water_temperature_c`)
  - Reservoir-fed (long storage time)

**Common SQL Usage**:
```sql
-- Chlorine compliance by city
SELECT city, AVG(chlorine_compliance_flag) * 100 AS compliance_pct
FROM water_nodes
GROUP BY city
ORDER BY compliance_pct;

-- Factors driving non-compliance
SELECT
  chlorine_compliance_flag,
  AVG(distance_to_treatment_plant_km) AS avg_distance,
  AVG(water_age_hours) AS avg_water_age,
  AVG(water_temperature_c) AS avg_temp
FROM water_nodes
GROUP BY chlorine_compliance_flag;

-- Trend over months
SELECT month_name, AVG(chlorine_compliance_flag) * 100 AS compliance_pct
FROM water_nodes
GROUP BY month_num, month_name
ORDER BY month_num;
```

---

## Quick Reference: Column Summary Table

| # | Column | Type | Unit | Range / Values |
|---|---|---|---|---|
| 1 | record_id | TEXT | — | REC-0000001 to REC-0163904 |
| 2 | node_id | TEXT | — | WN-00001 to WN-00832 |
| 3 | utility_name | TEXT | — | 10 utilities |
| 4 | city | TEXT | — | 10 cities |
| 5 | state | TEXT | — | 9 states |
| 6 | zone_id | TEXT | — | Zone_A to Zone_E |
| 7 | node_type | TEXT | — | 4 types |
| 8 | pipe_material | TEXT | — | 5 materials |
| 9 | pipe_age_years | INT | years | 3 – 55 |
| 10 | pipe_diameter_mm | INT | mm | 75 – 500 |
| 11 | elevation_m | FLOAT | m | 5.1 – 149.4 |
| 12 | distance_to_treatment_plant_km | FLOAT | km | 1.0 – 40.0 |
| 13 | pump_station_nearby | INT | 0/1 | 47% = 1 |
| 14 | reservoir_fed | INT | 0/1 | 33% = 1 |
| 15 | num_customer_connections | INT | count | 50 – 598 |
| 16 | demand_category | TEXT | — | 5 categories |
| 17 | pipe_length_upstream_m | INT | m | 52 – 1,996 |
| 18 | observation_date | TEXT | YYYY-MM-DD | 2024-01-01 to 2024-07-15 |
| 19 | day_of_week | TEXT | — | Mon – Sun |
| 20 | is_weekend | INT | 0/1 | 0=Weekday, 1=Weekend |
| 21 | month_num | INT | — | 1 – 7 |
| 22 | month_name | TEXT | — | Jan – Jul |
| 23 | season | TEXT | — | Winter, Summer, Pre_Monsoon |
| 24 | inlet_pressure_bar | FLOAT | bar | 0.5 – 6.96 |
| 25 | outlet_pressure_bar | FLOAT | bar | 0.2 – 6.67 |
| 26 | pressure_differential_bar | FLOAT | bar | 0.05 – 1.42 |
| 27 | min_pressure_bar | FLOAT | bar | 0.1 – 6.59 |
| 28 | max_pressure_bar | FLOAT | bar | 0.56 – 7.0 |
| 29 | pressure_hourly_variance | FLOAT | bar² | 0.0 – 0.76 |
| 30 | avg_flow_lps | FLOAT | LPS | 0.5 – 114.3 |
| 31 | peak_flow_lps | FLOAT | LPS | 0.8 – 180.0 |
| 32 | daily_volume_m3 | FLOAT | m³ | 5.4 – 8,356 |
| 33 | flow_velocity_m_s | FLOAT | m/s | 0.01 – 5.0 |
| 34 | hydraulic_head_loss_m_per_km | FLOAT | m/km | 0.3 – 26.3 |
| 35 | ph_value | FLOAT | pH | 6.0 – 8.34 |
| 36 | turbidity_ntu | FLOAT | NTU | 0.05 – 29.2 |
| 37 | residual_chlorine_mg_l | FLOAT | mg/L | 0.01 – 1.11 |
| 38 | total_dissolved_solids_mg_l | FLOAT | mg/L | 30 – 975 |
| 39 | conductivity_us_cm | FLOAT | µS/cm | 60 – 1,435 |
| 40 | water_temperature_c | FLOAT | °C | 10.0 – 41.3 |
| 41 | water_hardness_mg_l | FLOAT | mg/L CaCO₃ | 20 – 556 |
| 42 | iron_ppb | FLOAT | ppb | 5 – 416 |
| 43 | nitrate_mg_l | FLOAT | mg/L | 0.2 – 72.8 |
| 44 | coliform_cfu_100ml | FLOAT | CFU/100ml | 0 – 200 |
| 45 | water_age_hours | FLOAT | hours | 0.5 – 80.9 |
| 46 | supply_hours_per_day | FLOAT | hours | 3 – 24 |
| 47 | leak_detection_events | INT | count | 0 – 7 |
| 48 | service_interruptions_count | INT | count | 0 – 6 |
| 49 | non_revenue_water_pct | FLOAT | % | 2 – 70.5 |
| 50 | pressure_compliance_flag | INT | 0/1 | 99.2% = 1 |
| 51 | chlorine_compliance_flag | INT | 0/1 | 61.8% = 1 |

---

## Common Query Patterns

### Filtering by Geography
```sql
-- Always combine city + zone for zone-level analysis
WHERE city = 'Mumbai' AND zone_id = 'Zone_A'

-- State-level (remember Maharashtra has 2 cities)
WHERE state = 'Maharashtra'
```

### Aggregation Levels
```sql
-- System-wide (all nodes, all dates)
SELECT AVG(metric) FROM water_nodes;

-- City-level
SELECT city, AVG(metric) FROM water_nodes GROUP BY city;

-- Node-level (aggregate across dates for a single node)
SELECT node_id, AVG(metric) FROM water_nodes GROUP BY node_id;

-- Time-series (aggregate across nodes for each date)
SELECT observation_date, AVG(metric) FROM water_nodes GROUP BY observation_date;
```

### Compliance Queries
```sql
-- Overall compliance rates
SELECT
  AVG(pressure_compliance_flag) * 100 AS pressure_compliance_pct,
  AVG(chlorine_compliance_flag) * 100 AS chlorine_compliance_pct
FROM water_nodes;

-- Compliance by group
SELECT city,
       AVG(pressure_compliance_flag) * 100 AS pressure_pct,
       AVG(chlorine_compliance_flag) * 100 AS chlorine_pct
FROM water_nodes
GROUP BY city;
```

### Multi-metric Analysis
```sql
-- Comprehensive node health report
SELECT node_id, city, zone_id, pipe_material, pipe_age_years,
       AVG(inlet_pressure_bar) AS avg_pressure,
       AVG(residual_chlorine_mg_l) AS avg_chlorine,
       AVG(non_revenue_water_pct) AS avg_nrw,
       AVG(supply_hours_per_day) AS avg_supply,
       SUM(leak_detection_events) AS total_leaks,
       AVG(pressure_compliance_flag) * 100 AS pressure_compliance,
       AVG(chlorine_compliance_flag) * 100 AS chlorine_compliance
FROM water_nodes
GROUP BY node_id, city, zone_id, pipe_material, pipe_age_years;
```

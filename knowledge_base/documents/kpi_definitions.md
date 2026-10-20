# Water Utility Key Performance Indicators (KPI) Framework

## Overview
This document defines operational, hydraulic, water quality, and asset reliability Key Performance Indicators (KPIs) monitored across the municipal water distribution networks of UtilPulse Command Centre. These definitions govern computational logic, SQL aggregation standards, and operational decision-making across Indian municipal utilities.

---

## 1. Pressure Compliance Rate
- **Metric Name**: Pressure Compliance Percentage (`pressure_compliance_pct`)
- **Formula**:
  $$\text{Pressure Compliance (\%)} = \left(\frac{\sum \text{pressure\_compliance\_flag}}{\text{Total Observations}}\right) \times 100$$
- **Dataset Column**: `pressure_compliance_flag` (1 = Compliant, 0 = Non-compliant)
- **Standard Benchmark**:
  - Acceptable minimum: ≥ 95.0%
  - Target: ≥ 99.0%
  - Critical threshold: < 90.0%
- **SQL Implementation**:
  ```sql
  SELECT
      city,
      zone_id,
      ROUND(AVG(pressure_compliance_flag) * 100, 2) AS pressure_compliance_pct,
      ROUND(AVG(inlet_pressure_bar), 2) AS avg_inlet_pressure_bar,
      ROUND(AVG(outlet_pressure_bar), 2) AS avg_outlet_pressure_bar
  FROM water_nodes
  GROUP BY city, zone_id
  ORDER BY pressure_compliance_pct ASC;
  ```
- **Operational Interpretation**:
  Adequate pressure (typically 1.5 to 4.5 bar at terminal delivery points) prevents back-siphonage contamination, satisfies multistory building demand, and prevents consumer complaints. Sustained overpressure (> 5.5 bar) induces pipe bursting and accelerates joint leakage.

---

## 2. Chlorine Compliance Rate
- **Metric Name**: Disinfection Residual Chlorine Compliance (`chlorine_compliance_pct`)
- **Formula**:
  $$\text{Chlorine Compliance (\%)} = \left(\frac{\sum \text{chlorine\_compliance\_flag}}{\text{Total Observations}}\right) \times 100$$
- **Dataset Column**: `chlorine_compliance_flag` (1 = Compliant: 0.2 to 1.0 mg/L, 0 = Non-compliant)
- **Standard Benchmark (CPHEEO / IS 10500)**:
  - Minimum consumer-end residual: 0.2 mg/L
  - Optimal range: 0.2 to 0.5 mg/L
  - Disinfection breakpoint target: ≥ 90.0% compliance
  - Urgent intervention: < 70.0% compliance
- **SQL Implementation**:
  ```sql
  SELECT
      city,
      zone_id,
      ROUND(AVG(chlorine_compliance_flag) * 100, 2) AS chlorine_compliance_pct,
      ROUND(AVG(residual_chlorine_mg_l), 3) AS avg_residual_chlorine_mg_l,
      ROUND(AVG(coliform_cfu_100ml), 2) AS avg_coliform_cfu
  FROM water_nodes
  GROUP BY city, zone_id
  ORDER BY chlorine_compliance_pct ASC;
  ```
- **Operational Interpretation**:
  Residual free chlorine guards against secondary microbial contamination within distribution networks. Non-compliance indicates chlorine decay due to excessive water age, organic matter reaction, pipe biofilm, or inadequate dosing at treatment plants.

---

## 3. Non-Revenue Water (NRW)
- **Metric Name**: Non-Revenue Water Percentage (`avg_nrw_pct`)
- **Formula**:
  $$\text{NRW (\%)} = \left(\frac{\text{System Input Volume} - \text{Billed Authorized Consumption}}{\text{System Input Volume}}\right) \times 100$$
- **Dataset Column**: `non_revenue_water_pct`
- **Standard Benchmark (Ministry of Housing and Urban Affairs - MoHUA / CPHEEO)**:
  - Benchmark target: ≤ 15.0%
  - Acceptable upper limit: ≤ 20.0%
  - High loss alarm: > 30.0%
  - Severe physical loss: > 45.0%
- **SQL Implementation**:
  ```sql
  SELECT
      city,
      pipe_material,
      ROUND(AVG(non_revenue_water_pct), 2) AS avg_nrw_pct,
      ROUND(SUM(leak_detection_events), 0) AS total_leaks,
      ROUND(AVG(daily_volume_m3), 2) AS avg_daily_volume_m3
  FROM water_nodes
  GROUP BY city, pipe_material
  ORDER BY avg_nrw_pct DESC;
  ```
- **Operational Interpretation**:
  Represents financial and volumetric water loss through underground distribution pipe bursts, joint weeping, unmetered public taps, illegal tapping, and meter inaccuracies.

---

## 4. Supply Continuity
- **Metric Name**: Daily Supply Hours (`avg_supply_hours`)
- **Formula**:
  $$\text{Supply Hours} = \text{Average of daily supply duration in hours}$$
- **Dataset Column**: `supply_hours_per_day` (Range: 3.0 to 24.0 hours)
- **Standard Benchmark (National Urban Water Policy)**:
  - National Mission Goal: 24.0 hours (Continuous 24x7 pressurized supply)
  - Intermittent threshold: < 12.0 hours
  - Severe distress: < 6.0 hours
- **SQL Implementation**:
  ```sql
  SELECT
      city,
      demand_category,
      ROUND(AVG(supply_hours_per_day), 2) AS avg_supply_hours,
      ROUND(MIN(supply_hours_per_day), 2) AS min_supply_hours,
      ROUND(MAX(supply_hours_per_day), 2) AS max_supply_hours
  FROM water_nodes
  GROUP BY city, demand_category
  ORDER BY avg_supply_hours ASC;
  ```
- **Operational Interpretation**:
  Intermittent supply induces negative hydraulic pressures during shutdown, causing contaminated groundwater ingestion into distribution pipes through cracks and faulty joints. Transition to 24x7 supply is the primary safeguard against waterborne epidemics.

---

## 5. Leak Detection Event Frequency
- **Metric Name**: Leak Events Per Node / Zone (`leak_frequency`)
- **Formula**:
  $$\text{Leak Frequency} = \frac{\sum \text{leak\_detection\_events}}{\text{Number of Unique Monitored Nodes}}$$
- **Dataset Column**: `leak_detection_events` (daily count: 0 to 7)
- **Standard Benchmark**:
  - Acceptable: < 0.15 leaks per node per month
  - Elevated risk: 0.15 to 0.40 leaks per node per month
  - Critical asset deterioration: > 0.40 leaks per node per month
- **SQL Implementation**:
  ```sql
  SELECT
      node_id,
      city,
      zone_id,
      pipe_material,
      pipe_age_years,
      SUM(leak_detection_events) AS total_leaks,
      ROUND(AVG(non_revenue_water_pct), 2) AS avg_nrw_pct
  FROM water_nodes
  GROUP BY node_id, city, zone_id, pipe_material, pipe_age_years
  ORDER BY total_leaks DESC
  LIMIT 20;
  ```

---

## 6. Service Reliability & Interruption Rate
- **Metric Name**: Service Interruption Count (`service_interruptions_count`)
- **Formula**:
  $$\text{Reliability Index (\%)} = \left(1 - \frac{\text{Days with Interruptions}}{\text{Total Monitored Days}}\right) \times 100$$
- **Dataset Column**: `service_interruptions_count` (daily count: 0 to 6)
- **Standard Benchmark**:
  - Target: Zero unplanned interruptions
  - Acceptable: < 2 interruptions per connection per quarter
- **SQL Implementation**:
  ```sql
  SELECT
      city,
      zone_id,
      SUM(service_interruptions_count) AS total_interruptions,
      ROUND(AVG(service_interruptions_count), 3) AS avg_daily_interruptions,
      ROUND(AVG(supply_hours_per_day), 2) AS avg_supply_hours
  FROM water_nodes
  GROUP BY city, zone_id
  ORDER BY total_interruptions DESC;
  ```

---

## 7. Composite Water Quality Index (WQI)
- **Metric Name**: Potability & Quality Aggregate
- **Key Parameters Tracked**:
  - pH: 6.5 – 8.5
  - Turbidity: ≤ 1.0 NTU (Desirable), ≤ 5.0 NTU (Permissible)
  - Residual Chlorine: 0.2 – 1.0 mg/L
  - Total Dissolved Solids: ≤ 500 mg/L
  - Coliform Bacteria: 0 CFU/100 mL
  - Iron: ≤ 300 ppb
  - Nitrate: ≤ 45 mg/L
- **SQL Implementation**:
  ```sql
  SELECT
      city,
      zone_id,
      ROUND(AVG(ph_value), 2) AS avg_ph,
      ROUND(AVG(turbidity_ntu), 2) AS avg_turbidity,
      ROUND(AVG(residual_chlorine_mg_l), 3) AS avg_chlorine,
      ROUND(AVG(total_dissolved_solids_mg_l), 1) AS avg_tds,
      ROUND(AVG(coliform_cfu_100ml), 2) AS avg_coliform
  FROM water_nodes
  GROUP BY city, zone_id
  ORDER BY avg_coliform DESC;
  ```

---

## 8. Pipe Asset Risk & Failure Susceptibility Score
- **Concept**: Identifies pipes vulnerable to rupture based on structural age, material vulnerability (Cast Iron and Asbestos Cement vs. HDPE/Ductile Iron), head loss, and hydraulic pressure variance.
- **SQL Implementation**:
  ```sql
  SELECT
      pipe_material,
      CASE
          WHEN pipe_age_years > 35 THEN 'Critical (>35 yrs)'
          WHEN pipe_age_years > 20 THEN 'Aging (20-35 yrs)'
          ELSE 'Sound (<20 yrs)'
      END AS age_bracket,
      COUNT(DISTINCT node_id) AS node_count,
      ROUND(AVG(non_revenue_water_pct), 2) AS avg_nrw_pct,
      SUM(leak_detection_events) AS total_leaks,
      ROUND(AVG(hydraulic_head_loss_m_per_km), 2) AS avg_head_loss
  FROM water_nodes
  GROUP BY pipe_material, age_bracket
  ORDER BY total_leaks DESC;
  ```

---

## 9. Per Connection Consumption Demand
- **Metric Name**: Specific Consumption (`m3_per_connection_daily`)
- **Formula**:
  $$\text{Consumption per Connection} = \frac{\text{daily\_volume\_m3}}{\text{num\_customer\_connections}}$$
- **SQL Implementation**:
  ```sql
  SELECT
      demand_category,
      city,
      ROUND(AVG(daily_volume_m3 / num_customer_connections), 3) AS m3_per_connection_day,
      ROUND(AVG(avg_flow_lps), 2) AS avg_flow_lps,
      ROUND(AVG(peak_flow_lps), 2) AS peak_flow_lps
  FROM water_nodes
  GROUP BY demand_category, city
  ORDER BY m3_per_connection_day DESC;
  ```

---

## 10. Hydraulic Transport Efficiency
- **Metric Name**: Head Loss & Friction Gradient (`hydraulic_head_loss_m_per_km`)
- **Benchmark**:
  - Efficient transmission: < 5.0 m/km
  - Moderate resistance: 5.0 to 10.0 m/km
  - Severe encrustation or throttling: > 12.0 m/km
- **SQL Implementation**:
  ```sql
  SELECT
      pipe_material,
      pipe_diameter_mm,
      ROUND(AVG(hydraulic_head_loss_m_per_km), 2) AS avg_head_loss_m_km,
      ROUND(AVG(flow_velocity_m_s), 2) AS avg_velocity_m_s,
      ROUND(AVG(pressure_differential_bar), 2) AS avg_pressure_diff_bar
  FROM water_nodes
  GROUP BY pipe_material, pipe_diameter_mm
  ORDER BY avg_head_loss_m_km DESC;
  ```

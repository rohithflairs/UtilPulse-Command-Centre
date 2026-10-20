# Indian Water Sector Regulatory Frameworks & Compliance Mandates

## 1. National Urban Water Supply & Sanitation Policy
The Government of India, through the **Ministry of Housing and Urban Affairs (MoHUA)**, has instituted the **National Service Level Benchmarks (SLBs)** to standardize, evaluate, and upgrade municipal water delivery systems across Urban Local Bodies (ULBs).

### Service Level Benchmarks (SLB) Target Matrix

| Indicator | MoHUA National Benchmark | Indian City Realities (Baseline) | UtilPulse Command Role |
|---|---|---|---|
| **Coverage of Water Supply Connections** | 100.0% | 60% – 85% | Track connection density per distribution node. |
| **Per Capita Supply Quantum** | 135 Liters Per Capita Daily (LPCD) | 70 – 160 LPCD | Monitor flow volume (`daily_volume_m3`) and demand categories. |
| **Extent of Metering** | 100.0% | 15% – 60% | Track metered nodes and consumption anomalies. |
| **Extent of Non-Revenue Water (NRW)** | **≤ 15.0%** | **30% – 55%** | Primary metric for distribution efficiency and loss reduction. |
| **Continuity of Water Supply** | **24.0 Hours (24x7)** | **1.5 – 6.0 Hours** | Intermittent delivery transition tracking (`supply_hours_per_day`). |
| **Quality of Water Supplied** | **100.0% Compliance with IS 10500** | 70% – 90% | Physical/chemical/bacteriological compliance auditing. |
| **Cost Recovery in Water Supply Services** | 100.0% | 30% – 70% | Direct financial link to NRW reduction. |
| **Efficiency in Redressal of Customer Complaints** | 80.0% within 24 hours | 50% – 75% | Service interruption root-cause analysis. |

---

## 2. CPHEEO Manual on Water Supply and Treatment
The **Central Public Health and Environmental Engineering Organisation (CPHEEO)** technical manual is the statutory engineering benchmark for design and operation of municipal systems:

### Key Operational Standards
1. **Terminal Residual Pressures**:
   - Single-story dwellings: 7.0 meters head (~0.7 bar)
   - Two-story dwellings: 12.0 meters head (~1.2 bar)
   - Three-story dwellings: 17.0 meters head (~1.7 bar)
   - Recommended distribution main pressure: **1.5 to 3.0 bar**
2. **Maximum Permissible Pipeline Velocity**:
   - Optimal economic velocity: **0.9 to 1.8 m/s**
   - High velocity (> 2.5 m/s) induces severe friction loss, water hammer, and cavitation.
   - Low velocity (< 0.6 m/s) allows particle settling, bio-sedimentation, and excessive water age.
3. **Disinfection Contact Time**:
   - Minimum contact time of 30 minutes at peak flow prior to release into distribution network.

---

## 3. Atal Mission for Rejuvenation and Urban Transformation (AMRUT 2.0)
Under AMRUT 2.0, the central government has allocated substantial budgetary outlays tied directly to performance against:
1. **Universal 100% functional tap connection** in all statutory towns.
2. **City Water Balance Plans (CWBP)**: Requires explicit accounting of input, billed, unbilled, and lost water.
3. **Piped 24x7 Water Supply in 500 Cities**: Mandatory conversion from intermittent to pressurized continuous supply to eliminate negative pressure contamination.

---

## 4. Smart Cities Mission & SCADA Integration
Under the Smart Cities Mission, Indian municipal corporations (including MCGM, DJB, BWSSB, HMWSSB, CMWSSB) have deployed SCADA and IoT sensor arrays at:
- Raw water intake pump stations
- Water treatment plant discharge manifolds
- Master balancing reservoirs (MBRs) and elevated service reservoirs (ESRs)
- District Metered Area (DMA) inlet boundaries
- Critical distribution junctions and terminal dead-ends

UtilPulse Command Centre acts as the cognitive layer atop these SCADA and IoT streams, democratizing analytics for field operators and executive directors without requiring low-level SQL or telemetry engineering expertise.


import streamlit as st
import math

st.title("Air-Cooled Condenser Design: Tube Length and Row Estimator")

st.header("1. Coil and Fin Geometry Inputs")
D_od = st.number_input("Tube Outer Diameter (mm)", value=9.52) / 1000  # m
FPI = st.number_input("Fin Pitch (Fins Per Inch)", value=14)
fin_thk_mm = st.number_input("Fin Thickness (mm)", value=0.12)
fin_OD_mm = st.number_input("Fin Outer Diameter (mm)", value=25.4)
fin_ID_mm = st.number_input("Fin Inner Diameter (mm)", value=9.52)
fin_eff = st.number_input("Fin Efficiency (0–1)", value=0.9)

coil_length = st.number_input("Tube Length (Horizontal Coil Length, m)", value=1.2)
coil_width = st.number_input("Coil Width (Across Airflow, m)", value=1.0)

tubes_per_row = int(coil_width / 0.0254)  # 1 inch tube pitch assumed
st.write(f"Tubes per Row: {tubes_per_row}")

st.header("2. Thermal and Operating Inputs")
T_in = st.number_input("Refrigerant Inlet Temperature (°C)", value=86.0)
T_sat = st.number_input("Condensing Temperature (°C)", value=65.0)
T_out = st.number_input("Refrigerant Outlet Temp (°C)", value=58.0)
T_air = st.number_input("Air Inlet Temp (°C)", value=50.0)

m_dot = st.number_input("Mass Flow Rate of Refrigerant (kg/s)", value=0.48)
cp_liquid = st.number_input("Specific Heat of Liquid (kJ/kg·K)", value=1.45)
h_fg = st.number_input("Latent Heat of Condensation (kJ/kg)", value=100.1)
U = st.number_input("Overall Heat Transfer Coefficient (W/m²·K)", value=45)

def compute_airside_area_per_m(D_od, FPI, fin_thk_mm, fin_OD_mm, fin_ID_mm, fin_eff=0.9):
    fins_per_m = FPI * 39.37
    tube_circ = math.pi * D_od
    A_bare = tube_circ * 1.0
    A_fin = math.pi * ((fin_OD_mm/1000)**2 - (fin_ID_mm/1000)**2) / 4
    A_fins = A_fin * fins_per_m * fin_eff
    return A_bare + A_fins, A_bare, A_fins

def calculate_required_length(Q_kW, U, A_per_m, delta_T_lm):
    A_required = (Q_kW * 1000) / (U * delta_T_lm)
    L_total = A_required / A_per_m
    return A_required, L_total

def log_mean_temp_diff(T_hot_in, T_hot_out, T_air):
    dT1 = T_hot_in - T_air
    dT2 = T_hot_out - T_air
    if dT1 == dT2:
        return dT1
    return (dT1 - dT2) / math.log(dT1 / dT2)

# Heat loads
Q_desuper = m_dot * 1.05 * (T_in - T_sat)
Q_cond = m_dot * h_fg
Q_sub = m_dot * cp_liquid * (T_sat - T_out)

DT_desuper = log_mean_temp_diff(T_in, T_sat, T_air)
DT_cond = log_mean_temp_diff(T_sat, T_sat, T_air)
DT_sub = log_mean_temp_diff(T_sat, T_out, T_air)

A_per_m, A_bare, A_fins = compute_airside_area_per_m(D_od, FPI, fin_thk_mm, fin_OD_mm, fin_ID_mm, fin_eff)

A1, L1 = calculate_required_length(Q_desuper, U, A_per_m, DT_desuper)
A2, L2 = calculate_required_length(Q_cond, U, A_per_m, DT_cond)
A3, L3 = calculate_required_length(Q_sub, U, A_per_m, DT_sub)

L_total = L1 + L2 + L3
total_tubes_per_row = tubes_per_row
L_per_row = total_tubes_per_row * coil_length
rows_required = L_total / L_per_row

st.header("3. Results")

st.write(f"🔹 Finned Surface Area per Meter: {A_per_m:.4f} m²")
st.write(f"🔸 Desuperheating Zone: {Q_desuper:.2f} kW | ΔT: {DT_desuper:.2f} K | Length: {L1:.2f} m")
st.write(f"🔸 Condensation Zone: {Q_cond:.2f} kW | ΔT: {DT_cond:.2f} K | Length: {L2:.2f} m")
st.write(f"🔸 Subcooling Zone: {Q_sub:.2f} kW | ΔT: {DT_sub:.2f} K | Length: {L3:.2f} m")

st.success(f"✅ Total Tube Length Required: {L_total:.2f} m")
st.success(f"📏 Estimated Number of Rows Required: {rows_required:.2f}")

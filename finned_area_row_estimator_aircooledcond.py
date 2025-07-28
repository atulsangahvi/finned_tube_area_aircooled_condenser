
import math

def compute_airside_area_per_m(D_od, FPI, fin_thk_mm, fin_OD_mm, fin_ID_mm, fin_eff=0.9):
    fins_per_m = FPI * 39.37  # convert FPI to fins/m
    tube_circ = math.pi * D_od
    A_bare = tube_circ * 1.0  # per meter

    A_fin = math.pi * ( (fin_OD_mm/1000)**2 - (fin_ID_mm/1000)**2 ) / 4  # one fin area
    A_fins = A_fin * fins_per_m * fin_eff

    A_total = A_bare + A_fins
    return A_total, A_bare, A_fins

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

# Inputs
D_od = 0.00952  # 3/8 inch OD in meters
FPI = 14  # fins per inch
fin_thk_mm = 0.12
fin_OD_mm = 25.4  # 1 inch
fin_ID_mm = 9.52  # match tube OD

# Geometry
coil_length = 1.2  # m horizontal tube length
coil_width = 1.0   # m coil width
tubes_per_row = int(coil_width / 0.0254)  # 1 inch tube pitch

# Heat loads
m_dot = 0.48
cp_liquid = 1.45
h_fg = 100.1
T_in = 86
T_sat = 65
T_out = 58
T_air = 50
U = 45  # W/m2.K

Q_desuper = m_dot * 1.05 * (T_in - T_sat)
Q_cond = m_dot * h_fg
Q_sub = m_dot * cp_liquid * (T_sat - T_out)

DT_desuper = log_mean_temp_diff(T_in, T_sat, T_air)
DT_cond = log_mean_temp_diff(T_sat, T_sat, T_air)
DT_sub = log_mean_temp_diff(T_sat, T_out, T_air)

A_per_m, A_bare, A_fins = compute_airside_area_per_m(D_od, FPI, fin_thk_mm, fin_OD_mm, fin_ID_mm)

A1, L1 = calculate_required_length(Q_desuper, U, A_per_m, DT_desuper)
A2, L2 = calculate_required_length(Q_cond, U, A_per_m, DT_cond)
A3, L3 = calculate_required_length(Q_sub, U, A_per_m, DT_sub)

L_total = L1 + L2 + L3
total_tubes = tubes_per_row * coil_length
rows_required = L_total / (tubes_per_row * coil_length)

print(f"Finned Area per meter: {A_per_m:.4f} m²")
print(f"Zone Lengths: Desuper={L1:.2f} m, Cond={L2:.2f} m, Sub={L3:.2f} m")
print(f"Total Tube Length Required: {L_total:.2f} m")
print(f"Estimated Number of Rows Required: {rows_required:.2f}")

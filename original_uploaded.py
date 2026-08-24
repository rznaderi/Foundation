import numpy as np
import matplotlib.pyplot as plt

# Input the main parameters
ToF = int(input('input Type of Foundation 1 for single and 2 for strip 3 for mat ?   '))
if ToF == 1:
    LoB = 1.0
else:
    LoB = float(input('input L/B =  ?   '))

if ToF <= 2:
    delta = 0.03
else:
    delta = 0.04

D = float(input('input Footing Depth (m) =  ?   '))
Cu = float(input('input Soil Cohesion (kPa) =  ?   '))
phi = float(input('input Internal Friction Angle =  ?   '))
Gama = float(input('input Soil Unit Weight (kN/m3) =  ?   '))
fix = int(input('input Soil Modulus of Elasticity   1  for average value  2 for values  =  '))

if fix == 1:
    Es = float(input('input Soil Modulus of Elasticity (kPa) =  ?   '))
else:
    nol = int(input('No of layers =  ?   '))
    len = []
    Ess = []
    for i in range(nol):
        len.append(float(input('input Layer Length (m) =  ?   ')))
        Ess.append(float(input('input Soil Modulus of Elasticity for layer (kPa) =  ?   ')))
    Es = sum(np.array(len) * np.array(Ess)) / sum(len)

mu = 0.3  # Soil Poisson's Ratio (---)
ss = 0.025 * Es
FOS = 3.0  # Factor of safety
qd = Gama * D  # overburden pressure
phi = np.radians(phi)
Nq = np.exp(np.pi * np.tan(phi)) * (np.tan(np.pi / 4 + phi / 2)) ** 2
Nc = (Nq - 1) * (1 / np.tan(phi))
Nr = 2 * (Nq + 1) * np.tan(phi)

if ToF < 2.5:
    nn = 37
    dd = 5
else:
    nn = 370
    dd = 40

B_values = []
qal_values = []
ksv_values = []

for j in range(1, nn + 1):
    B = 0.3 + j / 10
    L = B * LoB
    if D / B <= 1.0:
        dq = 1.0 + 2 * np.tan(phi) * (1 - np.sin(phi)) ** 2 * (D / B)
        dc = dq - (1 - dq) / (Nc * np.tan(phi))
        dr = 1.0
    else:
        dq = 1.0 + 2 * np.tan(phi) * (1 - np.sin(phi)) ** 2 * np.arctan(D / B)
        dc = dq - (1 - dq) / (Nc * np.tan(phi))
        dr = 1.0

    Sc = 1.0 + (Nq / Nc) * (B / L)
    Sq = 1.0 + (B / L) * np.tan(phi)
    Sr = 1.0 - 0.4 * (B / L)
    if phi == 0.0:
        Sc = 0.2 * (B / L)
    if Sr < 0.6:
        Sr = 0.6

    qu = Cu * Nc * dc * Sc + qd * Nq * dq * Sq + 0.5 * Gama * B * Nr * dr * Sr
    qa = qu / FOS
    M = L / B
    N = 10
    m = 4  # Number of contributing corners
    a0 = M * np.log((1 + np.sqrt(M ** 2 + 1)) * (np.sqrt(M ** 2 + N ** 2)) / (M * (1 + np.sqrt(M ** 2 + N ** 2 + 1))))
    a1 = np.log(((M + np.sqrt(M ** 2 + 1)) * (np.sqrt(1 + N ** 2)) / (M + (np.sqrt(M ** 2 + N ** 2 + 1)))))
    a2 = M / (N * np.sqrt(M ** 2 + N ** 2 + 1))
    I1 = (a0 + a1) / np.pi
    I2 = N * np.arctan(a2) / (2 * np.pi)
    Is = (I1 + (1 - 2 * mu) / (1 - mu) * I2)
    IF = (1.001 + 1.194 * (D / B) + 0.842 * (L / B) + 7.63 * mu) / (1 + 3.738 * (D / B) + 0.839 * (L / B) + 7.3 * mu)
    q0 = delta / (m * B / 2 * (1 - mu ** 2) * Is * IF / Es)
    qal = min(qa, q0)

    B_values.append(B)
    qal_values.append(qal)
    ksv = Es / (B * (1 - mu) ** 2)
    ksv_values.append(ksv)

# Plotting Allowable Bearing Capacity
plt.figure(1)
plt.plot(B_values, qal_values, 'b--.')
plt.grid(True)
plt.xlabel('Width of Foundation (m)')
plt.ylabel('Allowable Bearing Capacity (kPa)')
plt.axis([0, dd, 0, ss])

# Plotting Modulus of Subgrade Reaction
plt.figure(2)
plt.plot(B_values, ksv_values, 'r--.')
plt.legend(['Vesic'])
plt.grid(True)
plt.xlabel('Width of Foundation (m)')
plt.ylabel('Modulus of Subgrade Reaction (kN/m^3)')
plt.xlim([0, dd] if dd == 5 else [5, dd])

plt.show()

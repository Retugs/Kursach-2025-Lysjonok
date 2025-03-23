import numpy as np
import numpy.linalg as la
import matplotlib.pyplot as plt

# Given parameters (can be adjusted as needed)
a = 1.0   # length unit for 'a' (set a=1 for simplicity; total beam length = 3a)
M = 1.0   # applied moment at x=0 (clockwise positive)
q = 1.0   # uniformly distributed load from x=0 to x=a (upward positive)
P = 1.0   # concentrated load at x=5a/2 (downward positive)

# 1. Compute support reactions R0, R2, R3.
# Set up linear equations from equilibrium and compatibility (deflection at x=2a = 0).
# Unknowns will be initial parameters C1, C3 (related to slope/moment at x=0) and reaction R2.
# Equation form derived by method of initial parameters:
#    32*C1*a^2 + 48*C3 + 48*M*a - 15*a^3*q = 0        (1)  [deflection at x=2a condition]
#    152*C1*a^2 + 48*C3 + 8*R2*a^2 - P*a^2 + 120*M*a - 100*a^3*q = 0   (2)  [deflection at x=2a condition]
#    6*C1*a + 2*R2*a - P*a + 2*M - 5*a^2*q = 0        (3)  [slope/moment conditions at x=3a]
# Solve the system for C1, C3, R2:
A = np.array([
    [32*a**2, 48,       0      ],   # coefficients for C1, C3, R2 in eq(1)
    [152*a**2, 48,      8*a**2 ],   # coefficients in eq(2)
    [6*a,     0,        2*a    ]    # coefficients in eq(3)
], dtype=float)
B = np.array([
    15*a**3*q - 48*M*a,                     # right-hand side of eq(1)
    P*a**2 - 120*M*a + 100*a**3*q,          # right-hand side of eq(2)
    P*a - 2*M + 5*a**2*q                    # right-hand side of eq(3)
], dtype=float)
C1, C3, R2 = la.solve(A, B)  # solve for C1, C3, R2

# Now compute reactions at supports:
R0 = C1       # reaction at x=0 (since C1 = initial shear = R0 for equilibrium)
R3 = P - q*a - R0 - R2   # reaction at x=3a from equilibrium (sum of vertical forces = 0)

# Print the support reactions (numerical values):
print(f"Support reactions: R0 = {R0:.4f},  R2 = {R2:.4f},  R3 = {R3:.4f}")

# 2. Compute deflection curve using method of initial parameters (piecewise integration).
# Define functions for deflection and its derivatives in each segment of the beam.

# **Segment 1: 0 <= x <= a** (with uniform load q and applied moment M at x=0)
# General solution for deflection in this segment (EI=1):
#    y1(x) = -q*x^4/24 + (C1/6)*x^3 + (M/2)*x^2 + C3*x
# Where C1 and C3 have been determined above.
def y1(x):
    return -q * x**4 / 24 + C1 * x**3 / 6 + M * x**2 / 2 + C3 * x

def y1p(x):
    # first derivative (slope) in segment 1
    return -q * x**3 / 6 + C1 * x**2 / 2 + M * x + C3

def y1pp(x):
    # second derivative (bending moment) in segment 1
    return -q * x**2 / 2 + C1 * x + M

def y1ppp(x):
    # third derivative (shear) in segment 1
    return -q * x + C1

# Calculate values at x = a (end of segment 1) to use as initial conditions for segment 2
y_a     = y1(a)
yprime_a= y1p(a)
ypp_a   = y1pp(a)
yppp_a  = y1ppp(a)

# **Segment 2: a <= x <= 2a** (no distributed load)
# In this span, the shear is constant (no load), equal to y'''(a) = yppp_a.
# Use the method of initial parameters to write deflection in segment 2 based on values at x=a:
#    y2(x) = y(a) + y'(a)*(x - a) + 0.5*y''(a)*(x - a)^2 + (1/6)*y'''(a)*(x - a)^3
def y2(x):
    dx = x - a
    return y_a + yprime_a * dx + 0.5 * ypp_a * dx**2 + (1.0/6.0) * yppp_a * dx**3

# Compute values at x = 2a (support B, just before applying reaction R2):
y_2a_left      = y2(2*a)       # deflection at x=2a from left (should be some value before applying support condition)
yprime_2a_left = yprime_a + ypp_a * a + 0.5 * yppp_a * a**2   # slope at 2a (from left side)
ypp_2a_left    = ypp_a + yppp_a * a                           # bending moment at 2a (from left side)
yppp_2a_left   = yppp_a                                       # shear at 2a (from left side)

# Apply support B at x=2a (hinged support):
# Deflection at x=2a must be zero, so the actual deflection y(2a) = 0.
# The reaction R2 causes a jump in shear: y'''(2a+)_right = y'''(2a-_left) + R2.
y_B       = 0.0                     # y(2a) = 0 (support deflection)
yprime_B  = yprime_2a_left          # slope at 2a remains the same (continuous rotation at hinge)
ypp_B     = ypp_2a_left             # bending moment at 2a remains the same (continuous through beam)
yppp_B_after = yppp_2a_left + R2    # shear just after x=2a, including reaction R2

# **Segment 3: 2a <= x <= 2.5a** (from support B to the point load at 5a/2, no distributed load)
# Using initial values at x=2a (after R2) as starting conditions:
#    y3(x) = y_B + yprime_B*(x - 2a) + 0.5*ypp_B*(x - 2a)^2 + (1/6)*yppp_B_after*(x - 2a)^3
def y3(x):
    dx = x - 2*a
    return y_B + yprime_B * dx + 0.5 * ypp_B * dx**2 + (1.0/6.0) * yppp_B_after * dx**3

# Calculate values at x = 5a/2 (point where load P is applied):
x_load = 2.5 * a
y_load_before     = y3(x_load)
yprime_load_before= yprime_B + ypp_B * (0.5 * a) + 0.5 * yppp_B_after * (0.5 * a)**2
ypp_load_before   = ypp_B + yppp_B_after * (0.5 * a)
yppp_load_before  = yppp_B_after  # shear just before the point load

# Apply the point load P at x = 5a/2 (downward load causes a drop in shear):
y_load_after    = y_load_before          # deflection is continuous
yprime_load_after = yprime_load_before   # slope is continuous at the load point
ypp_load_after    = ypp_load_before      # bending moment is continuous at the load point
yppp_load_after   = yppp_load_before - P # shear just after the load (jump down by magnitude P)

# **Segment 4: 2.5a <= x <= 3a** (from point load to right support, no distributed load)
# Using initial values at x=5a/2 after the load as starting conditions:
#    y4(x) = y_load_after + yprime_load_after*(x - 2.5a) + 0.5*ypp_load_after*(x - 2.5a)^2
#             + (1/6)*yppp_load_after*(x - 2.5a)^3
def y4(x):
    dx = x - x_load
    return y_load_after + yprime_load_after * dx + 0.5 * ypp_load_after * dx**2 + (1.0/6.0) * yppp_load_after * dx**3

# Generate points along the beam and compute deflection for each segment
x_vals = np.linspace(0, 3*a, 301)
y_vals = np.empty_like(x_vals)
for i, xv in enumerate(x_vals):
    if xv <= a:
        y_vals[i] = y1(xv)
    elif xv <= 2*a:
        y_vals[i] = y2(xv)
    elif xv <= 2.5*a:
        y_vals[i] = y3(xv)
    else:
        y_vals[i] = y4(xv)

# Plot the deflection curve
plt.figure(figsize=(6,4))
plt.plot(x_vals, y_vals, label='Elastic line (deflection)')
plt.axhline(0, color='gray', linewidth=0.8)
plt.axvline(0,   color='gray', linestyle='--', linewidth=0.8)    # support at x=0
plt.axvline(2*a, color='gray', linestyle='--', linewidth=0.8)    # support at x=2a
plt.axvline(3*a, color='gray', linestyle='--', linewidth=0.8)    # support at x=3a
plt.title('Deflection curve of the beam')
plt.xlabel('Position x along beam')
plt.ylabel('Deflection y')
plt.legend(loc='upper right')
plt.grid(True)
plt.show()
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# ==========================================
# 1. Generación de Datos Sintéticos (Motor CD)
# ==========================================
np.random.seed(42)
N_samples = 1000

# Entradas: Voltaje (0 a 24 V) y Par de Carga (0 a 5 Nm)
V_a = np.random.uniform(0, 24, N_samples)
T_L = np.random.uniform(0, 5, N_samples)

# Salida: Velocidad (rad/s) con modelo no lineal simplificado
omega = 45 * V_a * np.exp(-0.05 * T_L) - 8 * T_L**1.5 + np.random.normal(0, 2, N_samples)
omega = np.clip(omega, 0, None) # La velocidad no puede ser negativa

# Empaquetar y normalizar datos
X = np.column_stack((V_a, T_L))
y = omega.reshape(-1, 1)

scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

X_norm = scaler_X.fit_transform(X)
y_norm = scaler_y.fit_transform(y)

# Convertir a tensores de PyTorch
X_tensor = torch.tensor(X_norm, dtype=torch.float32)
y_tensor = torch.tensor(y_norm, dtype=torch.float32)

# ==========================================
# 2. Definición del Modelo MotorANFIS
# ==========================================
class MotorANFIS(nn.Module):
    def __init__(self, n_mfs=3):
        super(MotorANFIS, self).__init__()
        self.n_mfs = n_mfs
        self.n_rules = n_mfs * n_mfs  # 3 * 3 = 9 reglas

        # Parámetros Antecedentes (Centros y Sigmas para 2 entradas)
        self.c1 = nn.Parameter(torch.linspace(0, 1, n_mfs))
        self.c2 = nn.Parameter(torch.linspace(0, 1, n_mfs))
        self.s1 = nn.Parameter(torch.ones(n_mfs) * 0.3)  # Sigmas (anchos)
        self.s2 = nn.Parameter(torch.ones(n_mfs) * 0.3)

        # Parámetros Consecuentes (p, q, r para cada regla)
        self.p = nn.Parameter(torch.randn(self.n_rules) * 0.1)
        self.q = nn.Parameter(torch.randn(self.n_rules) * 0.1)
        self.r = nn.Parameter(torch.randn(self.n_rules) * 0.1)

    def forward(self, x1, x2):
        # Asegurar que las sigmas sean positivas para evitar división por cero o NaN
        s1 = torch.abs(self.s1) + 1e-4
        s2 = torch.abs(self.s2) + 1e-4

        # Capa 1: Difusificación (Gaussianas)
        mu1 = torch.exp(-0.5 * ((x1.unsqueeze(1) - self.c1) / s1) ** 2)
        mu2 = torch.exp(-0.5 * ((x2.unsqueeze(1) - self.c2) / s2) ** 2)

        # Capa 2: Fuerza de disparo (Producto de membresías)
        w = torch.bmm(mu1.unsqueeze(2), mu2.unsqueeze(1)).view(-1, self.n_rules)

        # Capa 3: Normalización
        w_sum = torch.sum(w, dim=1, keepdim=True) + 1e-8
        w_norm = w / w_sum

        # Capas 4 y 5: Consecuentes y Salida global combinada
        x1_b = x1.unsqueeze(1)
        x2_b = x2.unsqueeze(1)
        rule_outputs = self.p.unsqueeze(0) * x1_b + self.q.unsqueeze(0) * x2_b + self.r.unsqueeze(0)

        output = torch.sum(w_norm * rule_outputs, dim=1, keepdim=True)
        return output

# ==========================================
# 3. Entrenamiento del Modelo
# ==========================================
model = MotorANFIS(n_mfs=3)  # 3 MFs por entrada = 9 reglas
optimizer = torch.optim.Adam(model.parameters(), lr=0.05)
criterion = nn.MSELoss()

epochs = 150
loss_history = []

print("Iniciando entrenamiento ANFIS...")
for epoch in range(epochs):
    optimizer.zero_grad()

    # Forward pass
    predictions = model(X_tensor[:, 0], X_tensor[:, 1])
    loss = criterion(predictions, y_tensor)

    # Backward pass y optimización
    loss.backward()
    optimizer.step()

    loss_history.append(loss.item())

# ==========================================
# 4. Evaluación, Métricas y Gráficas
# ==========================================
with torch.no_grad():
    y_pred_norm = model(X_tensor[:, 0], X_tensor[:, 1]).numpy()

y_pred = scaler_y.inverse_transform(y_pred_norm.reshape(-1, 1)).flatten()
y_true = scaler_y.inverse_transform(y_tensor.numpy().reshape(-1, 1)).flatten()

# Calcular error
rmse = np.sqrt(np.mean((y_true - y_pred)**2))
print(f"\nRMSE en datos de entrenamiento: {rmse:.4f} rad/s")

# Gráficas de resultados (1x3 subplots según tu estructura)
fig, axs = plt.subplots(1, 3, figsize=(18, 5))

# 1. Curva de aprendizaje
axs[0].plot(loss_history, color='blue', lw=2)
axs[0].set_title('Curva de Aprendizaje (MSE)', fontsize=12)
axs[0].set_xlabel('Épocas')
axs[0].set_ylabel('Pérdida')
axs[0].grid(True)

# 2. Velocidad Real vs Predicha
axs[1].scatter(y_true, y_pred, alpha=0.5, color='purple', edgecolors='k')
axs[1].plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2, label='Ideal')
axs[1].set_title('Velocidad Real vs Predicha (ANFIS)', fontsize=12)
axs[1].set_xlabel('Velocidad Real (rad/s)')
axs[1].set_ylabel('Velocidad Predicha (rad/s)')
axs[1].legend()
axs[1].grid(True)

# 3. Superficie de Respuesta del Motor (Voltaje vs Par -> Velocidad)
V_grid = np.linspace(0, 24, 30)
T_grid = np.linspace(0, 5, 30)
VV, TT = np.meshgrid(V_grid, T_grid)

# Normalizar la malla para el modelo
X_grid_raw = np.column_stack((VV.ravel(), TT.ravel()))
X_grid_norm = scaler_X.transform(X_grid_raw)

with torch.no_grad():
    grid_pred_norm = model(torch.tensor(X_grid_norm[:, 0], dtype=torch.float32),
                           torch.tensor(X_grid_norm[:, 1], dtype=torch.float32)).numpy()

grid_pred = scaler_y.inverse_transform(grid_pred_norm.reshape(-1, 1)).reshape(VV.shape)

axs[2].remove() # Eliminar el subplot 2D para colocar uno 3D
ax3 = fig.add_subplot(1, 3, 3, projection='3d')
surf = ax3.plot_surface(VV, TT, grid_pred, cmap='viridis', edgecolor='none', alpha=0.8)
ax3.set_title('Superficie de Respuesta ANFIS', fontsize=12)
ax3.set_xlabel('Voltaje (V)')
ax3.set_ylabel('Par de Carga (Nm)')
ax3.set_zlabel('Velocidad (rad/s)')
fig.colorbar(surf, ax=ax3, shrink=0.5, aspect=5)

plt.tight_layout()
plt.savefig('output.png')

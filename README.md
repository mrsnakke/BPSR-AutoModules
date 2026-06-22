# BPSR Module Optimizer Season 3

<p align="center">
  <img src="icon.ico" width="120" height="120" alt="BPSR Module Optimizer Logo">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow.svg" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/UI-PyQt6-green.svg" alt="UI">
  <img src="https://img.shields.io/badge/Core-C%2B%2B-orange.svg" alt="Core">
</p>

---

<p align="center">
  <b>Language / Idioma</b><br>
  <a href="#english-version">🇬🇧 English</a> | <a href="#spanish-version">🇪🇸 Español</a>
</p>

---

<a name="english-version"></a>

# 🇬🇧 English Version
<img width="1399" height="881" alt="image" src="https://github.com/mrsnakke/gachaIMG/blob/main/newss.png?raw=true" />

A high-performance module optimization tool with a modern graphical user interface for **"Blue Protocol Star Resonance" (BPSR)**.

## 🌟 Key Features

*   **Modern GUI Includes:**
    *   **Optimizer:** High-speed configuration and calculation.
    *   **Inventory:** Visual representation of modules through detailed cards.
    *   **Settings:** Network management, interface, and language options.
*   **Automated Network Sniffing:** No manual input needed! Just change channels, teleport, or relogin to automatically import your inventory.
*   **Dynamic Monitoring:** Real-time tracking of the `modules.vdata` file. Changes are loaded instantly without restarting the application.
*   **High-Performance C++ Core:** Built with `pybind11`, utilizing beam search and parallel enumeration to calculate trillions of combinations in seconds.
*   **Hardware Acceleration:** Native support for CUDA (NVIDIA) and OpenCL (AMD/Intel) with automatic fallback to CPU.
*   **Multilingual:** Fully translated into English, Spanish, and Chinese.

## 📦 Installation & Usage (Recommended)

1.  **Download the executable:** Get `BPSR_Module_Optimizer.exe` from the [Releases](#) section.
2.  **Install Npcap:** Download and install [Npcap](https://npcap.com/). This is **mandatory** for real-time data capture.
3.  **Run the App:** Save the file in any folder and open it.
4.  **Capture your Modules:**
    *   Launch the app and add stats by priority. It is recommended to add all possible stats for your build (e.g., 6 stats) for better results.
    *   Choose the **Optimization Method** according to your goals:
        *   **Standard**: Focuses on balanced and well-rounded combat score. Highly recommended for general gameplay and overall attribute value optimization.
        *   **Priority Lv.6/Lv.5**: A strict mode focused purely on reaching the highest levels (Lv.5 or Lv.6) on your filtered stats, regardless of overall balance.
        *   **Auto (Recommended)**: An intelligent multiclass algorithm that maximizes Lv.6 stats prioritising your filters, actively seeking ideal synergy combinations (e.g., granting massive bonuses for a perfect 6xLv.6 + 1xLv.2 combo).
    *   Click on **Calculate 5-module combo sets**.
    *   In-game, **teleport or switch channels**.
    *   The app will automatically save your modules to `modules.vdata`.
    *   Status: `🟢 Inventory Loaded (X modules)`.
5.  **Optimize:** Select your priorities in the **Optimizer** tab and click **Calculate**.
	*   ⚠️ If your inventory is already loaded (`🟢 Inventory Loaded`), you can use the **"Use existing data"** option to recalculate without having to capture the data again.

## 💻 Advanced Installation (Source Code)

### Requirements
*   Python 3.10+
*   Visual Studio Build Tools 2019/2022 (C++ Desktop Development)
*   Windows SDK
*   *(Optional)* CUDA Toolkit 12.8 for NVIDIA support.

### Steps
```bash
# 1. Clone repository
git clone https://github.com/mrsnakke/BPSR-AutoModules.git
cd BPSR-AutoModules

# 2. Install dependencies
pip install -r requirements.txt

# 3. Build C++ extension
cd cpp_extension
python setup.py build_ext --inplace
cd ..

# 4. Run
python gui/main_window.py

# 5. Build executable (.exe) (Requires PyInstaller)
pip install pyinstaller
python build.py
```

## ⚠️ Known Issues
*   The UI may briefly become unresponsive during massive optimization calculations due to high CPU load. We are working on improving asynchronous processing.

## ❤️ Credits & Disclaimer
*   **Fork based on:** [StarResonanceAutoMod](https://github.com/fudiyangjin/StarResonanceAutoMod) by fudiyangjin.
*   **Special thanks to:** [StarResonanceDamageCounter](https://github.com/dmlgzs/StarResonanceDamageCounter) by dmlgzs.

**Disclaimer:** This tool is for educational and data analysis purposes only. The user assumes all risks. The author is not responsible for any violations of the game's terms of service.

---

<a name="spanish-version"></a>

# 🇪🇸 Versión en Español
<img width="1399" height="881" alt="image" src="https://github.com/mrsnakke/gachaIMG/blob/main/newss.png?raw=true" />

Una herramienta de optimización de módulos con interfaz gráfica para **"Blue Protocol Star Resonance" (BPSR)**.

## 🌟 Características Clave

*   **La Interfaz Incluye:**
    *   **Optimizador:** Configuración y cálculo de alta velocidad.
    *   **Inventario:** Visualización gráfica de módulos mediante tarjetas detalladas.
    *   **Ajustes:** Gestión de Red, interfaz e idioma.
*   **Captura Automática de Red:** ¡Sin entrada manual! Cambia de canal, teletranspórtate o reinicia sesión para importar automáticamente tu inventario.
*   **Detección Dinámica:** Monitorea el archivo `modules.vdata` en tiempo real. Los cambios se cargan instantáneamente sin reiniciar la app.
*   **Núcleo C++ de Alto Rendimiento:** Implementado con `pybind11`, utiliza búsqueda de haz (beam search) y enumeración paralela para calcular billones de opciones en segundos.
*   **Aceleración por Hardware:** Soporte nativo para CUDA (NVIDIA) y OpenCL (AMD/Intel) con transición automática a CPU.
*   **Multilingüe:** Traducido al Inglés, Español y Chino.

## 📦 Instalación y Uso (Recomendado)

1.  **Descarga el ejecutable:** Consigue `BPSR_Module_Optimizer.exe` en la sección de [Releases](#).
2.  **Instala Npcap:** Descarga e instala [Npcap](https://npcap.com/). Es **indispensable** para la captura de datos en tiempo real.
3.  **Ejecuta la App:** Guarda el archivo en cualquier carpeta y ábrelo.
4.  **Captura tus Módulos:**
    *   Ejecutar la app y añadir los stats por prioridad. Se recomienda poner todos los que pueda llevar tu build (por ejemplo 6 stats) para mejores resultados.
    *   Elige el **Método de Optimización** según tus objetivos:
        *   **Estándar (Standard)**: Valora estadísticas de nivel alto, pero busca una distribución general equilibrada y balanceada basada en el poder de combate general.
        *   **Prioridad Lv.6/Lv.5**: Enfoque estricto para maximizar y obtener niveles altos (Lv.5 o Lv.6) exclusivamente en tus estadísticas filtradas, sin importar el balance de otras estadísticas.
        *   **Auto (Recomendado)**: Algoritmo inteligente multicapa que maximiza estadísticas en Lv.6 priorizando de forma inteligente tus filtros y buscando combinaciones ideales (como el combo perfecto de 6 Lv.6 + 1 Lv.2 para darte un bono masivo).
    *   Presionar **Calcular conjuntos de 5 módulos**.
    *   Dentro del juego, **cambia de canal o teletranspórtate**.
    *   La app guardará los módulos automáticamente en `modules.vdata`.
    *   Estado: `🟢 Inventario Cargado (X módulos)`.
5.  **Optimiza:** Selecciona tus prioridades en la pestaña **Optimizador** y pulsa **Calcular**.
	*   ⚠️ Si ya cargaste tu inventario (`🟢 Inventario Cargado`) cuando pulses a **Calcular** puedes usar la opción de **"Usar datos existentes"** para recalcular sin tener que capturar de nuevo los datos.

## 💻 Instalación Avanzada (Código Fuente)

### Requisitos
*   Python 3.10+
*   Visual Studio Build Tools 2019/2022 (Desarrollo de escritorio con C++)
*   Windows SDK
*   *(Opcional)* CUDA Toolkit 12.8 para soporte NVIDIA.

### Pasos
```bash
# 1. Clonar repositorio
git clone https://github.com/mrsnakke/BPSR-AutoModules.git
cd BPSR-AutoModules

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Compilar extensión C++
cd cpp_extension
python setup.py build_ext --inplace
cd ..

# 4. Ejecutar
python gui/main_window.py

# 5. Compilar ejecutable (.exe) (Requiere PyInstaller)
pip install pyinstaller
python build.py
```

## ⚠️ Problemas Conocidos
*   La interfaz puede no responder brevemente durante cálculos de optimización masivos debido a la carga del procesador. Estamos trabajando en mejorar la asincronía.

## ❤️ Créditos y Descargo de Responsabilidad
*   **Fork basado en:** [StarResonanceAutoMod](https://github.com/fudiyangjin/StarResonanceAutoMod) de fudiyangjin.
*   **Agradecimientos:** [StarResonanceDamageCounter](https://github.com/dmlgzs/StarResonanceDamageCounter) de dmlgzs.

**Descargo de responsabilidad:** Herramienta para fines de análisis y aprendizaje. El usuario asume todos los riesgos. El autor no se responsabiliza por violaciones de los términos de servicio del juego.

---

<p align="center">
  <a href="#bpsr-module-optimizer">Back to top / Volver arriba ↑</a>
</p>
```

# BPSR Module Optimizer

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

An intelligent, high-performance module optimization tool with a modern PyQt6 graphical user interface for the game **"Blue Protocol Star Resonance" (BPSR)**.

## 🌟 Key Features

*   **Modern PyQt6 GUI:** A beautiful dark-themed interface built for a seamless user experience. Includes tabs for:
    *   **Optimizer:** Configuration and high-speed calculation.
    *   **Inventory:** Visualizing all captured modules with beautiful cards.
    *   **Settings:** Paths, interface, and language customization.
*   **Automated Network Packet Sniffing:** No manual input needed! Simply change channels, teleport, or relogin in the game, and the program automatically captures and imports your module inventory.
*   **Dynamic File Watching:** Automatically monitors `modules.vdata`. Any updates from network capture or file changes are loaded instantly without restarting.
*   **Ultra-Fast C++ Core Optimizer:** Employs parallel strategy enumeration + beam search compiled in C++ (via pybind11). Capable of calculating trillions of combinations in seconds.
*   **Hardware Acceleration:** Automatic GPU acceleration (CUDA for NVIDIA, OpenCL for AMD/Intel) with seamless fallback to CPU.
*   **Bilingual Support:** Fully localized in English, Spanish, and Chinese.

## 📦 Installation & Usage (Recommended)

1.  **Download the executable:** Get the latest precompiled `BPSR_Module_Optimizer.exe` from the [Releases](#) section.
2.  **Install Npcap:** Download and install [Npcap](https://npcap.com/). This is **required** for live network packet capturing.
3.  **Run the App:** Place the executable in any folder and run it. No Python installation required!
4.  **Capture Modules:** 
    *   While the game is open, **teleport, switch channel, or relogin**.
    *   The app will automatically save your modules to `modules.vdata`.
    *   Status: `🟢 Inventory Loaded (X modules)`.
5.  **Optimize:** Choose your attributes in the **Optimizer** tab and click **Calculate**.

## 💻 Advanced Installation (From Source)

### Requirements
*   Python 3.10+
*   Visual Studio Build Tools 2019/2022 (C++ Desktop Development)
*   Windows SDK
*   *(Optional)* CUDA Toolkit 12.8 for NVIDIA GPU acceleration.

### Steps
```bash
# 1. Clone the repository
git clone https://github.com/fudiyangjin/StarResonanceAutoMod.git
cd StarResonanceAutoMod

# 2. Install dependencies
pip install -r requirements.txt

# 3. Build C++ core extension
cd cpp_extension
python setup.py build_ext --inplace
cd ..

# 4. Run application
python gui/main_window.py
```

## ⚠️ Known Issues
*   The UI may appear unresponsive for a few seconds during extremely intensive calculations. We are working on offloading these tasks to improve fluidity.

## ❤️ Credits & Disclaimer
*   **Fork based on:** [StarResonanceAutoMod](https://github.com/fudiyangjin/StarResonanceAutoMod) by fudiyangjin.
*   **Inspiration:** [StarResonanceDamageCounter](https://github.com/dmlgzs/StarResonanceDamageCounter) by dmlgzs.

**Disclaimer:** This tool is for learning and data analysis only. Use at your own risk. The author is not responsible for any misuse or violations of the game's terms of service.

---

<a name="spanish-version"></a>

# 🇪🇸 Versión en Español

Una herramienta inteligente de optimización de módulos de alto rendimiento con interfaz gráfica moderna en PyQt6 para el juego **"Blue Protocol Star Resonance" (BPSR)**.

## 🌟 Características Clave

*   **Interfaz Gráfica Moderna (PyQt6):** Tema oscuro diseñado para una experiencia fluida. Incluye:
    *   **Optimizador:** Configuración y cálculo de alta velocidad.
    *   **Inventario:** Visualización gráfica de módulos mediante tarjetas detalladas.
    *   **Ajustes:** Gestión de rutas, interfaz e idioma.
*   **Captura Automática de Red:** ¡Sin entrada manual! Cambia de canal, teletranspórtate o reinicia sesión para importar automáticamente tu inventario.
*   **Detección Dinámica:** Monitorea el archivo `modules.vdata` en tiempo real. Los cambios se cargan instantáneamente sin reiniciar la app.
*   **Núcleo C++ de Alto Rendimiento:** Implementado con `pybind11`, utiliza búsqueda de haz (beam search) y enumeración paralela para calcular billones de opciones en segundos.
*   **Aceleración por Hardware:** Soporte nativo para CUDA (NVIDIA) y OpenCL (AMD/Intel) con transición automática a CPU.
*   **Multilingüe:** Traducido al Inglés, Español y Chino.

## 📦 Instalación y Uso (Recomendado)

1.  **Descarga el ejecutable:** Consigue `BPSR_Module_Optimizer.exe` en la sección de [Releases](#).
2.  **Instala Npcap:** Descarga e instala [Npcap](https://npcap.com/). Es **indispensable** para la captura de datos en tiempo real.
3.  **Ejecuta la App:** Guarda el archivo en cualquier carpeta y ábrelo. ¡No requiere Python!
4.  **Captura tus Módulos:**
    *   Dentro del juego, **cambia de canal o teletranspórtate**.
    *   La app guardará los módulos automáticamente en `modules.vdata`.
    *   Estado: `🟢 Inventario Cargado (X módulos)`.
5.  **Optimiza:** Selecciona tus prioridades en la pestaña **Optimizador** y pulsa **Calcular**.

## 💻 Instalación Avanzada (Código Fuente)

### Requisitos
*   Python 3.10+
*   Visual Studio Build Tools 2019/2022 (Desarrollo de escritorio con C++)
*   Windows SDK
*   *(Opcional)* CUDA Toolkit 12.8 para soporte NVIDIA.

### Pasos
```bash
# 1. Clonar repositorio
git clone https://github.com/fudiyangjin/StarResonanceAutoMod.git
cd StarResonanceAutoMod

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Compilar extensión C++
cd cpp_extension
python setup.py build_ext --inplace
cd ..

# 4. Ejecutar
python gui/main_window.py
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
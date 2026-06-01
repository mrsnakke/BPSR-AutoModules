<!-- Botón para saltar a la versión en Español -->
[![Español](https://img.shields.io/badge/Español%20🇪🇸-C60B1E?style=for-the-badge)](#spanish-version)

<a id="english-version"></a>
# ✨ BPSR Auto Modules — Module Optimizer

![Application Screenshot]([https://github.com/mrsnakke/gachaIMG/blob/main/imagen_2025-11-06_182613541.png?raw=true](https://github.com/mrsnakke/gachaIMG/blob/main/moduss3.png?raw=true))

🚀 A graphical interface tool to capture and analyze in-game modules, facilitating the automatic discovery of optimal equipment combinations.

![Application Screenshot](https://github.com/mrsnakke/gachaIMG/blob/main/cap1.png?raw=true)

## 🌟 Key Features

- 🖱️ Intuitive graphical interface — all functionality is accessible via buttons and menus.
- 🎮 Automatic data capture — start monitoring from the application, and the program detects game data.
- 🔍 Advanced filtering:
    - 🛡️ Filter by module type: Attack, Guard, Support, or All.
    - ✨ Filter by specific attributes to search for concrete combinations.
    - 🎯 Pre-configured attribute presets for popular classes.
    - 📊 Attribute distribution filter (Lv.5, Lv.5/Lv.5, Lv.5/Lv.6, Lv.6/Lv.6) to further refine results.
- 🔄 Instant re-filtering — change filters and use "Refilter" to update results without re-capturing.
- 📊 Detailed results visualization:
    - Combinations ordered by a "fitness" score.
    - Visualization of each module (image, rarity, and attributes).
    - Summary of total attribute distribution and estimated combat power calculation.
- 💻 Integrated console — process logs visible in a panel that you can show or hide.

## 🛠️ Installation and Usage (For Users preferring a simple installation - Recommended)
[![PORTADA DE VIDEO](https://github.com/mrsnakke/gachaIMG/blob/main/PORTADA%202026%20(1).jpg?raw=true)](https://youtu.be/P_VSNP-Y9ME?si=j-Ubt9q6ZCfzbC3e)

🚀 For a quick and easy setup, use our installer.

1.  ⬇️ **Download the Installer**:
    Download the latest version of `BPSR Module Optimizer Setup.exe` from the [releases page](https://github.com/mrsnakke/BPSR-AutoModules/releases).

2.  ▶️ **Run the Installer**:
    -   Double-click `BPSR Module Optimizer Setup.exe` to start the installation.
    -   🚶 The installer will guide you through the process.
    -   ⚠️ **Npcap Installation (Important!)**: The application requires `Npcap` to capture game data.
        -   If `Npcap` is not detected on your system, the installer will prompt you to install it. Follow the on-screen instructions for `Npcap`.
        -   ✅ During `Npcap` installation, make sure to check the option "Install Npcap in WinPcap API-compatible Mode" if available. This is crucial for the application to function correctly.
        -   If `Npcap` is already installed, the installer will proceed directly with the application installation.

3.  🚀 **Launch the Application**:
    -   Once the installation is complete, you can launch "BPSR Module Optimizer" from your desktop shortcut or the Start Menu.

4.  ⚙️ **Initial Configuration in the Application**:
    -   Select the network interface you use (Ethernet or Wi-Fi).
    -   Choose the module type (Attack / Guard / Support / All).
    -   Define attributes manually or select a preset.
    -   (Optional) Adjust the attribute distribution filter to view specific combinations (e.g., Lv.5/Lv.5).

5.  ▶️ **Start Monitoring**:
    -   Click "Start Monitoring" to begin capturing.
    -   🎮 In the game, trigger data transmission (e.g., changing channels or returning to the character selection screen).
    -   📈 The application will detect the data and display the best results in the main panel.

6.  🔄 **Adjust and Re-filter**:
    -   Adjust filters and use "Refilter" to recalculate without re-capturing.
    -   ⏹️ When finished, click "Stop Monitoring".

## 💻 Installation and Usage (For Advanced Users - Direct Python Execution)

If you prefer to run the application directly from Python, follow these steps.

### ✅ Prerequisites

To run this project, you will need the following:

1.  Python 3.8 or higher: If you don't have Python installed, download it from the official website: [python.org](https://www.python.org/downloads/). Make sure to check the "Add Python to PATH" option during installation.
2.  Npcap: Npcap must be installed for the application to capture game network traffic.
    -   Download the Npcap installer (version npcap-1.83 or higher is recommended) from [npcap.com](https://npcap.com/#download).
    -   During installation, check the "Install Npcap in WinPcap API-compatible Mode" option if available.

Npcap allows the application to read the network packets necessary to extract module data.

### ⚙️ Installation

Follow these steps to set up and run the project:

1.  ⬇️ **Clone the repository**:
    Open a terminal (CMD, PowerShell, or Git Bash) and run the following command to clone the repository:
    ```bash
    git clone https://github.com/mrsnakke/BPSR-AutoModules.git
    cd BPSR-AutoModules
    ```

2.  🐍 **Create and activate a virtual environment (recommended)**:
    It is good practice to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    ```
    -   **On Windows**:
        ```bash
        .\venv\Scripts\activate
        ```

3.  📦 **Install dependencies**:
    With the virtual environment activated, install the necessary Python libraries:
    ```bash
    pip install customtkinter Pillow scapy zstandard protobuf
    ```
    ⚠️ *Note: `scapy` may require administrator permissions on some systems for installation or execution.*

### ▶️ Usage

1.  🚀 **Run the application**:
    Once all dependencies are installed, you can start the application by running the main script:
    ```bash
    python gui_app.py
    ```

2.  ⚙️ **Initial configuration in the application**:
    -   Select the network interface you use (Ethernet or Wi-Fi).
    -   Choose the module type (Attack / Guard / Support / All).
    -   Define attributes manually or select a preset.
    -   (Optional) Adjust the attribute distribution filter to view specific combinations (e.g., Lv.5/Lv.5).

3.  ▶️ **Start monitoring**:
    -   Click "Start Monitoring" to begin capturing.
    -   🎮 In the game, trigger data transmission (e.g., changing channels or returning to the character selection screen).
    -   📈 The application will detect the data and display the best results in the main panel.

4.  🔄 **Adjust and Re-filter**:
    -   Adjust filters and use "Refilter" to recalculate without re-capturing.
    -   ⏹️ When finished, click "Stop Monitoring".

## 🤝 Contributions

We appreciate your contributions! 🐛 If you find a bug, ✨ have a suggestion for improvement, or 🚀 want to add new features, feel free to open an "issue" or submit a "pull request".

**⚠️ Known issues:**
-   ⏳ The user interface may appear unresponsive for a few seconds while intensive background tasks are performed (e.g., module optimization). This is due to the nature of parallel operations and GUI updates. We are working on improving fluidity.

## ❤️ Credits

-   This project is a fork that integrates and adapts previous work by other authors.
-   Main credits:
    -   Fork based on: StarResonanceAutoMod — author: fudiyangjin
        https://github.com/fudiyangjin/StarResonanceAutoMod
    -   We also appreciate the complementary work of StarResonanceDamageCounter (dmlgzs):
        https://github.com/dmlgzs/StarResonanceDamageCounter

📜 If you use this project, please respect the original licenses and attributions.

---

🚨 **Disclaimer**: This tool is for learning and data analysis purposes only. It should not be used for activities that violate the game's terms of service. The user assumes the associated risks. The project author is not responsible for misuse by third parties. Make sure to comply with game and community rules and policies before using it.

<br>

<a id="spanish-version"></a>
# ✨ BPSR Auto Modules — Optimizador de Módulos

![Application Screenshot](https://github.com/mrsnakke/gachaIMG/blob/main/imagen_2025-11-06_182613541.png?raw=true)

🚀 Herramienta con interfaz gráfica para capturar y analizar los módulos del juego, que facilita encontrar combinaciones óptimas de equipamiento de forma automática.

![Captura de pantalla de la aplicación](https://github.com/mrsnakke/gachaIMG/blob/main/cap1.png?raw=true)

## 🌟 Características principales

- 🖱️ Interfaz gráfica intuitiva — toda la funcionalidad está accesible mediante botones y menús.
- 🎮 Captura de datos automática — inicia el monitoreo desde la aplicación y el programa detecta los datos del juego.
- 🔍 Filtrado avanzado:
    - 🛡️ Filtra por tipo de módulo: Ataque, Guardia, Soporte o Todos.
    - ✨ Filtra por atributos específicos para buscar combinaciones concretas.
    - 🎯 Presets de atributos preconfigurados para clases populares.
    - 📊 Filtro de distribución de atributos (Lv.5, Lv.5/Lv.5, Lv.5/Lv.6, Lv.6/Lv.6) para refinar aún más los resultados.
- 🔄 Re-filtrado instantáneo — cambia los filtros y usa "Refiltrar" para actualizar resultados sin volver a capturar.
- 📊 Visualización detallada de resultados:
    - Combinaciones ordenadas por una puntuación de "fitness".
    - Visualización de cada módulo (imagen, rareza y atributos).
    - Resumen de la distribución total de atributos y cálculo del poder de combate estimado.
- 💻 Consola integrada — registros de proceso visibles en un panel que puedes mostrar u ocultar.

## 🛠️ Instalación y Uso (Para Usuarios que prefieren una instalación sencilla - Recomendado)
[![PORTADA DE VIDEO](https://github.com/mrsnakke/gachaIMG/blob/main/PORTADA%202026%20(1).jpg?raw=true)](https://youtu.be/P_VSNP-Y9ME?si=j-Ubt9q6ZCfzbC3e)
🚀 Para una configuración rápida y sencilla, utiliza nuestro instalador.

1.  ⬇️ **Descarga el Instalador**:
    Descarga la última versión de `BPSR Module Optimizer Setup.exe` desde la [página de lanzamientos](https://github.com/mrsnakke/BPSR-AutoModules/releases).

2.  ▶️ **Ejecuta el Instalador**:
    -   Haz doble clic en `BPSR Module Optimizer Setup.exe` para iniciar la instalación.
    -   🚶 El instalador te guiará a través del proceso.
    -   ⚠️ **Instalación de Npcap (¡Importante!)**: La aplicación requiere `Npcap` para capturar los datos del juego.
        -   Si `Npcap` no se detecta en tu sistema, el instalador te pedirá que lo instales. Sigue las instrucciones en pantalla para `Npcap`.
        -   ✅ Durante la instalación de `Npcap`, asegúrate de marcar la opción "Install Npcap in WinPcap API-compatible Mode" si está disponible. Esto es crucial para que la aplicación funcione correctamente.
        -   Si `Npcap` ya está instalado, el instalador procederá directamente con la instalación de la aplicación.

3.  🚀 **Inicia la Aplicación**:
    -   Una vez completada la instalación, puedes iniciar "BPSR Module Optimizer" desde el acceso directo en tu escritorio o desde el Menú Inicio.

4.  ⚙️ **Configuración inicial en la aplicación**:
    -   Selecciona la interfaz de red que utilizas (Ethernet o Wi-Fi).
    -   Elige el tipo de módulo (Ataque / Guardia / Soporte / Todos).
    -   Define los atributos manualmente o selecciona un preset.
    -   (Opcional) Ajusta el filtro de distribución de atributos para ver combinaciones específicas (por ejemplo, Lv.5/Lv.5).

5.  ▶️ **Iniciar monitoreo**:
    -   Haz clic en "Start Monitoring" para comenzar la captura.
    -   🎮 En el juego, provoca el envío de datos (por ejemplo, cambiando de canal o volviendo a la pantalla de selección de personaje).
    -   📈 La aplicación detectará los datos y mostrará los mejores resultados en el panel principal.

6.  🔄 **Ajustar y re-filtrar**:
    -   Ajusta los filtros y usa "Refiltrar" para recalcular sin volver a capturar.
    -   ⏹️ Cuando termines, haz clic en "Stop Monitoring".

## 💻 Instalación y Uso (Para Usuarios Avanzados - Ejecución Directa con Python)

Si prefieres ejecutar la aplicación directamente desde Python, sigue estos pasos.

### ✅ Requisitos previos

Para ejecutar este proyecto, necesitarás lo siguiente:

1.  Python 3.8 o superior: Si no tienes Python instalado, descárgalo desde el sitio web oficial: [python.org](https://www.python.org/downloads/). Asegúrate de marcar la opción "Add Python to PATH" durante la instalación.
2.  Npcap: Es necesario instalar Npcap para que la aplicación pueda capturar tráfico de red del juego.
    -   Descarga el instalador de Npcap (se recomienda la versión npcap-1.83 o superior) desde [npcap.com](https://npcap.com/#download).
    -   Durante la instalación, marca la opción "Install Npcap in WinPcap API-compatible Mode" si está disponible.

Npcap permite que la aplicación lea los paquetes de red necesarios para extraer los datos de los módulos.

### ⚙️ Instalación

Sigue estos pasos para configurar y ejecutar el proyecto:

1.  ⬇️ **Clona el repositorio**:
    Abre una terminal (CMD, PowerShell o Git Bash) y ejecuta el siguiente comando para clonar el repositorio:
    ```bash
    git clone https://github.com/mrsnakke/BPSR-AutoModules.git
    cd BPSR-AutoModules
    ```

2.  🐍 **Crea y activa un entorno virtual (recomendado)**:
    Es una buena práctica usar un entorno virtual para gestionar las dependencias del proyecto.
    ```bash
    python -m venv venv
    ```
    -   **En Windows**:
        ```bash
        .\venv\Scripts\activate
        ```

3.  📦 **Instala las dependencias**:
    Con el entorno virtual activado, instala las librerías de Python necesarias:
    ```bash
    pip install customtkinter Pillow scapy zstandard protobuf
    ```
    ⚠️ *Nota: `scapy` puede requerir permisos de administrador en algunos sistemas para su instalación o ejecución.*

### ▶️ Uso

1.  🚀 **Ejecuta la aplicación**:
    Una vez instaladas todas las dependencias, puedes iniciar la aplicación ejecutando el script principal:
    ```bash
    python gui_app.py
    ```

2.  ⚙️ **Configuración inicial en la aplicación**:
    -   Selecciona la interfaz de red que utilizas (Ethernet o Wi-Fi).
    -   Elige el tipo de módulo (Ataque / Guardia / Soporte / Todos).
    -   Define los atributos manualmente o selecciona un preset.
    -   (Opcional) Ajusta el filtro de distribución de atributos para ver combinaciones específicas (por ejemplo, Lv.5/Lv.5).

3.  ▶️ **Iniciar monitoreo**:
    -   Haz clic en "Start Monitoring" para comenzar la captura.
    -   🎮 En el juego, provoca el envío de datos (por ejemplo, cambiando de canal o volviendo a la pantalla de selección de personaje).
    -   📈 La aplicación detectará los datos y mostrará los mejores resultados en el panel principal.

4.  🔄 **Ajustar y re-filtrar**:
    -   Ajusta los filtros y usa "Refiltrar" para recalcular sin volver a capturar.
    -   ⏹️ Cuando termines, haz clic en "Stop Monitoring".

## 🤝 Contribuciones

¡Agradecemos tus contribuciones! 🐛 Si encuentras un error, ✨ tienes una sugerencia de mejora o 🚀 quieres añadir nuevas características, no dudes en abrir un "issue" o enviar un "pull request".

**⚠️ Problemas conocidos:**
-   ⏳ La interfaz de usuario puede parecer no responder durante unos segundos mientras se realizan tareas intensivas en segundo plano (por ejemplo, la optimización de módulos). Esto se debe a la naturaleza de las operaciones paralelas y las actualizaciones de la GUI. Estamos trabajando para mejorar la fluidez.

## ❤️ Créditos

-   Este proyecto es un fork que integra y adapta trabajo previo de otros autores.
-   Créditos principales:
    -   Fork basado en: StarResonanceAutoMod — autor: fudiyangjin
        https://github.com/fudiyangjin/StarResonanceAutoMod
    -   También agradecemos el trabajo complementario de StarResonanceDamageCounter (dmlgzs):
        https://github.com/dmlgzs/StarResonanceDamageCounter

📜 Si utilizas este proyecto, por favor, respeta las licencias y atribuciones originales.

---

🚨 **Descargo de responsabilidad**: Esta herramienta tiene fines de aprendizaje y análisis de datos únicamente. No debe ser utilizada para actividades que violen los términos de servicio del juego. El usuario asume los riesgos asociados. El autor del proyecto no se responsabiliza del mal uso por parte de terceros. Asegúrate de cumplir con las reglas y políticas del juego y de la comunidad antes de usarla.

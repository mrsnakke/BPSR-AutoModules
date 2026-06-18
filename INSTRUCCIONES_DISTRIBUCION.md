dir dist
# Instrucciones para compartir la aplicación con tu amigo

¡Listo! Hemos compilado la aplicación en un único archivo ejecutable independiente (`.exe`) de Windows. Tu amigo **no necesitará instalar Python, PyQt6, bibliotecas de C++ ni tocar la consola en absoluto**.

El archivo compilado se encuentra en:
👉 `dist/BPSR_Module_Optimizer.exe`

---

## 🚀 ¿Cómo compartirlo y qué necesita tu amigo?

### 1. Enviar el archivo
Simplemente copia el archivo `BPSR_Module_Optimizer.exe` de la carpeta `dist/` y envíaselo por cualquier medio (Discord, Telegram, Google Drive, OneDrive, Mega, etc.).

### 2. Ejecución directa (Sin Consola)
Tu amigo solo tiene que:
1. Guardar el archivo `BPSR_Module_Optimizer.exe` en cualquier carpeta de su computadora (por ejemplo, una carpeta llamada "BPSR Optimizer" en su Escritorio).
2. Hacer doble clic sobre él.
3. ¡Y listo! Se abrirá la interfaz gráfica directamente.

### 3. Cargar e Importar Módulos (Requisito de Npcap)
Como la aplicación lee los paquetes de red del juego para capturar tus módulos automáticamente, **es necesario que el sistema tenga instalado Npcap** (el controlador de red estándar para captura de paquetes en Windows):
* Si tu amigo ya juega o usa herramientas que capturan red (como Wireshark), es probable que ya lo tenga.
* Si no lo tiene, puede descargarlo e instalarlo de manera gratuita y segura en menos de un minuto desde la página oficial:
  👉 **[https://npcap.com/](https://npcap.com/)** (se descarga el "Npcap Installer" y se instala con las opciones por defecto).
* **Nota:** Si no tiene Npcap, el programa no podrá realizar la captura en vivo, pero aun así podrá abrirse y usar un archivo de datos offline `modules.vdata` preexistente si se coloca en la misma carpeta.

### 4. ¿Cómo funciona el guardado de datos (`modules.vdata`)?
La primera vez que tu amigo haga la captura de red (cambiando de canal, teletransportándose o volviendo a iniciar sesión en el juego), el programa guardará automáticamente un archivo llamado `modules.vdata` en la **misma carpeta** donde esté el ejecutable.
* En las siguientes ejecuciones, el programa detectará ese archivo y cargará sus datos inmediatamente de forma offline.
* Si quiere actualizar su inventario, solo tiene que darle a "Calculate" y volver a hacer un cambio de canal en el juego para que capture los nuevos datos de red.

import customtkinter as ctk
import tkinter.filedialog as filedialog
import math
import random
import re
from PIL import ImageGrab, ImageFilter, ImageEnhance

# ==============================================================================
# LÓGICA MATEMÁTICA RSA
# ==============================================================================
def is_prime(num):
    if num < 2: return False
    for i in range(2, int(math.sqrt(num)) + 1):
        if num % i == 0: return False
    return True

def extended_gcd(a, b):
    if a == 0: return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(e, phi):
    gcd, x, y = extended_gcd(e, phi)
    if gcd != 1: return None
    return (x % phi + phi) % phi

# ==============================================================================
# CONFIGURACIÓN PRINCIPAL
# ==============================================================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==============================================================================
# CLASE PRINCIPAL DE LA APLICACIÓN
# ==============================================================================
class CriptoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuración de la Ventana ---
        self.title("CriptoRSA - Desktop Edition")
        self.geometry("1300x730")
        self.minsize(1100, 680)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Estado de la Aplicación ---
        self.current_keys = {"n": 0, "e": 0, "d": 0}
        self.str_log_gen = ""
        self.str_log_e = ""
        self.str_log_d = ""

        # --- Construcción de la Interfaz ---
        self._build_header()
        self._build_panel_console()
        self._build_panel_keys()
        self._build_panel_encrypt()
        self._build_panel_decrypt()

    # --------------------------------------------------------------------------
    # CONSTRUCCIÓN DE LA INTERFAZ (UI BUILDERS)
    # --------------------------------------------------------------------------
    def _build_header(self):
        self.lbl_title = ctk.CTkLabel(self, text="🔒 CriptoRSA", font=ctk.CTkFont(family="Outfit", size=32, weight="bold"))
        self.lbl_title.grid(row=0, column=0, columnspan=4, pady=(20, 10))

        self.btn_theme = ctk.CTkButton(self, text="☼", width=36, height=36, corner_radius=8,
                                       fg_color=("gray86", "gray17"), hover_color=("gray75", "gray25"), 
                                       text_color=("black", "white"), font=ctk.CTkFont(size=20), 
                                       command=self.toggle_theme)
        self.btn_theme.place(x=20, y=20)

    def _build_panel_keys(self):
        self.frame_keys = ctk.CTkFrame(self, corner_radius=15)
        self.frame_keys.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")
        
        ctk.CTkLabel(self.frame_keys, text="Generar Claves", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        # Primos
        frame_primes_lbl = ctk.CTkFrame(self.frame_keys, fg_color="transparent")
        frame_primes_lbl.pack(fill="x", padx=20)
        ctk.CTkLabel(frame_primes_lbl, text="Ingresa dos primos:").pack(side="left")
        self.btn_rand_primes = ctk.CTkButton(frame_primes_lbl, text="🎲 Auto", width=60, height=24, corner_radius=4, fg_color=("#f3e8ff", "#4c1d95"), hover_color=("#e9d5ff", "#581c87"), text_color=("black", "white"), border_width=1, border_color="#a855f7", command=self.generate_random_primes)
        self.btn_rand_primes.pack(side="right")

        self.entry_p = ctk.CTkEntry(self.frame_keys, placeholder_text="Primo p", height=40)
        self.entry_p.pack(pady=(5, 10), padx=20, fill="x")
        self.entry_q = ctk.CTkEntry(self.frame_keys, placeholder_text="Primo q", height=40)
        self.entry_q.pack(pady=(5, 10), padx=20, fill="x")

        # Botón Generar
        self.btn_gen = ctk.CTkButton(self.frame_keys, text="Generar Par de Claves", height=45, fg_color="#a855f7", hover_color="#9333ea", command=self.generate_keys)
        self.btn_gen.pack(pady=15, padx=20, fill="x")

        # Resultados de n y phi
        self.lbl_n = ctk.CTkLabel(self.frame_keys, text="Módulo (n): -", font=ctk.CTkFont(family="Courier", size=13))
        self.lbl_n.pack(pady=2)
        self.lbl_phi = ctk.CTkLabel(self.frame_keys, text="Euler φ(n): -", font=ctk.CTkFont(family="Courier", size=13))
        self.lbl_phi.pack(pady=2)
        self.lbl_security = ctk.CTkLabel(self.frame_keys, text="Seguridad: -", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_security.pack(pady=(2, 10))
        
        # Selección interactiva
        self.lbl_sel_e = ctk.CTkLabel(self.frame_keys, text="Seleccionar Exponente Pública (e):", font=ctk.CTkFont(size=13))
        self.lbl_sel_e.pack(anchor="w", padx=20, pady=(5,0))
        self.combo_e = ctk.CTkComboBox(self.frame_keys, values=[], command=self.on_e_select, state="disabled")
        self.combo_e.pack(padx=20, pady=2, fill="x")

        self.lbl_sel_d = ctk.CTkLabel(self.frame_keys, text="Seleccionar Clave Privada (d):", font=ctk.CTkFont(size=13))
        self.lbl_sel_d.pack(anchor="w", padx=20, pady=(5,0))
        self.combo_d = ctk.CTkComboBox(self.frame_keys, values=[], command=self.on_d_select, state="disabled")
        self.combo_d.pack(padx=20, pady=2, fill="x")

        # Claves Finales
        self.lbl_e = ctk.CTkLabel(self.frame_keys, text="Pública (e): -", text_color="#3b82f6", font=ctk.CTkFont(family="Courier", size=14, weight="bold"))
        self.lbl_e.pack(pady=(10,2))
        self.lbl_d = ctk.CTkLabel(self.frame_keys, text="Privada (d): -", text_color="#ef4444", font=ctk.CTkFont(family="Courier", size=14, weight="bold"))
        self.lbl_d.pack(pady=2)

    def _build_panel_encrypt(self):
        self.frame_enc = ctk.CTkFrame(self, corner_radius=15)
        self.frame_enc.grid(row=1, column=2, padx=15, pady=15, sticky="nsew")

        ctk.CTkLabel(self.frame_enc, text="Cifrar Mensaje", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        # Mensaje Original
        frame_msg_lbl = ctk.CTkFrame(self.frame_enc, fg_color="transparent")
        frame_msg_lbl.pack(fill="x", padx=20)
        ctk.CTkLabel(frame_msg_lbl, text="Mensaje Original:").pack(side="left")
        self.btn_spy = ctk.CTkButton(frame_msg_lbl, text="⏳ Mensaje Espía", width=100, height=24, corner_radius=4, fg_color=("#dbeafe", "#1e3a8a"), hover_color=("#bfdbfe", "#1e40af"), text_color=("black", "white"), border_width=1, border_color="#3b82f6", command=self.generate_spy_message)
        self.btn_spy.pack(side="right")

        self.txt_plain = ctk.CTkTextbox(self.frame_enc, height=100, wrap="word")
        self.txt_plain.pack(pady=5, padx=20, fill="x")

        # Botón Cifrar
        self.btn_enc = ctk.CTkButton(self.frame_enc, text="🔒 Encriptar", height=45, fg_color="#3b82f6", hover_color="#2563eb", command=self.encrypt_message)
        self.btn_enc.pack(pady=20, padx=20, fill="x")

        # Resultado
        frame_res_lbl = ctk.CTkFrame(self.frame_enc, fg_color="transparent")
        frame_res_lbl.pack(fill="x", padx=20)
        ctk.CTkLabel(frame_res_lbl, text="Criptograma Resultante:").pack(side="left")
        self.btn_copy_cipher = ctk.CTkButton(frame_res_lbl, text="📋 Copiar", width=60, height=24, corner_radius=4, fg_color=("#e2e8f0", "#1e293b"), hover_color=("#cbd5e1", "#334155"), text_color=("black", "white"), border_width=1, border_color="#64748b", command=lambda: self.copy_to_clipboard(self.txt_cipher_out.get("0.0", "end-1c")))
        self.btn_copy_cipher.pack(side="right")
        self.btn_calc = ctk.CTkButton(frame_res_lbl, text="📊 Ver Cálculos", width=100, height=24, corner_radius=4, fg_color=("#d1fae5", "#064e3b"), hover_color=("#a7f3d0", "#065f46"), text_color=("black", "white"), border_width=1, border_color="#10b981", command=self.show_calculations)
        self.btn_calc.pack(side="right", padx=(0, 10))

        self.txt_cipher_out = ctk.CTkTextbox(self.frame_enc, height=110, text_color="#93c5fd", font=ctk.CTkFont(family="Courier"))
        self.txt_cipher_out.pack(pady=5, padx=20, fill="x")

        self.btn_save = ctk.CTkButton(self.frame_enc, text="💾 Guardar en Archivo", height=35, fg_color="#10b981", hover_color="#059669", command=self.save_to_file)
        self.btn_save.pack(pady=10, padx=20, fill="x")

    def _build_panel_decrypt(self):
        self.frame_dec = ctk.CTkFrame(self, corner_radius=15)
        self.frame_dec.grid(row=1, column=3, padx=15, pady=15, sticky="nsew")

        ctk.CTkLabel(self.frame_dec, text="Descifrar Mensaje", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        # Entrada de Criptograma
        frame_cipher_in_lbl = ctk.CTkFrame(self.frame_dec, fg_color="transparent")
        frame_cipher_in_lbl.pack(fill="x", padx=20)
        ctk.CTkLabel(frame_cipher_in_lbl, text="Criptograma:").pack(side="left")
        self.btn_load = ctk.CTkButton(frame_cipher_in_lbl, text="📂 Cargar Archivo", width=100, height=24, corner_radius=4, fg_color=("#fef3c7", "#78350f"), hover_color=("#fde68a", "#92400e"), text_color=("black", "white"), border_width=1, border_color="#f59e0b", command=self.load_from_file)
        self.btn_load.pack(side="right")
        
        self.txt_cipher_in = ctk.CTkTextbox(self.frame_dec, height=80, font=ctk.CTkFont(family="Courier"))
        self.txt_cipher_in.pack(pady=5, padx=20, fill="x")

        # Campos de Clave
        self.entry_n = ctk.CTkEntry(self.frame_dec, placeholder_text="Módulo (n)", height=40)
        self.entry_n.pack(pady=10, padx=20, fill="x")
        self.entry_d = ctk.CTkEntry(self.frame_dec, placeholder_text="Clave Privada (d)", height=40)
        self.entry_d.pack(pady=10, padx=20, fill="x")

        # Botón Descifrar
        self.btn_dec = ctk.CTkButton(self.frame_dec, text="🔓 Descifrar", height=45, fg_color="#ef4444", hover_color="#dc2626", command=self.decrypt_message)
        self.btn_dec.pack(pady=20, padx=20, fill="x")

        # Salida
        frame_out_lbl = ctk.CTkFrame(self.frame_dec, fg_color="transparent")
        frame_out_lbl.pack(fill="x", padx=20)
        ctk.CTkLabel(frame_out_lbl, text="Texto Recuperado:").pack(side="left")
        self.btn_copy_plain = ctk.CTkButton(frame_out_lbl, text="📋 Copiar", width=60, height=24, corner_radius=4, fg_color=("#e2e8f0", "#1e293b"), hover_color=("#cbd5e1", "#334155"), text_color=("black", "white"), border_width=1, border_color="#64748b", command=lambda: self.copy_to_clipboard(self.txt_plain_out.get("0.0", "end-1c")))
        self.btn_copy_plain.pack(side="right")

        self.txt_plain_out = ctk.CTkTextbox(self.frame_dec, height=100, font=ctk.CTkFont(size=16, weight="bold"), wrap="word")
        self.txt_plain_out.pack(pady=5, padx=20, fill="x")

    def _build_panel_console(self):
        self.frame_proc = ctk.CTkFrame(self, corner_radius=15)
        self.frame_proc.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")

        ctk.CTkLabel(self.frame_proc, text="Proceso Detallado", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        self.txt_console = ctk.CTkTextbox(self.frame_proc, font=ctk.CTkFont(size=13))
        self.txt_console.pack(padx=15, pady=5, fill="both", expand=True)
        self.txt_console.insert("0.0", "> Esperando generación de claves...\n")
        self.txt_console.configure(state="disabled")

    # --------------------------------------------------------------------------
    # LÓGICA DE EVENTOS PRINCIPALES
    # --------------------------------------------------------------------------
    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            ctk.set_appearance_mode("Light")
            self.btn_theme.configure(text="☾")
        else:
            ctk.set_appearance_mode("Dark")
            self.btn_theme.configure(text="☼")

    def generate_random_primes(self):
        def get_random_prime(min_val, max_val):
            while True:
                num = random.randint(min_val, max_val)
                if is_prime(num):
                    return num
        p = get_random_prime(50, 500)
        q = get_random_prime(50, 500)
        while p == q:
            q = get_random_prime(50, 500)
            
        self.entry_p.delete(0, 'end')
        self.entry_p.insert(0, str(p))
        self.entry_q.delete(0, 'end')
        self.entry_q.insert(0, str(q))

    def generate_keys(self):
        try:
            p_val = self.entry_p.get()
            q_val = self.entry_q.get()
            if not p_val or not q_val:
                self.show_message("Atención", "Ingresa ambos números primos.", "warning")
                return

            p = int(p_val)
            q = int(q_val)

            if not is_prime(p) or not is_prime(q):
                self.show_message("Error", "Ambos números deben ser primos válidos.", "error")
                return
            if p == q:
                self.show_message("Error", "p y q deben ser números primos diferentes.", "error")
                return

            n = p * q
            phi = (p - 1) * (q - 1)
            
            self.current_n = n
            self.current_phi = phi

            possible_e = []
            for i in range(3, phi, 2):
                if math.gcd(i, phi) == 1:
                    possible_e.append(i)
                    if len(possible_e) >= 20: break
            
            if not possible_e:
                self.show_message("Error", "No se encontró un exponente 'e' válido.", "error")
                return
                
            self.str_log_gen = (
                f"> Iniciando generación de claves ...\n\n"
                f"> Cálculo de n:\n  {p} * {q} = {n}\n\n"
                f"> Función totiente de Euler φ(n):\n  ({p}-1) * ({q}-1) = {phi}\n\n"
                f"> Posibles valores de e determinados:\n{possible_e}...\n\n"
            )
            self.str_log_e = ""
            self.str_log_d = ""
            self.update_console()

            # Actualizar interfaz simple
            self.lbl_n.configure(text=f"Módulo (n): {n}")
            self.lbl_phi.configure(text=f"Euler φ(n): {phi}")
            
            if n < 1000:
                self.lbl_security.configure(text="Seguridad: Muy Débil 🔴", text_color="#ef4444")
            elif n < 50000:
                self.lbl_security.configure(text="Seguridad: Moderada 🟡", text_color="#f59e0b")
            else:
                self.lbl_security.configure(text="Seguridad: Fuerte 🟢", text_color="#10b981")

            # Poblar y activar comboboxes
            self.combo_e.configure(values=[str(x) for x in possible_e], state="normal")
            self.combo_e.set(str(possible_e[0]))
            self.on_e_select(str(possible_e[0]))

        except ValueError:
            self.show_message("Error", "Por favor ingresa únicamente números enteros.", "error")

    def on_e_select(self, val):
        if not val or not hasattr(self, 'current_phi'): return
        e = int(val)
        
        self.str_log_e = (
            f"> Selección del exponente público e: {e}\n\n"
            f"> Determinación de d mediante Algoritmo Extendido de Euclides...\n\n"
        )
        
        d0 = mod_inverse(e, self.current_phi)
        if d0 is None: return
        
        possible_d = [str(d0 + k * self.current_phi) for k in range(5)]
        self.str_log_e += f"> Posibles valores de d determinados:\n{possible_d}\n\n"
        
        self.str_log_d = ""
        self.update_console()
        
        self.combo_d.configure(values=possible_d, state="normal")
        self.combo_d.set(possible_d[0])
        self.on_d_select(possible_d[0])

    def on_d_select(self, val):
        if not val: return
        e = int(self.combo_e.get())
        d = int(val)
        self.current_keys = {"n": self.current_n, "e": e, "d": d}

        self.str_log_d = f"> Selección de la clave privada d: {d}\n\n"
        self.update_console()

        self.lbl_e.configure(text=f"Pública (e): {e}")
        self.lbl_d.configure(text=f"Privada (d): {d}")

        self.entry_d.delete(0, 'end')
        self.entry_d.insert(0, str(d))
        self.entry_n.delete(0, 'end')
        self.entry_n.insert(0, str(self.current_n))

    def generate_spy_message(self):
        messages = [
            "El águila ha aterrizado en el nido.",
            "Nos vemos en el punto de extracción a las 0400.",
            "El paquete fue entregado sin contratiempos.",
            "Abortar misión. Repito, abortar misión.",
            "La llave está debajo de la maceta azul.",
            "Operación 'Sombra Nocturna' iniciada."
        ]
        self.txt_plain.delete("0.0", "end")
        self.txt_plain.insert("0.0", random.choice(messages))

    def encrypt_message(self):
        text = self.txt_plain.get("0.0", "end-1c")
        if not text:
            self.show_message("Atención", "Ingresa un mensaje para cifrar.", "warning")
            return
        if self.current_keys["n"] == 0:
            self.show_message("Atención", "Primero debes generar el par de claves en el Paso 1.", "warning")
            return

        n = self.current_keys["n"]
        e = self.current_keys["e"]

        self.last_encryption_trace = []
        cipher_array = []
        for char in text:
            m = ord(char)
            if m >= n:
                self.show_message("Error Matemático de RSA", 
                    f"El código del carácter '{char}' ({m}) es mayor o igual al módulo n ({n}).\n"
                    "RSA requiere que el tamaño del bloque sea estrictamente menor que el módulo.\n"
                    "¡Usa números primos más grandes!", "error")
                return
            c = pow(m, e, n)
            cipher_array.append(str(c))
            self.last_encryption_trace.append({
                "char": char,
                "m": m,
                "eq": f"{m}^{e} mod {n}",
                "c": c
            })
        
        cipher_str = ",".join(cipher_array)
        
        self.txt_cipher_out.delete("0.0", "end")
        self.txt_cipher_out.insert("0.0", cipher_str)
        
        self.txt_cipher_in.delete("0.0", "end")
        self.txt_cipher_in.insert("0.0", cipher_str)

    def decrypt_message(self):
        cipher_str = self.txt_cipher_in.get("0.0", "end-1c").strip()
        
        if not cipher_str:
            self.show_message("Atención", "No hay criptograma para descifrar.", "warning")
            return

        try:
            d = int(self.entry_d.get())
            n = int(self.entry_n.get())
        except ValueError:
            self.show_message("Error", "La clave privada y el módulo deben ser números válidos.", "error")
            return

        codes = cipher_str.split(",")
        plain = ""
        try:
            for code in codes:
                code = code.strip()
                if not code: continue
                c = int(code)
                m = pow(c, d, n)
                plain += chr(m)
            
            self.txt_plain_out.delete("0.0", "end")
            self.txt_plain_out.insert("0.0", plain)
        except Exception as err:
            self.show_message("Error de Descifrado", f"Ha ocurrido un error:\n{err}", "error")

    # --------------------------------------------------------------------------
    # UTILIDADES (ARCHIVOS Y PORTAPAPELES)
    # --------------------------------------------------------------------------
    def save_to_file(self):
        cipher_text = self.txt_cipher_out.get("0.0", "end-1c").strip()
        if not cipher_text:
            self.show_message("Atención", "No hay ningún mensaje cifrado para guardar.", "warning")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Guardar Criptograma y Clave Privada"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("--- MENSAJE CIFRADO (CRIPTOGRAMA) ---\n")
                    f.write(cipher_text + "\n\n")
                    f.write("--- CLAVE PRIVADA PARA DESCIFRAR ---\n")
                    f.write(f"Módulo (n): {self.current_keys['n']}\n")
                    f.write(f"Clave Privada (d): {self.current_keys['d']}\n")
                self.show_message("Éxito", "El archivo se ha guardado correctamente.\nCompártelo junto con la clave privada.", "success")
            except Exception as err:
                self.show_message("Error", f"No se pudo guardar el archivo:\n{err}", "error")

    def load_from_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Cargar Criptograma y Claves"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Extraer criptograma
                cipher_match = re.search(r"--- MENSAJE CIFRADO \(CRIPTOGRAMA\) ---\n(.*?)\n\n---", content, re.DOTALL)
                if cipher_match:
                    cipher_text = cipher_match.group(1).strip()
                    self.txt_cipher_in.delete("0.0", "end")
                    self.txt_cipher_in.insert("0.0", cipher_text)
                
                # Extraer n
                n_match = re.search(r"Módulo \(n\):\s*(\d+)", content)
                if n_match:
                    self.entry_n.delete(0, 'end')
                    self.entry_n.insert(0, n_match.group(1))
                    
                # Extraer d
                d_match = re.search(r"Clave Privada \(d\):\s*(\d+)", content)
                if d_match:
                    self.entry_d.delete(0, 'end')
                    self.entry_d.insert(0, d_match.group(1))
                    
                self.show_message("Éxito", "Archivo cargado correctamente.", "success")
            except Exception as err:
                self.show_message("Error", f"No se pudo leer el archivo:\n{err}", "error")

    def copy_to_clipboard(self, text):
        if text.strip():
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()
            self.show_message("Copiado", "Texto copiado al portapapeles exitosamente.", "success")

    # --------------------------------------------------------------------------
    # COMPONENTES VISUALES ADICIONALES (CONSOLA, MODALES)
    # --------------------------------------------------------------------------
    def update_console(self):
        self.txt_console.configure(state="normal")
        self.txt_console.delete("0.0", "end")
        
        if hasattr(self, 'str_log_gen') and self.str_log_gen:
            self.txt_console.insert("end", self.str_log_gen)
        if hasattr(self, 'str_log_e') and self.str_log_e:
            self.txt_console.insert("end", self.str_log_e)
        if hasattr(self, 'str_log_d') and self.str_log_d:
            self.txt_console.insert("end", self.str_log_d)
            
        self.txt_console.see("end")
        self.txt_console.configure(state="disabled")

    def show_calculations(self):
        if not hasattr(self, 'last_encryption_trace') or not self.last_encryption_trace:
            self.show_message("Información", "Primero debes encriptar un mensaje.", "info")
            return

        self.update_idletasks()
        
        x_root = self.winfo_rootx()
        y_root = self.winfo_rooty()
        w_main = self.winfo_width()
        h_main = self.winfo_height()

        # 1. Capa de oscurecimiento y desenfoque
        backdrop = ctk.CTkToplevel(self)
        backdrop.overrideredirect(True)
        backdrop.geometry(f"{w_main}x{h_main}+{x_root}+{y_root}")
        backdrop.transient(self)
        
        try:
            img = ImageGrab.grab(bbox=(x_root, y_root, x_root + w_main, y_root + h_main))
            img = img.filter(ImageFilter.GaussianBlur(radius=8))
            img = ImageEnhance.Brightness(img).enhance(0.4)
            
            bg_image = ctk.CTkImage(light_image=img, size=(w_main, h_main))
            bg_label = ctk.CTkLabel(backdrop, text="", image=bg_image)
            bg_label.pack(fill="both", expand=True)
            backdrop.bg_image = bg_image
        except Exception:
            backdrop.configure(fg_color="#050505")
            backdrop.attributes("-alpha", 0.75)

        # 2. Ventana modal real
        win = ctk.CTkToplevel(self)
        win.overrideredirect(True)
        win.transient(self)
        win.attributes("-topmost", True)
        win.configure(fg_color="#2b2b2b")
        
        win_w, win_h = 800, 450
        x_win = x_root + (w_main // 2) - (win_w // 2)
        y_win = y_root + (h_main // 2) - (win_h // 2)
        win.geometry(f"{win_w}x{win_h}+{x_win}+{y_win}")

        def sync_windows(event):
            if event.widget != self: return
            if not win.winfo_exists() or not backdrop.winfo_exists(): return
            x, y = self.winfo_rootx(), self.winfo_rooty()
            w, h = self.winfo_width(), self.winfo_height()
            backdrop.geometry(f"{w}x{h}+{x}+{y}")
            win.geometry(f"{win_w}x{win_h}+{x + (w // 2) - (win_w // 2)}+{y + (h // 2) - (win_h // 2)}")

        bind_id = self.bind("<Configure>", sync_windows, add="+")

        def on_focus(event):
            if event.widget == self:
                if backdrop.winfo_exists(): backdrop.lift()
                if win.winfo_exists(): win.lift()

        focus_bind_id = self.bind("<FocusIn>", on_focus, add="+")

        backdrop.lift()
        win.lift()
        win.focus()

        # 3. Frame principal
        main_frame = ctk.CTkFrame(win, border_width=2, border_color="#3f3f46", corner_radius=0, fg_color="#2b2b2b")
        main_frame.pack(fill="both", expand=True)

        lbl_title = ctk.CTkLabel(main_frame, text="📊 Trazabilidad de Cifrado (Decimal a Criptograma)", font=ctk.CTkFont(size=20, weight="bold"), text_color="#4ade80")
        lbl_title.pack(pady=(20, 10))

        table_container = ctk.CTkFrame(main_frame, border_width=1, border_color="#3f3f46", corner_radius=10, fg_color="#242424")
        table_container.pack(padx=30, pady=10, fill="both", expand=True)

        header_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=(2, 18), pady=(10, 5))

        scroll_frame = ctk.CTkScrollableFrame(table_container, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=2, pady=2)

        for i in range(4):
            header_frame.grid_columnconfigure(i, weight=1)
            scroll_frame.grid_columnconfigure(i, weight=1)

        headers = ["Carácter", "Unicode (m)", "Ecuación (m^e mod n)", "Cifrado (c)"]
        for i, h in enumerate(headers):
            lbl = ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(weight="bold", size=14))
            lbl.grid(row=0, column=i, sticky="nsew")

        for row_idx, row_data in enumerate(self.last_encryption_trace):
            real_row = row_idx * 2
            line = ctk.CTkFrame(scroll_frame, height=1, fg_color="#3f3f46")
            line.grid(row=real_row, column=0, columnspan=4, sticky="ew", padx=10)

            ctk.CTkLabel(scroll_frame, text=row_data["char"], font=ctk.CTkFont(weight="bold", size=14)).grid(row=real_row+1, column=0, pady=10)
            ctk.CTkLabel(scroll_frame, text=str(row_data["m"]), text_color="#fbbf24", font=ctk.CTkFont(weight="bold", size=13)).grid(row=real_row+1, column=1, pady=10)
            ctk.CTkLabel(scroll_frame, text=row_data["eq"], text_color="#a1a1aa", font=ctk.CTkFont(family="Courier", size=13)).grid(row=real_row+1, column=2, pady=10)
            ctk.CTkLabel(scroll_frame, text=str(row_data["c"]), text_color="#3b82f6", font=ctk.CTkFont(weight="bold", size=14)).grid(row=real_row+1, column=3, pady=10)

        def close_modal():
            try:
                self.unbind("<Configure>", bind_id)
                self.unbind("<FocusIn>", focus_bind_id)
            except: pass
            win.destroy()
            backdrop.destroy()
            self.focus_force()

        btn_close = ctk.CTkButton(main_frame, text="Cerrar Tabla", height=45, font=ctk.CTkFont(weight="bold", size=15), fg_color="#4b5563", hover_color="#374151", command=close_modal)
        btn_close.pack(padx=30, pady=(10, 25), fill="x")

    def show_message(self, title, message, icon_type="info"):
        msg_box = ctk.CTkToplevel(self)
        msg_box.title(title)
        
        width, height, wrap_len = 340, 145, 220
        if len(message) > 100 or message.count('\n') > 1:
            width, height, wrap_len = 400, 180, 280
        
        msg_box.update_idletasks() 
        x = self.winfo_x() + (self.winfo_width() // 2) - (width // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (height // 2)
        msg_box.geometry(f"{width}x{height}+{x}+{y}")
        
        msg_box.resizable(False, False)
        msg_box.transient(self)
        msg_box.grab_set()

        msg_box.grid_columnconfigure(1, weight=1)
        msg_box.grid_rowconfigure(0, weight=1)

        themes = {
            "info": {"color": "#3b82f6", "hover": "#2563eb", "icon": "ℹ️"},
            "warning": {"color": "#f59e0b", "hover": "#d97706", "icon": "⚠️"},
            "error": {"color": "#ef4444", "hover": "#dc2626", "icon": "❌"},
            "success": {"color": "#10b981", "hover": "#059669", "icon": "✅"}
        }
        
        theme = themes.get(icon_type, themes["info"])

        icon_label = ctk.CTkLabel(msg_box, text=theme["icon"], font=ctk.CTkFont(size=35), text_color=theme["color"])
        icon_label.grid(row=0, column=0, padx=(20, 5), pady=(20, 10), sticky="e")

        msg_label = ctk.CTkLabel(msg_box, text=message, font=ctk.CTkFont(size=13), wraplength=wrap_len, justify="left", anchor="w")
        msg_label.grid(row=0, column=1, padx=(10, 20), pady=(20, 10), sticky="w")

        btn_ok = ctk.CTkButton(msg_box, text="Aceptar", width=100, height=32, fg_color=theme["color"], hover_color=theme["hover"], command=msg_box.destroy)
        btn_ok.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        msg_box.focus_set()
        self.wait_window(msg_box)

if __name__ == "__main__":
    app = CriptoApp()
    app.mainloop()


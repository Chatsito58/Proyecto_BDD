import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from utils import mostrar_error, mostrar_notificacion
import re
from ttkthemes import ThemedTk
from tkinter import filedialog
from mysql.connector import Error, InterfaceError
from conexion.conexion import ConexionBD


class MySQLApp:
    def __init__(self, root, conexion: ConexionBD | None = None):
        self.sql_keywords = [
            "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES", "UPDATE", "SET",
            "DELETE", "JOIN", "INNER", "LEFT", "RIGHT", "ON", "GROUP BY", "ORDER BY",
            "LIMIT", "DISTINCT", "AS", "AND", "OR", "NOT", "NULL"
        ]

        self.root = root
        self.root.title("🌐 Panel de Consultas MySQL")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2a2a2a")
        self.historial_consultas = []

        self.configurar_estilo()
        self.conexion = conexion or ConexionBD()

        self.crear_encabezado()
        self.crear_tabs()
        self.crear_barra_estado()

    def _normalizar_query(self, query: str) -> str:
        """Inserta espacios entre palabras clave y símbolos para evitar errores."""
        # Separar operadores y paréntesis
        query = re.sub(r"([(),=*<>])", r" \1 ", query)
        # Agregar espacios en keywords importantes
        keywords = (
            r"SELECT|FROM|WHERE|INSERT|INTO|VALUES|UPDATE|SET|DELETE|JOIN|INNER|"
            r"LEFT|RIGHT|ON|GROUP|BY|ORDER|LIMIT|DISTINCT|AS|AND|OR|NOT|NULL"
        )
        query = re.sub(fr"(?i)\b({keywords})\b", r" \1 ", query)
        return re.sub(r"\s+", " ", query).strip()

    def mostrar_tablas(self):
        """Mostrar todas las tablas de la base de datos en el Treeview."""
        try:
            columnas, filas = self.conexion.ejecutar_con_columnas("SHOW TABLES")
        except InterfaceError as exc:
            mostrar_error(exc)
            return
        except Error as e:
            mostrar_error(e)
            return

        self.mostrar_resultados(columnas, filas)
        self.tab_control.select(self.tab_resultado)
    def describir_tabla(self, tabla):
        try:
            columnas, filas = self.conexion.ejecutar_con_columnas(
                f"DESCRIBE {tabla}"
            )
            self.mostrar_resultados(columnas, filas)
            self.tab_control.select(self.tab_resultado)
        except InterfaceError as exc:
            mostrar_error(exc)
        except Error as e:
            mostrar_error(e)


    def mostrar_autocompletado(self, event=None):
        if hasattr(self, 'popup_menu'):
            self.popup_menu.destroy()

        # Obtener la palabra parcial donde está el cursor
        index = self.query_text.index(tk.INSERT)
        linea, columna = map(int, index.split('.'))
        texto_linea = self.query_text.get(f"{linea}.0", f"{linea}.end")
        palabra_actual = ''
        for c in reversed(texto_linea[:columna]):
            if c.isalnum() or c == '_':
                palabra_actual = c + palabra_actual
            else:
                break

        if not palabra_actual:
            return

        sugerencias = [kw for kw in self.sql_keywords if kw.startswith(palabra_actual.upper())]

        if not sugerencias:
            return

        # Crear menú emergente
        self.popup_menu = tk.Toplevel(self.root)
        self.popup_menu.wm_overrideredirect(True)

        x, y = self.query_text.winfo_rootx(), self.query_text.winfo_rooty()
        bbox = self.query_text.bbox(tk.INSERT)
        if bbox:
            x += bbox[0]
            y += bbox[1] + bbox[3]

        self.popup_menu.geometry(f"+{x}+{y}")

        listbox = tk.Listbox(self.popup_menu, height=min(len(sugerencias), 6), font=("Courier", 10))
        listbox.pack()
        for s in sugerencias:
            listbox.insert(tk.END, s)

        listbox.focus_set()

        def insertar_seleccion(event=None):
            seleccion = listbox.get(tk.ACTIVE)
            self.query_text.delete(f"{index} - {len(palabra_actual)} chars", index)
            self.query_text.insert(index, seleccion + " ")
            self.popup_menu.destroy()

        listbox.bind("<Return>", insertar_seleccion)
        listbox.bind("<Double-Button-1>", insertar_seleccion)
        listbox.bind("<Escape>", lambda e: self.popup_menu.destroy())


    def configurar_estilo(self):
        estilo = ttk.Style(self.root)
        estilo.theme_use("arc")
        estilo.configure("TNotebook.Tab", font=("Segoe UI", 11, "bold"), padding=[15, 10])
        estilo.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        estilo.configure("Treeview", font=("Segoe UI", 10), rowheight=28)

    def crear_encabezado(self):
        encabezado = ttk.Frame(self.root, padding=10)
        encabezado.pack(fill="x", padx=15, pady=(10, 5))

        ttk.Label(
            encabezado,
            text="🛠️ Consultas a Base de Datos MySQL",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="center")

        ttk.Label(
            encabezado,
            text="Ejecuta instrucciones SQL y visualiza los resultados de forma clara y rápida",
            font=("Segoe UI", 11),
            foreground="#666"
        ).pack(anchor="center", pady=(5, 0))

    def crear_tabs(self):
        self.tab_control = ttk.Notebook(self.root)
        self.tab_consulta = ttk.Frame(self.tab_control, padding=20)
        self.tab_resultado = ttk.Frame(self.tab_control, padding=10)

        self.tab_control.add(self.tab_consulta, text="📝 Consulta SQL")
        self.tab_control.add(self.tab_resultado, text="📊 Resultados")
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=5)

        self.crear_tab_consulta()
        self.crear_tab_resultado()

    def crear_tab_consulta(self):
        # Etiqueta
        ttk.Label(self.tab_consulta, text="📄 Ingresar Consulta:", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        # Historial desplegable
        historial_frame = ttk.Frame(self.tab_consulta)
        historial_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(historial_frame, text="🕓 Historial:", font=("Segoe UI", 10)).pack(side="left")
        self.combo_historial = ttk.Combobox(historial_frame, state="readonly", width=80)
        self.combo_historial.pack(side="left", padx=10)

        self.combo_historial.bind("<<ComboboxSelected>>", self.cargar_historial)

        # Área de texto
        self.query_text = scrolledtext.ScrolledText(
            self.tab_consulta,
            height=12,
            font=("Consolas", 11),
            bg="#ffffff",
            relief="flat",
            borderwidth=1
        )
        self.query_text.pack(fill="both", expand=True, pady=(0, 10))
        self.query_text.bind("<Control-Key-space>", self.mostrar_autocompletado)

        # Botones
        botones = ttk.Frame(self.tab_consulta)
        botones.pack(anchor="e", pady=(5, 0))

        ttk.Button(botones, text="🧹 Limpiar", command=self.limpiar_consulta).pack(side="right", padx=5)
        ttk.Button(botones, text="▶ Ejecutar Consulta", command=self.ejecutar_consulta).pack(side="right", padx=5)
        frame_botones_secundarios = ttk.Frame(self.tab_consulta)
        frame_botones_secundarios.pack(pady=5)
        ttk.Button(frame_botones_secundarios, text="📥 Cargar consulta", command=self.cargar_consulta).pack(side="left", padx=5)
        ttk.Button(frame_botones_secundarios, text="📤 Guardar consulta", command=self.guardar_consulta).pack(side="left", padx=5)
        ttk.Button(frame_botones_secundarios, text="📋 Ver estructura de tabla", command=self.mostrar_tablas).pack(side="left", padx=5)


    def guardar_consulta(self):
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Consulta vacía", "No hay consulta para guardar.")
            return

        archivo = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("Archivos SQL", "*.sql"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                with open(archivo, "w", encoding="utf-8") as f:
                    f.write(query)
                mostrar_notificacion("Guardado", f"Consulta guardada en:\n{archivo}")
            except Exception as e:
                mostrar_error(e)

    def cargar_consulta(self):
        archivo = filedialog.askopenfilename(
            filetypes=[("Archivos SQL", "*.sql"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    contenido = f.read()
                    self.query_text.delete("1.0", tk.END)
                    self.query_text.insert(tk.END, contenido)
                mostrar_notificacion("Carga exitosa", "Consulta cargada correctamente.")
            except Exception as e:
                mostrar_error(e)


    def crear_tab_resultado(self):
        self.tree = ttk.Treeview(self.tab_resultado, show="headings", style="Treeview")
        self.tree.pack(expand=True, fill="both", padx=5, pady=5)

        vsb = ttk.Scrollbar(self.tab_resultado, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tab_resultado, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

    def crear_barra_estado(self):
        self.status_var = tk.StringVar()
        self.status_var.set("ℹ️ Esperando consulta...")

        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            relief="sunken",
            padding=6,
            background="#e9eef2"
        )
        status_bar.pack(fill="x", side="bottom", padx=1)

    def ejecutar_consulta(self):
        query = self.query_text.get("1.0", tk.END).strip()
        query = self._normalizar_query(query)

        if not query:
            messagebox.showwarning("⚠ Consulta vacía", "Debes escribir una consulta SQL.")
            return

        # Guardar en historial
        self.actualizar_historial(query)

        if not self.conexion.conn or not self.conexion.conn.is_connected():
            self.conexion.conectar()
        if not self.conexion.conn or not self.conexion.conn.is_connected():
            mostrar_error(Exception("No hay conexión a la base de datos."))
            return

        try:
            columnas, filas = self.conexion.ejecutar_con_columnas(query)
        
            if query.lower().startswith("select"):
                self.mostrar_resultados(columnas, filas)
                self.status_var.set(f"✅ {len(filas)} filas recuperadas.")
                self.tab_control.select(self.tab_resultado)
            else:
                mostrar_notificacion("✅ Éxito", "Consulta ejecutada correctamente.")
                self.status_var.set("✅ Consulta ejecutada con éxito.")
        except InterfaceError as exc:
            mostrar_error(exc)
            self.status_var.set("❌ Error al ejecutar la consulta.")
        except Error as e:
            msg = str(e)
            if "doesn't exist" in msg:
                msg = "La tabla no existe"
            elif "syntax" in msg.lower():
                msg = "Error de sintaxis SQL"
            mostrar_error(Exception(msg))
            self.status_var.set("❌ Error al ejecutar la consulta.")

    def mostrar_resultados(self, columnas, filas):
        self.tree.delete(*self.tree.get_children())
        if filas:
            self.tree["columns"] = columnas

            for col in columnas:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", stretch=True, width=140)

            for i, fila in enumerate(filas):
                color = "#f0f8ff" if i % 2 == 0 else "#ffffff"
                self.tree.insert("", tk.END, values=fila, tags=(f"fila{i}",))
                self.tree.tag_configure(f"fila{i}", background=color)
        else:
            self.tree["columns"] = ["Resultado"]
            self.tree.heading("Resultado", text="Resultado")
            self.tree.column("Resultado", anchor="center", stretch=True)
            self.tree.insert("", tk.END, values=("Consulta realizada, sin resultados.",))

    def limpiar_consulta(self):
        self.query_text.delete("1.0", tk.END)
        self.status_var.set("ℹ️ Área de consulta vacía.")

    def actualizar_historial(self, nueva):
        if not self.historial_consultas or self.historial_consultas[-1] != nueva:
            self.historial_consultas.append(nueva)
            self.historial_consultas = self.historial_consultas[-10:]  # solo los últimos 10
            self.combo_historial['values'] = self.historial_consultas

    def cargar_historial(self, event):
        seleccionada = self.combo_historial.get()
        self.query_text.delete("1.0", tk.END)
        self.query_text.insert(tk.END, seleccionada)


# ========== Ejecutar la app ==========
def run_gui() -> None:
    """Lanzar la interfaz gráfica de consultas."""
    root = ThemedTk(theme="arc")
    app = MySQLApp(root, ConexionBD())
    root.mainloop()


def main() -> None:
    """Punto de entrada en consola con autenticación por roles."""
    from getpass import getpass

    from auth import login
    from cliente import menu_cliente
    from empleado import menu_empleado
    from gerente import menu_gerente

    conexion = ConexionBD()
    print("Sistema de Alquiler de Vehículos")
    for _ in range(3):
        correo = input("Correo: ").strip()
        password = getpass("Contraseña: ")
        rol = login(conexion, correo, password)
        if rol:
            break
        print("Credenciales inválidas. Intente nuevamente.\n")
    else:
        print("Demasiados intentos fallidos")
        return

    if rol == "cliente":
        menu_cliente(conexion, correo)
    elif rol == "empleado":
        menu_empleado(conexion, correo)
    else:  # gerente o admin
        menu_gerente(conexion, correo, es_admin=(rol == "admin"))


if __name__ == "__main__":
    main()

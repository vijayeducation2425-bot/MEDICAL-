import sqlite3
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk


DB_PATH = "outpatient_records.db"

COLORS = {
    "navy": "#123047",
    "teal": "#0f766e",
    "teal_light": "#dff5f0",
    "ink": "#18252f",
    "muted": "#667784",
    "line": "#d7e0e5",
    "canvas": "#f4f7f8",
    "white": "#ffffff",
    "warning": "#b45309",
}


class OutpatientRecordsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CareLedger | Outpatient Records")
        self.geometry("1280x780")
        self.minsize(980, 650)
        self.configure(bg=COLORS["canvas"])
        self.selected_id = None
        self.vars = {}
        self.text_widgets = {}
        self.setup_database()
        self.setup_styles()
        self.build_shell()
        self.refresh_patients()

    def setup_database(self):
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_number TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    date_of_birth TEXT,
                    sex TEXT,
                    phone TEXT,
                    address TEXT,
                    occupation TEXT,
                    emergency_contact TEXT,
                    visit_date TEXT,
                    chief_complaint TEXT,
                    case_history TEXT,
                    examination TEXT,
                    investigations TEXT,
                    diagnosis TEXT,
                    treatment TEXT,
                    follow_up TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )"""
            )

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["canvas"])
        style.configure("Card.TFrame", background=COLORS["white"])
        style.configure("TLabel", background=COLORS["canvas"], foreground=COLORS["ink"], font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=COLORS["canvas"], foreground=COLORS["muted"], font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=COLORS["canvas"], foreground=COLORS["navy"], font=("Georgia", 24, "bold"))
        style.configure("Section.TLabel", background=COLORS["white"], foreground=COLORS["navy"], font=("Segoe UI", 12, "bold"))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8))
        style.configure("Primary.TButton", background=COLORS["teal"], foreground=COLORS["white"], borderwidth=0)
        style.map("Primary.TButton", background=[("active", "#0b5f59")])
        style.configure("Treeview", rowheight=38, font=("Segoe UI", 10), background=COLORS["white"], fieldbackground=COLORS["white"], borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), foreground=COLORS["muted"])
        style.map("Treeview", background=[("selected", COLORS["teal_light"])], foreground=[("selected", COLORS["ink"])])

    def build_shell(self):
        header = tk.Frame(self, bg=COLORS["navy"], height=82)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="CARELEDGER", bg=COLORS["navy"], fg="#8ce1d0", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=28, pady=(14, 0))
        tk.Label(header, text="Outpatient records", bg=COLORS["navy"], fg=COLORS["white"], font=("Georgia", 20, "bold")).pack(anchor="w", padx=28)

        content = tk.Frame(self, bg=COLORS["canvas"])
        content.pack(fill="both", expand=True, padx=24, pady=22)
        content.columnconfigure(0, weight=1, minsize=350)
        content.columnconfigure(1, weight=2, minsize=570)
        content.rowconfigure(1, weight=1)

        title_row = tk.Frame(content, bg=COLORS["canvas"])
        title_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        title_row.columnconfigure(0, weight=1)
        ttk.Label(title_row, text="Patient registry", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(title_row, text="Secure local workspace  |  " + date.today().strftime("%d %b %Y"), style="Muted.TLabel").grid(row=0, column=1, sticky="e", padx=(0, 4))

        self.build_registry(content)
        self.build_editor(content)

    def build_registry(self, parent):
        card = tk.Frame(parent, bg=COLORS["white"], highlightbackground=COLORS["line"], highlightthickness=1)
        card.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        card.rowconfigure(2, weight=1)
        card.columnconfigure(0, weight=1)
        top = tk.Frame(card, bg=COLORS["white"])
        top.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 12))
        top.columnconfigure(0, weight=1)
        tk.Label(top, text="PATIENTS", bg=COLORS["white"], fg=COLORS["muted"], font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w")
        self.count_label = tk.Label(top, text="0 records", bg=COLORS["white"], fg=COLORS["teal"], font=("Segoe UI", 9, "bold"))
        self.count_label.grid(row=0, column=1, sticky="e")
        search_frame = tk.Frame(card, bg=COLORS["white"])
        search_frame.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
        search_frame.columnconfigure(0, weight=1)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_patients())
        search = tk.Entry(search_frame, textvariable=self.search_var, relief="flat", bg="#f0f4f5", fg=COLORS["ink"], font=("Segoe UI", 10), insertbackground=COLORS["teal"])
        search.grid(row=0, column=0, sticky="ew", ipady=9, padx=(0, 8))
        ttk.Button(search_frame, text="+ New patient", style="Primary.TButton", command=self.new_patient).grid(row=0, column=1)
        tree_frame = tk.Frame(card, bg=COLORS["white"])
        tree_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(tree_frame, columns=("number", "name", "visit"), show="headings", selectmode="browse")
        self.tree.heading("number", text="ID")
        self.tree.heading("name", text="PATIENT")
        self.tree.heading("visit", text="LAST VISIT")
        self.tree.column("number", width=82, anchor="w")
        self.tree.column("name", width=170, anchor="w")
        self.tree.column("visit", width=95, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self.load_selected)

    def build_editor(self, parent):
        self.editor = tk.Frame(parent, bg=COLORS["white"], highlightbackground=COLORS["line"], highlightthickness=1)
        self.editor.grid(row=1, column=1, sticky="nsew")
        self.editor.rowconfigure(1, weight=1)
        self.editor.columnconfigure(0, weight=1)
        self.editor_header = tk.Frame(self.editor, bg=COLORS["white"])
        self.editor_header.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 10))
        self.editor_header.columnconfigure(0, weight=1)
        self.patient_title = tk.Label(self.editor_header, text="Select a patient", bg=COLORS["white"], fg=COLORS["navy"], font=("Georgia", 18, "bold"))
        self.patient_title.grid(row=0, column=0, sticky="w")
        self.status_label = tk.Label(self.editor_header, text="", bg=COLORS["white"], fg=COLORS["teal"], font=("Segoe UI", 9, "bold"))
        self.status_label.grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.save_button = ttk.Button(self.editor_header, text="Save record", style="Primary.TButton", command=self.save_record, state="disabled")
        self.save_button.grid(row=0, column=1, rowspan=2, sticky="e")

        self.notebook = ttk.Notebook(self.editor)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        self.add_demographics_tab()
        self.add_clinical_tab()

    def add_demographics_tab(self):
        tab = tk.Frame(self.notebook, bg=COLORS["white"])
        tab.columnconfigure(1, weight=1)
        tab.columnconfigure(3, weight=1)
        self.notebook.add(tab, text="Demographics")
        fields = [("patient_number", "Patient ID", 0, 0), ("full_name", "Full name", 0, 2), ("date_of_birth", "Date of birth", 1, 0), ("sex", "Sex", 1, 2), ("phone", "Phone", 2, 0), ("occupation", "Occupation", 2, 2), ("address", "Address", 3, 0), ("emergency_contact", "Emergency contact", 3, 2)]
        for key, label, row, col in fields:
            tk.Label(tab, text=label.upper(), bg=COLORS["white"], fg=COLORS["muted"], font=("Segoe UI", 8, "bold")).grid(row=row * 2, column=col, sticky="w", padx=(18 if col == 0 else 10, 8), pady=(18 if row == 0 else 10, 4))
            if key == "sex":
                widget = ttk.Combobox(tab, textvariable=self.make_var(key), values=("Female", "Male", "Other"), state="readonly")
            else:
                widget = tk.Entry(tab, textvariable=self.make_var(key), relief="flat", bg="#f4f7f8", fg=COLORS["ink"], font=("Segoe UI", 10))
            widget.grid(row=row * 2 + 1, column=col, columnspan=1, sticky="ew", padx=(18 if col == 0 else 10, 18 if col == 2 else 10), ipady=7)

    def add_clinical_tab(self):
        tab = tk.Frame(self.notebook, bg=COLORS["white"])
        tab.columnconfigure(1, weight=1)
        self.notebook.add(tab, text="Clinical record")
        fields = [("visit_date", "Visit date (YYYY-MM-DD)"), ("chief_complaint", "Chief complaint"), ("case_history", "Case history"), ("examination", "Examination findings"), ("investigations", "Investigations"), ("diagnosis", "Diagnosis"), ("treatment", "Treatment plan"), ("follow_up", "Follow-up / advice")]
        for row, (key, label) in enumerate(fields):
            tk.Label(tab, text=label.upper(), bg=COLORS["white"], fg=COLORS["muted"], font=("Segoe UI", 8, "bold")).grid(row=row, column=0, sticky="nw", padx=(18, 14), pady=(16 if row == 0 else 10, 4))
            if key in {"chief_complaint", "case_history", "examination", "investigations", "diagnosis", "treatment", "follow_up"}:
                widget = tk.Text(tab, height=2 if key in {"chief_complaint", "diagnosis"} else 3, wrap="word", relief="flat", bg="#f4f7f8", fg=COLORS["ink"], font=("Segoe UI", 10), padx=8, pady=7)
                self.text_widgets[key] = widget
            else:
                widget = tk.Entry(tab, textvariable=self.make_var(key), relief="flat", bg="#f4f7f8", fg=COLORS["ink"], font=("Segoe UI", 10))
            widget.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=(16 if row == 0 else 10, 4))

    def make_var(self, key):
        self.vars[key] = tk.StringVar()
        return self.vars[key]

    def refresh_patients(self):
        if not hasattr(self, "tree"):
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = self.search_var.get().strip() if hasattr(self, "search_var") else ""
        with sqlite3.connect(DB_PATH) as connection:
            rows = connection.execute("SELECT id, patient_number, full_name, visit_date FROM patients WHERE full_name LIKE ? OR patient_number LIKE ? ORDER BY full_name", (f"%{query}%", f"%{query}%")).fetchall()
        for row in rows:
            self.tree.insert("", "end", iid=str(row[0]), values=(row[1], row[2], row[3] or "-"))
        self.count_label.config(text=f"{len(rows)} record" + ("s" if len(rows) != 1 else ""))

    def load_selected(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            return
        self.selected_id = int(selection[0])
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.execute("SELECT * FROM patients WHERE id = ?", (self.selected_id,))
            row = cursor.fetchone()
            columns = [description[0] for description in cursor.description]
        if not row:
            return
        record = dict(zip(columns, row))
        for key, value in self.vars.items():
            value.set(record.get(key) or "")
        for key, widget in self.text_widgets.items():
            widget.delete("1.0", "end")
            widget.insert("1.0", record.get(key) or "")
        self.patient_title.config(text=record["full_name"])
        self.status_label.config(text=f"{record['patient_number']}  |  Last updated {record['created_at'][:10]}")
        self.save_button.config(state="normal")

    def new_patient(self):
        self.selected_id = None
        for variable in self.vars.values():
            variable.set("")
        self.vars["patient_number"].set(self.next_patient_number())
        self.vars["visit_date"].set(date.today().isoformat())
        for widget in self.text_widgets.values():
            widget.delete("1.0", "end")
        self.patient_title.config(text="New patient record")
        self.status_label.config(text="Complete demographics and clinical notes")
        self.save_button.config(state="normal")
        self.notebook.select(0)

    def next_patient_number(self):
        with sqlite3.connect(DB_PATH) as connection:
            value = connection.execute("SELECT COUNT(*) FROM patients").fetchone()[0] + 1
        return f"OP-{value:04d}"

    def save_record(self):
        full_name = self.vars["full_name"].get().strip()
        if not full_name:
            messagebox.showwarning("Missing name", "Please enter the patient's full name.")
            self.notebook.select(0)
            return
        data = {key: variable.get().strip() for key, variable in self.vars.items()}
        data.update({key: widget.get("1.0", "end").strip() for key, widget in self.text_widgets.items()})
        columns = list(data)
        with sqlite3.connect(DB_PATH) as connection:
            if self.selected_id:
                assignments = ", ".join(f"{column} = ?" for column in columns)
                connection.execute(f"UPDATE patients SET {assignments} WHERE id = ?", [data[column] for column in columns] + [self.selected_id])
            else:
                placeholders = ", ".join("?" for _ in columns)
                connection.execute(f"INSERT INTO patients ({', '.join(columns)}) VALUES ({placeholders})", [data[column] for column in columns])
                self.selected_id = connection.execute("SELECT last_insert_rowid()").fetchone()[0]
        self.refresh_patients()
        self.tree.selection_set(str(self.selected_id))
        self.tree.see(str(self.selected_id))
        self.status_label.config(text=f"{data['patient_number']}  |  Saved just now")
        messagebox.showinfo("Record saved", "The outpatient record has been saved locally.")


if __name__ == "__main__":
    OutpatientRecordsApp().mainloop()
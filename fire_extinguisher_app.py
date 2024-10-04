import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta
import csv
import sys
import os
from datetime import datetime

class FireExtinguisherApp:
    def __init__(self, master, initial_csv=None):
        self.master = master
        self.master.title("Fire Extinguisher Inventory")
        self.master.geometry("800x600")

        # Create in-memory database
        self.conn = sqlite3.connect(':memory:')
        self.create_table()

        self.setup_ui()

        # Load initial CSV if provided
        if initial_csv:
            self.import_csv(initial_csv)

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extinguishers (
                id INTEGER PRIMARY KEY,
                building TEXT,
                room TEXT,
                type TEXT,
                weight REAL,
                date_refilled TEXT,
                date_expiration TEXT,
                supplier TEXT,
                notes TEXT
            )
        ''')
        self.conn.commit()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Inventory tab
        inventory_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(inventory_frame, text="Inventory")

        # Treeview for inventory
        self.tree = ttk.Treeview(inventory_frame, columns=("ID", "Building", "Room", "Type", "Weight", "Date Refilled", "Expiration Date", "Supplier", "Notes"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Buttons for add, edit, delete
        button_frame = ttk.Frame(inventory_frame)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="Add", command=self.add_extinguisher).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit", command=self.edit_extinguisher).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_extinguisher).pack(side=tk.LEFT, padx=5)

        # Reports tab
        reports_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(reports_frame, text="Reports")

        report_buttons_frame = ttk.Frame(reports_frame)
        report_buttons_frame.pack(fill=tk.X, pady=10)

        ttk.Button(report_buttons_frame, text="Generate Full Report", command=lambda: self.generate_report("full")).pack(side=tk.LEFT, padx=5)
        ttk.Button(report_buttons_frame, text="Expiring Soon Report", command=lambda: self.generate_report("expiring")).pack(side=tk.LEFT, padx=5)
        ttk.Button(report_buttons_frame, text="Tally Report", command=self.show_tally_dialog).pack(side=tk.LEFT, padx=5)

        self.report_text = tk.Text(reports_frame, wrap=tk.WORD, width=80, height=20)
        self.report_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(reports_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_text.configure(yscrollcommand=scrollbar.set)

        # Import/Export buttons
        import_export_frame = ttk.Frame(self.master)
        import_export_frame.pack(fill=tk.X, pady=10)

        ttk.Button(import_export_frame, text="Import CSV", command=self.import_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(import_export_frame, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)

        # Refresh inventory display
        self.refresh_inventory()

    def refresh_inventory(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch all items from the database
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM extinguishers")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def add_extinguisher(self):
        # Create a dialog for adding a new extinguisher
        dialog = tk.Toplevel(self.master)
        dialog.title("Add Extinguisher")

        # Building dropdown
        ttk.Label(dialog, text="Building:").grid(row=0, column=0, padx=5, pady=5)
        buildings = ["EDS", "BRS", "MB", "SB", "CHTM", "PE", "Legarda", "Campo Libertad", "Others"]
        building_var = tk.StringVar()
        building_dropdown = ttk.Combobox(dialog, textvariable=building_var, values=buildings)
        building_dropdown.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Room:").grid(row=1, column=0, padx=5, pady=5)
        room_entry = ttk.Entry(dialog)
        room_entry.grid(row=1, column=1, padx=5, pady=5)

        # Type dropdown
        ttk.Label(dialog, text="Type:").grid(row=2, column=0, padx=5, pady=5)
        types = ["Red", "Green", "Gray"]
        type_var = tk.StringVar()
        type_dropdown = ttk.Combobox(dialog, textvariable=type_var, values=types)
        type_dropdown.grid(row=2, column=1, padx=5, pady=5)

        # Weight dropdown
        ttk.Label(dialog, text="Weight (lbs):").grid(row=3, column=0, padx=5, pady=5)
        weights = [5, 10, 20, 50, 120, 150, 180]
        weight_var = tk.StringVar()
        weight_dropdown = ttk.Combobox(dialog, textvariable=weight_var, values=weights)
        weight_dropdown.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Date Refilled (mm/dd/yyyy):").grid(row=4, column=0, padx=5, pady=5)
        date_refilled_entry = ttk.Entry(dialog)
        date_refilled_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Expiration Date (mm/dd/yyyy):").grid(row=5, column=0, padx=5, pady=5)
        date_expiration_entry = ttk.Entry(dialog)
        date_expiration_entry.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Supplier:").grid(row=6, column=0, padx=5, pady=5)
        supplier_entry = ttk.Entry(dialog)
        supplier_entry.grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Notes:").grid(row=7, column=0, padx=5, pady=5)
        notes_entry = ttk.Entry(dialog)
        notes_entry.grid(row=7, column=1, padx=5, pady=5)

        def validate_date(date_string):
            try:
                datetime.strptime(date_string, '%m/%d/%Y')
                return True
            except ValueError:
                return False

        def save_extinguisher():
            if not validate_date(date_refilled_entry.get()) or not validate_date(date_expiration_entry.get()):
                messagebox.showerror("Invalid Date", "Please enter dates in the format mm/dd/yyyy")
                return

            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO extinguishers (building, room, type, weight, date_refilled, date_expiration, supplier, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (building_var.get(), room_entry.get(), type_var.get(), weight_var.get(),
                  date_refilled_entry.get(), date_expiration_entry.get(),
                  supplier_entry.get(), notes_entry.get()))
            self.conn.commit()
            dialog.destroy()
            self.refresh_inventory()

        ttk.Button(dialog, text="Save", command=save_extinguisher).grid(row=8, column=0, columnspan=2, pady=10)

    def edit_extinguisher(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an extinguisher to edit.")
            return

        item_id = self.tree.item(selected_item)['values'][0]

        # Fetch the current values
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM extinguishers WHERE id = ?", (item_id,))
        extinguisher = cursor.fetchone()

        # Create a dialog for editing
        dialog = tk.Toplevel(self.master)
        dialog.title("Edit Extinguisher")

        ttk.Label(dialog, text="Building:").grid(row=0, column=0, padx=5, pady=5)
        building_entry = ttk.Entry(dialog)
        building_entry.insert(0, extinguisher[1])
        building_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Room:").grid(row=1, column=0, padx=5, pady=5)
        room_entry = ttk.Entry(dialog)
        room_entry.insert(0, extinguisher[2])
        room_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Type:").grid(row=2, column=0, padx=5, pady=5)
        type_entry = ttk.Entry(dialog)
        type_entry.insert(0, extinguisher[3])
        type_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Weight:").grid(row=3, column=0, padx=5, pady=5)
        weight_entry = ttk.Entry(dialog)
        weight_entry.insert(0, extinguisher[4])
        weight_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Date Refilled:").grid(row=4, column=0, padx=5, pady=5)
        date_refilled_entry = ttk.Entry(dialog)
        date_refilled_entry.insert(0, extinguisher[5])
        date_refilled_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Expiration Date:").grid(row=5, column=0, padx=5, pady=5)
        date_expiration_entry = ttk.Entry(dialog)
        date_expiration_entry.insert(0, extinguisher[6])
        date_expiration_entry.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Supplier:").grid(row=6, column=0, padx=5, pady=5)
        supplier_entry = ttk.Entry(dialog)
        supplier_entry.insert(0, extinguisher[7])
        supplier_entry.grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Notes:").grid(row=7, column=0, padx=5, pady=5)
        notes_entry = ttk.Entry(dialog)
        notes_entry.insert(0, extinguisher[8])
        notes_entry.grid(row=7, column=1, padx=5, pady=5)

        def update_extinguisher():
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE extinguishers
                SET building = ?, room = ?, type = ?, weight = ?, date_refilled = ?, date_expiration = ?, supplier = ?, notes = ?
                WHERE id = ?
            ''', (building_entry.get(), room_entry.get(), type_entry.get(), weight_entry.get(),
                  date_refilled_entry.get(), date_expiration_entry.get(), supplier_entry.get(), notes_entry.get(), item_id))
            self.conn.commit()
            dialog.destroy()
            self.refresh_inventory()

        ttk.Button(dialog, text="Update", command=update_extinguisher).grid(row=8, column=0, columnspan=2, pady=10)

    def delete_extinguisher(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an extinguisher to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this extinguisher?"):
            item_id = self.tree.item(selected_item)['values'][0]
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM extinguishers WHERE id = ?", (item_id,))
            self.conn.commit()
            self.refresh_inventory()

    def show_tally_dialog(self):
        categories = ["Building", "Weight", "Type", "Supplier"]
        dialog = tk.Toplevel(self.master)
        dialog.title("Select Tally Categories")
        dialog.geometry("300x200")
        
        var_dict = {cat: tk.BooleanVar() for cat in categories}
        
        for cat in categories:
            tk.Checkbutton(dialog, text=cat, variable=var_dict[cat]).pack(anchor="w", padx=20, pady=5)
        
        tk.Button(dialog, text="Generate Tally Report", command=lambda: self.generate_tally_report(var_dict, dialog)).pack(pady=10)

    def generate_tally_report(self, var_dict, dialog):
        selected_categories = [cat for cat, var in var_dict.items() if var.get()]
        if not selected_categories:
            messagebox.showwarning("Warning", "Please select at least one category.")
            return
        
        dialog.destroy()
        self.generate_report("tally", selected_categories)

    def generate_report(self, report_type, categories=None):
        self.report_text.delete(1.0, tk.END)
        cursor = self.conn.cursor()

        if report_type == "full":
            cursor.execute("SELECT * FROM extinguishers ORDER BY building, room")
            rows = cursor.fetchall()

            self.report_text.insert(tk.END, "Full Inventory Report\n")
            self.report_text.insert(tk.END, "======================\n\n")

            for row in rows:
                self.report_text.insert(tk.END, f"Building: {row[1]}\n")
                self.report_text.insert(tk.END, f"Room: {row[2]}\n")
                self.report_text.insert(tk.END, f"Type: {row[3]}\n")
                self.report_text.insert(tk.END, f"Weight: {row[4]} lbs\n")
                self.report_text.insert(tk.END, f"Date Refilled: {row[5]}\n")
                self.report_text.insert(tk.END, f"Expiration Date: {row[6]}\n")
                self.report_text.insert(tk.END, f"Supplier: {row[7]}\n")
                self.report_text.insert(tk.END, f"Notes: {row[8]}\n")
                self.report_text.insert(tk.END, "--------------------\n")

        elif report_type == "expiring":
            today = datetime.now().date()
            one_month_later = today + timedelta(days=30)
            
            cursor.execute("SELECT * FROM extinguishers WHERE date_expiration BETWEEN ? AND ? ORDER BY date_expiration", (today.isoformat(), one_month_later.isoformat()))
            rows = cursor.fetchall()

            self.report_text.insert(tk.END, "Extinguishers Expiring Soon Report\n")
            self.report_text.insert(tk.END, "====================================\n\n")

            for row in rows:
                self.report_text.insert(tk.END, f"Building: {row[1]}\n")
                self.report_text.insert(tk.END, f"Room: {row[2]}\n")
                self.report_text.insert(tk.END, f"Type: {row[3]}\n")
                self.report_text.insert(tk.END, f"Expiration Date: {row[6]}\n")
                self.report_text.insert(tk.END, "--------------------\n")

        elif report_type == "tally":
            self.report_text.insert(tk.END, "Tally Report\n")
            self.report_text.insert(tk.END, "============\n\n")

            for category in categories:
                self.report_text.insert(tk.END, f"{category} Tally:\n")
                self.report_text.insert(tk.END, "--------------\n")

                if category == "Building":
                    cursor.execute("SELECT building, COUNT(*) FROM extinguishers GROUP BY building ORDER BY COUNT(*) DESC")
                elif category == "Weight":
                    cursor.execute("SELECT weight, COUNT(*) FROM extinguishers GROUP BY weight ORDER BY COUNT(*) DESC")
                elif category == "Type":
                    cursor.execute("SELECT type, COUNT(*) FROM extinguishers GROUP BY type ORDER BY COUNT(*) DESC")
                elif category == "Supplier":
                    cursor.execute("SELECT supplier, COUNT(*) FROM extinguishers GROUP BY supplier ORDER BY COUNT(*) DESC")

                rows = cursor.fetchall()
                for row in rows:
                    self.report_text.insert(tk.END, f"{row[0]}: {row[1]}\n")
                
                self.report_text.insert(tk.END, "\n")

            if len(categories) > 1:
                self.report_text.insert(tk.END, "Combined Tally:\n")
                self.report_text.insert(tk.END, "----------------\n")

                group_by = ", ".join(categories)
                select = ", ".join([f"COALESCE({cat.lower()}, 'N/A') as {cat.lower()}" for cat in categories])
                query = f"SELECT {select}, COUNT(*) FROM extinguishers GROUP BY {group_by} ORDER BY COUNT(*) DESC"
                cursor.execute(query)
                rows = cursor.fetchall()

                for row in rows:
                    tally_str = ", ".join([f"{cat}: {row[i]}" for i, cat in enumerate(categories)])
                    self.report_text.insert(tk.END, f"{tally_str}: {row[-1]}\n")

        self.report_text.see(tk.END)

    def import_csv(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
            if not file_path:
                return

        try:
            with open(file_path, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)  # Skip header row
                cursor = self.conn.cursor()
                cursor.executemany('''
                    INSERT INTO extinguishers (building, room, type, weight, date_refilled, date_expiration, supplier, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', csv_reader)
                self.conn.commit()
            messagebox.showinfo("Import Successful", "Data has been imported successfully.")
        except Exception as e:
            messagebox.showerror("Import Error", f"An error occurred while importing: {str(e)}")

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM extinguishers")
            rows = cursor.fetchall()

            with open(file_path, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(["ID", "Building", "Room", "Type", "Weight", "Date Refilled", "Expiration Date", "Supplier", "Notes"])
                csv_writer.writerows(rows)

            messagebox.showinfo("Export Successful", "Data has been exported successfully.")
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred while exporting: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FireExtinguisherApp(root)
    root.mainloop()
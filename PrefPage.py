import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class PrefPhraseController:
    def __init__(self, master, pdf_viewer_app):  # Use master instead of root
        self.master = master
        self.master.title("Preferences")
        self.pdf_viewer_app = pdf_viewer_app

        self.confirm_save = 0

        # Initialize variables (replace with actual values or types)
        self.export_csv_flag = tk.BooleanVar(value=True)
        self.export_app_flag = tk.BooleanVar(value=True)
        self.regex_as_text=[]
        self.regexPairs = []
        self.dataReplacePairs = []
        self.people = []
        self.export_csv = ""
        self.app_path = ""
        self.settings = ""

        #initialize buttons and such:
        self.dataRep_add_button = None
        self.dataRep_exp_type_label = None
        self.dataRep_spacer = None
        self.dataRep_data_type_label = None
        self.dataRep_remove_button = None
        self.regex_add_button = None
        self.regex_exp_type_label = None
        self.regex_spacer = None
        self.regex_data_type_label = None
        self.regex_remove_button = None
        self.cancel_settings_button = None
        self.confirm_settings_button = None
        self.error_text_label = None
        self.load_settings_button = None
        self.load_settings_textfield = None
        self.load_settings_label = None
        self.save_warning_label = None
        self.save_settings_button = None
        self.save_settings_label = None
        self.Save_settings_tab = None
        self.replace_phrase_result_textfield = None
        self.phrase_to_replace_textfield = None
        self.data_replace_listbox = None
        self.dataReplace_subtab = None
        self.end_phrase_textfield = None
        self.start_phrase_textfield = None
        self.data_sweep_listbox = None
        self.regex_subtab = None
        self.subtabpane = None
        self.Data_sweep_tab = None
        self.path_to_app_button = None
        self.app_path_textfield = None
        self.export_to_app_toggle = None
        self.path_to_csv_button = None
        self.export_to_csv_filename_textfield = None
        self.export_to_csv_toggle = None
        self.export_tab = None
        self.tabpane = None
        self.save_settings_textfield = None

        # Create and place your widgets (using master instead of root)
        self.create_widgets()

    def create_widgets(self):
        # tabs
        self.tabpane = ttk.Notebook(self.master)
        self.tabpane.grid(row=0, column=0, columnspan=4)

        #Tab 1
        self.export_tab = tk.Frame(self.tabpane)
        self.tabpane.add(self.export_tab, text="Export Settings")

        #CSV
        self.export_to_csv_toggle = ttk.Checkbutton(
            self.export_tab,
            text="Export to CSV",
            variable=self.export_csv_flag,
            command=self.on_export_to_csv_toggle_click
        )
        self.export_to_csv_toggle.grid(row=0, column= 0, padx=5, pady=5)

        self.export_to_csv_filename_textfield = ttk.Entry(self.export_tab)
        self.export_to_csv_filename_textfield.grid(row=0, column= 1, padx=5, pady=5)

        self.path_to_csv_button = ttk.Button(
            self.export_tab, text="Path to CSV", command=self.on_path_to_csv_click
        )
        self.path_to_csv_button.grid(row=0, column=2, padx=5, pady=5)
        #APP
        self.export_to_app_toggle = ttk.Checkbutton(
            self.export_tab,
            text="Export to App",
            variable=self.export_app_flag,
            command=self.on_export_to_app_toggle_click
        )
        self.export_to_app_toggle.grid(row=1, column= 0, padx=5, pady=5)


        self.app_path_textfield = ttk.Entry(self.export_tab)
        self.app_path_textfield.grid(row=1, column= 1, padx=5, pady=5)

        self.path_to_app_button = ttk.Button(
            self.export_tab, text="Path to App", command=self.on_path_to_app_click
        )
        self.path_to_app_button.grid(row=1, column= 2, padx=5, pady=5)

        #Second tab
        self.Data_sweep_tab = tk.Frame(self.tabpane)
        self.tabpane.add(self.Data_sweep_tab, text="Data Export")
        self.subtabpane = ttk.Notebook(self.Data_sweep_tab)
        self.subtabpane.pack(fill="both", expand=True)

        # subtab 1
        self.regex_subtab = tk.Frame(self.subtabpane)
        self.subtabpane.add(self.regex_subtab, text="Regex Settings")

        self.data_replace_listbox = tk.Listbox(self.regex_subtab, selectmode=tk.MULTIPLE)
        self.data_replace_listbox.grid(row=0, column=0, columnspan=7, pady=5)
        self.data_replace_listbox.config(height=20, width=120)

        self.regex_remove_button = ttk.Button(
            self.regex_subtab, text="Remove", command=self.regex_remove_click
        )
        self.regex_remove_button.grid(row=1, column=0, padx=5, pady=5)

        self.regex_data_type_label = ttk.Label(self.regex_subtab, text="Data Name:")
        self.regex_data_type_label.grid(row=1, column=1, padx=5, pady=5)

        self.start_phrase_textfield = ttk.Entry(self.regex_subtab)
        self.start_phrase_textfield.grid(row=1, column=2, pady=5)

        self.regex_spacer = ttk.Label(self.regex_subtab, text="")
        self.regex_spacer.grid(row=1, column=3, padx=10, pady=5)

        self.regex_exp_type_label = ttk.Label(self.regex_subtab, text="Regex Expression:")
        self.regex_exp_type_label.grid(row=1, column=4, padx=5, pady=5)

        self.end_phrase_textfield = ttk.Entry(self.regex_subtab)
        self.end_phrase_textfield.grid(row=1, column=5, pady=5)

        self.regex_add_button = ttk.Button(
            self.regex_subtab, text="Add", command=self.regex_add_click
        )
        self.regex_add_button.grid(row=1, column=6, padx=5, pady=5)

        # subtab 2
        self.dataReplace_subtab = tk.Frame(self.subtabpane)
        self.subtabpane.add(self.dataReplace_subtab, text="Data Replace Settings")

        self.data_sweep_listbox = tk.Listbox(self.dataReplace_subtab, selectmode=tk.MULTIPLE)
        self.data_sweep_listbox.grid(row=0, column=0, columnspan=7, pady=5)
        self.data_sweep_listbox.config(height=20, width=120)

        self.dataRep_remove_button = ttk.Button(
            self.dataReplace_subtab, text="Remove", command=self.dataRep_remove_click
        )
        self.dataRep_remove_button.grid(row=1, column=0, padx=5, pady=5)

        self.dataRep_data_type_label = ttk.Label(self.dataReplace_subtab, text="Original Phrase:")
        self.dataRep_data_type_label.grid(row=1, column=1, padx=5, pady=5)

        self.phrase_to_replace_textfield = ttk.Entry(self.dataReplace_subtab)
        self.phrase_to_replace_textfield.grid(row=1, column=2, pady=5)

        self.dataRep_spacer = ttk.Label(self.dataReplace_subtab, text="")
        self.dataRep_spacer.grid(row=1, column=3, padx=10, pady=5)

        self.dataRep_exp_type_label = ttk.Label(self.dataReplace_subtab, text="End Phrase:")
        self.dataRep_exp_type_label.grid(row=1, column=4, padx=5, pady=5)

        self.replace_phrase_result_textfield = ttk.Entry(self.dataReplace_subtab)
        self.replace_phrase_result_textfield.grid(row=1, column=5, pady=5)

        self.dataRep_add_button = ttk.Button(
            self.dataReplace_subtab, text="Add", command=self.dataRep_add_click
        )
        self.dataRep_add_button.grid(row=1, column=6, padx=5, pady=5)


        # Third tab
        self.Save_settings_tab = tk.Frame(self.tabpane)
        self.tabpane.add(self.Save_settings_tab, text="Save to File Settings")

        self.save_settings_label = tk.Label(self.Save_settings_tab, text="Save:", font=("TkDefaultFont", 10))
        self.save_settings_label.grid(row=0, column=0, padx=5, pady=5)

        self.save_settings_textfield = ttk.Entry(self.Save_settings_tab)
        self.save_settings_textfield.grid(row=0, column=1, padx=5, pady=5)

        self.save_settings_button = ttk.Button(
            self.Save_settings_tab, text=" Save to File ", command=self.save_to_file_path_click
        )
        self.save_settings_button.grid(row=0, column=2, padx=5, pady=5)
        self.save_warning_label = ttk.Label(
            self.Save_settings_tab, text="Warning: Overwriting existing settings", foreground="red"
        )
        self.save_warning_label.grid_forget()  # Initially hidden

        self.load_settings_label = tk.Label(self.Save_settings_tab, text="Load:", font=("TkDefaultFont", 10))
        self.load_settings_label.grid(row=1, column=0, padx=5, pady=5)

        self.load_settings_textfield = ttk.Entry(self.Save_settings_tab)
        self.load_settings_textfield.grid(row=1, column=1, padx=5, pady=5)

        self.load_settings_button = ttk.Button(
            self.Save_settings_tab, text="Load From File", command=self.load_from_file_path_click
        )
        self.load_settings_button.grid(row=1, column=2, padx=5, pady=5)

        self.clear_settings_button = ttk.Button(
            self.Save_settings_tab, text="Clear File", command=self.clear_file_path_click
        )
        if self.settings:
            self.clear_settings_button.grid(row=2, column=1, columnspan=3, padx=5, pady=5)
        else:
            self.clear_settings_button.grid_forget()

        self.error_text_label = ttk.Label(self.master, text="", foreground="red")
        self.error_text_label.grid(row=1, column=1, sticky="e", padx=5, pady=5)
        self.cancel_settings_button = ttk.Button(
            self.master, text="Cancel", command=self.cancel_click
        )
        self.cancel_settings_button.grid(row=1, column=2, sticky="e",padx=1, pady=5)
        self.confirm_settings_button = ttk.Button(
            self.master, text="Confirm", command=self.confirm_click
        )
        self.confirm_settings_button.grid(row=1, column=3, sticky="e",padx=1, pady=5)

    def on_export_to_csv_toggle_click(self):
        if self.export_csv_flag.get():
            self.export_csv_flag.set(True)
            self.export_to_csv_filename_textfield.grid(row=0, column=1, padx=5, pady=5)
            self.path_to_csv_button.grid(row=0, column=2, padx=5, pady=5)
        else:
            self.export_csv_flag.set(False)
            self.path_to_csv_button.grid_forget()
            self.export_to_csv_filename_textfield.grid_forget()

    def on_export_to_app_toggle_click(self):
        if self.export_app_flag.get():
            self.export_app_flag.set(True)
            self.app_path_textfield.grid(row=1, column=1, padx=5, pady=5)
            self.path_to_app_button.grid(row=1, column=2, padx=5, pady=5)
        else:
            self.export_app_flag.set(False)
            self.path_to_app_button.grid_forget()
            self.app_path_textfield.grid_forget()

    def on_path_to_csv_click(self):
        print("on_path_to_csv_click clicked")
        filetypes = (("csv files", "*.csv"),("txt files", "*.txt"), ("all files", "*.*"))
        self.export_csv = filedialog.askopenfilename(title="Open a file", initialdir="/", filetypes=filetypes)
        self.export_to_csv_filename_textfield.delete(0, tk.END)
        self.export_to_csv_filename_textfield.insert(0, self.export_csv)

    def on_path_to_app_click(self):
        print("on_path_to_app_click clicked")
        filetypes = (("EXE", "*.exe"), ("all files", "*.*"))
        self.app_path = filedialog.askopenfilename(title="Open a file", initialdir="/", filetypes=filetypes)
        self.app_path_textfield.delete(0, tk.END)
        self.app_path_textfield.insert(0, self.app_path)

    def regex_add_click(self):
        print("regex add")
        dataName = self.start_phrase_textfield.get()
        regex = self.end_phrase_textfield.get()
        if dataName or regex:
            print(dataName+": + "+regex)
            self.regexPairs.append((dataName,regex))
            self.data_replace_listbox.insert("end",dataName+": + "+regex)
            self.start_phrase_textfield.delete(0, tk.END)
            self.end_phrase_textfield.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "No Text in fields")

    def regex_remove_click(self):
        # Function to handle deleting a file
        print("regex remove")
        selection = self.data_replace_listbox.curselection()
        offset = 0
        if selection:  # Check if anything is selected
            for selected_item in selection:
                selected_item = selected_item - offset
                self.data_replace_listbox.delete(selected_item)
                self.regexPairs.pop(selected_item)
                print(selected_item)
                offset += 1

    def dataRep_add_click(self):
        print("data replace add")
        dataPhrase = self.phrase_to_replace_textfield.get()
        dataResult = self.replace_phrase_result_textfield.get()
        if dataPhrase or dataResult:
            print(dataPhrase + ": + " + dataResult)
            self.dataReplacePairs.append((dataPhrase, dataResult))
            self.data_sweep_listbox.insert("end", dataPhrase + " -> " + dataResult)
            self.phrase_to_replace_textfield.delete(0, tk.END)
            self.replace_phrase_result_textfield.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "No Text in fields")

    def dataRep_remove_click(self):
        # Function to handle deleting a file
        print("data replace remove")
        selection = self.data_sweep_listbox.curselection()
        offset = 0
        if selection:  # Check if anything is selected
            for selected_item in selection:
                selected_item = selected_item - offset
                self.data_sweep_listbox.delete(selected_item)
                self.dataReplacePairs.pop(selected_item)
                print(selected_item)
                offset += 1

    def save_to_file_path_click(self):
        print("save_to_file_path_click clicked")
        if self.save_settings_textfield.get() and self.confirm_save == 0:
            self.confirm_save = 1
            messagebox.showerror("Warning!", "Warning! there is text in save box. pushing save one more time will overwrite the data to that location")
        elif self.save_settings_textfield.get() and self.confirm_save == 1:
            self.confirm_save = 0
            self.save_to_file()
        else:
            filetypes = (("txt files", "*.txt"), ("all files", "*.*"))
            self.settings = filedialog.askopenfilename(title="Open a file", initialdir="/", filetypes=filetypes)
            if self.settings:
                self.save_settings_textfield.delete(0, tk.END)
                self.load_settings_textfield.delete(0, tk.END)
                self.save_settings_textfield.insert(0, self.settings)
                self.load_settings_textfield.insert(0, self.settings)
                self.confirm_save = 0
                self.save_to_file()
                self.clear_settings_button.grid(row=2, column=1, columnspan=3, padx=5, pady=5)

    def load_from_file_path_click(self):
        print("on_path_to_csv_click clicked")
        if self.load_settings_textfield.get():
            self.load_from_file()
        else:
            filetypes = (("txt files", "*.txt"), ("all files", "*.*"))
            self.settings = filedialog.askopenfilename(title="Open a file", initialdir="/", filetypes=filetypes)
            if self.settings:
                self.save_settings_textfield.delete(0, tk.END)
                self.load_settings_textfield.delete(0, tk.END)
                self.save_settings_textfield.insert(0, self.settings)
                self.load_settings_textfield.insert(0, self.settings)
                self.load_from_file()
                self.clear_settings_button.grid(row=2, column=1, columnspan=3, padx=5, pady=5)

    def clear_file_path_click(self):
        print("clear_file_path_click clicked")
        self.save_settings_textfield.delete(0, tk.END)
        self.load_settings_textfield.delete(0, tk.END)
        self.settings = ""
        self.clear_settings_button.grid_forget()

    def save_to_file(self):
        print("saving")
        try:
            text_to_export = ""
            with open(self.settings, "w") as file_writer:  # Use 'with' for automatic file closing
                text_to_export += "Settings for Preference page: \n"
                text_to_export += "------------------------------Export Settings:------------------------------ \n"
                text_to_export += "                              -Export to CSV-                                \n"
                text_to_export += "Checked: \n"
                text_to_export += str(self.export_csv_flag.get()) + "\n"  # Assuming these are Tkinter variables
                text_to_export += "CSV filepath and name: \n"
                text_to_export += self.export_to_csv_filename_textfield.get() + "\n"
                text_to_export += "                              -Export to App-                                \n"
                text_to_export += "Checked: \n"
                text_to_export += str(self.export_app_flag.get()) + "\n"
                text_to_export += "App filepath: \n"
                text_to_export += self.app_path + "\n"  # Assuming appPath is a string
                text_to_export += "----------------------------Data Export Settings:---------------------------- \n"
                text_to_export += "                                -Data Sweep-                                  \n"
                text_to_export += "Search terms: \n"
                index = 0
                for data_name, regex_exp in self.regexPairs:
                    text_to_export += data_name+": "+self.regex_as_text[index] + "\n"
                    index +=1
                text_to_export += "                              -Data Replace-                                \n"
                text_to_export += "Replace Phrases \n"
                for data_start, data_end in self.dataReplacePairs:
                    text_to_export += data_start + " -> " + data_end + "\n"
                text_to_export += "---------------------------Save Settings to File:--------------------------- \n"
                text_to_export += "File path and name: \n"
                text_to_export += self.settings + "\n"  # Assuming Settings is a string

                file_writer.write(text_to_export)

        finally:
            file_writer.close()

    def load_from_file(self):
        print("loading")
        try:
            with open(self.settings, "r") as file_reader:  # Use 'with' for automatic file closing
                # Skip header lines and check if empty
                if not file_reader.readline():
                    messagebox.showerror("Error", "Error settings empty!")
                    return
                file_reader.readline()

                # --- Export to CSV ---
                for _ in range(2):
                    file_reader.readline()
                csv_setting = file_reader.readline().strip().lower() == "true"
                self.export_csv_flag.set(csv_setting)  # Assuming these are Tkinter variables
                self.on_export_to_csv_toggle_click()

                file_reader.readline()
                csv_path_load = file_reader.readline().strip()
                self.export_to_csv_filename_textfield.delete(0, tk.END)
                self.export_to_csv_filename_textfield.insert(0, csv_path_load)
                self.export_csv = csv_path_load

                # --- Export to App ---
                for _ in range(2):
                    file_reader.readline()
                app_setting = file_reader.readline().strip().lower() == "true"
                self.export_app_flag.set(app_setting)
                self.on_export_to_app_toggle_click()

                file_reader.readline()
                app_path_load = file_reader.readline().strip()
                if "null" in app_path_load:
                    self.app_path_textfield.delete(0, tk.END)
                    self.app_path = ""
                else:
                    self.app_path_textfield.delete(0, tk.END)
                    self.app_path_textfield.insert(0, app_path_load)
                    self.app_path = app_path_load

                # --- Data Export Settings ---
                for _ in range(3):
                    file_reader.readline()
                while True:
                    data = file_reader.readline().strip()
                    if "-Data Replace-" in data:
                        break
                    start, end = data.split(": ",1)
                    regex = re.compile(end.strip(),re.MULTILINE)
                    self.regex_as_text.append(end.strip())
                    self.regexPairs.append((start, regex))
                    self.data_replace_listbox.insert("end", start + ": " + end.strip())

                file_reader.readline()
                while True:
                    data = file_reader.readline().strip()
                    if "-Save Settings to File:-" in data:
                        break
                    start, end = data.split(" -> ",1)
                    self.dataReplacePairs.append((start, end))
                    self.data_sweep_listbox.insert("end", start + " -> " + end)

                # --- Save Settings to File ---
                file_reader.readline()
                settings_path_load = file_reader.readline().strip()
                self.settings = settings_path_load
                self.save_settings_textfield.delete(0, tk.END)
                self.load_settings_textfield.delete(0, tk.END)
                self.save_settings_textfield.insert(0, self.settings)
                self.load_settings_textfield.insert(0, self.settings)


        except Exception as e:
            print("Load settings failed")

    def confirm_click(self):
        # Get the data you want to pass
        data_to_pass = {
            "export_csv": self.export_csv,
            "csv_flag": bool(self.export_csv_flag),
            "app_path": self.app_path,
            "app_flag": bool(self.export_app_flag),
            "settings": self.settings,
            "regex pairs": self.regexPairs,
            "data Replace Pairs": self.dataReplacePairs
        }

        # Pass the data to the PdfViewer instance
        self.pdf_viewer_app.update_from_settings(data_to_pass)  # Assuming pdf_viewer_app is accessible

        self.master.destroy()

    def cancel_click(self):
        self.master.destroy()

    def is_valid_path(self, path):
        try:
            return os.path.exists(path)
        except (TypeError, ValueError):
            return False

    def rename_file(self, old_path_string, new_path_string, file_changed):
        try:
            os.rename(old_path_string, new_path_string)
            file_changed = new_path_string
        except OSError:
            self.print_error("Rename file error")
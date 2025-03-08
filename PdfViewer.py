import re
import tkinter as tk
import difflib
import csv
#import PyMuPDF
import PyPDF2
from PrefPage import PrefPhraseController
from tkinter import ttk, filedialog, messagebox  # For TabPane and other modern widgets
from PyPDF2 import PdfReader

import tkPDFViewerUpdated as pdf
from robot import Robot


class APP:
    def __init__(self):
        self.files = []
        self.activePDF = "" #r "C:\Users\spide\Downloads\_FACESHEETS_01042024.pdf"
        self.prevPDF = ""

        self.export_csv = ""
        self.csv_flag = False
        self.app_path = ""
        self.app_flag = False
        self.settings = ""
        self.regex_pairs = []
        self.data_replace_pairs = []
        self.people = []

        #application
        # Create the main window
        self.root = tk.Tk()
        self.root.title("PDF Data Dumper")
        self.root.geometry("1200x900")

        # Create the menu bar
        self.menubar = tk.Menu(self.root)

        # File menu
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="New File", command=self.onAddPdfButtonClick)
        self.openRecentMenu = tk.Menu(self.filemenu, tearoff=0)
        self.openRecentMenuItem = tk.Menu(self.openRecentMenu, tearoff=0)
        self.openRecentMenuItem.add_command(label="", command=self.onOpenRecentMenuItemClick)
        self.filemenu.add_cascade(label="Open Recent", menu=self.openRecentMenuItem)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Preferences...", command=self.onPrefClick)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=self.root.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        # Edit menu
        self.editmenu = tk.Menu(self.menubar, tearoff=0)
        self.editmenu.add_command(label="Delete", command=self.onDeleteFileClick)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Select All", command=self.onSelectAllClick)
        self.editmenu.add_command(label="Unselect All", command=self.onUnselectAllClick)
        self.menubar.add_cascade(label="Edit", menu=self.editmenu)

        # Help menu
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About PDF Data Dumper", command=self.onAboutMenuItemClick)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        self.root.config(menu=self.menubar)

        # Create the SplitPane (using PanedWindow in Tkinter)
        self.splitpane = tk.PanedWindow(self.root, orient="horizontal")
        self.splitpane.pack(fill="both", expand=True)

        # Left pane (VBox)
        self.left_pane = tk.Frame(self.splitpane)
        self.splitpane.add(self.left_pane)

        tk.Label(self.left_pane, text="Files", font=("TkDefaultFont", 18)).pack(pady=10)
        self.filesList = tk.Listbox(self.left_pane, selectmode=tk.SINGLE)
        self.filesList.pack(fill="both", expand=True)
        self.filesList.bind("<<ListboxSelect>>", self.on_filesList_select)
        tk.Button(self.left_pane, text="Add PDF", command=self.onAddPdfButtonClick).pack(pady=5)

        # Center pane (VBox)
        self.center_pane = tk.Frame(self.splitpane)
        self.splitpane.add(self.center_pane)

        tk.Label(self.center_pane, text="PDF", font=("TkDefaultFont", 18)).pack(pady=10)
        self.pdf_content_label =tk.Label()
        self.pdfView = pdf.ShowPdf().pdf_view(self.center_pane)
        # Use a Label to display the PDF content for now
        if not self.activePDF:
            self.pdf_content_label = tk.Label(self.center_pane, text="PDF content will be displayed here")
            self.pdf_content_label.pack(fill="both", expand=True)
        else:
            # Create the tkPDFViewer and place it INSIDE the frame

            # Adding pdf location and width and height.
            self.pdfView = self.showPDF.pdf_view(self.center_pane,
                             pdf_location=self.activePDF,
                             width=100, height=100)
            self.pdfView.pack()

        # Right pane (VBox)
        self.right_pane = tk.Frame(self.splitpane)
        self.splitpane.add(self.right_pane)

        # Create the TabPane (using ttk.Notebook in Tkinter)
        self.tabpane = ttk.Notebook(self.right_pane)
        self.tabpane.pack(fill="both", expand=True)

        # Raw PDF Text tab
        self.raw_text_tab = tk.Frame(self.tabpane)
        self.tabpane.add(self.raw_text_tab, text="Raw PDF Text")
        self.raw_text_scroll = tk.Scrollbar(self.raw_text_tab)
        self.raw_text_scroll.pack(side="right", fill="y")
        self.raw_text_area = tk.Text(self.raw_text_tab, yscrollcommand=self.raw_text_scroll.set)
        self.raw_text_area.pack(fill="both", expand=True)
        self.raw_text_scroll.config(command=self.raw_text_area.yview)

        # Simplified Text tab
        self.simplified_text_tab = tk.Frame(self.tabpane)
        self.tabpane.add(self.simplified_text_tab, text="Simplified Text")
        self.tabpane.bind("<ButtonRelease-1>", self.TextTabChanged)
        self.simplified_text_scroll = tk.Scrollbar(self.simplified_text_tab)
        self.simplified_text_scroll.pack(side="right", fill="y")
        self.simplified_text_area = tk.Text(self.simplified_text_tab, yscrollcommand=self.simplified_text_scroll.set)
        self.simplified_text_area.pack(fill="both", expand=True)
        self.simplified_text_scroll.config(command=self.simplified_text_area.yview)
        tk.Button(self.simplified_text_tab, text="Export", command=self.onExportClick).pack(pady=5)

        # Status bar (HBox)
        self.status_bar = tk.Frame(self.root)
        self.status_bar.pack(fill="x")

        self.left_status_label = tk.Label(self.status_bar, text="Left status")
        self.left_status_label.pack(side="left")

        self.right_status_label = tk.Label(self.status_bar, text="Right status")
        self.right_status_label.pack(side="right")

        # Set the initial divider positions
        self.splitpane.paneconfig(self.left_pane, width=300)
        self.splitpane.paneconfig(self.center_pane, width=600)
        self.splitpane.paneconfig(self.right_pane, width=300)

        self.root.mainloop()


    def onAddPdfButtonClick(self):
        # Function to handle adding a PDF file
        print("Add PDF button clicked")
        filetypes = (("PDF files", "*.pdf"), ("all files", "*.*"))
        file = filedialog.askopenfilename(title="Open a file", initialdir="/", filetypes=filetypes)
        if file:
            # Process the selected file
            self.prevPDF = self.activePDF
            self.files.append(file)
            self.filesList.insert("end",file)
            self.activePDF = file
            self.filesList.selection_clear(0, tk.END)
            self.filesList.selection_set(self.filesList.size()-1)
            self.setPDFView(self.activePDF)
            self.openRecentMenuItem.entryconfig(0,label=self.prevPDF)
            self.people = []
            #print("Selected file:", file)

    def on_filesList_select(self,event):
        print("Select event")
        selection = self.filesList.curselection()
        if selection:  # Check if anything is selected
            selected_item = self.filesList.get(selection[0])  # Get the string value
            print("Selected item:", selected_item)
            print("Active item:", self.activePDF)
            # Or do something else with the selected item(s)
            matcher = difflib.SequenceMatcher(None, self.activePDF, selected_item)
            # ratio = matcher.ratio()
            print(matcher.ratio())
            if matcher.ratio() < 0.95:
                self.prevPDF = self.activePDF
                self.activePDF = selected_item
                self.setPDFView(self.activePDF)
                self.people = []

        else:
            print("ERROR: Nothing Selected")

    def setPDFView(self,pdfPath):
        self.pdf_content_label.pack_forget()
        self.pdfView.destroy()
        self.pdfView = pdf.ShowPdf().pdf_view(self.center_pane,
                                             pdf_location=pdfPath,
                                             width=100, height=100)
        self.extract_text_from_pdf(pdfPath)
        self.pdfView.pack()

    def extract_text_from_pdf(self,pdf_path):
        """Extracts text from a PDF file."""
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            text.replace(" ", " ")
            # Clear existing content in the Text widget
            self.raw_text_area.delete("1.0", tk.END)

            # Insert the extracted text
            self.raw_text_area.insert(tk.END, text)

    def onOpenRecentMenuItemClick(self):
        # Function to handle opening a recent file
        print("Open Recent menu item clicked")
        self.setPDFView(self.prevPDF)
        self.filesList.selection_clear(0, tk.END)
        self.filesList.selection_set(self.filesList.get(0,tk.END).index(self.prevPDF))
        self.openRecentMenuItem.entryconfig(0, label=self.activePDF)
        temp = self.activePDF
        self.activePDF = self.prevPDF
        self.prevPDF = temp
        self.people = []


    def onPrefClick(self):
        # Function to handle opening preferences
        print("Preferences menu item clicked")
        # Create the settings window
        settings_window = tk.Toplevel(self.root)
        pref_controller = PrefPhraseController(settings_window, self)
        pref_controller.settings = "settings.txt"
        pref_controller.load_from_file()

    def update_from_settings(self, data):
        """Updates the PdfViewer with data from the settings."""
        print("Export_Csv: " + self.export_csv)
        print("App_path: " + self.app_path)
        print("Settings: " + self.settings)

        self.export_csv = data["export_csv"]
        self.csv_flag = data["csv_flag"]
        self.app_path = data["app_path"]
        self.app_flag = data["app_flag"]
        self.settings = data["settings"]
        self.regex_pairs = data["regex pairs"]
        self.data_replace_pairs = data["data Replace Pairs"]

        print("Export_Csv: " + self.export_csv)
        print("App_path: " + self.app_path)
        print("Settings: " + self.settings)
        print("Regex pairs:")
        for data_name, regex_exp in self.regex_pairs:
            print(data_name + ": "+str(regex_exp))
        print("Data Replace")
        for data_name, data_end in self.data_replace_pairs:
            print(data_name + " -> " + data_end)

    def onDeleteFileClick(self):
        # Function to handle deleting a file
        print("Delete menu item clicked")
        selection = self.filesList.curselection()
        offset = 0
        if selection:  # Check if anything is selected
            for selected_item in selection:
                selected_item = selected_item - offset
                if self.files[selected_item]==self.activePDF:
                    self.activePDF = ""
                    self.pdfView.destroy()
                    self.pdf_content_label = tk.Label(self.center_pane, text="Active PDF cleared please select another")
                    self.raw_text_area.delete("1.0", tk.END)
                    self.simplified_text_area.delete("1.0", tk.END)
                    self.pdf_content_label.pack(fill="both", expand=True)
                self.filesList.delete(selected_item)
                self.files.pop(selected_item)
                print(selected_item)
                offset += 1

    def onSelectAllClick(self):
        # Function to handle selecting all files
        print("Select All menu item clicked")
        self.filesList.select_set(0, tk.END)

    def onUnselectAllClick(self):
        # Function to handle unselecting all files
        print("Unselect All menu item clicked")
        self.filesList.selection_clear(0, tk.END)
        self.filesList.selection_set(self.filesList.get(0, tk.END).index(self.activePDF))

    def TextTabChanged(self,event):
        # Function to handle text tab change
        selected_tab = event.widget.select()
        tab_id = event.widget.index(selected_tab)
        print(f"Tab {tab_id + 1} clicked!")
        if tab_id == 1:
            if not self.regex_pairs and not self.files:
                self.simplified_text_area.delete("1.0", tk.END)
                self.simplified_text_area.insert(1.0, "Please load PDF and add preferences to settings")
            elif not self.files:
                self.simplified_text_area.delete("1.0", tk.END)
                self.simplified_text_area.insert(1.0, "Please load PDF")
            elif not self.regex_pairs:
                self.simplified_text_area.delete("1.0", tk.END)
                self.simplified_text_area.insert(1.0, "Add preferences to settings")
            elif not self.people:
                current_person = {}
                with open(self.activePDF, 'rb') as pdf_file:
                    pdf_reader = PdfReader(pdf_file)
                    for page in pdf_reader.pages:
                        for data_name, regex in self.regex_pairs:
                            matches = regex.findall(page.extract_text())
                            index = 0
                            for item in matches:
                                personData = []
                                if isinstance(item, tuple):
                                    for tupleEntry in item:
                                        for start, end in self.data_replace_pairs:
                                            tupleEntry = tupleEntry.replace(start, end)
                                        if not tupleEntry.strip():
                                            tupleEntry = ""
                                        personData.append(tupleEntry)
                                else:
                                    for start, end in self.data_replace_pairs:
                                        item = item.replace(start, end)
                                    personData.append(item)
                                if len(matches) > 1:
                                    current_person[data_name + " " + str(index)] = personData
                                else:
                                    current_person[data_name] = personData
                                index += 1
                        self.people.append(current_person)
                        current_person= {}

                text = ""
                text += str(self.extract_unique_keys(self.people))
                text += "\n"
                for person in self.people:
                    if len(person) > 0:
                        for value in person.values():
                            text += str(value)
                            text += ", "
                        text += "\n"

                self.simplified_text_area.delete("1.0", tk.END)
                self.simplified_text_area.insert(1.0, text)



    def onExportClick(self):
        # Function to handle export click
        print("Export button clicked")
        if self.people:
            if self.app_flag:
                print("Exporting to App")
                robot = Robot(self)
                robot.create_new_patients()
            if self.csv_flag:
                print("Exporting to CSV")
                self.write_dict_list_to_csv(self.people)
            print(self.people)
        else:
            messagebox.showerror("Warning!","Please load a pdf or check preferences")

    def extract_unique_keys(self,data):
        fieldnames = set()
        for dict in data:
            fieldnames.update(dict.keys())
        return list(fieldnames)

    def write_dict_list_to_csv(self,data, fieldnames=None):
        if fieldnames is None:
            if not data:
                raise ValueError("fieldnames must be provided if the data list is empty.")
            fieldnames = self.extract_unique_keys(data)

        try:
            with open(self.export_csv, 'w', newline='', encoding='utf-8') as csvfile:  # Use 'with' for automatic file closing
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()  # Write the header row

                for row in data:
                    if len(row) > 0:
                        writer.writerow(row)

        except Exception as e:
            print(f"An error ocurred writing into the file: {e}")
            raise
        finally:
            csvfile.close()

    def onAboutMenuItemClick(self):
        # Function to handle About menu item click
        print("About button clicked")
        # Create the settings window
        about_window = tk.Toplevel(self.root)
        about_window.title("about")

        # About label
        tk.Label(about_window, text="About Window").pack(pady=20)

        # Button to close the about window
        close_button = tk.Button(about_window, text="Close", command=about_window.destroy)
        close_button.pack()


def main():
    App = APP()

if __name__ == '__main__':
    main()




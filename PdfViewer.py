import re
import threading
import tkinter as tk
import difflib
import csv
#import PyMuPDF
import PyPDF2
from PrefPage import PrefPhraseController
from tkinter import ttk, filedialog, messagebox  # For TabPane and other modern widgets
from PyPDF2 import PdfReader
from google import genai

import tkPDFViewerUpdated as pdf
from robot import Robot


class APP:
    def __init__(self):
        self.client = genai.Client(api_key="GEMINI_API_KEY")
        self.files = []
        self.activePDF = "" #r "C:\Users\spide\Downloads\_FACESHEETS_01042024.pdf"
        self.prevPDF = ""

        self.export_csv = ""
        self.csv_flag = False
        self.app_path = ""
        self.app_flag = False
        self.ai_mode = False
        self.ai_prompt = ""
        self.ai_search = []
        self.settings = ""
        self.regex_pairs = []
        self.data_replace_pairs = []
        self.people = []
        self.ai_pdf_results = []
        self.ai_results = []
        self.pages=0
        self.start = -1
        self.end = -1

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
        self.export_button =tk.Button(self.simplified_text_tab, text="Export", command=self.onExportClick)
        self.export_button.pack(pady=5)

        self.export_start_label = ttk.Label(self.simplified_text_tab, text="Start on Page:")
        self.export_start_label.pack(side=tk.LEFT, padx=(5, 2), pady=5)

        self.export_start_text = ttk.Entry(self.simplified_text_tab)
        self.export_start_text.pack(side=tk.LEFT, padx=(0, 5), pady=5)
        self.export_start_text.insert(0,"0")

        # AI mode
        self.ai_text_tab = tk.Frame(self.tabpane)
        if self.ai_mode:
            self.tabpane.add(self.ai_text_tab, text="AI Mode")
        self.ai_text_scroll = tk.Scrollbar(self.ai_text_tab)
        self.ai_text_scroll.pack(side="right", fill="y")
        self.ai_text_area = tk.Text(self.ai_text_tab, yscrollcommand=self.ai_text_scroll.set)
        self.ai_text_scroll.config(command=self.ai_text_area.yview)
        self.ai_text_area.pack(fill="both", expand=True)

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
        # print("Add PDF button clicked")
        filetypes = (("PDF files", "*.pdf"), ("all files", "*.*"))
        file = filedialog.askopenfilename(title="Open a file", initialdir="/", filetypes=filetypes)
        if file:
            # Process the selected file
            self.prevPDF = self.activePDF
            self.files.append(file)
            self.filesList.insert("end",file)
            self.activePDF = file

            with open(self.activePDF, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                self.pages = len(reader.pages)

            self.filesList.selection_clear(0, tk.END)
            self.filesList.selection_set(self.filesList.size()-1)
            self.setPDFView(self.activePDF)
            self.openRecentMenuItem.entryconfig(0,label=self.prevPDF)
            self.people = []
            ## print("Selected file:", file)

    def on_filesList_select(self,event):
        # print("Select event")
        selection = self.filesList.curselection()
        if selection:  # Check if anything is selected
            selected_item = self.filesList.get(selection[0])  # Get the string value
            # print("Selected item:", selected_item)
            # print("Active item:", self.activePDF)
            # Or do something else with the selected item(s)
            matcher = difflib.SequenceMatcher(None, self.activePDF, selected_item)
            # ratio = matcher.ratio()
            # print(matcher.ratio())
            if matcher.ratio() < 0.95:
                self.prevPDF = self.activePDF
                self.activePDF = selected_item
                self.setPDFView(self.activePDF)
                with open(self.activePDF, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    self.pages = len(reader.pages)
                self.people = []

        else:
            pass
            # print("ERROR: Nothing Selected")

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
        # print("Open Recent menu item clicked")
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
        # print("Preferences menu item clicked")
        # Create the settings window
        settings_window = tk.Toplevel(self.root)
        pref_controller = PrefPhraseController(settings_window, self)
        pref_controller.load_from_json()

    def update_from_settings(self, data):
        """Updates the PdfViewer with data from the settings."""
        # print("Export_Csv: " + self.export_csv)
        # print("App_path: " + self.app_path)
        # print("Settings: " + str(self.settings))

        self.export_csv = data["export_csv"]
        self.csv_flag = data["csv_flag"]
        self.app_path = data["app_path"]
        self.app_flag = data["app_flag"]
        self.ai_mode = data["AI mode flag"]
        self.settings = data["settings"]
        self.regex_pairs = data["regex pairs"]
        self.data_replace_pairs = data["data Replace Pairs"]
        self.ai_prompt = data["active AI prompt"]
        self.ai_search = data["AI pdf terms"]

        if self.ai_mode:
            self.tabpane.add(self.ai_text_tab, text="AI Mode")
        else:
            self.tabpane.forget(2)

        # print("Export_Csv: " + self.export_csv)
        # print("App_path: " + self.app_path)
        # print("Settings: " + str(self.settings))
        # print("Regex pairs:")
        # for data_name, regex_exp in self.regex_pairs:
            # print(data_name + ": "+str(regex_exp))
        # print("Data Replace")
        # for data_name, data_end in self.data_replace_pairs:
            # print(data_name + " -> " + data_end)

    def onDeleteFileClick(self):
        # Function to handle deleting a file
        # print("Delete menu item clicked")
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
                # print(selected_item)
                offset += 1

    def onSelectAllClick(self):
        # Function to handle selecting all files
        # print("Select All menu item clicked")
        self.filesList.select_set(0, tk.END)

    def onUnselectAllClick(self):
        # Function to handle unselecting all files
        # print("Unselect All menu item clicked")
        self.filesList.selection_clear(0, tk.END)
        self.filesList.selection_set(self.filesList.get(0, tk.END).index(self.activePDF))

    def TextTabChanged(self,event):
        # Function to handle text tab change
        selected_tab = event.widget.select()
        tab_id = event.widget.index(selected_tab)
        # print(f"Tab {tab_id + 1} clicked!")
        if tab_id == 1:
            self.simplifyText()
        elif tab_id == 2:
            self.AIMode()


    def simplifyText(self):
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
            self.export_button.config(state='disabled')
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
                                    if "Printed by" in str(tupleEntry):
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
                    current_person = {}

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
            self.export_button.config(state='normal')

    def AIMode(self):
        print("no")
        if not self.ai_prompt:
            self.ai_text_area.delete("1.0", tk.END)
            self.ai_text_area.insert(1.0, "Prompt missing please give prompt in settings")
        elif not self.ai_search:
            self.ai_text_area.delete("1.0", tk.END)
            self.ai_text_area.insert(1.0, "PDF Search terms missing please load in settings")
        elif not self.files:
            self.ai_text_area.delete("1.0", tk.END)
            self.ai_text_area.insert(1.0, "Please load PDF")
        elif not self.ai_pdf_results:
            self.ai_text_area.delete("1.0", tk.END)
            exclude_phrases = ["Printed by","Encounter Date:"]

            self.ai_pdf_results = self.extract_text_blocks_between_markers(self.ai_search[0],self.ai_search[1],exclude_phrases)
            for result in self.ai_pdf_results:
                response = self.client.models.generate_content(
                    model="gemma-3-27b-it",
                    contents=[self.ai_prompt+"\n"+str(result)]
                )
                self.ai_results.append(response.text)
                self.ai_text_area.insert(1.0, response.text)
                self.ai_text_area.insert(1.0, "\n\n")
                #print(response.text)
            print(self.ai_results)

    def extract_text_blocks_between_markers(
            self,
            start_term: str,
            end_term: str,
            exclude_phrases: [str]
    ) -> [str]:  # Return type is now List[str]
        all_found_blocks = []
        current_block_lines = []
        capturing = False

        try:
            with open(self.activePDF, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(reader.pages)
                print(f"Processing {num_pages} pages...")

                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    try:
                        page_text = page.extract_text()
                    except Exception as e:
                        print(f"Warning: Could not extract text from page {page_num + 1}. Error: {e}")
                        page_text = None  # Ensure page_text is None on extraction error

                    if page_text is None:
                        # print(f"Warning: Could not extract text from page {page_num + 1}") # Already printed above potentially
                        continue

                    lines = page_text.splitlines()  # Split text into lines

                    for line in lines:
                        # --- State Machine Logic ---

                        # 1. If we are currently capturing: Check for the end term
                        if capturing:
                            end_index = line.find(end_term)
                            if end_index != -1:
                                # End term found! Capture text *before* it on this line
                                content_before_end = line[:end_index]
                                is_excluded = any(phrase in content_before_end for phrase in exclude_phrases)
                                # Add if not excluded and not just whitespace
                                if content_before_end.strip() and not is_excluded:
                                    current_block_lines.append(content_before_end)

                                # --- Finalize the current block ---
                                if current_block_lines:  # Only add if we actually captured something
                                    completed_block = "\n".join(current_block_lines)
                                    all_found_blocks.append(completed_block)

                                # --- Reset for the next potential block ---
                                current_block_lines = []
                                capturing = False
                                # Continue searching on the rest of the page after this line

                            else:
                                # End term not on this line, process whole line if capturing
                                is_excluded = any(phrase in line for phrase in exclude_phrases)
                                if not is_excluded:
                                    current_block_lines.append(line)

                        # 2. If we are not capturing: Check for the start term
                        # This part only executes if capturing is False (i.e., after finding end or before finding first start)
                        else:  # not capturing
                            start_index = line.find(start_term)
                            if start_index != -1:
                                # Start term found!
                                capturing = True
                                current_block_lines = []  # Ensure we start fresh for this new block

                                # Capture text *after* start term on the *same line*
                                content_after_start = line[start_index + len(start_term):]

                                # Check if end term is *also* on this same line, after start term
                                end_index_same_line = content_after_start.find(end_term)
                                if end_index_same_line != -1:
                                    # Start and End on the same line!
                                    content_between = content_after_start[:end_index_same_line]
                                    is_excluded = any(phrase in content_between for phrase in exclude_phrases)
                                    # Add if not excluded and not just whitespace
                                    if content_between.strip() and not is_excluded:
                                        current_block_lines.append(content_between)  # Add to current block

                                    # --- Finalize this same-line block ---
                                    if current_block_lines:
                                        completed_block = "\n".join(current_block_lines)
                                        all_found_blocks.append(completed_block)

                                    # --- Reset ---
                                    current_block_lines = []
                                    capturing = False  # Stop capturing immediately, ready for next start term
                                else:
                                    # End term not on the same line, capture the rest of this line
                                    is_excluded = any(phrase in content_after_start for phrase in exclude_phrases)
                                    # Add if not excluded and not just whitespace
                                    if content_after_start.strip() and not is_excluded:
                                        current_block_lines.append(content_after_start)
                                # Continue processing next lines (now potentially capturing or looking for end)

                # After processing all pages, check if we were left capturing (unclosed block)
                if capturing:
                    print(
                        f"Warning: Reached end of document while still capturing. The last block starting with '{start_term}' might be incomplete as '{end_term}' was not found.")
                    # Decide if you want to include incomplete blocks:
                    if current_block_lines:
                        all_found_blocks.append("\n".join(current_block_lines) + "\n[INCOMPLETE BLOCK]")

            return all_found_blocks
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []  # Return empty list on error


    def onExportClick(self):
        # Function to handle export click
        # print("Export button clicked")
        if self.people:
            if self.app_flag:
                print("Patient creation started. Press Ctrl+Q to stop.")
                try:
                    try:
                        start_text = self.export_start_text.get()
                        if not start_text:
                            return
                        start_num = int(start_text)
                        if start_num < self.pages:
                            self.start = start_num
                    except ValueError:
                        return
                    if self.start > -1:
                        robot = Robot(self)
                        robot.create_new_patients()

                    if self.end > -1:
                        self.start = self.end
                        self.export_start_text.delete(0, tk.END)
                        self.export_start_text.insert(0,str(self.start))
                except Exception as e:
                    print(f"Exception occurred during creation: {e}. Catching to make CSV")

            if self.csv_flag:
                # print("Exporting to CSV")
                self.write_dict_list_to_csv(self.people)
            # print(self.people)
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
            # print(f"An error occurred writing into the file: {e}")
            raise
        finally:
            csvfile.close()

    def onAboutMenuItemClick(self):
        # Function to handle About menu item click
        # print("About button clicked")
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




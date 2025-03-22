import os.path
import subprocess
import time
from tkinter import messagebox

import pyautogui
import psutil
from difflib import SequenceMatcher
import numpy as np
import pyperclip
import keyboard
import tkinter as tk

from pathlib import Path


class Robot:
    def __init__(self,pdf_viewer_app):
        #self.text_area = text_area

        self.cmd = None
        self.pdf_viewer_app = pdf_viewer_app
        self.app_path = pdf_viewer_app.app_path
        self.filename = os.path.basename(pdf_viewer_app.app_path)
        self.script_dir = Path(__file__).parent
        self.png_folder = self.script_dir / "Screencaps"
        # print("Png_folder: "+ str(self.png_folder))
        self.dir_to_list = list(self.png_folder.iterdir())
        self.png_locations = {}
        self.clipboard = ""
        self.pdf_viewer_app = pdf_viewer_app
        self.stop_typing = False  # flag to stop typing
        self.billing_loaded = False


        keyboard.add_hotkey('ctrl+q', self.stop_typing_func)
        self.start_application()
        self.load_locations()

        # self.create_new_patients()

        # print(self.png_locations)


    def check_if_process_running(self,process_name):
        for process in psutil.process_iter(['name']):
            if process.info['name'] == process_name:
                return True
        return False

    def stop_typing_func(self):
        print("Hotkey pressed. Stopping typing.")
        self.stop_typing = True  # Set the flag to True

    def cleanup_and_exit(self):
        """Helper function for graceful exit."""
        # self.text_area.insert(tk.END,
        #                      "Process killed with keyboard. Closing this window in 3 seconds" + "\n")
        # self.text_area.see(tk.END)
        print("Process killed with keyboard")

    def create_new_patients(self):
        # self.text_area.insert(tk.END, "Adding data to App. Press Ctrl+Q to kill process.\n")
        # self.text_area.see(tk.END)

        for person in self.pdf_viewer_app.people:
            # try: # Removed outer try-except.  Handle exception within the loop.
            self.person = person
            print("Adding: " + str(person))
            # self.text_area.insert(tk.END, "Adding: " + str(person) + "\n")
            # self.text_area.see(tk.END)

            # --- Check stop_typing flag *before* each major step ---
            if self.stop_typing:
                self.cleanup_and_exit()  # Call a cleanup function
                return  # Exit the create_new_patients() function early

            self.type_patient_info()

            if self.stop_typing:
                self.cleanup_and_exit()
                return

            self.type_insurance()

            if self.stop_typing:
                self.cleanup_and_exit()
                return

            self.finish_patient()
            if self.stop_typing:  # Check one last time after finish_patient
                self.cleanup_and_exit()
                return  # Exit function to not assign to Chart Number.
            person["Chart Number"] = self.clipboard

            self.type_billing()

            print("Finished: " + str(self.clipboard))
            # self.text_area.insert(tk.END, "Finished: " + str(self.clipboard) + "\n")
            # self.text_area.see(tk.END)
            if self.stop_typing:  # Check one last time after finish_patient
                self.cleanup_and_exit()
                return  # Exit function to not assign to Chart Number.

        self.cleanup_and_exit()
        #messagebox.showerror("Complete!", "All data entered with no error. Please close this window and the log window")


    def type_patient_info(self):
        try:
            pyautogui.click(self.png_locations["LedgerList"][0], self.png_locations["LedgerList"][1])
            pyautogui.sleep(1.5)
            pyautogui.press('f8')

            time.sleep(3.5)
            if self.stop_typing: return

            pyautogui.click(self.png_locations["FirstNameBox"][0] + 40, self.png_locations["FirstNameBox"][1] + 10)
            pyautogui.write(self.person["Legal Name"][1].upper())
            if self.stop_typing: return

            pyautogui.click(self.png_locations["LastNameBox"][0] + 40, self.png_locations["LastNameBox"][1])
            pyautogui.write(self.person["Legal Name"][0].upper())
            if self.stop_typing: return

            pyautogui.click(self.png_locations["MiddleInitalBox"][0] + 40, self.png_locations["MiddleInitalBox"][1])
            pyautogui.write(self.person["Legal Name"][2].upper())
            if self.stop_typing: return
        except (KeyError, TypeError) as e:
            pass
            print("No middle name")

        try:
            pyautogui.click(self.png_locations["StreetAddressBox"][0] + 40,
                            self.png_locations["StreetAddressBox"][1])
            pyautogui.write(self.person["Address"][0].upper())
            if self.stop_typing: return

            pyautogui.click(self.png_locations["CityBox"][0] + 40, self.png_locations["CityBox"][1])
            pyautogui.write(self.person["Address"][1].upper())
            pyautogui.press('enter')
            if self.stop_typing: return

            pyautogui.doubleClick(self.png_locations["StateBox"][0] + 40, self.png_locations["StateBox"][1],
                                  interval=0.2)
            pyautogui.write(self.person["Address"][2].upper())
            if self.stop_typing: return

            pyautogui.click(self.png_locations["PostCodeBox"][0] + 40, self.png_locations["PostCodeBox"][1])
            pyautogui.write(self.person["Address"][3].upper())
            if self.stop_typing: return
        except KeyError as e:
            pyautogui.click(self.png_locations["StreetAddressBox"][0] + 40,
                            self.png_locations["StreetAddressBox"][1])
            pyautogui.write(self.person["Address (Apt)"][0].upper())
            if self.stop_typing: return

            pyautogui.click(self.png_locations["AptBox"][0] + 40, self.png_locations["AptBox"][1] + 20)
            pyautogui.write(self.person["Address (Apt)"][1].upper())
            if self.stop_typing: return

            pyautogui.click(self.png_locations["CityBox"][0] + 40, self.png_locations["CityBox"][1])
            pyautogui.write(self.person["Address (Apt)"][2].upper())
            pyautogui.press('enter')
            if self.stop_typing: return

            pyautogui.click(self.png_locations["StateBox"][0] + 40, self.png_locations["StateBox"][1])
            pyautogui.write(self.person["Address (Apt)"][3].upper())
            if self.stop_typing: return

            pyautogui.click(self.png_locations["PostCodeBox"][0] + 40, self.png_locations["PostCodeBox"][1])
            pyautogui.write(self.person["Address (Apt)"][4].upper())
            if self.stop_typing: return

        try:
            pyautogui.click(self.png_locations["PhoneBox"][0] + 40, self.png_locations["PhoneBox"][1])
            pyautogui.write(self.person["Phone"][0])
            if self.stop_typing: return
        except KeyError as e:
            pass
            print("no phone")

        pyautogui.click(self.png_locations["GenderBox"][0] + 40, self.png_locations["GenderBox"][1])
        pyautogui.write(self.person["Legal Sex"][0][0].upper())
        pyautogui.press('enter')
        if self.stop_typing: return

        pyautogui.click(self.png_locations["DOBBox"][0], self.png_locations["DOBBox"][1])
        pyautogui.write(self.person["Date of Birth"][0])
        if self.stop_typing: return


    def type_insurance(self):
        pyautogui.click(self.png_locations["InsuranceList"][0], self.png_locations["InsuranceList"][1])
        if self.stop_typing: return

        try:
            pyautogui.click(self.png_locations["InsuranceNameBox"][0][0] + 40,
                            self.png_locations["InsuranceNameBox"][0][1])
            pyautogui.write(self.person["Insurance"][0])
            pyautogui.press('enter')
            pyautogui.sleep(0.2)
            if self.stop_typing: return

            pyautogui.click(self.png_locations["PolicyIDBox"][0][0] + 50, self.png_locations["PolicyIDBox"][0][1])
            pyautogui.write(self.person["Insurance"][3])
            pyautogui.press('enter')
            pyautogui.sleep(0.2)
            if self.stop_typing: return

            pyautogui.click(self.png_locations["GroupNoBox"][0][0] + 50, self.png_locations["GroupNoBox"][0][1])
            pyautogui.write(self.person["Insurance"][2])
            pyautogui.press('enter')
            pyautogui.sleep(0.2)
            if self.stop_typing: return
        except KeyError as e:
            try:
                pyautogui.click(self.png_locations["InsuranceNameBox"][0][0] + 40,
                                self.png_locations["InsuranceNameBox"][0][1])
                pyautogui.write(self.person["Insurance 0"][0])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)
                if self.stop_typing: return

                pyautogui.click(self.png_locations["PolicyIDBox"][0][0] + 50,
                                self.png_locations["PolicyIDBox"][0][1])
                pyautogui.write(self.person["Insurance 0"][3])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)
                if self.stop_typing: return

                pyautogui.click(self.png_locations["GroupNoBox"][0][0] + 50, self.png_locations["GroupNoBox"][0][1])
                pyautogui.write(self.person["Insurance 0"][2])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)
                if self.stop_typing: return

                pyautogui.click(self.png_locations["InsuranceNameBox"][1][0] + 40,
                                self.png_locations["InsuranceNameBox"][1][1])
                pyautogui.write(self.person["Insurance 1"][0])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)
                if self.stop_typing: return

                pyautogui.click(self.png_locations["PolicyIDBox"][1][0] + 50,
                                self.png_locations["PolicyIDBox"][1][1])
                pyautogui.write(self.person["Insurance 1"][3])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)
                if self.stop_typing: return

                pyautogui.click(self.png_locations["GroupNoBox"][1][0] + 50, self.png_locations["GroupNoBox"][1][1])
                pyautogui.write(self.person["Insurance 1"][2])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)
                if self.stop_typing: return

                pyautogui.click(self.png_locations["InsuranceNameBox"][2][0] + 40,
                                self.png_locations["InsuranceNameBox"][2][1])
                pyautogui.write(self.person["Insurance 2"][0])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)
                if self.stop_typing: return

                # RELATION
                pyautogui.click(self.png_locations["InsuranceNameBox"][2][0] + 40,
                                self.png_locations["InsuranceNameBox"][2][1] + 20)
                pyautogui.write("S")
                pyautogui.press('enter')
                pyautogui.sleep(0.2)
                if self.stop_typing: return

                pyautogui.click(self.png_locations["PolicyIDBox"][2][0] + 50,
                                self.png_locations["PolicyIDBox"][2][1])
                pyautogui.write(self.person["Insurance 2"][3])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)
                if self.stop_typing: return

                pyautogui.click(self.png_locations["GroupNoBox"][2][0] + 50, self.png_locations["GroupNoBox"][2][1])
                pyautogui.write(self.person["Insurance 2"][2])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)
                if self.stop_typing: return
            except KeyError as e:
                pass
                print("Ran out of insurances")

    def type_billing(self):
        time.sleep(2)
        # Open Ledger
        pyautogui.click(self.png_locations["LedgerList"][0], self.png_locations["LedgerList"][1])
        time.sleep(1)

        # Load last saved patient into box
        pyautogui.click(self.png_locations["ChartLedger"][0], self.png_locations["ChartLedger"][1])
        pyautogui.write(self.clipboard)
        pyautogui.press('enter')
        time.sleep(2)
        if self.stop_typing: return

        # Click billing box and open the billing page
        pyautogui.click(self.png_locations["BillingBox"][0], self.png_locations["BillingBox"][1])
        pyautogui.press('f8')
        time.sleep(2)
        pyautogui.doubleClick(self.png_locations["BillingBox"][0] + 100, self.png_locations["BillingBox"][1],interval=0.2)
        time.sleep(3)

        if not self.billing_loaded:
            self.load_billing_locations()

        if self.stop_typing: return

        pyautogui.click(self.png_locations["AuthNo"][0] + 80,
                        self.png_locations["AuthNo"][1])
        try:
            pyautogui.write(self.person["Insurance"][4])
        except KeyError as e:
            pyautogui.write(self.person["Insurance 0"][4])

        pyautogui.click(self.png_locations["ClaimInfoTab"][0], self.png_locations["ClaimInfoTab"][1])
        time.sleep(0.2)
        if self.stop_typing: return
        pyautogui.click(self.png_locations["AdmissionDateBox"][0]+60, self.png_locations["AdmissionDateBox"][1])
        pyautogui.write(self.person["Admission date"][0])

        if self.stop_typing: return
        time.sleep(1)
        pyautogui.press('f3')
        time.sleep(0.5)
        pyautogui.press('esc')

    def load_billing_locations(self):
        # Load inital Billing locations
        self.load_png_list(self.get_elements_at_indices(self.dir_to_list, [2,4,8]))

        # Click and load
        pyautogui.click(self.png_locations["ClaimInfoTab"][0], self.png_locations["ClaimInfoTab"][1])
        time.sleep(0.5)
        self.load_png_list(self.get_elements_at_indices(self.dir_to_list, [0]))

        # Go back to Billing so it can be loaded
        pyautogui.click(self.png_locations["BillingInfoTab"][0]-80, self.png_locations["BillingInfoTab"][1])
        time.sleep(0.2)
        self.billing_loaded = True

    def finish_patient(self):
        pyautogui.click(self.png_locations["PatientInfoList"][0], self.png_locations["PatientInfoList"][1])
        if self.stop_typing: return

        pyautogui.hotkey('shift', 'f3')
        time.sleep(1)
        pyautogui.doubleClick(self.png_locations["ChartNumberBox"][0] + 50, self.png_locations["ChartNumberBox"][1],
                              interval=0.2)
        pyautogui.sleep(0.1)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.5)
        self.clipboard = pyperclip.paste()

        if self.stop_typing: return
        pyautogui.press("esc")
        pyautogui.sleep(0.5)
        pyautogui.press("esc")
        time.sleep(3)


    def find_similar_index(self, list_of_strings, target_string, similarity_threshold=0.8):
        best_match_index = -1
        highest_similarity = 0

        for index, item in enumerate(list_of_strings):
            similarity_ratio = SequenceMatcher(None, target_string, str(item)).ratio()
            if similarity_ratio > highest_similarity and similarity_ratio >= similarity_threshold:
                highest_similarity = similarity_ratio
                best_match_index = index

        return best_match_index if best_match_index != -1 else None

    def load_locations(self):
        # load "ledger" Location
        index = self.find_similar_index(self.dir_to_list, "LedgerList", 0.15)
        self.load_png_list(self.dir_to_list[index:index + 1])

        # Open Ledger
        pyautogui.click(self.png_locations["LedgerList"][0], self.png_locations["LedgerList"][1])
        pyautogui.sleep(1)

        # Load chart and billing box locations on ledger page
        self.load_png_list(self.get_elements_at_indices(self.dir_to_list,[3,5]))

        # Open Patient Page
        pyautogui.press('f8')
        time.sleep(3.5)

        # Load patient Info boxes locations
        self.load_png_list(self.get_elements_at_indices(self.dir_to_list,[1,6,7,9,10,11,13,15,17,19,20,22,23,24]))

        # Open Insurance tab
        pyautogui.click(self.png_locations["InsuranceList"][0], self.png_locations["InsuranceList"][1])
        time.sleep(2)

        # Load Insurance Info boxes locations
        self.load_png_list(self.get_elements_at_indices(self.dir_to_list,[12,14,21]), multi=True)

        #Go home
        pyautogui.press('esc')
        pyautogui.sleep(1)
        pyautogui.press('esc')

    def load_png_list(self, png_list,multi=False):
        for png in png_list:
            if png.is_file() and png.suffix.lower() == ".png":
                if multi:
                    try:
                        centers = []
                        location = pyautogui.locateAllOnScreen(str(png), confidence=0.8)
                        for locations in location:
                            centers.append(pyautogui.center(locations))
                        location = centers
                    except pyautogui.ImageNotFoundException:
                        location = "Not on this screen"
                else:
                    try:
                        location = pyautogui.locateCenterOnScreen(str(png),confidence=0.8)
                    except pyautogui.ImageNotFoundException:
                        location = "Not on this screen"
                self.png_locations[png.stem] = location

    def get_elements_at_indices(self, original_list, indices):
        """
        Creates a new list using a list.

        Args:
            original_list: The original list.
            indices: A list of integer indices.

        Returns:
            A new list, or an empty list if inputs are invalid.

        Raises:
            TypeError: If original_list isn't a list or indices contains non-integers.
            IndexError: If any index is out of range.

        """
        if not isinstance(original_list, list):
            raise TypeError("original_list must be a list")
        if not isinstance(indices, list):
            raise TypeError("indices must be a list")
        if not all(isinstance(i, int) for i in indices):
            raise TypeError("All indices must be integers.")
        if not original_list or not indices:
            return []

        try:
            new_list = [original_list[i] for i in indices]
            return new_list
        except IndexError as e:
            raise IndexError(f"An index is out of bounds: {e}") from e  # add better error context

    def start_application(self):
        if self.check_if_process_running(self.filename):
            # data = pyautogui.getWindowsWithTitle("TotalMD")
            try:
                self.np = pyautogui.getWindowsWithTitle(self.filename[:-4])[0].activate()
                time.sleep(2)
            except Exception as e:
                print(self.filename[:-4]+" is running but not selectable please kill "+self.filename[:-4]+" process in Task Manager")
                raise Exception("Error grabbing app")
        else:
            self.proc = subprocess.Popen([self.app_path, ])
            time.sleep(4)

        self.np = pyautogui.getActiveWindow()

        self.size = pyautogui.size()

        pyautogui.moveTo(200, 210)
        self.np.moveTo(150, 200)

        pyautogui.mouseDown()
        pyautogui.moveTo(x=self.size[0] - 1, y=self.size[1] / 2, duration=0.1)
        pyautogui.mouseUp()

        time.sleep(2)
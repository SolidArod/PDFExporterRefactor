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
    def __init__(self,master,pdf_viewer_app):
        self.master = master
        self.master.title("Patients added")

        self.text_frame = tk.Frame(self.master)
        self.text_scroll = tk.Scrollbar(self.text_frame)
        self.text_scroll.pack(side="right", fill="y")
        self.text_area = tk.Text(self.text_frame, yscrollcommand=self.text_scroll.set)
        self.text_area.pack(fill="both", expand=True)
        self.text_scroll.config(command=self.text_area.yview)

        self.pdf_viewer_app = pdf_viewer_app
        self.app_path = pdf_viewer_app.app_path
        self.filename = os.path.basename(pdf_viewer_app.app_path)
        self.script_dir = Path(__file__).parent
        self.png_folder = self.script_dir / "Screencaps"
        self.dir_to_list = list(self.png_folder.iterdir())
        self.png_locations = {}
        self.clipboard = ""
        self.pdf_viewer_app = pdf_viewer_app
        self.stop_typing = False  # flag to stop typing

        self.start_application()
        self.load_locations()

        keyboard.add_hotkey('ctrl+q', self.stop_typing_func)


        print(self.png_locations)

    def check_if_process_running(self,process_name):
        for process in psutil.process_iter(['name']):
            if process.info['name'] == process_name:
                return True
        return False

    def stop_typing_func(self):
        print("Hotkey pressed. Stopping typing.")
        raise CustomError("Keyboard stop")

    def create_new_patients(self):
        self.text_area.insert(tk.END, "Adding data to App. Press Ctrl+Q to kill process.\n")
        try:
            for person in self.pdf_viewer_app.people:
                self.person = person
                self.text_area.insert(tk.END, "Adding: "+str(person)+"\n")
                self.text_area.see(tk.END)

                self.type_patient_info()
                self.type_insurance()
                self.finish_patient()
                person["Chart Number"] = self.clipboard

                self.text_area.insert(tk.END, "Finished: " + str(self.clipboard)+"\n")
                self.text_area.see(tk.END)

            messagebox.showerror("Complete!", "All data entered with no error. Please close this window and the log window")
        except CustomError as e:
            self.text_area.insert(tk.END, "Process killed with keyboard. Closing this window in 3 seconds"+"\n")
            self.text_area.see(tk.END)
            print("stopping process")
            time.sleep(3)
            self.master.destroy()

    def type_patient_info(self):
        try:
            pyautogui.click(self.png_locations["patientList"][0], self.png_locations["patientList"][1])
            pyautogui.sleep(1.5)
            pyautogui.press('f8')

            time.sleep(3.5)



            pyautogui.click(self.png_locations["FirstNameBox"][0] + 40, self.png_locations["FirstNameBox"][1] + 10)
            pyautogui.write(self.person["Legal Name"][1].upper())

            pyautogui.click(self.png_locations["LastNameBox"][0] + 40, self.png_locations["LastNameBox"][1])
            pyautogui.write(self.person["Legal Name"][0].upper())

            pyautogui.click(self.png_locations["MiddleInitalBox"][0] + 40, self.png_locations["MiddleInitalBox"][1])
            pyautogui.write(self.person["Legal Name"][2].upper())
        except:
            print("No middle name")

        try:
            pyautogui.click(self.png_locations["StreetAddressBox"][0] + 40, self.png_locations["StreetAddressBox"][1])
            pyautogui.write(self.person["Address"][0].upper())

            pyautogui.click(self.png_locations["CityBox"][0] + 40, self.png_locations["CityBox"][1])
            pyautogui.write(self.person["Address"][1].upper())
            pyautogui.press('enter')

            pyautogui.doubleClick(self.png_locations["StateBox"][0] + 40, self.png_locations["StateBox"][1],interval=0.2)
            pyautogui.write(self.person["Address"][2].upper())

            pyautogui.click(self.png_locations["PostCodeBox"][0] + 40, self.png_locations["PostCodeBox"][1])
            pyautogui.write(self.person["Address"][3].upper())
        except KeyError as e:
            pyautogui.click(self.png_locations["StreetAddressBox"][0] + 40, self.png_locations["StreetAddressBox"][1])
            pyautogui.write(self.person["Address (Apt)"][0].upper())

            pyautogui.click(self.png_locations["AptBox"][0] + 40, self.png_locations["AptBox"][1]+20)
            pyautogui.write(self.person["Address (Apt)"][1].upper())

            pyautogui.click(self.png_locations["CityBox"][0] + 40, self.png_locations["CityBox"][1])
            pyautogui.write(self.person["Address (Apt)"][2].upper())
            pyautogui.press('enter')

            pyautogui.click(self.png_locations["StateBox"][0] + 40, self.png_locations["StateBox"][1])
            pyautogui.write(self.person["Address (Apt)"][3].upper())

            pyautogui.click(self.png_locations["PostCodeBox"][0] + 40, self.png_locations["PostCodeBox"][1])
            pyautogui.write(self.person["Address (Apt)"][4].upper())

        try:
            pyautogui.click(self.png_locations["PhoneBox"][0] + 40, self.png_locations["PhoneBox"][1])
            pyautogui.write(self.person["Phone"][0])
        except KeyError as e:
            print("no phone")

        pyautogui.click(self.png_locations["GenderBox"][0] + 40, self.png_locations["GenderBox"][1])
        pyautogui.write(self.person["Legal Sex"][0][0].upper())
        pyautogui.press('enter')

        pyautogui.click(self.png_locations["DOBBox"][0], self.png_locations["DOBBox"][1])
        pyautogui.write(self.person["Date of Birth"][0])

    def type_insurance(self):
        pyautogui.click(self.png_locations["InsuranceList"][0], self.png_locations["InsuranceList"][1])

        try:
            pyautogui.click(self.png_locations["InsuranceNameBox"][0][0] + 40, self.png_locations["InsuranceNameBox"][0][1])
            pyautogui.write(self.person["Insurance"][0])
            pyautogui.press('enter')
            pyautogui.sleep(0.2)

            pyautogui.click(self.png_locations["PolicyIDBox"][0][0] + 50, self.png_locations["PolicyIDBox"][0][1])
            pyautogui.write(self.person["Insurance"][3])
            pyautogui.press('enter')
            pyautogui.sleep(0.2)

            pyautogui.click(self.png_locations["GroupNoBox"][0][0] + 50, self.png_locations["GroupNoBox"][0][1])
            pyautogui.write(self.person["Insurance"][2])
            pyautogui.press('enter')
            pyautogui.sleep(0.2)
        except:
            try:
                pyautogui.click(self.png_locations["InsuranceNameBox"][0][0] + 40,
                                self.png_locations["InsuranceNameBox"][0][1])
                pyautogui.write(self.person["Insurance 0"][0])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)

                pyautogui.click(self.png_locations["PolicyIDBox"][0][0] + 50, self.png_locations["PolicyIDBox"][0][1])
                pyautogui.write(self.person["Insurance 0"][3])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)

                pyautogui.click(self.png_locations["GroupNoBox"][0][0] + 50, self.png_locations["GroupNoBox"][0][1])
                pyautogui.write(self.person["Insurance 0"][2])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)

                pyautogui.click(self.png_locations["InsuranceNameBox"][1][0] + 40,
                                self.png_locations["InsuranceNameBox"][1][1])
                pyautogui.write(self.person["Insurance 1"][0])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)

                pyautogui.click(self.png_locations["PolicyIDBox"][1][0] + 50, self.png_locations["PolicyIDBox"][1][1])
                pyautogui.write(self.person["Insurance 1"][3])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)

                pyautogui.click(self.png_locations["GroupNoBox"][1][0] + 50, self.png_locations["GroupNoBox"][1][1])
                pyautogui.write(self.person["Insurance 1"][2])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)

                pyautogui.click(self.png_locations["InsuranceNameBox"][2][0] + 40,
                                self.png_locations["InsuranceNameBox"][2][1])
                pyautogui.write(self.person["Insurance 2"][0])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)

                #RELATION
                pyautogui.click(self.png_locations["InsuranceNameBox"][2][0] + 40,
                                self.png_locations["InsuranceNameBox"][2][1]+20)
                pyautogui.write("S")
                pyautogui.press('enter')
                pyautogui.sleep(0.2)

                pyautogui.click(self.png_locations["PolicyIDBox"][2][0] + 50, self.png_locations["PolicyIDBox"][2][1])
                pyautogui.write(self.person["Insurance 2"][3])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)

                pyautogui.click(self.png_locations["GroupNoBox"][2][0] + 50, self.png_locations["GroupNoBox"][2][1])
                pyautogui.write(self.person["Insurance 2"][2])
                pyautogui.press('enter')
                pyautogui.sleep(0.2)
            except:
                print("Ran out of insurances")




    def finish_patient(self):
        pyautogui.click(self.png_locations["PatientInfoList"][0], self.png_locations["PatientInfoList"][1])

        pyautogui.hotkey('shift', 'f3')
        time.sleep(1)
        pyautogui.doubleClick(self.png_locations["ChartNumberBox"][0] + 50, self.png_locations["ChartNumberBox"][1],interval=0.2)
        pyautogui.sleep(0.1)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.5)
        self.clipboard = pyperclip.paste()
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
        index = self.find_similar_index(self.dir_to_list, "patient", 0.15)
        self.load_png_list(self.dir_to_list[index:index + 1])

        pyautogui.click(self.png_locations["patientList"][0], self.png_locations["patientList"][1])
        pyautogui.sleep(1)
        pyautogui.press('f8')

        time.sleep(3.5)
        self.to_exclude = [6, 8, 12, 14]
        self.patient_page_items = np.array(self.dir_to_list)[
            ~np.isin(range(len(np.array(self.dir_to_list))), self.to_exclude)]
        self.load_png_list(self.patient_page_items)

        pyautogui.click(self.png_locations["InsuranceList"][0], self.png_locations["InsuranceList"][1])

        time.sleep(2)
        self.to_exclude = [0, 1, 2, 3, 4, 5, 7, 9, 10, 11, 12, 13, 15, 16, 17]
        self.insurance_list_page = np.array(self.dir_to_list)[
            ~np.isin(range(len(np.array(self.dir_to_list))), self.to_exclude)]
        self.load_png_list(self.insurance_list_page, multi=True)

        pyautogui.click(self.png_locations["PatientInfoList"][0], self.png_locations["PatientInfoList"][1])
        pyautogui.sleep(1)
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

    def start_application(self):
        if self.check_if_process_running(self.filename):
            # data = pyautogui.getWindowsWithTitle("TotalMD")
            self.np = pyautogui.getWindowsWithTitle(self.filename[:-4])[0].activate()
            time.sleep(2)
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

class CustomError(Exception):
    """A custom exception class."""
    def __init__(self, message="A custom error occurred"):
        self.message = message
        super().__init__(self.message)  # Initialize the base class

    def __str__(self):
        return f"CustomError: {self.message}"
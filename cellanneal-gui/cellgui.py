import tkinter as tk
from PIL import Image, ImageTk
import pandas as pd
from tkinter.filedialog import askopenfile, askdirectory
from tkinter import messagebox
from pathlib import Path
from cellanneal import cellanneal_pipe, repeatanneal_pipe

import sys
import os


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class cellgui:

    def __init__(self, root):
        self.root = root
        root.title("cellanneal")

        # place holders for required data
        self.bulk_df = pd.DataFrame()
        self.bulk_data_path = tk.StringVar()
        self.bulk_df_is_set = 0  # check later whether data has been selected
        self.celltype_df = pd.DataFrame()
        self.celltype_data_path = tk.StringVar()
        self.celltype_df_is_set = 0

        # output path
        self.output_path = tk.StringVar()
        self.output_path_is_set = 0

        # parameters for the deconvolution procedure, set to default values
        self.bulk_min = 1e-5  # minimum expression in bulk
        self.bulk_min_default = 1e-5

        self.bulk_max = 0.01  # maximum expression in bulk
        self.bulk_max_default = 0.01

        self.disp_min = 0.5  # minimum dispersion for highly variable genes
        self.disp_min_default = 0.5

        self.maxiter = 1000  # maximum annealing iterations
        self.maxiter_default = 1000

        self.N_repeat = 10  # deconvolution repeats in case of repeatanneal
        self.N_repeat_default = 10

        # basic layout considerations
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.grid(columnspan=7, rowspan=14)
        # for easier grid layout changes
        i_i = 1  # start of import section
        p_i = 5  # start of parameter section
        d_i = 11  # start of deconv section

        """ logo and welcome section """
        self.logo = Image.open(resource_path('logo_orange.png'))
        # convert pillow image to tkinter image
        self.logo = ImageTk.PhotoImage(self.logo)
        # place image inside label widget (both lines below are needed)
        self.logo_label = tk.Label(image=self.logo)
        self.logo_label.image = self.logo
        # place the self.logo label inside the box using grid method
        self.logo_label.grid(column=0, columnspan=2, sticky=tk.W+tk.E, row=0)

        self.welcome_label = tk.Label(
            text='Welcome to cellanneal, the user-friendly bulk deconvolution software.\nPlease visit the doumentation at https://github.com/LiBuchauer/cellanneal for instructions.',
            wraplength=450)
        self.welcome_label.grid(column=2, columnspan=4, sticky=tk.W+tk.E, row=0)
        # for buttons belows
        self.ca_button = Image.open(resource_path('cellanneal_button.png'))
        self.ca_button = ImageTk.PhotoImage(self.ca_button)
        self.ca_label = tk.Label(image=self.ca_button)
        self.ca_label.image = self.ca_button

        self.ra_button = Image.open(resource_path('repeatanneal_button.png'))
        self.ra_button = ImageTk.PhotoImage(self.ra_button)
        self.ra_label = tk.Label(image=self.ra_button)
        self.ra_label.image = self.ra_button

        """ main section labels, structure """
        self.sec1_label = tk.Label(root, text="1) Select source data \nand output folder.", font="-weight bold")
        self.sec2_label = tk.Label(root, text="2) Set parameters. \n[optional]", font="-weight bold")
        self.sec3_label = tk.Label(root, text="3) Run deconvolution.", font="-weight bold")
        self.sec1_label.grid(row=i_i, column=0, sticky='w')
        self.sec2_label.grid(row=p_i, column=0, sticky='w')
        self.sec3_label.grid(row=d_i, column=0, sticky='w')

        """ data import section """
        # import bulk data
        # label to indicate that we want bulk data here
        self.bulk_data_label = tk.Label(
                                    root,
                                    text="Select bulk data (*.csv).")
        self.bulk_data_label.grid(row=i_i, column=1, columnspan=2, sticky=tk.W)
        # path entry field
        self.bulk_data_entry = tk.Entry(
                                    root,
                                    textvariable=self.bulk_data_path)
        self.bulk_data_entry.grid(row=i_i, column=3, columnspan=2, sticky=tk.W+tk.E)
        # file system browse button
        self.bulk_browse_button = tk.Button(
                                        root,
                                        text="Browse file system",
                                        command=lambda: self.import_bulk_data())
        self.bulk_browse_button.grid(row=i_i, column=5, columnspan=2, sticky=tk.W+tk.E)

        # import celltype data
        # label to indicate that we want celltype data here
        self.celltype_data_label = tk.Label(root, text="Select celltype data (*.csv).")
        self.celltype_data_label.grid(row=i_i+1, column=1, columnspan=2, sticky=tk.W)
        # path entry field
        self.celltype_data_entry = tk.Entry(root, textvariable=self.celltype_data_path)
        self.celltype_data_entry.grid(row=i_i+1, column=3, columnspan=2, sticky=tk.W+tk.E)
        # file system browse button
        self.celltype_browse_button = tk.Button(
                                        root,
                                        text="Browse file system",
                                        command=lambda: self.import_celltype_data())
        self.celltype_browse_button.grid(row=i_i+1, column=5, columnspan=2, sticky=tk.W+tk.E)

        # select output folder
        # label to indicate that we want celltype data here
        self.output_folder_label = tk.Label(root, text="Select folder to store results.")
        self.output_folder_label.grid(row=i_i+2, column=1, columnspan=2, sticky=tk.W)
        # path entry field
        self.output_folder_entry = tk.Entry(root, textvariable=self.output_path)
        self.output_folder_entry.grid(row=i_i+2, column=3, columnspan=2, sticky=tk.W+tk.E)
        # file system browse button
        self.celltype_browse_button = tk.Button(
                                        root,
                                        text="Browse file system",
                                        command=lambda: self.select_output_folder())
        self.celltype_browse_button.grid(row=i_i+2, column=5, columnspan=2, sticky=tk.W+tk.E)

        """ parameter section """
        # for parameter bulk_min
        # title label and current value
        self.bulk_min_label = tk.Label(root, text="minimum expression in bulk", font="-weight bold")
        self.bulk_min_label.grid(row=p_i, column=1, columnspan=2, sticky=tk.W+tk.E)
        self.bulk_min_current_label = tk.Label(root, text="current value: {}".format(self.bulk_min), font="-slant italic")
        self.bulk_min_current_label.grid(row=p_i+1, column=1, columnspan=2, sticky=tk.W+tk.E)

        # entry field
        self.bulk_min_entry = tk.Entry(
                                    root,
                                    width=8)
        self.bulk_min_entry.grid(row=p_i+2, column=1, sticky=tk.E)
        self.bulk_min_entry.insert(tk.END, '1e-5')
        # set button
        self.bulk_min_set_button = tk.Button(
                                        root,
                                        text='set',
                                        command=lambda: self.set_bulk_min(),
                                        width=8)
        self.bulk_min_set_button.grid(row=p_i+2, column=2, sticky=tk.W)

        # for parameter bulk_max
        # title label and current value
        self.bulk_max_label = tk.Label(root, text="maximum expression in bulk", font="-weight bold")
        self.bulk_max_label.grid(row=p_i, column=3, columnspan=2, sticky=tk.W+tk.E)
        self.bulk_max_current_label = tk.Label(root, text="current value: {}".format(self.bulk_max), font="-slant italic")
        self.bulk_max_current_label.grid(row=p_i+1, column=3, columnspan=2, sticky=tk.W+tk.E)

        # entry field
        self.bulk_max_entry = tk.Entry(
                                    root,
                                    width=8)
        self.bulk_max_entry.grid(row=p_i+2, column=3, sticky=tk.E)
        self.bulk_max_entry.insert(tk.END, '0.01')

        # set button
        self.bulk_max_set_button = tk.Button(
                                        root,
                                        text='set',
                                        command=lambda: self.set_bulk_max(),
                                        width=8)
        self.bulk_max_set_button.grid(row=p_i+2, column=4, sticky=tk.W)


        # for parameter disp_min
        # title label and current value
        self.disp_min_label = tk.Label(root, text="minimum dispersion", font="-weight bold")
        self.disp_min_label.grid(row=p_i, column=5, columnspan=2, sticky=tk.W+tk.E)
        self.disp_min_current_label = tk.Label(root, text="current value: {}".format(self.disp_min), font="-slant italic")
        self.disp_min_current_label.grid(row=p_i+1, column=5, columnspan=2, sticky=tk.W+tk.E)

        # entry field
        self.disp_min_entry = tk.Entry(
                                    root,
                                    width=8)
        self.disp_min_entry.grid(row=p_i+2, column=5, sticky=tk.E)
        self.disp_min_entry.insert(tk.END, '0.5')

        # set button
        self.disp_min_set_button = tk.Button(
                                        root,
                                        text='set',
                                        command=lambda: self.set_disp_min(),
                                        width=8)
        self.disp_min_set_button.grid(row=p_i+2, column=6, sticky=tk.W)

        # for parameter maxiter
        # title label and current value
        self.maxiter_label = tk.Label(root, text="maximum number of\nannealing iterations", font="-weight bold")
        self.maxiter_label.grid(row=p_i+3, column=1, columnspan=2, sticky=tk.W+tk.E)
        self.maxiter_current_label = tk.Label(root, text="current value: {}".format(self.maxiter), font="-slant italic")
        self.maxiter_current_label.grid(row=p_i+4, column=1, columnspan=2, sticky=tk.W+tk.E)

        # entry field
        self.maxiter_entry = tk.Entry(
                                    root,
                                    width=8)
        self.maxiter_entry.grid(row=p_i+5, column=1, sticky=tk.E)
        self.maxiter_entry.insert(tk.END, '1000')

        # set button
        self.maxiter_set_button = tk.Button(
                                        root,
                                        text='set',
                                        command=lambda: self.set_maxiter(),
                                        width=8)
        self.maxiter_set_button.grid(row=p_i+5, column=2, sticky=tk.W)

        # for parameter N_repeat
        # title label and current value
        self.N_repeat_label = tk.Label(root, text="number of repeats\n(relevant for repeatanneal)", font="-weight bold")
        self.N_repeat_label.grid(row=p_i+3, column=3, columnspan=2, sticky=tk.W+tk.E)
        self.N_repeat_current_label = tk.Label(root, text="current value: {}".format(self.N_repeat), font="-slant italic")
        self.N_repeat_current_label.grid(row=p_i+4, column=3, columnspan=2, sticky=tk.W+tk.E)

        # entry field
        self.N_repeat_entry = tk.Entry(
                                    root,
                                    width=8)
        self.N_repeat_entry.grid(row=p_i+5, column=3, sticky=tk.E)
        self.N_repeat_entry.insert(tk.END, '10')
        # set button
        self.N_repeat_set_button = tk.Button(
                                        root,
                                        text='set',
                                        command=lambda: self.set_N_repeat(),
                                        width=8)
        self.N_repeat_set_button.grid(row=p_i+5, column=4, sticky=tk.W)


        """ run deconvolution section """
        # make button for cellanneal
        self.cellanneal_button = tk.Button(
                                        root,
                                        text='cellanneal',
                                        font="-weight bold ",
                                        image=self.ca_button,
                                        highlightbackground='#f47a60',
                                        command=lambda: self.cellanneal())
        self.cellanneal_button.grid(
                                row=d_i,
                                column=1,
                                columnspan=2,
                                sticky=tk.W+tk.E,
                                padx=10, pady=10)

        # make button for cellanneal
        self.repeatanneal_button = tk.Button(
                                        root,
                                        text='repeatanneal',
                                        font="-weight bold ",
                                        image=self.ra_button,
                                        command=lambda: self.repeatanneal(),
                                        highlightbackground='#f47a60')
        self.repeatanneal_button.grid(
                                    row=d_i,
                                    column=3,
                                    columnspan=2,
                                    sticky=tk.W+tk.E,
                                    padx=10, pady=10)


    # methods
    def import_bulk_data(self):
        file = askopenfile(
                parent=root,
                mode='rb',
                title="Choose a csv file.",
                filetypes=[("csv file", "*.csv")])
        if file:
            try:
                self.bulk_df = pd.read_csv(file, index_col=0)
                self.bulk_data_path.set(file.name)
                self.bulk_df_is_set = 1
            except:
                messagebox.showerror("Import error", """Your bulk data file could not be imported. Please check the documentation for format requirements and look at the example bulk data file.""")

    def import_celltype_data(self):
        file = askopenfile(
                parent=root,
                mode='rb',
                title="Choose a csv file.",
                filetypes=[("csv file", "*.csv")])
        if file:
            try:
                self.celltype_df = pd.read_csv(file, index_col=0)
                self.celltype_data_path.set(file.name)
                self.celltype_df_is_set = 1
            except:
                messagebox.showerror("Import error", """Your celltype data file could not be imported. Please check the documentation for format requirements and look at the example celltype data file.""")

    def select_output_folder(self):
        folder = askdirectory(
                parent=root,
                title="Choose a folder.")
        if folder:
            self.output_path.set(folder)
            self.output_path_is_set = 1

    def set_bulk_min(self):
        # get input and check validity
        input = self.bulk_min_entry.get()
        # can it be interpreted as float?
        try:
            new_val = float(input)
        except ValueError:
            messagebox.showerror("Input error", """Please provdide a numerical value between 0 (inclusive) and 1 (exclusive). Examples: "0", "0.01", "2e-5".""")
            return 0
        # check if value is between 0 and 1 and smaller than bulk_max
        if (0 <= new_val < 1) and (new_val < self.bulk_max):
            # update bulk_min
            self.bulk_min = new_val
            # update displa of current bulk_min
            self.bulk_min_current_label['text'] = "current value: {}".format(self.bulk_min)
        elif not (0 <= new_val < 1):
            messagebox.showerror("Input error", """Please provdide a numerical value between 0 (inclusive) and 1 (exclusive). Examples: "0", "0.01", "2e-5".""")
        elif not (new_val < self.bulk_max):
            messagebox.showerror("Input error", """Your value must be smaller than bulk_max.""")

    def set_bulk_max(self):
        # get input and check validity
        input = self.bulk_max_entry.get()
        # can it be interpreted as float?
        try:
            new_val = float(input)
        except ValueError:
            messagebox.showerror("Input error", """Please provdide a numerical value between 0 (exclusive) and 1 (inclusive). Examples: "0.01", "2e-5", "1".""")
            return 0
        # check if value is between 0 and 1 and if it is larger than bulk_min
        if (0 < new_val <= 1) and (new_val > self.bulk_min):
            # update bulk_min
            self.bulk_max = new_val
            # update display of current bulk_min
            self.bulk_max_current_label['text'] = "current value: {}".format(self.bulk_max)
        elif not (0 < new_val <= 1):
            messagebox.showerror("Input error", """Please provdide a numerical value between 0 (exclusive) and 1 (inclusive). Examples: "0.01", "2e-5", "1".""")
        elif not (new_val > self.bulk_min):
            messagebox.showerror("Input error", """Your value must be larger than bulk_min.""")

    def set_disp_min(self):
        # get input and check validity
        input = self.disp_min_entry.get()
        # can it be interpreted as float?
        try:
            new_val = float(input)
        except ValueError:
            messagebox.showerror("Input error", """Please provdide a positive numerical value. Examples: "0.5", "5e-1", "1".""")
            return 0
        # check if value is >0
        if new_val >= 0:
            # update disp_min
            self.disp_min = new_val
            # update display of current bulk_min
            self.disp_min_current_label['text'] = "current value: {}".format(self.disp_min)
        else:
            messagebox.showerror("Input error", """Please provdide a positive numerical value. Examples: "0.5", "5e-1", "1".""")

    def set_maxiter(self):
        # get input and check validity
        input = self.maxiter_entry.get()
        # can it be interpreted as float?
        try:
            new_val = int(input)
        except ValueError:
            messagebox.showerror("Input error", """Please provdide a positive integer. Examples: "50", "587", "1000".""")
            return 0
        # check if value is >0
        if new_val >= 1:
            # update disp_min
            self.maxiter = new_val
            # update display of current bulk_min
            self.maxiter_current_label['text'] = "current value: {}".format(self.maxiter)
        else:
            messagebox.showerror("Input error", """Please provdide a positive integer. Examples: "50", "587", "1000".""")

    def set_N_repeat(self):
        # get input and check validity
        input = self.N_repeat_entry.get()
        # can it be interpreted as float?
        try:
            new_val = int(input)
        except ValueError:
            messagebox.showerror("Input error", """Please provdide a positive integer. Examples: "5", "10", "21".""")
            return 0
        # check if value is >0
        if new_val >= 1:
            # update disp_min
            self.N_repeat = new_val
            # update display of current bulk_min
            self.N_repeat_current_label['text'] = "current value: {}".format(self.N_repeat)
        else:
            messagebox.showerror("Input error", """Please provdide a positive integer. Examples: "5", "10", "21".""")

    def cellanneal(self):
        # check if input and output is set
        if self.bulk_df_is_set == 0:
            messagebox.showerror("Data error", """Please select a bulk data file in section 1).""")
            return 0
        if self.celltype_df_is_set == 0:
            messagebox.showerror("Data error", """Please select a celltype data file in section 1).""")
            return 0
        if self.output_path_is_set == 0:
            messagebox.showerror("Data error", """Please select a folder for storing results in section 1).""")
            return 0

        print("\n\n+++ Welcome to cellanneal! +++ \n\n")
        # check if subprocess is still running, if so don't open another one
        cellanneal_pipe(
            Path(self.celltype_data_path.get()),  # path object!
            self.celltype_df,
            Path(self.bulk_data_path.get()),  # path object!
            self.bulk_df,
            self.disp_min,
            self.bulk_min,
            self.bulk_max,
            self.maxiter,
            Path(self.output_path.get()))  # path object!

    def repeatanneal(self):
        # check if input and output is set
        if self.bulk_df_is_set == 0:
            messagebox.showerror("Data error", """Please select a bulk data file in section 1).""")
            return 0
        if self.celltype_df_is_set == 0:
            messagebox.showerror("Data error", """Please select a celltype data file in section 1).""")
            return 0
        if self.output_path_is_set == 0:
            messagebox.showerror("Data error", """Please select a folder for storing results in section 1).""")
            return 0
        print("\n\n+++ Welcome to cellanneal! +++ \n\n")
        # check if subprocess is still running, if so don't open another one
        repeatanneal_pipe(
            Path(self.celltype_data_path.get()),  # path object!
            self.celltype_df,
            Path(self.bulk_data_path.get()),  # path object!
            self.bulk_df,
            self.disp_min,
            self.bulk_min,
            self.bulk_max,
            self.maxiter,
            self.N_repeat,
            Path(self.output_path.get()))  # path object!


root = tk.Tk()
ca_gui = cellgui(root)
root.mainloop()

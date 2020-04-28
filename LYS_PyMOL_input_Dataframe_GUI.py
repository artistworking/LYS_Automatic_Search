#CITATION https://www.biorxiv.org/content/10.1101/540229v1
#TKINKER IMPORTS
import tkinter
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames
from tkinter.messagebox import showerror
#Other imports
import sys, ast, json
import os
import argparse
import numpy as np
import pandas as pd
from pandas import Series
import itertools
import ntpath
import numbers
import decimal
#Biopython
# from Bio.Alphabet.IUPAC import ExtendedIUPACProtein
# from Bio.Alphabet import generic_protein
# from Bio import SeqRecord,Alphabet,SeqIO
# from Bio.SeqIO import SeqRecord
# from Bio.Seq import Seq
# from Bio import SeqIO
# import Bio.PDB as PDB
# from Bio.Seq import MutableSeq
# from Bio.PDB.Polypeptide import is_aa
# from Bio.SeqUtils import seq1
# from Bio.SeqRecord import SeqRecord
# from Bio.Alphabet import IUPAC
# from Bio.pairwise2 import format_alignment
#PyMOL
import inspect
import pymol
print(inspect.getmodule(pymol))
from pymol import cmd
from pymol.cgo import *
from pymol.vfont import plain
#Readline
try:
  import readline #Linux
except ImportError:
  import pyreadline as readline #Windows
import rlcompleter


def Treatment(Variable):
    try:
        Variable = eval(Variable)
    except:
        pass
    return Variable
def Folders(Genes, folder_name):
    """ Folder for all the generated images It will updated everytime!!! Save the previous folder before running again. Give full path to the Genes sequences file"""
    import os
    import shutil
    basepath = os.path.dirname(Genes)
    if not basepath:
        newpath = folder_name
    else:
        newpath = basepath + "/%s" % folder_name

    if not os.path.exists(newpath):
        try:
            original_umask = os.umask(0)
            os.makedirs(newpath, 0o777)
        finally:
            os.umask(original_umask)
    else:
        shutil.rmtree(newpath)  # removes all the subdirectories!
        os.makedirs(newpath,0o777)
def Pymol(Dataframe_path,angle_x,angle_y,angle_z,lab_x,lab_y,lab_z,zoom,shape):
    '''Visualization program'''

    #LAUNCH PYMOL
    launch=True
    if launch:
        pymol.pymol_argv = ['pymol'] + sys.argv[1:]
        pymol.finish_launching(['pymol'])
    #pymol. finish_launching()

    # Read User Input: PDB file should be in the folder created by LYS_PDB_Search
    PDB_file = os.path.abspath(os.path.join(os.path.dirname(Dataframe_path), '..','PDB_files',ntpath.basename(Dataframe_path).split('_')[-2]))
    sname = ntpath.basename(Dataframe_path).split('_')[1]  # Extract the filename without the path
    # Dataframe_path = os.path.abspath(sys.argv[2])  # Dataframe generated by LYS.py
    Dataframe = pd.read_csv(Dataframe_path, sep='\t')
    # Load Structures
    pymol.cmd.load(PDB_file, sname)
    pymol.cmd.disable("all")  # toggles off the display of all currently visible representations of an object. It is the equivalent of deselecting the object
    pymol.cmd.enable(sname)


    def Colour_by_Selection(selection="all",
                            Selected="orange",
                            Not='grey50',
                            Domain='lime',
                            Selected_and_Domain='magenta',
                            ):

        colors = {
            'Selected': Selected,
            'Not': Not,
            'Domain': Domain,
            'Selected_and_Domain': Selected_and_Domain
        }

        #BACKGROUND & SHAPES
        cmd.bg_color('white')
        cmd.show_as(shape, 'all')
        cmd.color('gray', 'all')
        #ROTATION
        cmd.rotate([1,0,0], angle = float(angle_x),selection = "all") # Commands to rotate the structures to visualize some specific side of the protein [x,y,z]
        cmd.rotate([0,1,0], angle = float(angle_y),selection = "all") # Commands to rotate the structures to visualize some specific side of the protein [x,y,z]
        cmd.rotate([0,0,1], angle = float(angle_z),selection = "all") # Commands to rotate the structures to visualize some specific side of the protein [x,y,z]

        #ELIMINATING CHAINS
        # Eliminating chains in the structure if desired
        # cmd.select('chainA', 'chain A')
        # cmd.remove('chain A')


        #LEGEND
        ###The text that appears in the image, change placement accordingly
        cgo = []
        axes = [[5.0, 0.0, 0.0], [0.0, 5.0, 0.0],[0.0, 0.0, 5.0]]  # Change the values if the protein does not quite fall into place

        cyl_text(cgo, plain, [float(lab_x),float(lab_y), float(lab_z)], '%s' % (ntpath.basename(Dataframe_path).split('_')[0:2]), radius=0.6, color=[0.0, 0.0, 0.0],axes=axes)  # x=60 for RIOK2, x=40 and z=60 for ROS1
        cyl_text(cgo, plain, [float(lab_x), float(lab_y)-10.0, float(lab_z)], 'Positively Selected', radius=0.6, color=[1.0, 0.5, 0.0], axes=axes)
        cyl_text(cgo, plain, [float(lab_x), float(lab_y)-20.0, float(lab_z)], 'Not selected', radius=0.6, color=[0.5, 0.5, 0.5], axes=axes)
        cyl_text(cgo, plain, [float(lab_x), float(lab_y)-30.0, float(lab_z)], 'Functional Domain', radius=0.6, color=[0.5, 1.0, 0.5], axes=axes)
        cyl_text(cgo, plain, [float(lab_x), float(lab_y)-40.0, float(lab_z)], 'Both', radius=0.6, color=[1.0, 0.0, 1.0], axes=axes)

        cmd.set("cgo_line_radius", 0.03)  # 0.03
        cmd.load_cgo(cgo, 'txt')
        #ZOOM
        cmd.zoom("all", zoom)  # Higher and positive values zoom  out, it accepts negative values

        #READ PREVIOUSLY CREATED DATAFRAME:

        #Option A: best alternative
        Dataframe['PDB_Position'] = Dataframe['PDB_Position'].astype(np.float64) #Need to convert to float to use isfinite
        Data = Dataframe[np.isfinite(Dataframe['PDB_Position'])]  # Remove the Residues that got 'nan' value in their equivalent positions
        position_phenotype_dict = Series(Data.Label.values, index=Data.PDB_Position).to_dict()
        #Option B: Not working sometimes
        # position_phenotype_dict = Series(Data.Label, index=Data.PDB_Position).to_dict() #suboption B
        # print(position_phenotype_dict)
        # from math import isnan
        # position_phenotype_dict = {k: position_phenotype_dict[k] for k in position_phenotype_dict if not isnan(k)}
        # position_phenotype_dict= {key: value for key, value in position_phenotype_dict.items() if not str(value) == 'nan'}

        # Colour the residues in the protein according to their label in the dataframe
        for key, value in position_phenotype_dict.items():
            #print(int(key), value, colors[value])
            cmd.color(colors[value], 'resi %s' % int(key))  # --------->If it does not work (no colour shown) probably it has to do with the Residues ID being wrong
            ###LABEL
            if value == 'Selected_and_Domain': #Label the alpha carbon from positions selected and in the domain
                print(key)
                #cmd.select('Both','resi %s' % int(key)) #Create a selection
                #cmd.label('Both and n. CA', '" %s %s" % (resn,resi)')
                cmd.label('resi %s and n. CA' % int(key), '" %s %s" % (resn,resi)')
                #cmd.label('resi %s' % int(key), '" %s %s" % (resn,resi)')

    cmd.extend("Colour_by_Selection", Colour_by_Selection)
    print("Structure will be at %s" % (os.path.abspath(os.path.join(os.path.dirname(Dataframe_path), '..','LYS_Pymol_Images'))))
    Colour_by_Selection(sname)
    pymol.cmd.png(os.path.abspath(os.path.join(os.path.dirname(Dataframe_path), '..','LYS_Pymol_Images',ntpath.basename(Dataframe_path))),dpi=600)


class MyFrame(Frame):
    def button_action(self): #Insert all the default values here
        pymol.cmd.reinitialize('everything')
        #Required arguments
        try:
            self.Dataframe = self.button1_entry.get()

        except:
            self.Dataframe = []

        #OPTIONAL ARGUMENTS

        try:
            self.Angle_x = self.angle_x.get()
        except:
            self.Angle_x = 0
        try:
            self.Angle_y = self.angle_y.get()
        except:
            self.Angle_y = 0
        try:
            self.Angle_z = self.angle_z.get()
        except:
            self.Angle_z = 0

        try:
            self.lab_x = self.label_x.get()
            self.lab_y = self.label_y.get()
            self.lab_z = self.label_z.get()
        except:
            self.lab_x = 70
            self.lab_y = 50
            self.lab_z = 80
        try:
            self.zoom = self.zoom_entry.get()
        except:
            self.zoom = 10
        try:
            self.shape = self.shape_entry.get()
        except:
            self.shape = "cartoon"



    def __init__(self,den):
        Frame.__init__(self,den)
        self.master.rowconfigure(10, weight=1)
        self.master.columnconfigure(7, weight=0)
        #self.grid(sticky=W + E + N + S)
        #####Required arguments:
        self.button1 = Button(den, text="Browse Positions Dataframe*", command=self.load_PDB, width=35)
        self.button1_entry=Entry(den)


        #####Optional arguments:

        #Rotate protein (x,y,z entries)
        self.angle_x_label = Label(den,text='Rotation axis x')
        self.angle_y_label = Label(den,text='Rotation axis y')
        self.angle_z_label = Label(den,text='Rotation axis z')
        self.angle_x = Entry(den,width=5)
        self.angle_y = Entry(den,width=5)
        self.angle_z = Entry(den,width=5)

        #Label placement (x,y,z entries)
        self.label_label = Label(den, text='Label Placement')
        self.label_x = Entry(den,width=5)
        self.label_y = Entry(den,width=5)
        self.label_z = Entry(den,width=5)
        #Zoom
        self.zoom_label = Label(den,text='Zoom')
        self.zoom_entry= Entry(den,width=5)
        #Shape
        self.shape_label=Label(den,text="Residues shape")
        self.shape_entry=Entry(den,width=7)
        #Default values shown to user

        self.angle_x.insert(0,0)
        self.angle_y.insert(0,0)
        self.angle_z.insert(0,0)
        self.label_x.insert(0,70)
        self.label_y.insert(0,50)
        self.label_z.insert(0,80)
        self.zoom_entry.insert(0,10)
        self.shape_entry.insert(0,"cartoon")


        ##RUN
        self.run = Button(den, text="RUN", command=lambda: [f() for f in [self.button_action, self.quit,self.destroy]],width=40, background='green')
        #self.run = Button(den, text="RUN", command= self.button_action,width=35)
        #self.run.bind("<Button-1>",self.destroy())
        ##GRID ######
        self.button1.grid(row=0, column=0)
        self.button1_entry.grid(row=0,column=1)

        self.angle_x_label.grid(row=0, column=2)
        self.angle_y_label.grid(row=1, column=2)
        self.angle_z_label.grid(row=2, column=2)
        self.angle_x.grid(row=0, column=3)
        self.angle_y.grid(row=1, column=3)
        self.angle_z.grid(row=2, column=3)
        self.label_label.grid(row=3, column=2)
        self.label_x.grid(row=3, column=3)
        self.label_y.grid(row=3, column=4)
        self.label_z.grid(row=3, column=5)
        self.zoom_label.grid(row=4, column=2)
        self.zoom_entry.grid(row=4, column=3)
        self.shape_label.grid(row=2,column=0)
        self.shape_entry.grid(row=2,column=1)
        self.run.grid(row=8, column=1)

    def load_PDB(self):
        PDB=askopenfilename()
        if PDB:
            try:
                self.PDB_file = PDB
                self.button1_entry.insert(0, self.PDB_file)
            except:
                showerror("Open Source File", "Failed to read file\n'%s'" % PDB)
            return
        else:
            print('Missing Positions Dataframe file')


if __name__ == "__main__":

     #Lists for one-time memory
     List = []
     List_angle_x=[]
     List_angle_y=[]
     List_angle_z=[]
     Label_x=[]
     Label_y=[]
     Label_z=[]
     List_zoom=[]
     List_shape=[]

     try:
        List = List[0]
        List_angle_x = List_angle_x[0]
        List_angle_y = List_angle_y[0]
        List_angle_z = List_angle_z[0]
        Label_x = Label_x[0]
        Label_y = Label_y[0]
        Label_z = Label_z[0]
        List_zoom = List_zoom[0]
        List_shape=List_shape[0]

     except:
         pass
     while True:
         #pymol.cmd.quit()
         den = tkinter.Tk()
         den.title("Link Your Sites GUI")
         prompt = MyFrame(den)
         try:
            prompt.button1_entry.insert(0,List[0]) #dataframe
            prompt.label_x.delete(0, "end")
            prompt.label_x.insert(0,Label_x[0])
            prompt.label_y.delete(0, "end")
            prompt.label_y.insert(0,Label_y[0])
            prompt.label_z.delete(0, "end")
            prompt.label_z.insert(0,Label_z[0])
            prompt.angle_x.delete(0, "end")
            prompt.angle_x.insert(0,List_angle_x[0])
            prompt.angle_y.delete(0, "end")
            prompt.angle_y.insert(0,List_angle_y[0])
            prompt.angle_z.delete(0, "end")
            prompt.angle_z.insert(0,List_angle_z[0])
            prompt.zoom_entry.delete(0, "end")
            prompt.zoom_entry.insert(0,List_zoom[0])
            prompt.shape_entry.delete(0,"end")
            prompt.shape_entry.insert(0,List_shape[0])
         except:
             pass
         del List[:]
         del List_angle_x[:]
         del List_angle_y[:]
         del List_angle_z[:]
         del Label_x[:]
         del Label_y[:]
         del Label_z[:]
         del List_zoom[:]
         del List_shape[:]

         den.mainloop()
         #VARIABLES:
         #####Required
         Dataframe = prompt.Dataframe
         List.append(Dataframe)

         ###Optional
         List_angle_x.append(prompt.Angle_x)
         List_angle_y.append(prompt.Angle_y)
         List_angle_z.append(prompt.Angle_z)
         Label_x.append(prompt.lab_x)
         Label_y.append(prompt.lab_y)
         Label_z.append(prompt.lab_z)
         List_zoom.append(prompt.zoom)
         List_shape.append(prompt.shape)
         angle_x = Treatment(prompt.Angle_x)
         angle_y = Treatment(prompt.Angle_y)
         angle_z = Treatment(prompt.Angle_z)
         label_x = Treatment(prompt.lab_x)
         label_y = Treatment(prompt.lab_y)
         label_z = Treatment(prompt.lab_z)
         zoom = Treatment(prompt.zoom)
         shape=prompt.shape


         den.destroy() #now is working (destroying the root)

         #PYMOL
         #Folder for images: Do not create the folder if already created before
         #Folders(Dataframe, "LYS_Pymol_Images")
         Pymol(Dataframe,angle_x,angle_y,angle_z,label_x,label_y,label_z,zoom,shape)

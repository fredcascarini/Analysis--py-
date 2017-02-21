# -*- coding: utf-8 -*-
"""
Created on Thu Nov 03 11:56:54 2016

@author: fc16020
"""
import matplotlib
matplotlib.use("TkAgg")
import Tkinter as Tk
import Tkconstants as Tkc
import tkFileDialog as tkFD
from analysis import analyse_file as af
from analysis import generate_dcs as gDCS
from analysis import dcs_cos_hist as gHIS
from analysis import generate_pd_arr as gPDA
import os
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

class TkWindow(Tk.Frame):
    
    def __init__ (self, root):
        
        Tk.Frame.__init__(self, root)
        
        self.var = Tk.StringVar()
        self.directory = Tk.StringVar()
        self.SucCount = 0
        self.DCS_Run = 0
        self.HIST_Run = 0
        self.FPDA_Run = 0
        self.pdchoice = {}
        self.pd_data = 0
        self.pd_data_arr = 0
        self.pd_counter_arr = 0
        
        # options for buttons
        button_opt = {'fill': Tkc.BOTH, 'padx': 5, 'pady': 5}

        # define buttons:
        NewAnalysis = Tk.Button(self, text = 'Initialise', command = self.create_analysis_window)
        FindLength = Tk.Button(self, text='Confirm Initialisation', command = self.checklen)
        
        # pack buttons
        NewAnalysis.pack(**button_opt)
        FindLength.pack(**button_opt)
        
        self.file_opt = options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt'), ('csv files', '.csv')]
        options['initialdir'] = os.getcwd()
        options['initialfile'] = ''
        options['parent'] = root
        options['title'] = 'Select txt file'
        
        self.dir_opt = options = {}
        options['initialdir'] = os.getcwd()
        options['mustexist'] = True
        options['parent'] = root
        options['title'] = 'Select directory'

    def create_analysis_window(self):
        self.CAW = Tk.Toplevel(self)
        # define buttons:
        DirExplainLabel = Tk.Label(self.CAW, text = 'Select directory that contains the batch folders')
        DirNameButton = Tk.Button(self.CAW, text = 'Select directory', command= lambda: self.askdirectory())
        AnlyFileButton = Tk.Button(self.CAW, text = 'Run initial analysis', command= lambda: self.analyse())
        DirectoryEntry = Tk.Entry(self.CAW, textvariable = self.directory)
        QuitWindow     = Tk.Button(self.CAW, text = 'Close', command = lambda: self.CAW.destroy())
        
        # pack buttons
        DirExplainLabel.pack()
        DirNameButton.pack()
        AnlyFileButton.pack()
        DirectoryEntry.pack()
        QuitWindow.pack()


    def askdirectory(self):
        
        directory = tkFD.askdirectory(**self.dir_opt)
        if directory:
            self.directory.set(directory)
        
        
    def analyse(self):
        
        dirname = self.directory.get()
        self.pd_data, self.pd_data_arr,  self.pd_counter_array  = af(isDir = True, dirname = dirname)
        self.pdchoice['data'] = self.pd_data
        self.pdchoice['data_arr'] = self.pd_data_arr
        self.pdchoice['counter_arr'] = self.pd_counter_array
        self.CAW.destroy()
    
    def checklen(self):
        try:
            x = len(self.pd_data_arr)
            if x != 0:
                if self.SucCount == 0:
                    self.createsuccesswindow()
                else:
                    self.createdatawindow()
            else:
                print 'empty data set'
        except AttributeError:
            print 'Run "New Analysis" first'
            
    def createsuccesswindow(self):
        
        self.SucCount = 1
        self.SUC = Tk.Toplevel(self)
        SuccessText = Tk.Label(self.SUC,text='Success!')
        SuccessOK = Tk.Button(self.SUC, text = 'OK', command = self.createdatawindow)
        SuccessText.pack()
        SuccessOK.pack()
        
    def createdatawindow(self):
        self.DTW = Tk.Toplevel(self)
        self.SUC.destroy()
        Create_Graph = Tk.Button(self.DTW, text = 'Create Graphs', command = self.creategraphwindow)
        Further_Anyl = Tk.Button(self.DTW, text = 'Further Analysis', command = self.createFAwindow)
        Save_CSV     = Tk.Button(self.DTW, text = 'Create CSV', command = self.createcsvwindow)
        Quit_Button  = Tk.Button(self.DTW, text = 'Quit to Home', command = lambda: self.DTW.destroy())
        
        Create_Graph.pack()
        Further_Anyl.pack()
        Save_CSV.pack()
        Quit_Button.pack()
        
    def createFAwindow(self):
        
        self.FAW = Tk.Toplevel(self)
        if self.DCS_Run == 0:
            Gen_DCS  = Tk.Button(self.FAW, text = 'Generate DCS', command = self.GenDCS)
            Gen_DCS.pack()
            
        if self.HIST_Run == 0:
            Gen_HIST = Tk.Button(self.FAW, text = 'Generate DCS approx.', command = self.GenHIST)
            Gen_HIST.pack()
        
        if self.FPDA_Run == 0:
            Gen_FPDA = Tk.Button(self.FAW, text = 'Generate further arrays', command = self.GenFPDA)
            Gen_FPDA.pack()
        
        if self.DCS_Run != 0 and self.HIST_Run != 0 and self.FPDA_Run != 0:
            self.FAW.destroy()
        
        return None
        
    def GenDCS(self):
        
        self.DCS = Tk.Toplevel(self)
        
        self.FAW.destroy()
        
        JMAX = self.pd_data.NROT.max()
        VMAX = self.pd_data.NVIB.max()
        JRANGE = np.arange(-1,JMAX+1,1)
        VRANGE = np.arange(-1,VMAX+1,1)
        ORANGE = np.arange(1,10,1)
        DRANGE = np.arange(0.1,1,0.1)

        self.sJ = Tk.StringVar()
        self.sJ.set(JRANGE[0])
        self.sV = Tk.StringVar()
        self.sV.set(VRANGE[0])
        self.sO = Tk.StringVar()
        self.sO.set(ORANGE[0])
        self.sD = Tk.StringVar()
        self.sD.set(DRANGE[0])
        
        J_Select = Tk.OptionMenu(self.DCS,self.sJ,*JRANGE)
        V_Select = Tk.OptionMenu(self.DCS,self.sV,*VRANGE)
        O_Select = Tk.OptionMenu(self.DCS,self.sO,*ORANGE)
        D_Select = Tk.OptionMenu(self.DCS,self.sD,*DRANGE)
        J_Label = Tk.Label(self.DCS, text = 'Select J Value, -1 is no restriction')
        V_Label = Tk.Label(self.DCS, text = 'Select V Value, -1 is no restriction')
        O_Label = Tk.Label(self.DCS, text = 'Select Maximum Order')
        D_Label = Tk.Label(self.DCS, text = 'Select step in angle')
        RunDCSB = Tk.Button(self.DCS, text = 'Run', command = self.RunDCS)
        ReturnD = Tk.Button(self.DCS, text = 'Return', command = self.DCSReturn)
        
        J_Label.pack()
        J_Select.pack()
        V_Label.pack()
        V_Select.pack()
        O_Label.pack()
        O_Select.pack()
        D_Label.pack()
        D_Select.pack()
        RunDCSB.pack()
        ReturnD.pack()
        
    def RunDCS(self):
        
        self.pd_DCS = gDCS(self.pd_data,J_select=float(self.sJ.get()),v_select=float(self.sV.get()), order_max=int(self.sO.get()))
        if self.DCS_Run == 0:
            self.pdchoice['DCS'] = self.pd_DCS
            self.DCS_Run = 1
        self.DCSReturn()
      
    def DCSReturn(self):
        self.createFAwindow()
        self.DCS.destroy()
            
    def GenHIST(self):
        
        self.HIST = Tk.Toplevel(self)
        self.FAW.destroy()
        
        BRANGE = np.arange(1,8,1)
        
        self.sB = Tk.StringVar()
        self.sB.set(BRANGE[0])
        
        B_Select = Tk.OptionMenu(self.HIST,self.sB,*BRANGE)
        B_Label = Tk.Label(self.HIST, text = 'Select Number of Bins (multiple of 180)')
        RunHISTB = Tk.Button(self.HIST, text = 'Run', command = self.RunHIST)
        ReturnH = Tk.Button(self.HIST, text = 'Return', command = self.HISTReturn)
        
        B_Label.pack()
        B_Select.pack()
        RunHISTB.pack()
        ReturnH.pack()
        
        return None
    
    def RunHIST(self):
        
        self.pd_bins_array = gHIS(self.pd_data.CSTH, bins=int(self.sB.get()) * 180)
        if self.HIST_Run == 0:
            self.pdchoice['DCS approx'] = self.pd_bins_array
            self.HIST_Run = 1
        self.HISTReturn()
            
    def HISTReturn(self):
        self.createFAwindow()
        self.HIST.destroy()
        
    def GenFPDA(self):
        #generate_pd_arr(pd_data, success_counter, time_min = -1, time_max = -1, interval_power_of_half = 1)
        
        self.FPDA = Tk.Toplevel(self)
        self.FAW.destroy()
        
        self.TMAX = self.pd_data.TIME.max()

        self.sTmx = Tk.StringVar()
        self.sTmx.set(-1)
        self.sTmn = Tk.StringVar()
        self.sTmn.set(-1)
        self.sItv = Tk.StringVar()
        self.sItv.set(1)

        
        Tmx_Select = Tk.Entry(self.FPDA,textvariable = self.sTmx)
        Tmn_Select = Tk.Entry(self.FPDA,textvariable = self.sTmn)
        Itv_Select = Tk.Entry(self.FPDA,textvariable = self.sItv)

        Tmx_Label = Tk.Label(self.FPDA, text = 'Select maximum time, up to ' + str(self.TMAX) + ',-1 is no restriction')
        Tmn_Label = Tk.Label(self.FPDA, text = 'Select minimum time, -1 is no restriction')
        Itv_Label = Tk.Label(self.FPDA, text = 'Select time interval as a power of 1/2')
        RunFPDA = Tk.Button(self.FPDA, text = 'Run', command = self.RunFPDA)
        ReturnF = Tk.Button(self.FPDA, text = 'Return', command = self.FPDAReturn)
        
        Tmx_Label.pack()
        Tmx_Select.pack()
        Tmn_Label.pack()
        Tmn_Select.pack()
        Itv_Label.pack()
        Itv_Select.pack()
        RunFPDA.pack()
        ReturnF.pack()
        
        return None
    
    def RunFPDA(self):
        
        if float(self.sTmx.get()) > float(self.TMAX) or (float(self.sTmn.get()) >= float(self.sTmx.get()) and float(self.sTmn.get()) >= 0 ) :
            self.ErrFPDA = Tk.Toplevel(root)
            ErrorText = Tk.Label(self.ErrFPDA,text='Error in values passed')
            ErrorOK = Tk.Button(self.ErrFPDA, text = 'OK', command = lambda: self.ErrFPDA.destroy())
            ErrorText.pack()
            ErrorOK.pack()
            
        else:
            self.pd_counter_array_nvib, self.pd_counter_array_nrot, self.pd_time_bin_arr = gPDA(self.pd_data,self.pd_counter_array.SuccessfulTrajs, float(self.sTmn.get()), float(self.sTmx.get()), int(self.sItv.get()))
            if self.FPDA_Run == 0:
                self.pdchoice['NVIB counter'] = self.pd_counter_array_nvib
                self.pdchoice['NROT counter'] = self.pd_counter_array_nrot
                self.pdchoice['Time Bins'] = self.pd_time_bin_arr
                self.FPDA_Run = 1
            
            self.createFAwindow()
            self.FPDA.destroy()
            
        return None
    
    
    def FPDAReturn(self):
        self.createFAwindow()
        self.FPDA.destroy()
        
    def createcsvwindow(self):
        self.CSV = Tk.Toplevel(self)
        
        self.sPda = Tk.StringVar()
        self.sCna = Tk.StringVar()
        
        pd_options = Tk.OptionMenu(self.CSV, self.sPda, *(self.pdchoice.keys()))
        csv_nameEn = Tk.Entry(self.CSV, textvariable = self.sCna)
        name_entry_label = Tk.Label(self.CSV, text = 'Name to save csv as:')
        RunCSV = Tk.Button(self.CSV, text = 'Run', command = self.RunCCsv)
        pd_options.pack()
        if self.DCS_Run != 0:
            DCS_label = Tk.Label(self.CSV, text='DCS Reminder: J_Select = ' + str(self.sJ.get()) + ' V_Select = ' + str(self.sV.get()) + ' Max_Order = ' + str(self.sO.get()) + ' Delta_Angle = ' + str(self.sD.get()))
            DCS_label.pack()
        if self.HIST_Run != 0:
            HIST_label =Tk.Label(self.CSV, text='HIST Reminder: Number of Bins = ' + str(int(self.sB.get()) * 180) )
            HIST_label.pack()
        if self.FPDA_Run != 0:
            FPDA_label =Tk.Label(self.CSV, text='FPDA Reminder: Tmax = ' + str(self.sTmx.get()) + ' Tmin = ' + str(self.sTmn.get()) + ' Time Interval = 1/' + str(2**int(self.sItv.get())))
            FPDA_label.pack()
            
        name_entry_label.pack()
        csv_nameEn.pack()
        RunCSV.pack()
      
    def RunCCsv(self):
        if self.sPda.get() and self.sCna.get():
            self.RCSV = Tk.Toplevel(self)
            self.ColSel = Tk.StringVar()
            ColList = list(self.pdchoice[self.sPda.get()].columns.values)
            ColList.append('All')
            self.ColSel.set(ColList[0])
            column_label = Tk.Label(self.RCSV, text = 'Select Column(s):')
            column_label.pack()
            column_select = Tk.OptionMenu(self.RCSV,self.ColSel,*ColList)
            column_select.pack()
            Save_Sel = Tk.Button(self.RCSV, text = 'Save', command = self.SaveCsv)
            Save_Sel.pack()
            
    def SaveCsv(self):
        if str(self.ColSel.get()) == 'All' :   
            self.pdchoice[self.sPda.get()].to_csv(os.getcwd() + "\\"  + str(self.sCna.get()) + ".csv")
        else:
            self.pdchoice[self.sPda.get()].loc[:,str(self.ColSel.get())].to_csv(os.getcwd() + "\\"  + str(self.sCna.get()) + ".csv")
    
    def creategraphwindow(self):
        
        self.CGW = Tk.Toplevel(self)
        
        x_DSRange = list(self.pdchoice.keys())
        x_DSRange.append('Index')
        GraphType = ['Scatter', 'Histogram']
        
        self.sXA = Tk.StringVar()
        self.sYA = Tk.StringVar()
        self.sXC = Tk.StringVar()
        self.sYC = Tk.StringVar()
        self.sGT = Tk.StringVar()
        self.sGT.set(GraphType[0])
        self.sHB = Tk.StringVar()
        self.sHB.set(10)
        
        x_label = Tk.Label(self.CGW, text = 'Select X Axis data set')
        x_select = Tk.OptionMenu(self.CGW, self.sXA, *x_DSRange)
        y_label = Tk.Label(self.CGW, text = 'Select Y Axis data set')
        y_select = Tk.OptionMenu(self.CGW, self.sYA, *(self.pdchoice.keys()))
        x_load = Tk.Button(self.CGW, text = 'Load X Axis data', command = lambda: self.CGWload('x'))
        y_load = Tk.Button(self.CGW, text = 'Load Y Axis data', command = lambda: self.CGWload('y'))
        Graph_Type = Tk.OptionMenu(self.CGW, self.sGT, *GraphType)
        GT_Set = Tk.Button(self.CGW, text = 'Set Graph Type', command = lambda: self.GTset())
        GenGraph = Tk.Button(self.CGW, text = 'Generate Graph', command = lambda: self.CGWgen())
        
        x_label.pack()
        x_select.pack()
        x_load.pack()
        y_label.pack()
        y_select.pack()
        y_load.pack()
        Graph_Type.pack()
        GT_Set.pack()
        GenGraph.pack()

    def GTset(self):
        self.GTs = Tk.Toplevel(self)
        if self.sGT.get() == 'Scatter':
            Sct_Conf = Tk.Label(self.GTs, text = 'Type set as Scatter')
            Sct_OK = Tk.Button(self.GTs, text = 'OK', command = lambda: self.GTs.destroy())
            Sct_Conf.pack()
            Sct_OK.pack()
        elif  self.sGT.get() == 'Histogram':
            SHB_Label = Tk.Label(self.GTs, text = 'Set Number of Bins')
            SHistBins = Tk.Entry(self.GTs, textvariable = self.sHB)
            SHB_Conf = Tk.Button(self.GTs, text = 'Set', command = lambda: self.SHBconfirm())
            SHB_Label.pack()
            SHistBins.pack()
            SHB_Conf.pack()
        else:
            Err_Label = Tk.Label(self.GTs, text = 'Undefined Graph Type')
            Err_OK = Tk.Button(self.GTs, text = 'OK', command = lambda: self.GTs.destroy())
            Err_Label.pack()
            Err_OK.pack()
            
    def SHBconfirm(self):
        self.SHBC = Tk.Toplevel(self)
        if self.sHB.get() > 0:
            self.GTs.destroy()
            SHB_correct = Tk.Label(self.SHBC, text = 'Set as ' + self.sHB.get() + ' Bins')
            SHB_c_ok = Tk.Button(self.SHBC, text = 'OK', command = lambda: self.SHBC.destroy())
            SHB_correct.pack()
            SHB_c_ok.pack()
        else:
            SHB_Err = Tk.Label(self.SHBC, text = 'Number of bins must be > 0')
            SHB_e_ok = Tk.Button(self.SHBC, text = 'OK', command = lambda: self.SHBC.destroy())
            SHB_Err.pack()
            SHB_e_ok.pack()
        
    def CGWload(self,axis):
        
        self.CGWL = Tk.Toplevel(self)
        
        if axis == 'x':
            if self.sXA.get() != '' and self.sXA.get() != 'Index':
                ColList = list(self.pdchoice[self.sXA.get()].columns.values)
                x_col_label = Tk.Label(self.CGWL, text = 'select column')
                x_col_sel = Tk.OptionMenu(self.CGWL, self.sXC, *ColList)
                x_col_ret = Tk.Button(self.CGWL, text = 'Select', command = lambda: self.CGWL.destroy())
                x_col_label.pack()
                x_col_sel.pack()
                x_col_ret.pack()
            elif self.sXA.get() == 'Index':
                self.sXC.set('Index')
                x_Indx_Suc = Tk.Label(self.CGWL, text = 'X axis set as index')
                x_col_Suc = Tk.Button(self.CGWL, text = 'OK', command = lambda: self.CGWL.destroy())
                x_Indx_Suc.pack()
                x_col_Suc.pack()
            else:
                x_col_Fail_Label = Tk.Label(self.CGWL, text = 'Error - no array selected')
                x_col_Fail_Button = Tk.Button(self.CGWL, text = 'OK', command = lambda: self.CGWL.destroy())
                x_col_Fail_Label.pack()
                x_col_Fail_Button.pack()
        if axis == 'y':
            if self.sYA.get() != '':
                ColList = list(self.pdchoice[self.sYA.get()].columns.values)
                y_col_label = Tk.Label(self.CGWL, text = 'select column')
                y_col_sel = Tk.OptionMenu(self.CGWL, self.sYC, *ColList)
                y_col_ret = Tk.Button(self.CGWL, text = 'Select', command = lambda: self.CGWL.destroy())
                y_col_label.pack()
                y_col_sel.pack()
                y_col_ret.pack()
            else:
                y_col_Fail_Label = Tk.Label(self.CGWL, text = 'Error - no array selected')
                y_col_Fail_Button = Tk.Button(self.CGWL, text = 'OK', command = lambda: self.CGWL.destroy())
                y_col_Fail_Label.pack()
                y_col_Fail_Button.pack()
        
        return None
        
    def CGWgen(self):
        
        
        if self.sXA.get() != '' and self.sYA.get() != '':
            self.CGWg = Tk.Toplevel(self)
            y_data_set = self.pdchoice[str(self.sYA.get())].loc[:,str(self.sYC.get())]
            if self.sXA.get() != 'Index': 
                x_data_set = self.pdchoice[str(self.sXA.get())].loc[:,str(self.sXC.get())]
                graph = Figure(figsize = (5,5))
                sub_graph = graph.add_subplot(111)
                if self.sGT.get() == 'Scatter':
                    sub_graph.plot(x_data_set,y_data_set,'o')
                elif self.sGT.get() == 'Histogram':
                    sub_graph.hist(y_data_set,bins = int(self.sHB.get()))
            else:
                x_data_set = 'Index'
                graph = Figure(figsize = (5,5))
                sub_graph = graph.add_subplot(111)
                if self.sGT.get() == 'Scatter':
                    sub_graph.plot(y_data_set,'o')
                elif self.sGT.get() == 'Histogram':
                    sub_graph.hist(y_data_set,bins = int(self.sHB.get()))
        
            
            canvas = FigureCanvasTkAgg(graph, self.CGWg)
            canvas.show()
            canvas.get_tk_widget().pack(expand=True)
            
            toolbar = NavigationToolbar2TkAgg(canvas, self.CGWg)
            toolbar.update()
            canvas._tkcanvas.pack(expand = True)
            
            CGW_OK = Tk.Button(self.CGWg, text = 'Close', command = lambda: self.CloseCGW())
            CGW_OK.pack()
            
            self.CGWg.protocol("WM_DELETE_WINDOW", lambda: self.CloseCGW())
            
    def CloseCGW(self):
        self.sXC.set('')
        self.sYC.set('')
        self.CGWg.destroy()
            
            
root = Tk.Tk()

app = TkWindow(root).pack()

root.mainloop()
import streamlit as st
import hydralit_components as hc
import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
from detect_delimiter import detect
import os
from impedance.models.circuits import CustomCircuit
import schemdraw
import schemdraw.elements as elm
import tempfile
#from streamlit_extras.app_logo import add_logo   # In newer versions of streamlit

#start_time = time.time()



#icon = st.image("Capture.PNG")
st.set_page_config(
     page_title="Battery Data Analytics",
     page_icon="Add later",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This app helps to quickly plot and analyse\
         battery cells electrochemical data. For more details or support, contact Kenneth Nwanoro"
     }
 )

st.markdown(
    """
    <style>
        .stProgress > div > div > div > div {
            background-image: linear-gradient(to right, #99ff99 , #00ccff);
        }
    </style>""",
    unsafe_allow_html=True,
)
   
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            ##MainMenu {visibility: hidden;}  # remove one hash to hide hamnurger menu
            </style>        


            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)



if "TestData" not in st.session_state:
    st.session_state.TestData = []
    
if "FileName" not in st.session_state:
    st.session_state.FileName = []


if "CellIds" not in st.session_state:
    st.session_state.CellIds = []
    
    
if "Active_CellIds" not in st.session_state:
    st.session_state.Active_CellIds = []

if "Current_plot_full_test_data" not in st.session_state:
    st.session_state.Current_plot_full_test_data = []
    # This handle is required to allow adjusting axis limits by user
    
 
if "Current_plot_full_test_xlabel" not in st.session_state:
    st.session_state.Current_plot_full_test_xlabel= None
    # This handle is required to allow adjusting plot labels by user
    
    
if "Current_plot_full_test_ylabel" not in st.session_state:
    st.session_state.Current_plot_full_test_ylabel= None
    # This handle is required to allow adjusting plot labels by user
    
if "Current_plot_full_test_legend " not in st.session_state:
    st.session_state.Current_plot_full_test_legend = None

if "Current_plot_full_test_xlim" not in st.session_state:
    st.session_state.Current_plot_full_test_xlim = []


if "Current_plot_full_test_ylim" not in st.session_state:
    st.session_state.Current_plot_full_test_ylim = []

if "All_cell_ids" not in st.session_state:
    st.session_state.All_cell_ids = []
    
    
if "Cycler_Name" not in st.session_state:
    st.session_state.Cycler_Name = None

if "Allow_legend" not in st.session_state:
    st.session_state.Allow_legend = "Yes"
if "Cycle_plot" not in st.session_state:
    st.session_state.Cycle_plot = "No"
    
if "EIS" not in st.session_state:
    st.session_state.EIS = "No"
    

if "linestyle" not in st.session_state:
     st.session_state.linestyle = "solid"   

if "Cell_ids_and_file_nums" not in st.session_state:
     st.session_state.Cell_ids_and_file_nums = {}

if "glob_Xlim" not in st.session_state:
     st.session_state.glob_Xlim = None
if "glob_Ylim" not in st.session_state:
     st.session_state.glob_Ylim = None   
     
if "Interactive_Plot" not in st.session_state:  
    st.session_state.Interactive_Plot = False

  
     


with st.expander("Important notes"):
    st.text("About importing data:")
    st.text("Expand the import data widget. Select the cycler type associated with your data.")
    st.text("The capability for cross cycler data analysis has not been implemented yet... Watch out for this!")
    st.text("Use the Browse files button to select data file(s) and then click Upload button to load data file into the app")
    """      
    * The app recognises the data format and structure of each cycler that is currently included in the tool.
        If using the app to visualise other generic data file, to avoid errors, ensure that the data  follows these structure:
         1. Only the column names should  be in the first line of the data file.The presence of any other unstructured information 
         like meta data is not suitable and will cause error.
    """



def gen_cmap(n,name = 'hsv'):
    return plt.cm.get_cmap(name,n)




def Draw_Circuit(ECM_model,circuit_config):
        schemdraw.theme('dark')
            #with schemdraw.Drawing(show=False) as d:
        with schemdraw.Drawing(file='my_circuit.png') as d:
                elm.Dot()
                #d.push()
                p_count = 0
                R_count = 0
                #C_count = 0
                W_count = 0
                comma_count = 0
                param_list = []
                elm.style(elm.STYLE_IEEE)
                for num,item in enumerate(circuit_config):
                    if item == "R0":
                        elm.Resistor().label("R0")
                        param_list.append(item)
                    if item == "p":
                        elm.Line().up()
                        elm.Line().right()
                        p_count = p_count +1
                    if "R" in item and item!= "R0":
                        elm.Resistor().label(item)
                        param_list.append(item)
                        R_count = R_count +1
                    if  "W" in item:
                        elm.style(elm.STYLE_IEC)
                        elm.Resistor().label(item)
                        param_list.append(item)
                        param_list.append(item+"_constant")
                        W_count = W_count +1
                    if item == ",":
                        comma_count = comma_count +1
                        all_counts = [p_count, W_count, R_count] # list number of series connections in current parallel arrangement
                        if all(x == all_counts[0] for x in all_counts): #check how many R and W present in series in the current parallel connection to determine line arrangement
                            
                          elm.Line().down()
                        else:
                          elm.Line().right()
                          elm.Line().down()
                        elm.Dot()
                        d.push()
                        elm.Line().down()
                    if "C" in item or "CPE" in item:
                        if comma_count>0 and p_count>0: # check if is in parallel arrangement
                           elm.Line().left()
                        elm.Capacitor().label(item)
                        param_list.append(item)
                        if "CPE" in item: # add additional constant in the parameter list
                            param_list.append(item+"_constant")
                    if item == ")":  # end of a parallel connection
                       elm.Line().left()
                       elm.Line().up()
                       d.pop()
                       elm.Line().right()
                       p_count = 0  # When each parallel arrangement closes, reset counts
                       R_count = 0
                       comma_count = 0
                       W_count = 0
      


        st.image("my_circuit.png",caption='Equivalent Circuit Model (ECM) Schematic')
        
        return param_list


#@st.cache_data
def Time_conversion(time_Data):
    All_time_Data = []
    if 'd' in time_Data[0]:
        for ii in range(0,len(time_Data)):
            data_ii = time_Data[ii]
            split_data =  data_ii.split(":")
            day_hour = split_data[0].split("d")
            day = float(day_hour[0])*24
            hour = float(day_hour[1])
            minutes = float(split_data[1])/60
            milli_sec = split_data[2].split(".")
            sec = float(milli_sec[0])/3600
            milli = float(milli_sec[1])/1000
            milli = milli/3600
            tot_time_val = day+hour+minutes+sec+milli    
            All_time_Data.append(tot_time_val)
     
    return All_time_Data
    
    
    
    


    
def generic_Plot(xaxis,yaxis): # For plotting generic imported files
     
    linestyle = st.session_state.linestyle
   
    
    ylim1 = []
    ylim2 = []
    xlim1 = []
    xlim2 = []
    titl = []
    alt_data = pd.DataFrame()
    plotdata = []
    
     
    for ii, active_id in enumerate(st.session_state.Active_CellIds):
        
          file_num = st.session_state.Cell_ids_and_file_nums[active_id]
          item  = st.session_state.TestData[file_num]
          xdata = item[xaxis]
          ydata = item[yaxis]
          tit = st.session_state.FileName[file_num].split(".csv")
          tit = tit[0]
          
          if len(xdata) == 0 and len(ydata) ==0:
              pass
          else:
              
              for idd,idata in enumerate(ydata):                 
                 xlabel = xaxis
                 ylabel = yaxis[idd]
                 id_Data = []
                 lt = len(xdata)
                 for inum in range(0,lt):
                     id_Data.append([tit])
              
                
                 id_Data = np.array(id_Data)
                 full_id = id_Data[:,0]
              
              #st.write(len(full_id))
                 ylab = yaxis[idd].split('[')
                 ylab = ylab[0]
                 xlab = xlabel.split('[')
                 xlab = xlab[0]
                 dat = np.column_stack((xdata,item[idata]))
                 plotdata.append(dat)
                 titl.append(tit + ' : ' + ylabel)
                 
                 #ax.plot(xdata,item[idata],linestyle = linestyle, markersize=2, label = tit + ' : ' + ylabel)
                 xlim2.append(xdata.max())
                 xlim1.append(xdata.min())
                 ylim2.append(ydata.max())
                 ylim1.append(ydata.min())
                 
                 
              tmp_data = item[yaxis[0]]
              temp_alt = pd.DataFrame({
                                      xlab: xdata,
                                      ylab: tmp_data,
                                      "File Id":full_id,
                                      })

              alt_data = pd.concat([alt_data, temp_alt], axis = 0) 
               
                
              
              
    ylim1 = np.min(ylim1)
    ylim2 = np.max(ylim2)
    ylim1 = ylim1 - (ylim1 *0.02)
    ylim2 = ylim2 + (ylim2 *0.02)
    ylim = [ylim1,ylim2]
        
    xlim1 = np.min(xlim1)
    xlim2 = np.max(xlim2)
    xlim1 = xlim1 - (xlim1 *0.02)
    xlim2 = xlim2 + (xlim2 *0.02)
    xlim = [xlim1,xlim2]     
    
    
    st.session_state.Current_plot_full_test_ylim = ylim
    st.session_state.Current_plot_full_test_xlim = xlim 
    #st.session_state.Current_plot_full_test_data = plotdata
    st.session_state.Current_plot_full_test_ylabel = ylabel
    st.session_state.Current_plot_full_test_xlabel = xlabel
    st.session_state.Current_plot_full_test_legend = titl
    
    if linestyle == 'Scatter plot':
           ScatterPlot(plotdata)        
    else:
        plot(plotdata)
        plot_altair(alt_data,ylim,xlim)
    
            
        
    
   
def formation_CE(counts,steps):
        max_cyc_num  = np.max(counts)
        max_step_num = np.max(steps)
        #st.write(max_cyc_num)
       # st.write(max_step_num)
              
        if max_step_num > max_cyc_num:
            if st.session_state.Cycler_Name == "PEC":
              
                charge_cap =     full_pec_test_data_plot("Charge Capacity (Ah)","Secondary variable") 
                discharge_cap =  full_pec_test_data_plot("Discharge Capacity (Ah)","Secondary variable")
                
            else:
                charge_cap = full_test_data_plot("Charge Capacity (Ah)","Secondary variable") 
                discharge_cap =  full_test_data_plot("Discharge Capacity (Ah)","Secondary variable")
        else:
            
            
            if st.session_state.Cycler_Name == "PEC":
                charge_cap    =     full_pec_test_data_plot("Charge Capacity (Ah)","Secondary variable") 
                discharge_cap =  full_pec_test_data_plot("Discharge Capacity (Ah)","Secondary variable")
                """ The capacities displayed here are the maximum charge and discharge capacity values.  
                 The Coulombic efficiency is calculated using these values.
                If cycling Coulombic efficiency plot is required, select the "Cycling Coulombic efficiency" option under "Cycle Data Analysis and Plots" block. """
               
               
            elif st.session_state.Cycler_Name == "BioLogic":
                charge_cap = full_cycle_data_plot("TestTime","Capacity (Ah)","CV","Secondary variable", counts) 
                discharge_cap =  full_cycle_data_plot("TestTime","Capacity (Ah)","D","Secondary variable",counts)                
            else:
               
                charge_cap = full_cycle_data_plot("TestTime","Capacity (Ah)","C","Secondary variable", counts) 
                discharge_cap =  full_cycle_data_plot("TestTime","Capacity (Ah)","D","Secondary variable",counts)
        
        st.write("Charge Capacity Table:")
        st.write(charge_cap)
        st.write("Discharge Capacity Table:")
        st.write(discharge_cap)
          
                
                
        # Make this a function
        charge_capacity = charge_cap.iloc[:,1]
        discharge_capacity = discharge_cap.iloc[:,1]
        num_ch_caps = len(charge_capacity)
        num_dch_caps = len(discharge_capacity)
        
        if max_step_num > max_cyc_num:  # Assume this is a formation only data
            charge_capacity = np.array(charge_capacity)
            discharge_capacity = np.array(discharge_capacity)
            curr_ids = list(discharge_cap.iloc[:,0])
            
        elif num_ch_caps == num_dch_caps:         # Cycling data but with equal number of data points
            charge_capacity = np.array(charge_capacity)
            discharge_capacity = np.array(discharge_capacity) 
            curr_ids = list(discharge_cap.iloc[:,0])

        else:
            # Create empty data frame to store data that are selected
            name_active_ids = charge_cap.iloc[:,0]
            name_active_ids = np.unique(name_active_ids)
            extra_capacity = pd.DataFrame()
            
            for ii_id in name_active_ids:
                ch_cap = charge_cap.loc[charge_cap["Cell Id"] == ii_id,"Capacity (Ah)"]
                dch_cap = discharge_cap.loc[(discharge_cap["Cell Id"] == ii_id),"Capacity (Ah)"]
                name_curr_id = discharge_cap.loc[discharge_cap["Cell Id"] == ii_id,"Cell Id"]
                len_ch_cap = len(ch_cap)
                len_dch_cap = len(dch_cap)
                
                if len_ch_cap == len_dch_cap:
                  
                   
                    temp_alt_CE =  pd.DataFrame({"Cell Id":name_curr_id,
                                          "Charge capacity": ch_cap,
                                          "Discharge capacity":dch_cap,
                                          })
                   
                    extra_capacity = pd.concat([extra_capacity, temp_alt_CE], axis = 0)
                else: # either one charge or discharge is missing
                     
                      min_len = min(len_ch_cap,len_dch_cap)
                      ch_cap = ch_cap.iloc[0:min_len]
                   
                      dch_cap = dch_cap.iloc[0:min_len]
                      name_curr_id = name_curr_id.iloc[0:min_len]
                      temp_alt_CE =  pd.DataFrame({"Cell Id":name_curr_id,
                                            "Charge capacity": ch_cap,
                                            "Discharge capacity":dch_cap,
                                            })
                     
                      extra_capacity = pd.concat([extra_capacity, temp_alt_CE], axis = 0)
        
                  
            st.write("Charge and Discharege Capacity Table:")
            st.write(extra_capacity)
            charge_capacity = extra_capacity.iloc[:,1]
            discharge_capacity = extra_capacity.iloc[:,2]
            curr_ids = extra_capacity.iloc[:,0]
            charge_capacity = np.array(charge_capacity)
            discharge_capacity = np.array(discharge_capacity) 
            
        
        CE =  (discharge_capacity/charge_capacity) *100
       # st.write(CE)
        ylo =  np.min(CE)-1
        yhi =   np.max(CE)+1
        #st.write(ylo)
        #st.write(yhi)
        
        user_data = np.column_stack((curr_ids,CE))
        user_data = pd.DataFrame(user_data, columns = ["Cell Id","Coulombic Efficiency"])
        user_data.index +=1   # Start numbering index from 1
        num = user_data.index 
        plot_data = np.column_stack((curr_ids,num,CE))
        plot_data = pd.DataFrame(plot_data, columns = ["Cell Id","Number","Coulombic Efficiency"])
        user_data.index.rename('Number', inplace=True)
        source = pd.DataFrame({"Number": num, "Coulombic Efficiency": CE,"Cell Id":curr_ids})
        meanCE= np.mean(CE)
        std = np.std(CE)
        var = np.var(CE)
        meanCE = np.around(meanCE, decimals=3, out=None)
        std = np.around(std, decimals=3, out=None)
        var = np.around(var, decimals=3, out=None)


        
        c = alt.Chart(source).mark_circle(size=120).encode(
              alt.Y("Coulombic Efficiency").scale(zero=False),
              alt.X("Number").scale(zero=False),
              #x="Number",             
              color="Cell Id",
              tooltip=['Cell Id',"Coulombic Efficiency"]
                ).properties(width = 800, height = 300).interactive()

        st.write(c)
        if max_step_num < max_cyc_num:
            fig,ax = plt.subplots(1,1)
            ax.scatter(num,CE)
           # ax.set_ylim([ylo,yhi])
            ax.set_xlabel("Number")
            ax.set_ylabel("Coulombic Efficiency")
            ax.legend()
            ax.grid()
            
            st.pyplot(fig)
            
        col1, col2,  = st.columns([3,1],gap = "small")
        with col1:
            st.subheader("Extracted Coulombic Efficiency Data Table")
            st.write(user_data)
            
            
        with col2:
            st.subheader("Statistics")
            st.write(" Average CE: ", meanCE) 
            st.write(" Standard deviation: ", std) 
            st.write(" Variance: ", var) 
    
              

   
       
    
#@st.cache_data  
def plot(plotdata):
         #,
    
     # Still need to allow user to change axis, title, legends, grid and using cmap for color
     #with st.expander("Full test time plots"):
      ylabel = st.session_state.Current_plot_full_test_ylabel 
      xlabel = st.session_state.Current_plot_full_test_xlabel 
      tit = st.session_state.Current_plot_full_test_legend 
      ylim = st.session_state.Current_plot_full_test_ylim
      xlim = st.session_state.Current_plot_full_test_xlim
      linestyle = st.session_state.linestyle
      
      glob_xlim = st.session_state.glob_Xlim
      glob_ylim = st.session_state.glob_Ylim
      #cmap = gen_cmap(len(plotdata)*3)
      if glob_xlim != None:
          glob_xlim = glob_xlim.split(",")
          glob_xlim1 = float(glob_xlim[0])
          glob_xlim2 = float(glob_xlim[1])
          xlim = [glob_xlim1,glob_xlim2]
          
      if glob_ylim != None:
          glob_ylim = glob_ylim.split(",")
          glob_ylim1 = float(glob_ylim[0])
          glob_ylim2 = float(glob_ylim[1])
          ylim = [glob_ylim1,glob_ylim2]
          
      fig,ax = plt.subplots(1,1)
      
      for k, item in enumerate(plotdata):
         #ax = fig.add_subplot(1,k+1,1)
             #ax.plot(item[:,0],item[:,1],color = cmap(k*3),linestyle = linestyle, markersize=2, label = tit[k])
             ax.plot(item[:,0],item[:,1],linestyle = linestyle, markersize=2, label = tit[k])
     
     
         
      
      ax.set_ylim(ylim)
      ax.set_xlim(xlim)
      ax.set_xlabel(xlabel)
      ax.set_ylabel(ylabel)
      if st.session_state.Allow_legend == "Yes":
         ax.legend(prop={'size': 5})
      ax.grid()
      st.pyplot(fig)
      




        


def stack_plot(variables):
        variable_type = "Secondary"
        linestyle = st.session_state.linestyle
        temp_plot = full_pec_test_data_plot(plot_type,variable_type)
        temp_dim = temp_plot.shape
        temp_dim = temp_dim[1]
        
        #st.write(temp_plot)
        
        fig,ax = plt.subplots()
    
        
        
        
        ax1 = ax.twinx()
        ax2 = ax.twinx()
        ax3 = ax.twinx()
        ax4 = ax.twinx()
        
        axes = [ax,ax1,ax2,ax3,ax4]
        
        colors = ['blue','black','g','red','maroon',]
        
    
        
        
        for ii in range(temp_dim-1):
            
            
            axes[ii].plot(temp_plot[:,0],temp_plot[:,ii+1],linestyle = linestyle,color = colors[ii])
            
            axes[ii].set_ylabel(variables[ii], color = colors[ii])
            
            
            
            
            
        ax.grid()
        ax.set_xlabel("Time")
        st.pyplot(fig)
        














#@st.cache_data      
def plot_altair(plotdata,ylim,xlim):
    
    #with st.expander("Full test time interactive plots"):
       cols = list(plotdata.columns.values)
       glob_xlim = st.session_state.glob_Xlim
       glob_ylim = st.session_state.glob_Ylim
       if glob_xlim != None:
           glob_xlim = glob_xlim.split(",")
           glob_xlim1 = float(glob_xlim[0])
           glob_xlim2 = float(glob_xlim[1])
           xlim = [glob_xlim1,glob_xlim2]
           
       if glob_ylim != None:
           glob_ylim = glob_ylim.split(",")
           glob_ylim1 = float(glob_ylim[0])
           glob_ylim2 = float(glob_ylim[1])
           ylim = [glob_ylim1,glob_ylim2]
       #st.write(cols[1])
       #st.write(plotdata)
       #st.write(cols)
       #st.write(plotdata.head(20))
       if st.session_state.Cycle_plot == "Yes" or st.session_state.EIS == "Yes":
           c = alt.Chart(plotdata).mark_point(color="black").encode(
                 # alt.Y(cols[1]).scale(zero=False),
                 # x=cols[0],
                  alt.Y(cols[1]).scale(domain = (ylim[0],ylim[1])), # Use limit values here prefered
                  alt.X(cols[0]).scale(domain = (xlim[0],xlim[1])), # Use limit values here prefered
                  #y=cols[1],
                  color ="Cell Id",
                  tooltip=['Cell Id',cols[0],cols[1]]
                   ).properties(width =900, height = 600).interactive()
       else:
           
            c = alt.Chart(plotdata).mark_line().encode(
             #alt.Y(cols[1]).scale(zero=False),
            # alt.Y(cols[1]).scale(domain = (0,0.04)), # Use limit values here prefered
               # x=cols[0],
               alt.Y(cols[1]).scale(domain = (ylim[0],ylim[1])), # Use limit values here prefered
               alt.X(cols[0]).scale(domain = (xlim[0],xlim[1])), # Use limit values here prefered
                color=cols[2], # originally Cell Id better to change to column number so that the third column can be any variable
                tooltip=[cols[2],cols[0],cols[1]]
                     ).properties(width =900, height = 600).interactive()
               
            
       st.write(c)
      
       
def DVA_plot_altair(plotdata,ylim,xlim):
    
    #with st.expander("Full test time interactive plots"):
        glob_xlim = st.session_state.glob_Xlim
        glob_ylim = st.session_state.glob_Ylim
        if glob_xlim != None:
            glob_xlim = glob_xlim.split(",")
            glob_xlim1 = float(glob_xlim[0])
            glob_xlim2 = float(glob_xlim[1])
            xlim = [glob_xlim1,glob_xlim2]
            
        if glob_ylim != None:
            glob_ylim = glob_ylim.split(",")
            glob_ylim1 = float(glob_ylim[0])
            glob_ylim2 = float(glob_ylim[1])
            ylim = [glob_ylim1,glob_ylim2] 
        cols = list(plotdata.columns.values)

            
        c = alt.Chart(plotdata).mark_line().encode(
             #alt.Y(cols[1]).scale(zero=False),
             alt.Y(cols[1]).scale(domain = (ylim[0],ylim[1])), # Use limit values here prefered
             alt.X(cols[0]).scale(domain = (xlim[0],xlim[1])), # Use limit values here prefered
                #x=cols[0],
                color="Cell Id",
                tooltip=['Cell Id',cols[0],cols[1]]
                     ).properties(width =900, height = 600).interactive()
               
            
        st.write(c)      
       
 
    
    
def Fit_EIS(EIS_fit_tool,ecm_model,eis_test_data,circuit,initial_guess): 
    
    if ecm_model == "Custom circuit" and circuit == '':
          st.error("Error: "+ "Enter  ECM configuration to continue")
          param_list = [0]
          circuit_parameters = [0]         
    else:
         
        
        frequencies = eis_test_data['freq/Hz']  
        Z_real = eis_test_data['Re(Z)/Ohm']
        Z_im = eis_test_data['Im(Z)/Ohm']
        Zn = np.column_stack((frequencies,Z_real,Z_im))
        Z_plot = Zn[:,1:3]
        
        
        frequencies = Zn[:,0]
        Zn_r = Zn[:,1]
        Zn_im = Zn[:,2]
        Z = []
        for ii, item in enumerate(Zn_r):
            # even after converting the sign from .mpt file, still need to multiply the complex part by -1
            Z.append(complex(float(item), -1*float(Zn_im[ii]))) 
            
    
        Z = np.array(Z)

        circuit_config = circuit.replace('p','-p').replace('(','-(-',).replace(',','-,-').replace(')','-)-')
        circuit_config = circuit_config.replace(' ','')
       
        circuit_config = circuit_config.split('-')

        circuit = CustomCircuit(circuit, initial_guess=initial_guess)
        circuit.fit(frequencies, Z)
        Z_fit = circuit.predict(frequencies)
        zim = []
        zre = []
        
        for ii, item in enumerate(Z_fit):
            zim.append(float(item.imag))
            zre.append(float(item.real))
            
        Z_fit = np.column_stack((zre,zim))
        Z_fit[:,1] = Z_fit[:,1] *-1  # change the sign of fitted Z_im for plotting
        plotdata = [Z_fit,Z_plot]
        
        ylim1 = np.min(Z_fit[:,1])
        ylim2 = np.max(Z_fit[:,1])
        ylim1 = ylim1 - (ylim1 *0.02)
        ylim2 = ylim2 + (ylim2 *0.02)
        ylim = [ylim1,ylim2]
        
        xlim1 = np.min(Z_fit[:,0])
        xlim2 = np.max(Z_fit[:,0])
        xlim1 = xlim1 - (xlim1 *0.02)
        xlim2 = xlim2 + (xlim2 *0.02)
        xlim = [xlim1,xlim2]
        ylabel = "Im(Z)/Ohm"
        xlabel = "Re(Z)/Ohm"
        titl = ["Fit","Test Data"]
        st.session_state.Current_plot_full_test_ylim = ylim
        st.session_state.Current_plot_full_test_xlim = xlim 
        st.session_state.Current_plot_full_test_data = plotdata
        st.session_state.Current_plot_full_test_ylabel = ylabel
        st.session_state.Current_plot_full_test_xlabel = xlabel
        st.session_state.Current_plot_full_test_legend = titl
        circuit_parameters =circuit.parameters_
        
        plot(plotdata)
        #plot_altair(alt_data,ylim,xlim)
        #plot_Circuit(ecm_model)
        param_list = Draw_Circuit(ecm_model,circuit_config)
    
    
    
    
    
    # MPT data format saves the imaginary portion as -Im(Z) not Im(Z)
    # So remember to multiply by -1 when importing data from raw biologic datajust
    
    
    
    
    return  param_list,circuit_parameters


#@st.cache_data      
def plotStep(plotdata,ylim,xlim,xlabel,ylabel,tit):

      linestyle = st.session_state.linestyle
      glob_xlim = st.session_state.glob_Xlim
      glob_ylim = st.session_state.glob_Ylim
      if glob_xlim != None:
          glob_xlim = glob_xlim.split(",")
          glob_xlim1 = float(glob_xlim[0])
          glob_xlim2 = float(glob_xlim[1])
          xlim = [glob_xlim1,glob_xlim2]
          
      if glob_ylim != None:
          glob_ylim = glob_ylim.split(",")
          glob_ylim1 = float(glob_ylim[0])
          glob_ylim2 = float(glob_ylim[1])
          ylim = [glob_ylim1,glob_ylim2]
          
      fig,ax = plt.subplots(1,1)
      
      for k, item in enumerate(plotdata):
         #ax = fig.add_subplot(1,k+1,1)
          ax.plot(item[:,0],item[:,1],linestyle = linestyle, label = tit[k])
         
                
      ax.set_ylim(ylim)
      ax.set_xlim(xlim)
      ax.set_xlabel(xlabel)
      ax.set_ylabel(ylabel)
      ax.legend(prop={'size': 5})
      #legend(loc=2, prop={'size': 6})
      ax.grid()
      st.pyplot(fig)

   
def ScatterPlot(plotdata):

      fig,ax = plt.subplots(1,1)
      
      ylabel = st.session_state.Current_plot_full_test_ylabel 
      xlabel = st.session_state.Current_plot_full_test_xlabel 
      tit = st.session_state.Current_plot_full_test_legend 
      ylim = st.session_state.Current_plot_full_test_ylim
      xlim = st.session_state.Current_plot_full_test_xlim
      
      glob_xlim = st.session_state.glob_Xlim
      glob_ylim = st.session_state.glob_Ylim
      if glob_xlim != None:
          glob_xlim = glob_xlim.split(",")
          glob_xlim1 = float(glob_xlim[0])
          glob_xlim2 = float(glob_xlim[1])
          xlim = [glob_xlim1,glob_xlim2]
          
      if glob_ylim != None:
          glob_ylim = glob_ylim.split(",")
          glob_ylim1 = float(glob_ylim[0])
          glob_ylim2 = float(glob_ylim[1])
          ylim = [glob_ylim1,glob_ylim2]
      
      for k, item in enumerate(plotdata):
         #ax = fig.add_subplot(1,k+1,1)
          ax.scatter(item[:,0],item[:,1],c = 'black',alpha = 0.3, label = tit[k])
         
                
      ax.set_ylim(ylim)
      ax.set_xlim(xlim)
      ax.set_xlabel(xlabel)
      ax.set_ylabel(ylabel)
      ax.legend()
      ax.grid()
      st.pyplot(fig)
      
      

    
    
#@st.cache_data   
def full_pec_test_data_plot(plot_type,variable_type):
    
    plotdata = []
    ylim1 = []
    ylim2 = []
    xlim1 = []
    xlim2 = []
    titl = []
    alt_data = pd.DataFrame()
    plotData =  []

    col_name =  plot_type
    if len(col_name) == 1:
        col_name = col_name[0]
    #st.write(col_name)
    try:
         for  active_id in st.session_state.Active_CellIds:
                #st.write(count,"  is:", active_id)
                #count =  count+1
                               #st.write(active_id)        
                               #st.write(st.session_state.Active_CellIds)
                               file_num = st.session_state.Cell_ids_and_file_nums[active_id]
                               item =  st.session_state.TestData[file_num]
                #for col_name in list(item.columns.values):    
                    
                   #if plot_type in col_name:

                               cellid_temp = "Cell ID"  # First cell data
                               time_col = "Total Time (Seconds)"
                               ylabel = col_name

                               test_value = item.loc[item[cellid_temp]==active_id,col_name]
                               time_value = item.loc[item[cellid_temp]==active_id,time_col]
                               full_id = item.loc[item[cellid_temp]==active_id,cellid_temp]
                               
                               #st.write(test_value)
                               #st.write(test_value.iloc[:,0].min())
                               
                               #min_data = test_value.iloc[:,0].min()
                               #max_data = test_value.iloc[:,0].max()
                               
                               #st.write(min_data)
                               #st.write(max_data)
                               

                               if len (test_value)>0: # only valid entries have data length greater than 0
                                     #st.write(active_id)
                                     plot_val = np.column_stack((time_value,test_value))
                                    
                                                                         
                                     #st.write(plot_val)
                                     #st.write(plot_val[:,1])
                                     
                                    #temp_alt_a = np.column_stack((time_value,test_value,full_id))
                                     #st.write("Here")
                                     temp_alt = pd.DataFrame({"Total Time (s)": time_value,  # Some issues here becuase test_value is not a list- Need to sort this out
                                                             ylabel: test_value,
                                                             "Cell Id":full_id,
                                                             })

                                     alt_data = pd.concat([alt_data, temp_alt], axis = 0)  # pandas version 2.0 and above deprecated append() function
                                     
                                     val = float(test_value.max())
                                     
                                     plotData.append([active_id, val])
                                     #stor_cell_id.append(active_id)
                                     plotdata.append(plot_val)
                             
                                     ylim1.append(test_value.min())
                                     ylim2.append(test_value.max())
                                     
                               
                                
                                     xlim1.append(time_value.min())
                                     xlim2.append(time_value.max())
                                     
                                 
                               
                                     testname = st.session_state.FileName[file_num].split(".csv")
                                     titl.append(testname[0] +"," + " Cell id: " + active_id)
                           #except:
                               #pass
    except:
          pass


    xlabel = "RunTime (seconds)"  
    #st.write(ylim1)
    try:
       ylim1 = np.min(ylim1)
       ylim2 = np.max(ylim2)
       ylim1 = ylim1 - (ylim1 *0.02)
       ylim2 = ylim2 + (ylim2 *0.02)
       ylim = [ylim1,ylim2]
       
       xlim1 = np.min(xlim1)
       xlim2 = np.max(xlim2)
       xlim1 = xlim1 - (xlim1 *0.02)
       xlim2 = xlim2 + (xlim2 *0.02)
       xlim = [xlim1,xlim2]
       
       return_data = pd.DataFrame(plotData, columns = ["Cell Id",ylabel])
       return_data.index +=1   # Start numbering index from 1
       return_data.index.rename('Number', inplace=True)
       
    except:
        xlim = []
        ylim = []
        return_data = plot_val
    



    
    st.session_state.Current_plot_full_test_data = plotdata
    st.session_state.Current_plot_full_test_ylabel = ylabel
    st.session_state.Current_plot_full_test_xlabel = xlabel
    st.session_state.Current_plot_full_test_legend = titl
   
    st.session_state.Current_plot_full_test_ylim = ylim
    st.session_state.Current_plot_full_test_xlim = xlim
    #plot(plotdata,ylim,xlim,xlabel,ylabel,titl)
    if variable_type == "Primary variable":  # Some variables such as coulombic efficiency needs be to reprocssed
       plot(plotdata)
       if  st.session_state.Interactive_Plot == True:
           plot_altair(alt_data,ylim,xlim)
    else:
       pass
  
 
    
    return return_data  # this is returned so that user can view the data in table format and download it 
 
   
 
    
 
 
@st.cache_data   
def full_test_data_plot(plot_type,variable_type):
    
    plotdata = []
    ylim1 = []
    ylim2 = []
    xlim1 = []
    xlim2 = []
    titl = []
    alt_data = pd.DataFrame()
    plotData =  []
    #stor_cell_id = []
    #st.write(st.session_state.Active_CellIds)


              
     
    try:
       for ii, active_id in enumerate(st.session_state.Active_CellIds):
             file_num = st.session_state.Cell_ids_and_file_nums[active_id]
             item =  st.session_state.TestData[file_num]
             
             ylabel = plot_type
             xlabel = "Test Time" 
             altair_ycolumn = ylabel.split("[")
             altair_ycolumn = altair_ycolumn[0]
             
             #st.write(st.session_state.Cycler_Name )
           
                 
             if plot_type == "Charge Capacity (Ah)":
                     
                        if st.session_state.Cycler_Name == "BioLogic":
                            
                               test_value = item["Charge Capacity (Ah)"]
                               time_value = item["TestTime"]
                        else:
                            
                              test_value = item.loc[(item["Instruction Name"]=="C"),"Capacity (Ah)"]
                              time_value = item.loc[(item["Instruction Name"]=="C"),"TestTime"]
                 
             elif plot_type == "Discharge Capacity (Ah)":
                         if st.session_state.Cycler_Name == "BioLogic":
                             test_value = item["Discharge Capacity (Ah)"]
                             time_value = item["TestTime"]
                             
                         else:
                                 
                              test_value = item.loc[(item["Instruction Name"]=="D"),"Capacity (Ah)"]
                              time_value = item.loc[(item["Instruction Name"]=="D"),"TestTime"]
             else:
                     time_value = item["TestTime"]
                     test_value = item[plot_type]
             
             
                    
                         
             
            
             #full_id = pd.DataFrame()
             #full_id = full_id.fill(active_id)
             id_Data = []
             for i, item_val in enumerate(test_value):
                id_Data.append([active_id])
            
             
             plot_val = np.column_stack((time_value,test_value))
             
             id_Data = np.array(id_Data)
             full_id = id_Data[:,0]
             #st.write("Got here")
             temp_alt = pd.DataFrame({xlabel: time_value,
                                     altair_ycolumn: test_value,
                                     "Cell Id":full_id,
                                     })
             


             alt_data = pd.concat([alt_data, temp_alt], axis = 0)  # pandas version 2.0 and above deprecated append() function
             val = float(test_value.max())
             plotData.append([active_id, val])
             #stor_cell_id.append(active_id)
             plotdata.append(plot_val)
             ylim1.append(test_value.min())
             ylim2.append(test_value.max())
             xlim1.append(time_value.min())
             xlim2.append(time_value.max())
             #ylim1.append(np.min(test_value))
             #ylim2.append(np.max(test_value))
       
             testname = st.session_state.FileName[file_num].split(".csv")
             titl.append(testname[0] +"," + " Cell id: " + active_id)
            
             
             
    except:
          pass
         


    
    ylim1 = np.min(ylim1)
    ylim2 = np.max(ylim2)
    ylim1 = ylim1 - (ylim1 *0.02)
    ylim2 = ylim2 + (ylim2 *0.02)
    ylim = [ylim1,ylim2]
    
    xlim1 = np.min(xlim1)
    xlim2 = np.max(xlim2)
    xlim1 = xlim1 - (xlim1 *0.02)
    xlim2 = xlim2 + (xlim2 *0.02)
    xlim = [xlim1,xlim2]
    

    st.session_state.Current_plot_full_test_data = plotdata
    st.session_state.Current_plot_full_test_ylabel = ylabel
    st.session_state.Current_plot_full_test_xlabel = xlabel
    st.session_state.Current_plot_full_test_legend = titl
   
    st.session_state.Current_plot_full_test_ylim = ylim
    st.session_state.Current_plot_full_test_xlim = xlim
    #plot(plotdata,ylim,xlim,xlabel,ylabel,titl)
    
    if variable_type == "Primary variable":  # Some variables such as coulombic efficiency needs be to reprocssed
       plot(plotdata)
       plot_altair(alt_data,ylim,xlim)
    else:
       pass
  
    return_data = pd.DataFrame(plotData, columns = ["Cell Id",ylabel])
    return_data.index +=1   # Start numbering index from 1
    return_data.index.rename('Number', inplace=True)
    
    return return_data  # this is returned so that user can view the data in table format and download it 
 
    



@st.cache_data   
def full_EIS_data_plot(plot_type,variable_type,cycle_counts):
    
    plotdata = []
    ylim1 = []
    ylim2 = []
    xlim1 = []
    xlim2 = []
    titl = []
    alt_data = pd.DataFrame()
    plotData =  []
    
    try:
       for ii, active_id in enumerate(st.session_state.Active_CellIds):
             file_num = st.session_state.Cell_ids_and_file_nums[active_id]
             item =  st.session_state.TestData[file_num]
             for icount in cycle_counts:
                    cycle =  item.loc[item["Cycle"] == icount,"Cycle"]
                    
                    if plot_type == "Nyquist Plot":
                                               
                        test_value = item.loc[(item["Cycle"] == icount),"Im(Z)/Ohm"]
                        time_value = item.loc[(item["Cycle"] == icount),"Re(Z)/Ohm"]                  
                        xlabel = "Re(Z)/Ohm"
                        ylabel = "Im(Z)/Ohm"
                    elif  plot_type == "Re-Bode Plot":
                         test_value = item.loc[(item["Cycle"] == icount),"Re(Z)/Ohm"]
                         time_value = item.loc[(item["Cycle"] == icount),"freq/Hz"]
                         xlabel = "freq/Hz"
                         ylabel = "Re(Z)/Ohm"
                         
                    elif  plot_type == "Im-Bode Plot":
                         test_value = item.loc[(item["Cycle"] == icount),"Im(Z)/Ohm"]
                         time_value = item.loc[(item["Cycle"] == icount),"freq/Hz"]
                         xlabel = "freq/Hz"
                         ylabel = "Im(Z)/Ohm"
                    elif  plot_type == "Log Im-Bode Plot":
                          test_value = item.loc[(item["Cycle"] == icount),"Im(Z)/Ohm"]
                          time_value = item.loc[(item["Cycle"] == icount),"freq/Hz"]
                          time_value = np.log10(time_value)
                          test_value = np.log10(test_value)
                          xlabel = "log (freq) Hz"
                          ylabel = "Log (Im(Z)) Ohm"
                    elif  plot_type == "Log Re-Bode Plot":
                           test_value = item.loc[(item["Cycle"] == icount),"Re(Z)/Ohm"]
                           time_value = item.loc[(item["Cycle"] == icount),"freq/Hz"]
                           time_value = np.log10(time_value)
                           test_value = np.log10(test_value)
                           
                           
                           xlabel = "log (freq) Hz"
                           ylabel = "Log (Im(Z)) Ohm"
                           
                    altair_ycolumn = ylabel
                    
                         

                    id_Data = []
                    for i, item_val in enumerate(test_value):
                        id_Data.append([active_id])
            
             
                    plot_val = np.column_stack((time_value,test_value))
             
                    id_Data = np.array(id_Data)
                    full_id = id_Data[:,0]
             #st.write("Got here")
                    temp_alt = pd.DataFrame({xlabel: time_value,
                                     altair_ycolumn: test_value,
                                     "Cell Id":full_id,
                                     "Cycle" :cycle
                                     })
             


                    alt_data = pd.concat([alt_data, temp_alt], axis = 0)  # pandas version 2.0 and above deprecated append() function
                    val = float(test_value.max())
                    plotData.append([active_id, val])
            
                    plotdata.append(plot_val)
                    ylim1.append(test_value.min())
                    ylim2.append(test_value.max())
                    xlim1.append(time_value.min())
                    xlim2.append(time_value.max())
             #ylim1.append(np.min(test_value))
             #ylim2.append(np.max(test_value))
       
                    testname = st.session_state.FileName[file_num].split(".csv")
                    titl.append(testname[0] +"," + " Cell id: " + active_id+ "  Cycle: " +str(cycle.iloc[1]))
            
             
             
             
             
    except:
          pass
         


    
    ylim1 = np.min(ylim1)
    ylim2 = np.max(ylim2)
    ylim1 = ylim1 - (ylim1 *0.02)
    ylim2 = ylim2 + (ylim2 *0.02)
    ylim = [ylim1,ylim2]
    
    xlim1 = np.min(xlim1)
    xlim2 = np.max(xlim2)
    xlim1 = xlim1 - (xlim1 *0.02)
    xlim2 = xlim2 + (xlim2 *0.02)
    xlim = [xlim1,xlim2]
    
    
    if ylim1 < 0:
            ylim1 = -ylim2
            ylim =  [ylim1,ylim2]
    st.session_state.Current_plot_full_test_data = plotdata
    st.session_state.Current_plot_full_test_ylabel = ylabel
    st.session_state.Current_plot_full_test_xlabel = xlabel
    st.session_state.Current_plot_full_test_legend = titl
   
    st.session_state.Current_plot_full_test_ylim = ylim
    st.session_state.Current_plot_full_test_xlim = xlim
    #plot(plotdata,ylim,xlim,xlabel,ylabel,titl)
    if variable_type == "Primary variable":  # Some variables such as coulombic efficiency needs be to reprocssed
       plot(plotdata)
       plot_altair(alt_data,ylim,xlim)
    else:
       pass
  
    return_data = pd.DataFrame(plotData, columns = ["Cell Id",ylabel])
    return_data.index +=1   # Start numbering index from 1
    return_data.index.rename('Number', inplace=True)
    
    return return_data  # this is returned so that user can view the data in table format and download it 
 




  
  

@st.cache_data     
def full_cycle_data_plot(plot_type_x,plot_type_y,state,variable_type, num_cycles):
    
    plotdata = []
    titl = []
    alt_data = pd.DataFrame()
    plotData =  []
    ylim1 = []
    ylim2 = []
    xlim1 = []
    xlim2 = []
    ylabel = plot_type_y
    xlabel = plot_type_x
    altair_ycolumn = ylabel.split("[")
    altair_ycolumn = altair_ycolumn[0]
    altair_xcolumn = xlabel.split("[")
    altair_xcolumn = altair_xcolumn[0]
    
         
    try:  # Searching for active cell/file id
         for  active_id in st.session_state.Active_CellIds:
             file_num = st.session_state.Cell_ids_and_file_nums[active_id]
             item =  st.session_state.TestData[file_num]
             #st.write(active_id)
             for icycle in num_cycles:
                 icycle = int(icycle)
             
                 try:  # Some files might be imcomplete 
                                                           
                     test_value = item.loc[(item["Instruction Name"]==state)&(item["Cycle"]==icycle),plot_type_y]
                     time_value = item.loc[(item["Instruction Name"]==state)&(item["Cycle"]==icycle),plot_type_x]
                        # voltage_values =  item.loc[(item["Instruction Name"]=="C")&(item["Cycle"]==icycle),"Voltage [V]"]
                     
                     id_Data = []
                     for i, item_val in enumerate(test_value):
                           id_Data.append([active_id])
                   
                    
                     plot_val = np.column_stack((time_value,test_value))
                    
                     id_Data = np.array(id_Data)
                     full_id = id_Data[:,0]
                    
                     temp_alt = pd.DataFrame({altair_xcolumn : time_value,
                                             altair_ycolumn: test_value,
                                            "Cell Id":full_id,
                                            })
                    
       
       
                     alt_data = pd.concat([alt_data, temp_alt], axis = 0,)  # pandas version 2.0 and above deprecated append() function
                     val = float(test_value.iloc[-1]) # for Capacities
                    
                     plotData.append([active_id, val])
                   
                     plotdata.append(plot_val)
                     #ylim = [test_value.min()-1,test_value.max()+0.2]
                     #xlim = [time_value.min()-5,time_value.max()+10]
                     ylim1.append(test_value.min())
                     ylim2.append(test_value.max())
                     xlim1.append(time_value.min())
                     xlim2.append(time_value.max())
              
                     testname = st.session_state.FileName[file_num].split(".csv")
                     titl.append(testname[0] +"," + " Cell id: " + active_id)
                 except:
                      pass
                
                
                
             
    except:
          pass
         


    xlabel = plot_type_x
    if plot_type_x == "Cycle":
        ylim = []
        xlim = []
    else:
        ylim1 = np.min(ylim1)
        ylim2 = np.max(ylim2)
        ylim1 = ylim1 - (ylim1 *0.02)
        ylim2 = ylim2 + (ylim2 *0.02)
        ylim = [ylim1,ylim2]
        
        xlim1 = np.min(xlim1)
        xlim2 = np.max(xlim2)
        xlim1 = xlim1 - (xlim1 *0.02)
        xlim2 = xlim2 + (xlim2 *0.02)
        xlim = [xlim1,xlim2]
    
    #ylim,
    st.session_state.Current_plot_full_test_data = plotdata
    st.session_state.Current_plot_full_test_ylabel = ylabel
    st.session_state.Current_plot_full_test_xlabel = xlabel
    st.session_state.Current_plot_full_test_legend = titl
   
    st.session_state.Current_plot_full_test_ylim = ylim
    st.session_state.Current_plot_full_test_xlim = xlim
    #plot(plotdata,ylim,xlim,xlabel,ylabel,titl)
    if variable_type == "Primary variable":  # Some variables such as coulombic efficiency needs be to reprocssed
       plot(plotdata)
       plot_altair(alt_data,ylim,xlim)
    else:
       pass
  
    return_data = pd.DataFrame(plotData, columns = ["Cell Id",ylabel])
    return_data.index +=1   # Start numbering index from 1
    return_data.index.rename('Number', inplace=True)
    
    return return_data  # this is returned so that user can view the data in table format and download it 
 






@st.cache_data      
def PEC_Cycle_Plot(plot_type_x,plot_type_y,state,variable_type,num_cycles):
            
    plotdata = []
    titl = []
    alt_data = pd.DataFrame()
    plotData =  []
    ylim1 = []
    ylim2 = []
    xlim1 = []
    xlim2 = []
    ylabel = plot_type_y
    xlabel = plot_type_x
    altair_ycolumn = ylabel.split("[")
    altair_ycolumn = altair_ycolumn[0]
    altair_xcolumn = xlabel.split("[")
    altair_xcolumn = altair_xcolumn[0]
    
    #try:
    for  active_id in st.session_state.Active_CellIds:
                file_num = st.session_state.Cell_ids_and_file_nums[active_id]
                item =  st.session_state.TestData[file_num]
                
                #st.write(count,"  is:", active_id)
                #count =  count+1
                #st.write(active_cell_id)           
              
                cellid_temp = "Cell ID"  # First cell data
                time_col = plot_type_x
                ylabel = plot_type_y
                ins_name = "Instruction Name"
                cyc = "Cycle"
                col_name = plot_type_y
                
              
                for icycle in num_cycles:
                                                                
                                   test_value = item.loc[(item[ins_name]==state) & (item[cyc]==icycle) & (item[cellid_temp]==active_id)
                                                         ,col_name]

                                    
                                   time_value = item.loc[(item[cellid_temp]==active_id) & (item[cyc]==icycle) & (item[ins_name]== state),
                                                         time_col]
                                  
                            
                                   full_id = item.loc[(item[cellid_temp]==active_id) & (item[cyc]==icycle) & (item[ins_name]==state),
                                                         cellid_temp]
                                 
                               
                                   if len (test_value)>1:
                                       
                                       plot_val = np.column_stack((time_value,test_value))
                                            
                                       val = float(test_value.iloc[-1]) # for Capacities
                                       plotData.append([active_id, val])
    
                                       temp_alt = pd.DataFrame({xlabel: time_value,
                                                                     ylabel: test_value,
                                                                     "Cell Id":full_id,
                                                                     })
    
                                       alt_data = pd.concat([alt_data, temp_alt], axis = 0)  # pandas versio
                                       plotdata.append(plot_val)
                                       ylim1.append(test_value.min())
                                       ylim2.append(test_value.max())
                                       xlim1.append(time_value.min())
                                       xlim2.append(time_value.max())
                                       
                                       testname = st.session_state.FileName[file_num].split(".csv")
                                       titl.append(testname[0] + "," +  "Cell id: " + active_id +" ," + "Step" + str(icycle))   
                                             #titl.append(testname[0] +"," + " Cell id: " + active_id)
                                         
    #except:
          #pass
      
    xlabel = plot_type_x
    if plot_type_x == "Cycle":
           ylim = []
           xlim = []
    else:
           ylim1 = np.min(ylim1)
           ylim2 = np.max(ylim2)
           ylim1 = ylim1 - (ylim1 *0.02)
           ylim2 = ylim2 + (ylim2 *0.02)
           ylim = [ylim1,ylim2]
           
           xlim1 = np.min(xlim1)
           xlim2 = np.max(xlim2)
           xlim1 = xlim1 - (xlim1 *0.02)
           xlim2 = xlim2 + (xlim2 *0.02)
           xlim = [xlim1,xlim2]
       
       #ylim,
    st.session_state.Current_plot_full_test_data = plotdata
    st.session_state.Current_plot_full_test_ylabel = ylabel
    st.session_state.Current_plot_full_test_xlabel = xlabel
    st.session_state.Current_plot_full_test_legend = titl
      
    st.session_state.Current_plot_full_test_ylim = ylim
    st.session_state.Current_plot_full_test_xlim = xlim
       #plot(plotdata,ylim,xlim,xlabel,ylabel,titl)
    if variable_type == "Primary variable":  # Some variables such as coulombic efficiency needs be to reprocssed
          plot(plotdata)
          if  st.session_state.Interactive_Plot == True:
              plot_altair(alt_data,ylim,xlim)

 
    return_data = pd.DataFrame(plotData, columns = ["Cell Id",ylabel])
    return_data.index +=1   # Start numbering index from 1
    return_data.index.rename('Number', inplace=True)
    
       
    return return_data     # this is returned so that user can view the data in table format and download it 
    





#@st.cache_data      
def PEC_Step_Plot(StepNumber,plot_type_x,plot_type_y,variable_type):
            
    plotdata = []
    titl = []
    alt_data = pd.DataFrame()
    plotData =  []
    ylim1 = []
    ylim2 = []
    xlim1 = []
    xlim2 = []
    ylabel = plot_type_y
    xlabel = plot_type_x
    col_name = ylabel
    altair_ycolumn = ylabel.split("[")
    altair_ycolumn = altair_ycolumn[0]
    altair_xcolumn = xlabel.split("[")
    altair_xcolumn = altair_xcolumn[0]


    #try:
    for  active_id in st.session_state.Active_CellIds:
                file_num = st.session_state.Cell_ids_and_file_nums[active_id]
                item =  st.session_state.TestData[file_num]
                #st.write(count,"  is:", active_id)
                #count =  count+1
            #st.write(active_cell_id)           
                #for col_name in list(item.columns.values):    
                   #st.write(col_name)
                    
                   #if plot_type_y in col_name:
                       #if "Open" in col_name:  # Open circuit voltage in the column name
                           #col_name = None
                       #elif "Contact" in col_name:   # Contact voltage is in the column names
                          # col_name = None
                      # else:
                           #try:
                               #st.write(plot_type_y)
                               #st.write(col_name)
                               #check_mult_cells = col_name.split(".")
                               #st.write(len(check_mult_cells))
                            
                               #if len(check_mult_cells)==1:
                                   
                                   #st.write("Got here first")
                cellid_temp = "Cell ID"  # First cell data
                time_col = plot_type_x
                #ylabel = col_name
                ylabel = plot_type_y
                stp = "Step"
                xlabel = time_col


                for num_step in StepNumber:
                                   test_value = item.loc[(item[cellid_temp]==active_id) & (item[stp]==num_step)
                                                         ,col_name]
                                   time_value = item.loc[(item[cellid_temp]==active_id) & (item[stp]==num_step),
                                                         time_col]
                                   
                                   full_id = item.loc[(item[cellid_temp]==active_id) & (item[stp]==num_step),
                                                         cellid_temp]
                                   #st.write(len (time_value))
                                   #st.write(len (test_value))
                                   #if len (test_value)>0: # only valid entries have data length greater than 0
                                        
                                   plot_val = np.column_stack((time_value,test_value))
                                   val = float(test_value.max())
                                   val_min = float(test_value.min())
                                         #st.write(val_min)
                                   plotData.append([active_id, val_min,val])
                                         #st.write(plotData)
                                         #stor_cell_id.append(active_id)
                                   temp_alt = pd.DataFrame({xlabel: time_value,
                                                                 ylabel: test_value,
                                                                 "Cell Id":full_id,
                                                                 })

                                   alt_data = pd.concat([alt_data, temp_alt], axis = 0)  # pandas versio
                                   plotdata.append(plot_val)
                                   ylim1.append(test_value.min())
                                   ylim2.append(test_value.max())
                                   xlim1.append(time_value.min())
                                   xlim2.append(time_value.max())
                                   
                                   testname = st.session_state.FileName[file_num].split(".csv")
                                   titl.append(testname[0] + "," +  "Cell id: " + active_id +" ," + "Step" + str(num_step))   
                                         #titl.append(testname[0] +"," + " Cell id: " + active_id)
                                         
    #except:
          #pass
      
    ylim = [np.nanmin(ylim1),np.nanmax(ylim2)] 
    ylim1 = np.min(ylim1)
    ylim2 = np.max(ylim2)
    ylim1 = ylim1 - (ylim1 *0.02)
    ylim2 = ylim2 + (ylim2 *0.02)
    ylim = [ylim1,ylim2]
    
    xlim1 = np.min(xlim1)
    xlim2 = np.max(xlim2)
    xlim1 = xlim1 - (xlim1 *0.02)
    xlim2 = xlim2 + (xlim2 *0.02)
    xlim = [xlim1,xlim2]

    if variable_type == "Primary variable":  # Some variables such as coulombic efficiency, DCIR needs be to reprocssed
        plotStep(plotdata,ylim,xlim,xlabel,ylabel,titl)
        if  st.session_state.Interactive_Plot == True:      
           plot_altair(alt_data,ylim,xlim)
       
    else:
        
       pass
  
    return_data = pd.DataFrame(plotData, columns = ["Cell Id", " Min "+ylabel," Max "+ylabel ])
    return_data.index +=1   # Start numbering index from 1
    return_data.index.rename('Cell Number', inplace=True)
    
    return plotdata, return_data
                           
 
                           
 
    
 

@st.cache_data                                              
def Step_Plot(StepNumber,plot_type_x,plot_type_y,variable_type):
            
    plotdata = []
    titl = []
    alt_data = pd.DataFrame()
    plotData =  []
    ylim1 = []
    ylim2 = []
    xlim1 = []
    xlim2 = []
    ylabel = plot_type_y
    xlabel = plot_type_x
    altair_ycolumn = ylabel.split("[")
    altair_ycolumn = altair_ycolumn[0]
    altair_xcolumn = xlabel.split("[")
    altair_xcolumn = altair_xcolumn[0]
    

              
     
    try:  # Searching for active cell/file id
         for  active_id in st.session_state.Active_CellIds:
             
             #st.write(active_id)
           #for count  in Cycle_count:  # If I decide to allow cycle count in steps
             file_num = st.session_state.Cell_ids_and_file_nums[active_id]
             item =  st.session_state.TestData[file_num]
             
             for num_step in StepNumber:
                              
                 try:  # Some files might be imcomplete 
                                                           
                     #test_value = item.loc[(item["Instruction Name"]==state) & (item["Step"]==num_step),plot_type_y]
                     #time_value = item.loc[(item["Instruction Name"]==state) & (item["Step"]==num_step),plot_type_x]
                     
                     test_value = item.loc[ (item["Step"]==num_step),plot_type_y]
                     time_value = item.loc[(item["Step"]==num_step),plot_type_x]
                        
                     
                     id_Data = []  # Need array same size as xvalue and yvalue for altair plot
                     for i, item_val in enumerate(test_value):
                           id_Data.append([active_id])
                   
                    
                     plot_val = np.column_stack((time_value,test_value))
                    
                     id_Data = np.array(id_Data)
                     full_id = id_Data[:,0]
                    
                     temp_alt = pd.DataFrame({altair_xcolumn : time_value,
                                             altair_ycolumn: test_value,
                                            "Cell Id":full_id,
                                            })
                    
       
       
                     alt_data = pd.concat([alt_data, temp_alt], axis = 0,)  # pandas version 2.0 and above deprecated append() function
                     val = float(test_value.iloc[-1]) # for Capacities
                    
                     plotData.append([active_id, val])
                   
                     plotdata.append(plot_val)
                     #ylim = [test_value.min()-1,test_value.max()+0.2]
                     #xlim = [time_value.min()-5,time_value.max()+10]
                     ylim1.append(test_value.min())
                     ylim2.append(test_value.max())
                     xlim1.append(time_value.min())
                     xlim2.append(time_value.max())
              
                     testname = st.session_state.FileName[file_num].split(".csv")
                     titl.append(testname[0] +"," + " Cell id: " + active_id)
                 except:
                      pass
                
                
                
             
    except:
          pass
         


    xlabel = plot_type_x

    ylim1 = np.min(ylim1)
    ylim2 = np.max(ylim2)
    ylim1 = ylim1 - (ylim1 *0.02)
    ylim2 = ylim2 + (ylim2 *0.02)
    ylim = [ylim1,ylim2]
    
    xlim1 = np.min(xlim1)
    xlim2 = np.max(xlim2)
    xlim1 = xlim1 - (xlim1 *0.02)
    xlim2 = xlim2 + (xlim2 *0.02)
    xlim = [xlim1,xlim2]
    
    #ylim,
    st.session_state.Current_plot_full_test_data = plotdata
    st.session_state.Current_plot_full_test_ylabel = ylabel
    st.session_state.Current_plot_full_test_xlabel = xlabel
    st.session_state.Current_plot_full_test_legend = titl
   
    st.session_state.Current_plot_full_test_ylim = ylim
    st.session_state.Current_plot_full_test_xlim = xlim
    #plot(plotdata,ylim,xlim,xlabel,ylabel,titl)
    if variable_type == "Primary variable":  # Some variables such as coulombic efficiency needs be to reprocssed
       plotStep(plotdata,ylim,xlim,xlabel,ylabel,titl)
       plot_altair(alt_data,ylim,xlim)
    else:
       pass
  
    return_data = pd.DataFrame(plotData, columns = ["Cell Id",ylabel])
    return_data.index +=1   # Start numbering index from 1
    return_data.index.rename('Number', inplace=True)
    
    return plotdata,return_data  # this is returned so that user can view the data in table format and download it 
                   





@st.cache_data                                              
def BioLogic_Step_Plot(StepNumber,count,state,plot_type_x,plot_type_y,variable_type):
            
    plotdata = []
    titl = []
    alt_data = pd.DataFrame()
    plotData =  []
    ylim1 = []
    ylim2 = []
    xlim1 = []
    xlim2 = []
    ylabel = plot_type_y
    xlabel = plot_type_x
    altair_ycolumn = ylabel.split("[")
    altair_ycolumn = altair_ycolumn[0]
    altair_xcolumn = xlabel.split("[")
    altair_xcolumn = altair_xcolumn[0]
    
    
         

    for  active_id in st.session_state.Active_CellIds:
             file_num = st.session_state.Cell_ids_and_file_nums[active_id]
             item =  st.session_state.TestData[file_num]
             
             #st.write(active_id)
           #for count  in Cycle_count:  # If I decide to allow cycle count in steps
             for num_step in StepNumber:
                 for icount in count:
                              
                     #try:  # Some files might be imcomplete 
                                                               
                         #test_value = item.loc[(item["Instruction Name"]==state) & (item["Step"]==num_step),plot_type_y]
                         #time_value = item.loc[(item["Instruction Name"]==state) & (item["Step"]==num_step),plot_type_x]
                         
                         test_value = item.loc[(item["Step"]==num_step)&(item["Cycle"]==icount)&(item["Instruction Name"]==state),plot_type_y]
                         time_value = item.loc[(item["Step"]==num_step)&(item["Cycle"]==icount)&(item["Instruction Name"]==state),plot_type_x]
                        
                         
                         cyc_num = []
                         id_Data = []  # Need array same size as xvalue and yvalue for altair plot
                         for i, item_val in enumerate(test_value):
                               id_Data.append([active_id])
                               cyc_num.append([icount])
                       
                        
                         plot_val = np.column_stack((time_value,test_value))
                        
                         id_Data = np.array(id_Data)
                         cyc_num = np.array(cyc_num)
                         full_id = id_Data[:,0]
                         cyc_num = cyc_num[:,0]
                        
                         temp_alt = pd.DataFrame({altair_xcolumn : time_value,
                                                 altair_ycolumn: test_value,
                                                "Cell Id":full_id,
                                                "Cycle": cyc_num,
                                                })
                        
           
           
                         alt_data = pd.concat([alt_data, temp_alt], axis = 0,)  # pandas version 2.0 and above deprecated append() function
                         val = float(test_value.iloc[-1]) # for Capacities
                        
                         plotData.append([active_id, val])
                       
                         plotdata.append(plot_val)
                         #ylim = [test_value.min()-1,test_value.max()+0.2]
                         #xlim = [time_value.min()-5,time_value.max()+10]
                         ylim1.append(test_value.min())
                         ylim2.append(test_value.max())
                         xlim1.append(time_value.min())
                         xlim2.append(time_value.max())
                  
                         testname = st.session_state.FileName[file_num].split(".csv")
                         titl.append(testname[0] +"," + " Cell id: " + active_id)
                     #except:
                         # pass
                
                
                
             
     # except:
      #    pass
         


    xlabel = plot_type_x

    ylim1 = np.min(ylim1)
    ylim2 = np.max(ylim2)
    ylim1 = ylim1 - (ylim1 *0.02)
    ylim2 = ylim2 + (ylim2 *0.02)
    ylim = [ylim1,ylim2]
    
    xlim1 = np.min(xlim1)
    xlim2 = np.max(xlim2)
    xlim1 = xlim1 - (xlim1 *0.02)
    xlim2 = xlim2 + (xlim2 *0.02)
    xlim = [xlim1,xlim2]
    
    #ylim,
    st.session_state.Current_plot_full_test_data = plotdata
    st.session_state.Current_plot_full_test_ylabel = ylabel
    st.session_state.Current_plot_full_test_xlabel = xlabel
    st.session_state.Current_plot_full_test_legend = titl
   
    st.session_state.Current_plot_full_test_ylim = ylim
    st.session_state.Current_plot_full_test_xlim = xlim
    #plot(plotdata,ylim,xlim,xlabel,ylabel,titl)
    if variable_type == "Primary variable":  # Some variables such as coulombic efficiency needs be to reprocssed
       plotStep(plotdata,ylim,xlim,xlabel,ylabel,titl)
       plot_altair(alt_data,ylim,xlim)
    else:
       pass
  
    return_data = pd.DataFrame(plotData, columns = ["Cell Id",ylabel])
    return_data.index +=1   # Start numbering index from 1
    return_data.index.rename('Number', inplace=True)
    
    return plotdata, return_data  # this is returned so that user can view the data in table format and download it 
                   



@st.cache_data 
def DVA_SG(currentData,cell_ids, plot_type_x, plot_type_y,align_state,smooth_win_value,xlim_value,ylim_value):
    plotdata = []
    #ylim1 = []
    #ylim2 = []
    #xlim1 = []
    #xlim2 = []
    titl = []
    alt_data = pd.DataFrame()
   
    for k, idata in enumerate(currentData):
        
        num_lines = len(idata[:,0])
        x_values = idata[:,0]
        y_values = idata[:,1]
        dva_values = np.zeros(len(x_values))
        ica_values = np.zeros(len(x_values))
        DVA_q_values = x_values
        ICA_Volt_values = np.zeros(len(x_values))
        
        #num_points_smoothed = 200
        num_points_smoothed = smooth_win_value
        std_wing_size = np.floor(num_lines/num_points_smoothed)
       
        max_wing_size = max([std_wing_size, 1])
        #st.write(max_wing_size)
        
        for row in np.arange(1,num_lines-1):
            
            distance_from_top = row - 1
            distance_from_bottom = (num_lines-1)-row  # need to check this
            wing_size = np.min([distance_from_top,distance_from_bottom,max_wing_size])
            wing_size = int(wing_size)
            #st.write(wing_size)
            if wing_size == 0:
                wing_size = 1
            x_sum = 0
            y_sum = 0
            
            y_aver = 0
            x_aver = 0
            
            # Do SG averaging and differentiation 
            # Need to vectorise this
            for idx in np.arange(-wing_size,wing_size+1):
                
                          
                x_sum = x_sum + (idx*x_values[row+idx])
                y_sum = y_sum + (idx*y_values[row+idx])
                x_aver = x_aver + x_values[row+idx]
                y_aver = y_aver+ y_values[row+idx]
               
            dva_values[row] = y_sum/x_sum
            ica_values [row] = x_sum/y_sum
            DVA_q_values[row] = x_aver/(2*wing_size+1) # current row average capacity  for DVA plot
            ICA_Volt_values[row] = y_aver/(2*wing_size+1) # current row average voltage  for ICA plot
           
        # extrapolate first and last points of the DVA and ICA
        dva_values[0] = dva_values[1] + (x_values[0]-x_values[1]) * (dva_values[2] - dva_values[1])/(x_values[2]-x_values[1])
        ica_values[0] = ica_values[1] + (y_values[0]-y_values[1]) * (ica_values[2] - ica_values[1])/(y_values[2]-y_values[1])
        
        dva_values[-1] =  dva_values[num_lines-2] + (x_values[-1]-x_values[num_lines-2])*(dva_values[num_lines-2] - dva_values[num_lines-3])/(x_values[num_lines-2]-x_values[num_lines-3])
        ica_values[-1] =  ica_values[num_lines-2] + (y_values[-1]-y_values[num_lines-2])*(ica_values[num_lines-2] - ica_values[num_lines-3])/(y_values[num_lines-2]-y_values[num_lines-3])
        DVA_q_values[0] = x_values[0] 
        ICA_Volt_values[0] = y_values[0]
        
        dva = np.column_stack((DVA_q_values,np.abs(dva_values)))
        ica = np.column_stack((ICA_Volt_values,ica_values))
        #st.write(dva_values)
        #st.write(DVA_q_values)
      
        
        if  plot_type_y == "DVA":
            if align_state == "Align right":
                dva[:,0] = dva[:,0][-1]-dva[:,0]
                DVA_q_values = DVA_q_values[-1]-DVA_q_values
            plotdata.append(dva)
            #ylim1 .append(np.min(dva_values))
            #ylim2 .append(np.max(dva_values))
            #xlim1.append(np.min(DVA_q_values))
            #xlim2.append(np.max(DVA_q_values))
            
            #step_num = []
            id_Data = []  # Need array same size as xvalue and yvalue for altair plot
            for i, item_val in enumerate(DVA_q_values):
                  id_Data.append([cell_ids[k]])
                  #step_num.append([Steps[k]])
                  
            id_Data = np.array(id_Data)
            #step_num = np.array(step_num)
            full_id = id_Data[:,0]
            #step_num = cyc_num[:,0]
            temp_alt = pd.DataFrame({plot_type_x +"  (Ah)" : DVA_q_values,
                                    plot_type_y + "  (V/Ah)": np.abs(dva_values),
                                   "Cell Id":full_id,
                                   #"Step Number": step_num,
                                   })
           


            
            
        else:
            if align_state == "Align right":
                ica[:,1] = ica[:,1][-1]-ica[:,1]
                ica_values = ica_values[-1]-ica_values
            plotdata.append(ica)
            #ylim1 .append(np.min(ica_values))
            #ylim2 .append(np.max(ica_values))
            #xlim1.append(np.min(ICA_Volt_values))
            #xlim2.append(np.max(ICA_Volt_values))
            #step_num = []
            id_Data = []  # Need array same size as xvalue and yvalue for altair plot
            for i, item_val in enumerate(ica_values):
                  id_Data.append([cell_ids[k]])
                  #step_num.append([Steps[k]])
                  
            id_Data = np.array(id_Data)
            #step_num = np.array(step_num)
            full_id = id_Data[:,0]
            #step_num = cyc_num[:,0]
            temp_alt = pd.DataFrame({plot_type_x +"  (V)" : ICA_Volt_values,
                                    plot_type_y + "  (Ah/V)": ica_values,
                                   "Cell Id":full_id,
                                   #"Cycle": step_num,
                                   })
       
        alt_data = pd.concat([alt_data, temp_alt], axis = 0,)    
    
        
    if plot_type_y == "DVA":
      xlabel = plot_type_x +"  (Ah)"
      ylabel =  plot_type_y + "  (V/Ah)"
    else:
        xlabel = plot_type_x +"  (V)"
        ylabel =  plot_type_y + "  (Ah/V)"
      

    #ylim1 = np.nanmin(ylim1)/100  # This is the zoom in factor that user can change as well as smooth window
    #ylim1_str = str(ylim1)
    #st.write(ylim1_str)
    #if ylim1_str == "-inf":
        ##ylim1 = 0
    #ylim2 = np.nanmax(ylim2)/100
    #ylim1 = ylim1 - (ylim1 *0.02)
    #ylim2 = ylim2 + (ylim2 *0.02)
    #if ylim1<0:
    #    ylim1 = 0
    #ylim = [ylim1,ylim2]
    #ylim = [0,200]
    #ylim = [0,0.5]
    #st.write(ylim)
    #xlim1 = np.min(xlim1)
    #xlim2 = np.max(xlim2)
    #xlim1 = xlim1 - (xlim1 *0.02)
    #xlim2 = xlim2 + (xlim2 *0.02)
    #xlim = [xlim1,xlim2]
    #xlim = [2.8,3.6]
    
    xlim = xlim_value
    ylim = ylim_value
        
        #ylim,
    #st.write(xlim)
    #st.write(ylim)
    st.session_state.Current_plot_full_test_data = plotdata
    st.session_state.Current_plot_full_test_ylabel = ylabel
    st.session_state.Current_plot_full_test_xlabel = xlabel
    st.session_state.Current_plot_full_test_legend = titl
       
    st.session_state.Current_plot_full_test_ylim = ylim
    st.session_state.Current_plot_full_test_xlim = xlim
    titl = cell_ids
    
    plotStep(plotdata,ylim,xlim,xlabel,ylabel,titl)
    DVA_plot_altair(alt_data,ylim,xlim)

   

    return plotdata

  

              
                                            
@st.cache_data    
def Import_Data(file,cycler,merge_data): 
    temp_dir = tempfile.mkdtemp()
    FileData = []
    FileName = []
    File_cell_IDs = []
    All_cell_ids = []
    Cell_id_file_num = {}
    file_num = 0
  
    if file is not None and file != []:
        
        if cycler == "Novonix":
           
            for ifile in file:
                #Works for Nonovix
                
                
                iifile = open(ifile.name,'r')  # needs file path here
                count = 0

                for line in iifile:
                    count += 1
                                        
                    if line.startswith('[Data]') or  line.startswith('#'):
                      #rows_to_skip.append(count)
                      break
  
                ReadData = pd.read_csv(ifile,skiprows = count,encoding= 'unicode_escape',)
                ReadData.columns = ["Date and Time","Cycle Numner","Step","RunTime","StepTime",
                                    "Current", "Voltage","Capacity","Temperature", "Circuit Temperature (Â°C)",
                                    "Energy (Wh)","dVdt (I/h)", "dIdt (V/h)","StepNumber","Step position"]
                
                FileData .append(ReadData)
             
                
        elif cycler == "Basytec":  
            
            
            for ifile in file: 
                path = os.path.join(temp_dir,ifile.name)
                with open(path,'wb') as f:
                    f.write(ifile.getvalue())
                append_cell_num = 1
                fille =  open(str(path),'r')                   
                #fille =  open(ifile.name,'r')
                lines = fille.readlines()
                count = 0  
                for ii in range(0,len(lines)):
                        if lines[ii].find('~Time[h]') !=-1 or lines[ii].find('#Time[h]') !=-1:
                            #st.write(lines[ii])
                            delimiter = detect(lines[ii])
                            count = ii
                            break
                #st.write(delimiter)
                skip_rows =  np.linspace(0,count-1,count) # should be plus 1
                if ".TXT" in ifile.name or ".txt" in ifile.name:

                    ReadData =  pd.read_csv(ifile, 
                                            #delimiter=" ", # space
                                            delimiter = delimiter,# need to try " " and "," 
                                            #sep = ",", 
                                            encoding= 'unicode_escape',
                                            skiprows = skip_rows,
                                            index_col=False)
                    
                       
                       
                    if ".TXT" in ifile.name:
                        file_extention = ".TXT"
                    else:
                        file_extention = ".txt"
                        
               
                elif ".CSV" in ifile.name or ".csv" in ifile.name:
                     file_extention = ".csv"
                    
                     ReadData =  pd.read_csv(ifile, skiprows = skip_rows)
                #st.write(ReadData.head(20))
                #st.write(skip_rows)
                col_names = ReadData.columns.values
                col_names = list(col_names)
                
                for item in col_names:
                    if item == "~Time[h]":
                        ReadData.rename(columns ={"~Time[h]":"TestTime"}, inplace = True)
                    elif  item  == "#Time[h]":
                        ReadData.rename(columns ={"#Time[h]":"TestTime"}, inplace = True)
                    elif  item  == "Time[h]":
                        ReadData.rename(columns ={"Time[h]":"TestTime"}, inplace = True)
                    elif item == 't-Step[h]':
                        ReadData.rename(columns = {'t-Step[h]':"StepTime"}, inplace = True)
                    elif item == "Line":
                        ReadData.rename(columns = {"Line":"Step"}, inplace = True)
                    elif item == "I[A]":
                        ReadData.rename(columns = {"I[A]":"Current (A)"}, inplace = True)
                    elif item == "U[V]":
                        ReadData.rename(columns = {"U[V]":"Voltage (V)"}, inplace = True)
                    elif item == "Ah[Ah]":
                        ReadData.rename(columns = {"Ah[Ah]":"Capacity (Ah)"}, inplace = True)
                    elif item == "Ah-Step":
                        ReadData.rename(columns = {"Ah-Step":"Step Capacity (Ah)"}, inplace = True)
                    elif item == "T1[°C]":
                            ReadData.rename(columns = {"T1[°C]":"Temperature"}, inplace = True)
                    elif item == "Count":
                            ReadData.rename(columns = {"Count":"Cycle"}, inplace = True)                     
                    elif item == "Command":
                        ReadData.rename(columns = {"Command":"Instruction Name"}, inplace = True)
                   # elif item == "State":
                         #ReadData.rename(columns = {"State":"Instruction Name"}, inplace = True)
                         
                # Check if Instruction Name exits, if yes, change the text to be the same as Maccor
                # Others create and add new column with instruction name
                col_names = ReadData.columns.values
                col_names = list(col_names)
                states = []      
                if "Instruction Name" in col_names:
                    bsy_states = ReadData["Instruction Name"]
                    for istate in bsy_states:
                        if istate == "Pause":
                            states.append("R")
                        elif istate == "Charge":
                            states.append("C")
                        else:
                            states.append("D")     
                    ReadData["Instruction Name"] = states
                else:
                               
                   
                    bsy_steps = ReadData["Step"]
                    bsy_steps = np.unique(bsy_steps)
                    for bsy_step in bsy_steps:
                        # Need to use this method rather than checking current values stepwise
                        # because sometimes, the current sign at the beginning of a step is different
                        bsy_current = ReadData.loc[(ReadData["Step"]==bsy_step),"Current (A)"]
                        
                        if bsy_current.iloc[-1] == 0: 
                            stat = "R"
                        elif bsy_current.iloc[-1]  > 0:
                             stat = "C"
                        else:
                            stat = "D"
                        for ii, ist in enumerate(bsy_current):
                            states.append(stat) 
                            
                    new_col = pd.DataFrame({"Instruction Name":states})
                    ReadData = pd.concat([ReadData,new_col],axis = 1)
                
                
                
                
                
               # num_cells = []
                cell_ids = [] 
                ifile_name = ifile.name
                cellid = ifile_name.split(file_extention)
                cellid =  cellid[0]
                #st.write(cellid)
                cell_ids.append(cellid)
                All_cell_ids.append(cellid)
                
                     
                    
                
                FileData .append(ReadData)
                #st.write(len(ReadData))
                FileName.append(ifile.name)
                File_cell_IDs.append(cell_ids)
                Cell_id_file_num.update({cellid:file_num})
                
                file_num = file_num+1
                
                # State value of 3 is the beginning of a step
                # State value of 2 is the end of a step
                
                
        elif cycler == "PEC": 
            
            
            for ifile in file:
                path = os.path.join(temp_dir,ifile.name)
                with open(path,'wb') as f:
                    f.write(ifile.getvalue())
                append_cell_num = 1
                #fille =  open(ifile.name,'r')
                fille =  open(str(path),'r')
                lines = fille.readlines()
                count = 0
                for ii in range(0,len(lines)):
                    if lines[ii].find('Cell ID') !=-1:
                        count = ii
                        break
                #st.write("count is: ", count)
                
             
                count = count -1
                skip_rows =  np.linspace(0,count,count+1)
                if  count == 0:
                    ReadData =  pd.read_csv(ifile)

                else:
                    ReadData =  pd.read_csv(ifile, skiprows = skip_rows,low_memory=False)
                #st.write(ReadData.head(20))
                #st.write(skip_rows)
                col_names = ReadData.columns.values
                col_names = list(col_names)
                cell_ids = []  
                

                for item in col_names:
                    #count = 0
              
                    if "Temperature" in item:
                        Temp = ReadData[item]
                        if Temp.isnull().any():
                            ReadData[item]= ReadData[item].fillna(0)
                    if  'Cell' in item and 'Cell ID' not in item:
                           ReadData = ReadData.drop(columns =[item])   
                    elif 'Shelf' in item:
                           ReadData = ReadData.drop(columns =[item]) 
                    elif 'Position' in item:
                          ReadData = ReadData.drop(columns =[item]) 
                    elif 'Rack' in item:
                        ReadData = ReadData.drop(columns =[item]) 
                    elif 'Load' in item:
                        ReadData = ReadData.drop(columns =[item]) 
                    elif 'Real' in item:
                        ReadData = ReadData.drop(columns =[item]) 
                    elif 'Cycle Charge Time' in item:
                        ReadData = ReadData.drop(columns =[item])
                    elif 'Cycle Discharge Time' in item:
                        ReadData = ReadData.drop(columns =[item])
                    elif 'ReasonCode' in item:
                        ReadData = ReadData.drop(columns =[item])
                    elif '50% DoD' in item:
                        ReadData = ReadData.drop(columns =[item])
                    elif 'PeakPower' in item:
                        ReadData = ReadData.drop(columns =[item])
                    elif 'Open Circuit' in item:
                        ReadData = ReadData.drop(columns =[item])
                    elif 'Resistance' in item:
                        ReadData = ReadData.drop(columns =[item])
                    elif 'Coulombic Efficiency' in item:
                        ReadData = ReadData.drop(columns =[item])
                    elif 'Energy' in item:
                        ReadData = ReadData.drop(columns =[item])
                    elif 'Contact' in item:
                        ReadData = ReadData.drop(columns =[item])
                    elif 'Unnamed' in item:
                        ReadData = ReadData.drop(columns =[item])
                    
                  
                        
                        # handle single file capacipity and voltage units
                        #multiple cell file will be handled later when we do column splitting
                    
                    if  item =="Voltage (mV)" :
                            #max_volt = ReadData[item]
                            #max_volt = max_volt.max()
                            ReadData[item] = ReadData[item]/1000
                            ReadData.rename(columns = {item:"Voltage (V)"}, inplace = True)
                            
                    if  item =="Current (mA)" :
                            #max_volt = ReadData[item]
                            #max_volt = max_volt.max()
                            ReadData[item] = ReadData[item]/1000
                            ReadData.rename(columns = {item:"Current (A)"}, inplace = True)
                            
                    if  item == "Charge Capacity (mAh)":
                        ReadData[item] = ReadData[item]/1000
                        ReadData.rename(columns = {item:"Charge Capacity (Ah)"}, inplace = True)
                        
                    if  item == "Discharge Capacity (mAh)":
                        ReadData[item] = ReadData[item]/1000
                        ReadData.rename(columns = {item:"Discharge Capacity (Ah)"}, inplace = True)   
                        
                        
                        
                        
                # Check if file contains multiples cells stacked vertically -
                
                check_col_stack = ReadData["Cell ID"]
                check_col_stack = check_col_stack .dropna()
                check_col_stack =  np.unique(check_col_stack )
                
               
                
                
               
                #check_col_stack = set(ReadData["Cell ID"])
                
                if len(check_col_stack) > 1:
                    for cellid in check_col_stack:
                        
                        temp_ReadData = ReadData.loc[(ReadData["Cell ID"]==cellid)]     
                                
                        if cellid in Cell_id_file_num.keys():
                                if merge_data == False:
                                   cellid =  cellid + '_count_' + str(append_cell_num)                           
                                   Cell_id_file_num.update({cellid:file_num})
                                   FileData .append(temp_ReadData)
                                   cell_ids.append(cellid)
                                   All_cell_ids.append(cellid)
                                   File_cell_IDs.append(cell_ids)
                                   FileName.append(ifile.name)
                                   file_num = file_num+1  # Herefile_num is no longer the actual file number but count of unique cell id and data in FileData
                                  
                                   
                                else:
                                     old_data_file_num = Cell_id_file_num[cellid]
                                     old_data =  FileData[old_data_file_num]
                                     old_test_num = old_data["Test"].iloc[0]
                                     new_test_num = temp_ReadData["Test"].iloc[0]
                                     
                                     if new_test_num>old_test_num: #append new file to old file
                                        last_old_test_time = old_data['Total Time (Seconds)'].iloc[-1]
                                        first_new_test_time = temp_ReadData['Total Time (Seconds)'].iloc[0]
                                        temp_ReadData['Cycle'] = temp_ReadData['Cycle'] + 1
                                        old_data_cyc = old_data['Cycle'].iloc[-1]
                                        temp_ReadData['Cycle'] = temp_ReadData['Cycle'] + old_data_cyc
                                        
                                        
                                        if first_new_test_time < 0 or first_new_test_time == 0:
                                            temp_ReadData['Total Time (Seconds)'].iloc[0] = 0.02      
                                            
                                        new_time = temp_ReadData['Total Time (Seconds)'] + last_old_test_time
                                        temp_ReadData['Total Time (Seconds)'] = new_time
                                                                           
                                        temp_ReadData=  pd.concat([old_data, temp_ReadData], axis = 0,)
                                       
                                     FileData[old_data_file_num] = temp_ReadData
                      
                        
                      
                        else:  # Cell Id has not repeated
                            
                            Cell_id_file_num.update({cellid:file_num})
                            cell_ids.append(cellid)
                            All_cell_ids.append(cellid)
                            FileData .append(temp_ReadData)
                            FileName.append(ifile.name)
                            File_cell_IDs.append(cell_ids)
                            file_num = file_num+1   # Herefile_num is no longer the actual file number but count of unique cell id and data in FileData

                    
                    
                
                
                
                        
                
                else: # Single cell file or multiple files concatenated horizontally
                    col_names = ReadData.columns.values
                    col_names = list(col_names)  
                    num_cell = col_names[-1].split(".")
                    #st.write(num_cell[1])
                   
                    
                    if len(num_cell)>1:
                      num_cell = int(num_cell[1])
                    else:
                        num_cell = 0
                    #st.write(num_cell)
                    
                   
                    cell0_columns = []
                    for item in col_names:
                        if "." not in item:
                            cell0_columns.append(item)
                    cell0 = ReadData.filter(items = cell0_columns)
                    
                    cell0 = cell0.dropna()
                    #st.write(cell0)
                    
                    cellid  = cell0['Cell ID'].iloc[0]
                   
                    
                    if cellid in Cell_id_file_num.keys():
                        if merge_data == False:
                           cellid =  cellid + '_count_' + str(append_cell_num)                           
                           Cell_id_file_num.update({cellid:file_num})
                           cell0['Cell ID'] = cellid
                           FileData .append(cell0)
                           cell_ids.append(cellid)
                           All_cell_ids.append(cellid)
                           File_cell_IDs.append(cell_ids)
                           FileName.append(ifile.name)
                           file_num = file_num+1  # Herefile_num is no longer the actual file number but count of unique cell id and data in FileData
                          
                           
                        else:
                             old_data_file_num = Cell_id_file_num[cellid]
                             old_data =  FileData[old_data_file_num]
                             old_test_num = old_data["Test"].iloc[0]
                             new_test_num = cell0["Test"].iloc[0]
                             
                             if new_test_num>old_test_num: #append new file to old file
                                last_old_test_time = old_data['Total Time (Seconds)'].iloc[-1]
                                first_new_test_time = cell0['Total Time (Seconds)'].iloc[0]
                                cell0['Cycle'] = cell0['Cycle'] + 1
                                old_data_cyc = old_data['Cycle'].iloc[-1]
                                cell0['Cycle'] = cell0['Cycle'] + old_data_cyc
                                
                                
                                if first_new_test_time < 0 or first_new_test_time == 0:
                                    cell0['Total Time (Seconds)'].iloc[0] = 0.02      
                                    
                                new_time = cell0['Total Time (Seconds)'] + last_old_test_time
                                cell0['Total Time (Seconds)'] = new_time
                                                                   
                                cell0 =  pd.concat([old_data, cell0], axis = 0,)
                               
                             FileData[old_data_file_num] = cell0
                            
    
                               
                        
                    else:  # Cell id is not found in another file yet
                                           
                        Cell_id_file_num.update({cellid:file_num})
                       
                      
                        cell_ids.append(cellid)
                        All_cell_ids.append(cellid)
                        FileData .append(cell0)
                        FileName.append(ifile.name)
                        File_cell_IDs.append(cell_ids)
                        file_num = file_num+1   # Herefile_num is no longer the actual file number but count of unique cell id and data in FileData
    
    
                    if num_cell >1:  # Multiple cells in a file concatenated horizontally
                        cell_list = np.linspace(1,num_cell,num_cell)
                        #st.write(cell_list)
                    
                       
                        for icell in cell_list:                        
                            icell = int(icell)
                            cc = rf'\.{icell}\b'   #adds boundary to the string so that the exact string is searched
                            
                            
                            #cell_n = ReadData.filter(like = cc, axis = 1)
                            cell_n = ReadData.loc[:,ReadData.columns.str.contains(cc)]
                          
                            #cell_n = ReadData.filter(regex = cc, axis = 1)
                            cell_n = cell_n.dropna()
                            cell_n_cols = cell_n.columns.values
                            #st.write(cell_n)
                         
        
                            for item in cell_n_cols:
                                item_n =  item.split(".")                       
                                item_n =  item_n[0]
                              
                                
                                if  item_n  == "Voltage (mV)" :
                                        #max_volt = ReadData[item]
                                        #max_volt = max_volt.max()
                                        cell_n.rename(columns = {item:"Voltage (V)"}, inplace = True)
                                        cell_n["Voltage (V)"] = cell_n["Voltage (V)"]/1000
                                        
                                        
                                elif  item_n =="Current (mA)":
                                        #max_volt = ReadData[item]
                                        #max_volt = max_volt.max()
                                        cell_n.rename(columns = {item:"Current (A)"}, inplace = True)
                                        cell_n["Current (A)"] = cell_n["Current (A)"]/1000
                                        
                                        
                                elif  item_n == "Charge Capacity (mAh)":
                                    cell_n.rename(columns = {item:"Charge Capacity (Ah)"}, inplace = True)
                                    cell_n["Charge Capacity (Ah)"] = cell_n["Charge Capacity (Ah)"]/1000
                                    
                                    
                                elif  item_n == "Discharge Capacity (mAh)":
                                    cell_n.rename(columns = {item:"Discharge Capacity (Ah)"}, inplace = True)
                                    cell_n["Discharge Capacity (Ah)"] = cell_n["Discharge Capacity (Ah)"]/1000
                                    
                                else: 
                                    cell_n.rename(columns = {item:item_n}, inplace = True)
                                
                                
                                
                           
                            cellid  = cell_n['Cell ID'].iloc[0]
                            
                            if cellid in Cell_id_file_num.keys():
                                if merge_data == False:
                                   cellid =  cellid + '_count_' + str(append_cell_num)                           
                                   Cell_id_file_num.update({cellid:file_num})
                                   cell_n['Cell ID'] = cellid
                                   FileData.append(cell_n)
                                   cell_ids.append(cellid)
                                   All_cell_ids.append(cellid)
                                   FileName.append(ifile.name)
                                   File_cell_IDs.append(cell_ids)
                                   file_num = file_num+1      # Herefile_num is no longer the actual file number but count of unique cell id and data in FileData
                           
                                   
                                   
                                else:
                                    
                                    old_data_file_num = Cell_id_file_num[cellid]
                                    old_data =  FileData[old_data_file_num]
                                    old_test_num = old_data["Test"].iloc[0]
                                    new_test_num = cell_n["Test"].iloc[0]
                                    
                                    if new_test_num>old_test_num: #append new file to old file
                                       last_old_test_time = old_data['Total Time (Seconds)'].iloc[-1]
                                       first_new_test_time = cell_n['Total Time (Seconds)'].iloc[0]
                                       cell_n['Cycle'] = cell_n['Cycle'] + 1
                                       old_data_cyc = old_data['Cycle'].iloc[-1]
                                       cell_n['Cycle'] = cell_n['Cycle'] + old_data_cyc
                                       
                                       if first_new_test_time < 0 or first_new_test_time == 0:
                                           cell_n['Total Time (Seconds)'].iloc[0] = 0.02      
                                           
                                       new_time = cell_n['Total Time (Seconds)'] + last_old_test_time
                                       cell_n['Total Time (Seconds)'] = new_time
                                          
                                       cell_n =  pd.concat([old_data, cell_n], axis = 0,)
                                      
                                    FileData[old_data_file_num] = cell_n # replace old data with new data
         
                                
                                
                            else:  # Cell id is not found in another file yet
                                
                                Cell_id_file_num.update({cellid:file_num})
                                cell_ids.append(cellid)
                                All_cell_ids.append(cellid)
                                FileData .append(cell_n)
                                FileName.append(ifile.name)
                                File_cell_IDs.append(cell_ids)
                                file_num = file_num+1   # Herefile_num is no longer the actual file number but count of unique cell id and data in FileData
                        
                
                

                append_cell_num =  append_cell_num + 1 
                
            #st.write(Cell_id_file_num)
            #st.write(FileName)
            #st.write(len(FileData))
            
           
                
                
                
            
        elif cycler == "Maccor": 
                
                for ifile in file:
                    #st.write(ifile)
                    #fille =  open(ifile.name,'r')
                    path = os.path.join(temp_dir,ifile.name)
                    with open(path,'wb') as f:
                        f.write(ifile.getvalue())
                    append_cell_num = 1
                    fille =  open(str(path),'r')   
                    lines = fille.readlines()
                    count = 0
                    
                    for ii in range(0,len(lines)):
                        if lines[ii].find('Rec') !=-1:
                            
                            count = ii
                            delimiter = detect(lines[ii])
                            break
                    #st.write("count is: ", count)
                    #st.write(ifile)
                 
                    
                    skip_rows =  np.linspace(0,count-1,count) # should be plus 1
                    if ".TXT" in ifile.name or ".txt" in ifile.name:
                        ReadData =  pd.read_csv(ifile, delimiter=delimiter,skiprows = skip_rows,index_col=False)
                        if ".TXT" in ifile.name:
                            file_extention = ".TXT"
                        else:
                            file_extention = ".txt"
                            
                   
                    elif ".CSV" in ifile.name or ".csv" in ifile.name:
                         file_extention = ".csv"
                        
                         ReadData =  pd.read_csv(ifile, skiprows = skip_rows)
                    #st.write(ReadData.head(20))
                    #st.write(skip_rows)
                    col_names = ReadData.columns.values
                    col_names = list(col_names)
                    #st.write(col_names)
                   # num_cells = []
                    cell_ids = []  # need to get cell ids as well as this will need to be used sellecting plots
                    
 
                            
                            
                    for item in col_names:
                        if item == "Cyc":
                            ReadData.rename(columns ={"Cyc":"Cycle"}, inplace = True)
                        elif  item  == "Cycle C":
                            ReadData.rename(columns = {"Cycle C":"Cycle"}, inplace = True)
                        elif item == "Cap. [Ah]":
                            ReadData.rename(columns = {"Cap. [Ah]":"Capacity (Ah)"}, inplace = True)
                        elif item == "Capacity[Ah]":
                             ReadData.rename(columns = {"Capacity[Ah]":"Capacity (Ah)"}, inplace = True)
                        elif item == "Temp 1":
                             ReadData.rename(columns = {"Temp 1":"Temperature"}, inplace = True)
                        elif item == "Capacity (AHr)":
                             ReadData.rename(columns = {"Capacity (AHr)":"Capacity (Ah)"}, inplace = True)
                        elif item == "Amphr":
                            ReadData.rename(columns = {"Amphr":"Capacity (Ah)"}, inplace = True)
                        elif item == "Amps":
                            ReadData.rename(columns = {"Amps":"Current (A)"}, inplace = True)
                        elif item == "Current [A]":
                            ReadData.rename(columns = {"Current [A]":"Current (A)"}, inplace = True)
                        elif item == "Voltage [V]":
                            ReadData.rename(columns = {"Voltage [V]":"Voltage (V)"}, inplace = True)   
                        elif item == "Test Time (min)":
                              ReadData.rename(columns = {"Test Time (min)":"TestTime"}, inplace = True)   
                        elif item == "Step Time (min)":
                              ReadData.rename(columns = {"Step Time (min)":"StepTime"}, inplace = True)     
                        elif item == "Volts":
                            ReadData.rename(columns = {"Volts":"Voltage (V)"}, inplace = True)
                            # Sometimes, the imported values use comma if units are in mV
                            ReadData["Voltage (V)"] = ReadData["Voltage (V)"].replace(",","", regex = True)
                            ReadData["Voltage (V)"] =  ReadData["Voltage (V)"].astype(float)
                            #ReadData["Voltage [V]"] =  float(ReadData["Voltage [V]"])
                            maxVolt = ReadData["Voltage (V)"].max()
                            if maxVolt>10:
                                ReadData["Voltage (V)"] = ReadData["Voltage (V)"]/1000
                        elif item == "Md":
                            ReadData.rename(columns = {"Md":"Instruction Name"}, inplace = True)
                        elif item == "MD":
                            ReadData.rename(columns = {"MD":"Instruction Name"}, inplace = True)
                        elif item == "State":
                             ReadData.rename(columns = {"State":"Instruction Name"}, inplace = True)
                      
                            
                     # Check if Cycle count is not included. This has been seen from data from Cognition why cycle data does not include cycle count but increments of steps
                     # Tried to use unique step values for each instruction block but the data from cognition does not assign unique step number for each half cycle block. The step numbers are repeated
                     
                    col_names = ReadData.columns.values
                    #st.write(col_names)
                    
                    if "Cycle" not in col_names:
                        ReadData["Cycle"] =  ReadData["Step"]
                        Ins = ReadData["Instruction Name"]
                        #uniq = np.unique(Ins)
                        #st.write(uniq)
                        cyc_count = 0

                        
                        # This block of conditional statement is based on pouch cell cycling data from cognition
                        for ii in range(0,len(Ins)):
                             ReadData["Cycle"][ii] =  cyc_count 
                             
                             if  Ins[ii] == "C" and  ReadData["ES"][ii]  == 133: 
                                 cc_cap =  ReadData["Capacity (Ah)"][ii]  # get the maximum  CC charge capacity - Maccor seperates the CC and CV charge capacities
                                 
                             if  Ins[ii] == "C" and ReadData["ES"][ii]  == 132:  
                                
                                 cv_cap =  ReadData["Capacity (Ah)"][ii]
                                 ReadData["Capacity (Ah)"][ii]  = cv_cap + cc_cap
                                 
                                 cyc_count  =  cyc_count  + 1
                                   
                            
                                 
                                 
                                 

                    
                    ifile_name = ifile.name
                    cellid = ifile_name.split(file_extention)
                    cellid =  cellid[0]
                    #st.write(cellid)
                    cell_ids.append(cellid)
                    All_cell_ids.append(cellid)
                    
                    time_data = ReadData["TestTime"]
                    step_time_data =  ReadData["StepTime"]
                    time_data_0 = str(time_data[0])
                    
                    
                    if 'd' in time_data_0:
                        convert_test_time = Time_conversion(time_data)
                        ReadData["TestTime"] = convert_test_time
                        convert_step_time = Time_conversion(step_time_data)
                        ReadData["StepTime"] = convert_step_time
                        st.write("Time data has been converted from days to hours")
                    else:
                        # the 
                        ReadData["TestTime"] = ReadData["TestTime"].replace(",","",regex = True)
                        ReadData["TestTime"] = ReadData["TestTime"].astype(float)
                        ReadData["StepTime"] = ReadData["TestTime"].replace(",","", regex = True)
                        ReadData["StepTime"] = ReadData["StepTime"].astype(float)
                    
                            
                            
                        
                        
                    
                    FileData .append(ReadData)
                    #st.write(len(ReadData))
                    FileName.append(ifile.name)
                    File_cell_IDs.append(cell_ids)  
                    Cell_id_file_num.update({cellid:file_num})                    
                    file_num = file_num+1
                    
                    
    
        elif cycler == "BioLogic":      
               for ifile in file:
                   #fille =  open(ifile.name,'r')
                   path = os.path.join(temp_dir,ifile.name)
                   with open(path,'wb') as f:
                       f.write(ifile.getvalue())
                   append_cell_num = 1
                   fille =  open(str(path),'r')   
                   lines = fille.readlines()
                   count = 0
                   for ii in range(0,len(lines)):
                       if lines[ii].find('(Q-Qo)') !=-1 or lines[ii].find('freq/Hz') !=-1:
                           
                           count = ii
                           delimiter = detect(lines[ii])
                           break
                   #st.write("count is: ", count)
                   #st.write(ifile)
                                  
                   skip_rows =  np.linspace(0,count-1,count) # should be plus 1
                   if ".TXT" in ifile.name or ".txt" in ifile.name:
                       ReadData =  pd.read_csv(ifile, delimiter=delimiter,skiprows = skip_rows,index_col=False)
                       if ".TXT" in ifile.name:
                           file_extention = ".TXT"
                       else:
                           file_extention = ".txt"
                           
                  
                   elif ".CSV" in ifile.name or ".csv" in ifile.name:
                        file_extention = ".csv"
                       
                        ReadData =  pd.read_csv(ifile, skiprows = skip_rows)
                   #st.write(ReadData.head(20))
                   #st.write(skip_rows)
                   col_names = ReadData.columns.values
                   col_names = list(col_names)
                   #st.write(col_names)
                  # num_cells = []
                   cell_ids = []  # need to get cell ids as well as this will need to be used sellecting plots
                   

                           
                           
                   for item in col_names:
                       if item == "time/s":
                           ReadData.rename(columns ={"time/s":"TestTime"}, inplace = True)
                       elif  item  == "cycle number":
                           ReadData.rename(columns = {"cycle number":"Cycle"}, inplace = True)
                       elif item == "Capacity/mA.h":
                           ReadData.rename(columns = {"Capacity/mA.h":"Capacity (Ah)"}, inplace = True)
                           ReadData["Capacity (Ah)"] = ReadData["Capacity (Ah)"]/1000
                       elif item == "<I>/mA":
                           ReadData.rename(columns = {"<I>/mA":"Current (A)"}, inplace = True)
                           ReadData["Current (A)"] = ReadData["Current (A)"]/1000
                       elif item == "Ewe/V" or item == "<Ewe/V>":
                           ReadData.rename(columns = {"Ewe/V":"Voltage (V)"}, inplace = True)
                       elif item == "<Ewe>/V":
                           ReadData.rename(columns = {"<Ewe>/V":"Voltage (V)"}, inplace = True)
                       elif item == "mode":
                           ReadData.rename(columns = {"mode":"Step"}, inplace = True)
                       elif item == "Q discharge/mA.h":
                          ReadData.rename(columns = {"Q discharge/mA.h":"Discharge Capacity (Ah)"}, inplace = True)
                          ReadData["Discharge Capacity (Ah)"] = ReadData["Discharge Capacity (Ah)"]/1000
                       elif item == "Q charge/mA.h":
                          ReadData.rename(columns = {"Q charge/mA.h":"Charge Capacity (Ah)"}, inplace = True)
                          ReadData["Charge Capacity (Ah)"] = ReadData["Charge Capacity (Ah)"]/1000
                          
                          
                    
                   col_names = ReadData.columns.values
                   if "Step" in col_names:
                       blg_steps = ReadData["Step"]
                       blg_redox = ReadData["ox/red"]
    
                       states = []
                       for istep, bgl_step in enumerate(blg_steps):
                            # Add instruction name column
                            mode =  blg_steps.iloc[istep]
                            redox = blg_redox.iloc[istep]
                           
                        
                            if mode == 3: 
                               states.append("R")
                            elif mode == 1 and redox == 1: 
                                states.append("C")
                            elif mode == 2 and redox == 1: 
                                states.append("CV")
                            elif mode == 1 and redox == 0: 
                                states.append("D")
                                
                                
                       new_col = pd.DataFrame({"Instruction Name":states})
                       ReadData = pd.concat([ReadData,new_col],axis =1)  
                       
                   if 'freq/Hz' in col_names:
                       st.session_state.EIS = "Yes"
                       if 'Step' not in col_names:
                           ReadData.rename(columns = {"Ns":"Step"}, inplace = True)
                       if '#NAME?' in col_names:
                           ReadData.rename(columns = {"#NAME?":"Im(Z)/Ohm"}, inplace = True)
                       if '-Im(Z)/Ohm' in col_names:
                           ReadData.rename(columns = {"-Im(Z)/Ohm":"Im(Z)/Ohm"}, inplace = True)
                           

                        
                   # Relevant data that is required can be filter by using this line of code
                   #ReadData = ReadData.filter(items = ['freq/Hz','Re(Z)/Ohm','Im(Z)/Ohm','Step','Cycle'])
                    
                   
                    
                   
                   ifile_name = ifile.name
                   cellid = ifile_name.split(file_extention)
                   cellid =  cellid[0]
                   cell_ids.append(cellid)
                  
                   
 
                       
                   
                   FileData .append(ReadData)
                   #st.write(len(ReadData))
                   FileName.append(ifile.name)
                   File_cell_IDs.append(cell_ids)  
                   All_cell_ids.append(cellid)
                   Cell_id_file_num.update({cellid:file_num})
                   
                   file_num = file_num+1
                   
                                              
        elif cycler == "Other data file":  
            
                for ifile in file:
                    #st.write(ifile)

                    if ".TXT" in ifile.name or ".txt" in ifile.name:
                        ReadData =  pd.read_csv(ifile, delimiter=delimiter,index_col=False)
                        if ".TXT" in ifile.name:
                            file_extention = ".TXT"
                        else:
                            file_extention = ".txt"
                            
                   
                    elif ".CSV" in ifile.name or ".csv" in ifile.name:
                         file_extention = ".csv"
                        
                         ReadData =  pd.read_csv(ifile)
                         
                    ifile_name = ifile.name                        
                    FileData .append(ReadData)
                    FileName.append(ifile.name)
                    cellid = ifile_name.split(file_extention)
                    cellid =  cellid[0]
                    File_cell_IDs.append(cellid)  
                    Cell_id_file_num.update({cellid:file_num})
                    All_cell_ids.append(cellid)
                    file_num = file_num+1
                    
                    

    return FileData,FileName,File_cell_IDs, All_cell_ids,Cell_id_file_num








with st.sidebar.expander("Import Data File"):
    form = st.form("Read Data")
    cycler_tip = "Select cycler associated with test data"
    cycler = form.radio("Cycler name",("Basytec",
                                       "Novonix",
                                       "PEC",
                                      "Maccor",
                                       "BioLogic",
                                       "Other data file"
                                       # Next generic file just to plot
                                       ), help = cycler_tip)
    
    merge_tip = " If this option is selected, "
    merge_tip2 = "all the data from the same cell id found in different imported files will be merged together. " 
    merge_tip3 = "This is only availaible for PEC cycler at the moment"
    merge_data = form.checkbox("Merge data", value = False, help = merge_tip+merge_tip2+merge_tip3)
    tip = "Upload test data files"
    
    file = form.file_uploader("Upload test data file",accept_multiple_files=True,
                            help = tip)

   
    
    #if st.session_state.sol is not False and PlotVariable is not None:
        #solData = session_state.sol[PlotVariable].entries
        #FileData.append(solData)
        


            
            
    FileData,FileName,File_cell_IDs, All_cell_ids,Cell_id_file_num =  Import_Data(file,cycler,merge_data)   
            
            
            
            
            
    
    
    submit = form.form_submit_button('Upload') 
    
    
    if submit:
        #st.write(FileName)
        #FileName = np.unique(FileName)
        st.session_state.TestData = FileData
        st.session_state.FileName = FileName
        #st.session_state.CellIds = File_cell_IDs
        st.session_state.CellIds = All_cell_ids
        st.session_state.Active_CellIds = All_cell_ids# File_cell_IDs  # default
        st.session_state.All_cell_ids = All_cell_ids
        st.session_state.Cycler_Name =  cycler
        st.session_state.Cell_ids_and_file_nums = Cell_id_file_num
        
        #st.write(st.session_state.All_cell_ids )
        #st.write(All_cell_ids)
     
      
        #Need to save cell ids in any file
     
 
    
 
    
 
if st.session_state.TestData == []:
    pass 
else:
    with st.sidebar.expander("Plot styles"):
        form = st.form("Line styles")
        
        if st.session_state.Cycler_Name == "Other data file": 
            ls = form.selectbox("Select plot linestyle", ('solid', 'dashed', 'dashdot', 'dotted',"Scatter plot"))
        else:
            ls = form.selectbox("Select plot linestyle", ('solid', 'dashed', 'dashdot', 'dotted'))
            
        user_xlim = form.text_input("Enter x-axis limits, separate with comma", value = None)
        user_ylim = form.text_input("Enter y-axis limits, separate with comma", value = None)
        reset_lims = form.checkbox("Reset axis limits", value = False)
        submit = form.form_submit_button('Ok')
        
        if submit:
        
            st.session_state.linestyle = ls
            if  reset_lims == True:
                user_xlim = None
                user_ylim = None
            st.session_state.glob_Xlim = user_xlim
            st.session_state.glob_Ylim = user_ylim
            
            
    

   
   
if st.session_state.TestData == []:
    
    pass
else:

    with st.sidebar.expander("Select Cells/Files for analysis"):
        form = st.form("Active Cell IDs")
        if st.session_state.Cycler_Name == "PEC":
            sect_name = "Cell Id"
        else:
            sect_name = "File Id"
        active_Cells = form.multiselect(sect_name,st.session_state.All_cell_ids+["All cells"])
        
        st.write("List of imported files",set(st.session_state.FileName))
        
        submit = form.form_submit_button('Ok')
    
        if submit:

           if active_Cells == ["All cells"]:
               st.session_state.Active_CellIds  = st.session_state.All_cell_ids
               
           else:
               st.session_state.Active_CellIds = active_Cells
           
           st.write("Current active cells", active_Cells)





# Display dataframe
if st.session_state.TestData == []:
    pass
elif st.session_state.Cycler_Name == "Other data file": 
    st.write(st.session_state.TestData[0])
else:
    st.write(st.session_state.TestData[0].head(20))
    #st.write(st.session_state.TestData[0])
    num_data = len(st.session_state.TestData)
    steps =  st.session_state.TestData[0]["Step"]
    counts = st.session_state.TestData[0]["Cycle"]
    counts = np.unique(counts)
    temp_data = st.session_state.TestData[0]
    steps = np.unique(steps)
    steps = steps[~np.isnan(steps)]
    counts = counts[~np.isnan(counts)]  # cycle count
    
    
    if num_data > 1:
        # steps_1 =  st.session_state.TestData[1]["Step"]
        # counts_1 = st.session_state.TestData[1]["Cycle"]
        # counts_1 = np.unique(counts_1)
        # temp_data_1 = st.session_state.TestData[1]
        # steps_1 = np.unique(steps_1)
        # steps_1 = steps_1[~np.isnan(steps_1)]
        # counts_1 = counts_1[~np.isnan(counts_1)]  # cycle count
        # step_size_1 = len(steps_1)
        # step_size = len(steps)
        # if step_size_1 > step_size:
        #     steps = steps_1
        #     counts = counts_1
        #     temp_data = temp_data_1
            
        ###################################    
        #steps_temp = []
        #counts_temp = []
        # This part esures that the highest number of counts and steps are used
        
        count_len = []
        step_len = []
        
        Count_dict = {}
        Step_dict = {}
       
        
       
        
        for ii in range(len(st.session_state.TestData)):
            stp =  st.session_state.TestData[ii]["Step"]
            cnt =  st.session_state.TestData[ii]["Cycle"]
            stp =  np.unique(stp)
            cnt =  np.unique(cnt)
            
            stp = stp[~np.isnan(stp)]
            cnt = cnt[~np.isnan(cnt)]  # cycle count
            
            
            ln_count = len(cnt)
            ln_stp = len(stp)
            
            Count_dict.update({ln_count:cnt})
            Step_dict.update({ln_stp:stp})
            
            
            #steps_temp.append(stp)
            #counts_temp.append(cnt)
            count_len.append(ln_count)
            step_len.append(ln_stp)
            
            
            
        #st.write(steps_temp)  
        #st.write(counts_temp)
        #st.write(step_len)
        #st.write(count_len)
        #st.write(Count_dict)
        #st.write(Step_dict)
        
        
        max_count = max(count_len)
        max_step = max(step_len)
        
        counts = Count_dict[max_count]
        steps = Step_dict[max_step]
        
        #st.write(max_count)
        #st.write(max_step)
        
        #st.write(counts)
        #st.write(steps)
        
        
        
     
        
        
        
        #findout the most effective how to now select the steps and counts with higher numbers
        

# Full data plots   

if  st.session_state.TestData == []:
    pass
elif st.session_state.EIS == "Yes": #cycle number sorts multiple EIS in a single file
    st.session_state.Allow_legend = "Yes"
    st.session_state.Cycle_plot = "No"
    empty_tab, Nyquist_plot, Bode_plot_real, Bode_plot_Im,log_Bode_plot_real, log_Bode_plot_Im,  = st.tabs([" ","Nyquist Plot", "Re-Bode Plot",
                   "Im-Bode Plot","Log Re-Bode Plot"," Log Im-Bode Plot",])
                                                           
    with empty_tab:
        pass
    with Nyquist_plot:
        eis = full_EIS_data_plot("Nyquist Plot","Primary variable",counts)
        
    with Bode_plot_real:
        eis = full_EIS_data_plot("Re-Bode Plot","Primary variable",counts)
        
    with Bode_plot_Im:
        eis = full_EIS_data_plot("Im-Bode Plot","Primary variable",counts)
        
    with log_Bode_plot_Im:
        eis = full_EIS_data_plot("Log Im-Bode Plot","Primary variable",counts)
        
    with log_Bode_plot_real:
        eis = full_EIS_data_plot("Log Re-Bode Plot","Primary variable",counts)
        
#elif st.session_state.Cycler_Name == "Other data file": 
    #pass       
elif st.session_state.Cycler_Name != "PEC" and st.session_state.Cycler_Name != "Other data file":
    st.session_state.Allow_legend = "Yes"
    st.session_state.Cycle_plot = "No"
    empty_tab, voltage_plot, current_plot, charge_capacity_plot,discharge_capacity_plot,temperature_plot,\
        CE_plot, \
        = st.tabs([" ","Voltage", "Current",
                   "Charge Capacity","Discharge Capacity","Temperature", 
                   "Coulombic Efficiency",])
                                                           
    with empty_tab:
        pass
        
    # need to make this function return these values some to be displayed in the table
    
    with voltage_plot:
        #if st.session_state.Cycler_Name == "PEC":
            
            #volt = full_pec_test_data_plot("Voltage (V)","Primary variable")
        #else:
            volt = full_test_data_plot("Voltage (V)","Primary variable")
            
        
    with current_plot:
        #if st.session_state.Cycler_Name == "PEC":      
            #curr =  full_pec_test_data_plot("Current (A)","Primary variable")
        #else:
            curr =  full_test_data_plot("Current (A)","Primary variable")
    
    
    with charge_capacity_plot:
       # if st.session_state.Cycler_Name == "PEC":
           # charge_cap = full_pec_test_data_plot("Charge Capacity (Ah)","Primary variable") 
       # else:
            charge_cap = full_test_data_plot("Charge Capacity (Ah)","Primary variable") 
       
            st.write(charge_cap)
    with discharge_capacity_plot:
          #if st.session_state.Cycler_Name == "PEC":
              #discharge_cap =  full_pec_test_data_plot("Discharge Capacity (Ah)","Primary variable")
          #else:
              discharge_cap =  full_test_data_plot("Discharge Capacity (Ah)","Primary variable")
             
          
              st.write(discharge_cap)
    
    with temperature_plot:
        #if st.session_state.Cycler_Name == "PEC":
            #full_pec_test_data_plot("Temperature","Primary variable")
       # else:
            pass
           
        
    with CE_plot:
        formation_CE(counts,steps)
        

      
            
      

                                
      
if  st.session_state.TestData == []:
     pass
elif st.session_state.Cycler_Name == "PEC":
    st.session_state.Allow_legend = "Yes"
    st.session_state.Cycle_plot = "No"
    with st.sidebar.expander("Full Test Data Plot"):
        form = st.form("Plot Variable Selection")
        plot_type = form.multiselect("Full test data plot",("Voltage (V)","Current (A)",
                                                                     "Charge Capacity (Ah)","Discharge Capacity (Ah)",
                                        "Temperature","Coulombic Efficiency"),
                                  placeholder="Select plot variable",)
        

        
        
        tip = "Checking the box will include interactive plots"
        interactive_plot = form.checkbox("Include interactive plot", value = False, help = tip)
        
        
    
        submit = form.form_submit_button('Plot')
    
    if submit:
        if  interactive_plot == True:
            st.session_state.Interactive_Plot = True
        else:
            st.session_state.Interactive_Plot = False
        if plot_type == "Coulombic Efficiency":
            
            formation_CE(counts,steps)
        else:
            if len (plot_type)>1: 
                plot_val =  stack_plot(plot_type)
               
            else:
                plot_val = full_pec_test_data_plot(plot_type,"Primary variable")
                
            
        if "Capacity" in plot_type:
            st.write(plot_val)
      
        #add another input box to allow multiple stack/layered plots












if  st.session_state.TestData == []:
     pass
elif st.session_state.EIS == "Yes":
    with st.expander("Info for EIS data fitting"):
        """
        EIS fitting is performed using Impedance.py tool.
        
        More details and documentation on impedance.py can be found here: https://impedancepy.readthedocs.io/en/latest/getting-started.html 
        
        To fit EIS data, select from the prebuilt equivaent circuit models or use the custom circuit option to
        configure your required ECM structure following the style described in impedance.py.
        
        For custom ECM structure, the circuit is defined as a string. 
        Elements in series are separated by a dash, 
        for example, a resistor R0 in series with a capacitor C1 can be represented as R0-C1. 
        Circuit elements in parallel are represented with letter p wrapped within a bracket, 
        for example, a resistor with R1 resistance in parallel with a capacitor with C1 capacitance is represented as  p(R1,C1).
       
        An ECM configuration represented as R0-p(R1,C1)-p(R2-Wo1,C2) indicates two RC networks in series with Ohmic resistor R0.
        The first RC network has R1 and C1 in parallel connection. The second RC network has R2 and Wo1 in series connection and in parallel connection with C2.
        
        Capacitor is repesented as C while a constant phase element is represented as CPE.
        Resistors within RC networks are represented as R.
        
        Increment the number of circuit elements in ECM configuration from 1. The value of 0 is reserved for Ohmic resistance R0.
        
        The initial guess values for each circuit element  in ECM either prebuilt or custom configuration is required. 
        These values can be entered in the Initial guess value space separated by comma or check the
        generate initial guess values button. This will randomly generate the initial guess values of the ECM model element parameters.
        The disadvantage of using randomly generated initial guess values is that fitted ECM parameters might
        be different when fitted repeatedly - Check if this happens with impendance py.
        
        The initial guess values should be entered in order the elements are arranged or configured in the circuit string.
        The total number of initial guess values should be equal to the number of circuit elements parameters in the circuit configuration.
        CPE (constant phase element) and Wo (Warbug) components have two parameters i.e. two initial guess values for components other circuit elements have only one parameters .
        """
       
    with st.sidebar.expander("Fit EIS data"):
        form = st.form("Fit EIS Data")
        EIS_fit_tool =  form.selectbox("Select EIS fitting tool", ("PyEIS","ImpedancePy"))
        ecm_model =  form.selectbox("Select EIS ECM model", ("Randles","Randles with CPE", "Custom circuit"))
        custm_circuit = form.text_input("Enter circuit elements configuration, only if custom circuit option is selected")
        initial_guess = form.text_input("Initial guess values for circuit element parameters, separate by comma")
                
        if len(counts)>1:
           cycle_number = form.selectbox("Select Cycle Number",counts)
        else:
              cycle_number = 1
        
        induction_phase = form.checkbox("Include inductive phase", value = False)
        tip1 = "Use this option to randomly generate the initial guess values of the circuit element parameters. "
        tip2 =  " Note that the ECM is highly sensitive to the initial guess values, therefore, if using the random initial guess value generator, "
        tip3 = " repeat the fitting several number of times until reasonable fitting parameter values are achieved."
        tip = tip1+tip2+tip3
        auto_init = form.checkbox("Randomly generate initial guess values", value = False, help = tip)
        
        submit = form.form_submit_button('Fit')
    
    if submit:
        num_active_cell_id =  len(st.session_state.Active_CellIds)
       
     
        
        
        if ecm_model == "Randles":
            circuit = 'R0-p(R1-Wo1,C1)'      # Randles
            #initial_guess = [.0, .0, .05, 100,1]  
        elif  ecm_model == "Randles with CPE":
            #initial_guess = [.05, .05, .05, 100,1,0.5]#,.0, .05, 100,1,0.5]
            circuit = 'R0-p(R1-Wo1,CPE1)'#'-p(R2-Wo2,CPE2)'      # Randles with CPE
        else:
            circuit = custm_circuit
        
        
        if initial_guess != '' and auto_init == False:
            
             initial_gus =  initial_guess.split(",")
             initial_values =  []
             for item in initial_gus:
                 
                initial_values.append(float(item))
             initial_guess =  initial_values
             
             
        if auto_init == True:    
            initial_guess =  []
            element_name = circuit.replace('p', '').replace('(', '').replace(')', '')
            element_name = element_name.replace(',', '-').replace(' ', '').split('-')
            
            
            for item in element_name:
                if "R0" in item or "R" in item:
                    initial_guess.append(np.random.uniform(0,0.09))
                if "C" in item and "CPE" not in item:
                    initial_guess.append(np.random.uniform(1,150))
                    st.write("here")
                if  "CPE" in item:
                    initial_guess.append(np.random.uniform(0,1))
                    initial_guess.append(np.random.uniform(0,1))
                    
                if "Wo" in item:
                    initial_guess.append(np.random.uniform(0,0.09))
                    initial_guess.append(np.random.uniform(50,150))
                
         
        
    
        
        
        if num_active_cell_id>1: # Need to check number of cycles in the EIS data too
             err_msg1 = " Only one EIS test data is required for fitting. "
             err_msg2 = " Please select only one cell id from Select Cells/Files for analysis to continue."
             err_msg3 = " For more than one cell ID or cycle number, fit each cell id or EIS cycle test data separately"
             st.error("Error:"+ err_msg1 + err_msg2)
        elif initial_guess == '' and auto_init == False:
            err_msg1 = "Enter the initial guess values for circuit element parameters or"
            err_msg2 = " the Randomly generate initial guess values option."
            st.error("Error:"+ err_msg1+err_msg2 )
            
        else:
            active_id = st.session_state.Active_CellIds
            file_num = st.session_state.Cell_ids_and_file_nums[active_id[0]]
            eis_test_data =  st.session_state.TestData[file_num]
            eis_test_data =  eis_test_data.filter(items = ['freq/Hz','Re(Z)/Ohm','Im(Z)/Ohm','Cycle'])
            #st.write(eis_test_data)
            if induction_phase == False:
                eis_test_data =  eis_test_data[(eis_test_data['Im(Z)/Ohm']>=0) & (eis_test_data['Cycle']== cycle_number)]
            else: 
                eis_test_data =  eis_test_data[(eis_test_data['Cycle']== cycle_number)]
            #st.write(eis_test_data)
            param_list,fitted_eis_params = Fit_EIS(EIS_fit_tool,ecm_model,eis_test_data,circuit,initial_guess)
                                           
            user_value = pd.DataFrame({"Model parameter": param_list, "Fitted value": fitted_eis_params})
            st.write("Fitted parameter values")
            st.write(user_value)
        
        
        
        
        
        




if  st.session_state.TestData == []:
    steps =[0]
    counts = [0]
elif st.session_state.EIS == "Yes":
    pass
elif st.session_state.Cycler_Name == "Other data file": 
    pass
else:
    with st.sidebar.expander("Step Plots"):
        st.session_state.Allow_legend = "Yes"
        st.session_state.Cycle_plot = "No"
        form = st.form("Step Plots")
        if st.session_state.Cycler_Name == "PEC": 
            plot_type_yvalue = form.selectbox("Step Plot: Y-axis value",("Voltage (V)","Current (A)",
                                                                         "Charge Capacity (Ah)","Discharge Capacity (Ah)",
                                            "Temperature","DCIR"),index=None,placeholder="Choose y-axis variable",)


            plot_type_xvalue = form.selectbox("Step Plot: X-axis value",("Step Time (Seconds)", "Current (A)","Charge Capacity (Ah)",
                                            "Discharge Capacity (Ah)",),index=None,placeholder="Choose x-axis variable",)
            
        elif st.session_state.Cycler_Name == "BioLogic":
                     plot_type_yvalue = form.selectbox("Step Plot: Y-axis value",("Charge Voltage", "Discharge Voltage",
                                                                                  " Charge Current", "Discharge Current",
                                                                                  "Charge Capacity","Discharge Capacity",
                                                     "Temperature","Charge DCIR", "Discharge DCIR"),index=None,placeholder="Choose y-axis variable",)


                     plot_type_xvalue = form.selectbox("Step Plot: X-axis value",("StepTime",
                                                                                  " Charge Current", "Discharge Current",
                                                                                  "Charge Capacity","Discharge Capacity",
                                                     ),index=None,placeholder="Choose x-axis variable",)
        else:
            
                  plot_type_yvalue = form.selectbox("Step Plot: Y-axis value",("Voltage (V)","Current (A)","Capacity (Ah)",
                                            "Temperature","DCIR"),index=None,placeholder="Choose y-axis variable",)


                  plot_type_xvalue = form.selectbox("Step Plot: X-axis value",("StepTime","Current (A)","Capacity (Ah)",
                                            ),index=None,placeholder="Choose x-axis variable",)

    
    
    
        #make this a function so that it can be called once
        steps_and_counts = []
        for ii in steps:
            avail_count = temp_data.loc[temp_data["Step"]==ii,"Cycle"]
            avail_count =  np.unique(avail_count)
            ii = int(ii)
            avail_count = str(avail_count)
            steps_and_counts.append (['Step '+str(ii) +' has cycle count number ' + str(avail_count)])
        #steps_and_counts = ' '.join(steps_and_counts)
        steps_and_counts = ' '.join(str(itemi) for itemi in steps_and_counts)
    
            
        # Clean this up, loop through all unique names in Instruction Name column and
        # extract their step numbers
        if st.session_state.Cycler_Name == "PEC":  
            cc_charge_steps = temp_data.loc[temp_data["Instruction Name"]=="I Charge","Step"]
        else:  
            cc_charge_steps = temp_data.loc[temp_data["Instruction Name"]=="C","Step"]
        cc_charge_steps = np.unique(cc_charge_steps)
        
            #st.write(cc_charge_steps)
        if st.session_state.Cycler_Name == "PEC":     
            cv_charge_steps = temp_data.loc[temp_data["Instruction Name"]=="V Charge","Step"]
            cv_charge_steps = np.unique(cv_charge_steps)
        else:
             cv_charge_steps = temp_data.loc[temp_data["Instruction Name"]=="CV","Step"]
             cv_charge_steps = np.unique(cv_charge_steps)
        
        if st.session_state.Cycler_Name == "PEC":     
            discharge_steps = temp_data.loc[temp_data["Instruction Name"]=="I Disch.","Step"]
            
        else:
             discharge_steps = temp_data.loc[temp_data["Instruction Name"]=="D","Step"]
        discharge_steps = np.unique(discharge_steps)

        if st.session_state.Cycler_Name == "PEC":     
               Rest_steps = temp_data.loc[temp_data["Instruction Name"]=="Idle","Step"]              
        else:
               Rest_steps = temp_data.loc[temp_data["Instruction Name"]=="R","Step"]
        Rest_steps = np.unique(Rest_steps)
        
        if st.session_state.Cycler_Name == "PEC":     
             Rest_steps_ccontrol = temp_data.loc[temp_data["Instruction Name"]=="Climate Control","Step"]   
             Rest_steps_ccontrol = np.unique(Rest_steps_ccontrol)
        else:
               Rest_steps_ccontrol = []
        Rest_steps = np.unique(Rest_steps)
            

        DCIR_steps = temp_data.loc[temp_data["Instruction Name"]=="Rint DC","Step"]
        DCIR_steps = np.unique(DCIR_steps)
            
        OCV_steps = temp_data.loc[temp_data["Instruction Name"]=="OCV","Step"]
        OCV_steps = np.unique(OCV_steps)
        
        
        if not DCIR_steps.any():
            DCIR_steps = "No DCIR steps"
        if not OCV_steps.any():
            OCV_steps = "No OCV steps"
        #
    
    
    
        StepNumber = form.multiselect("StepNumber",steps)
        Count = form.multiselect("Select Count Number",counts)
        marker_types = ["--",".","*","o","+","-."]
        #marker =  Count = form.multiselect("Select marker type", marker_types)
        #marker = str(marker)
        #form.text(steps_and_counts)
        
        
    
    
    
        submit = form.form_submit_button('Plot')


    if submit: # start at the same indent number as with st.expander to plot outside expander
    #plot_type = ["StepCapacity","R-DC","Power"]
    
    #plot_type = [plot_type]
    #st.write(plot_type)
    #st.write(marker)
    #st.write(Count)
  
        
        if plot_type_yvalue is None or plot_type_xvalue is None:
            st.error("X and Y axis variable not selected")
            st.write("Please select X and Y variables to plot")
            
        
        if StepNumber is None:
            st.error("No y-axis variable selected")
            st.write("Please select step numbers to plot")
                       
           
        else:
            
            if "DCIR" not in plot_type_yvalue:
                  
                  variable_type = "Primary variable"
                  if st.session_state.Cycler_Name == "PEC":  
                      step_val, step_data = PEC_Step_Plot(StepNumber,plot_type_xvalue,plot_type_yvalue,variable_type)
                      
                  elif  st.session_state.Cycler_Name == "BioLogic": 
                       if plot_type_xvalue == "StepTime":
                          plot_type_xvalue = "TestTime"
                                             
                       if "Charge" in plot_type_yvalue or "Charge" in plot_type_xvalue :                           
                            state = "C"
                            append = "Charge "
                           
                       elif "Discharge" in plot_type_yvalue or "Discharge" in plot_type_xvalue:                           
                            state = "D"
                            append = "Discharge"
                            
                       if "Voltage" in  plot_type_yvalue:
                           plot_type_yvalue =  "Voltage (V)"
                       elif "Capacity" in plot_type_yvalue:
                             plot_type_yvalue = "Capacity (Ah)"
                       elif "Current" in plot_type_yvalue:
                             plot_type_yvalue = "Current (A)"               
                       elif "Temperature" in plot_type_yvalue:
                             plot_type_yvalue = "Temperature"
                      
                        

                       if "Capacity" in plot_type_xvalue:
                           plot_type_xvalue = "Capacity (Ah)"  
                           
                       elif "Current" in plot_type_xvalue:
                              plot_type_xvalue = "Current (A)"
                              
                       step_val,step_data = BioLogic_Step_Plot(StepNumber,Count,state,plot_type_xvalue,plot_type_yvalue,variable_type)
                                                         
                  else:
                      step_val,step_data = Step_Plot(StepNumber,plot_type_xvalue,plot_type_yvalue,variable_type)
                      
                  #st.write(pec_variable_type)
                  if "Capacity" in plot_type_yvalue:
                      st.write(step_data)
            else:
                  variable_type = "Secondary variable"  # DCIR
                  
                  if st.session_state.Cycler_Name == "PEC": 
                      volt_val, step_volt = PEC_Step_Plot(StepNumber,"Step Time (Seconds)","Voltage (V)",variable_type)
                      curren_val,step_curr = PEC_Step_Plot(StepNumber,"Step Time (Seconds)","Current (A)",variable_type)
                      
                  elif st.session_state.Cycler_Name == "BioLogic": 
                      if "Charge" in plot_type_yvalue:
                          
                           state = "C"
                           append = "Charge "
                          
                      elif "Discharge" in plot_type_yvalue:
                          
                           state = "D"
                           append = "Discharge"
                           
                      volt_val,step_volt = BioLogic_Step_Plot(StepNumber,Count,state,"TestTime","Voltage (V)",variable_type) # No StepTime in BioLogic
                      curren_val,step_curr = BioLogic_Step_Plot(StepNumber,Count,state,"TestTime","Current (A)",variable_type)
                  else:     
                          
                      volt_val,step_volt = Step_Plot(StepNumber,"StepTime","Voltage (V)",variable_type)
                      curren_val,step_curr = Step_Plot(StepNumber,"StepTime","Current (A)",variable_type)
                      
                      
                  #st.write(step_curr)
                  #st.write(len(step_curr))
                  dcir = []
                  #temp_id = []
                  for ii_dc in range(0,len(step_curr)):
                      
                      cur_min = np.abs(step_curr.iloc[ii_dc][1])
                      cur_max = np.abs(step_curr.iloc[ii_dc][2])
                      max_cur = max(cur_max,cur_min)
                      if max_cur> 500:  # This must be in mA, better to get the unit from column name through string split
                         max_cur =  max_cur/1000 #  #changed from mA to Amps
                      
                      volt_min = step_volt.iloc[ii_dc][1]
                      volt_max = step_volt.iloc[ii_dc][2]
                      volt_diff = np.abs(volt_max - volt_min)
                      temp_dcir = volt_diff/max_cur
                      dcir.append(temp_dcir*1000)
                     
                      
                      
                      
                
                  temp_id = list(step_curr.iloc[:,0])  
                  #st.write(temp_id)
                  #st.write(dcir)
                  user_dcir_data = np.column_stack((temp_id,dcir))
                  user_dcir_data = pd.DataFrame(user_dcir_data, columns = ["Cell Id","DCIR mΩ"])
                  user_dcir_data.index +=1   # Start numbering index from 1
                  num = user_dcir_data.index  
                  
                  source_dcir = pd.DataFrame({"Number": num, "DCIR":dcir ,"Cell Id": temp_id})
                   
                  meanDCIR= np.mean(dcir)
                  std_dcir = np.std(dcir)
                  var_dcir = np.var(dcir)
                  meanDCIR = np.around(meanDCIR, decimals=3, out=None)
                  std_dcir = np.around(std_dcir, decimals=3, out=None)
                  var_dcir = np.around(var_dcir, decimals=3, out=None)
    
    
                  
                  c_dcir = alt.Chart(source_dcir).mark_circle(size=120).encode(
                        x="Number",
                        y="DCIR",
                        color="Cell Id",
                        tooltip=['Cell Id',"DCIR"]
                         ).properties(width = 800, height = 300).interactive()
                  #cola,colb,colc  = st.columns([0.5,0.5,0.5])
                  #with colb: 
                    #st.subheader("Interative plot")
                  st.write(c_dcir)
                    
                  # fig,ax = plt.subplots(1,1)
                  # ax.scatter(num,CE)
                  # ax.set_ylim([ylo,yhi])
                  # ax.set_xlabel("Cell Number")
                  # ax.set_ylabel("Coulombic Efficiency")
                  # ax.legend()
                  # ax.grid()
                  
                  #st.pyplot(fig)
                  col1a, col2a,  = st.columns([3,1],gap = "small")
                  with col1a:
                      st.subheader("Extracted DCIR Data Table")
                      st.write(user_dcir_data)
                      
                      
                  with col2a:
                      st.subheader("Statistics")
                      st.write(" Average DCIR [mΩ]: ", meanDCIR) 
                      st.write(" Standard deviation: ", std_dcir) 
                      st.write(" Variance: ", var_dcir) 
                  
              
    
 
    
            
    
if  st.session_state.TestData == []:
    pass
elif st.session_state.EIS == "Yes":
    pass
elif st.session_state.Cycler_Name == "Other data file": 
    pass
else:

    with st.sidebar.expander("DVA-ICA Plots"):
        form = st.form("Differential Analysis")   
        if st.session_state.Cycler_Name == "BioLogic": 
           plot_type_yvalue = form.selectbox("Differential Analysis",("Charge DVA","Charge ICA","Discharge DVA","Discharge ICA",),index=None,placeholder="",)      
        else:
            plot_type_yvalue = form.selectbox("Differential Analysis",("DVA","ICA",),index=None,placeholder="",)    
        
        StepNumber = form.multiselect("StepNumber",steps)
        Count = form.multiselect("Select Count Number",counts)
        
        align_tip1 = "Differential voltage or capacity analysis using discharge curves can be aligned right, such that the "
        align_tip2 = " resulting differential curves appear as if they are from charge curves."
        align_tip3 =  " This helps with the interpretation of differential curves and features."
        align_tip = align_tip1+align_tip2+align_tip3
        
        Alighment =  form.radio("Align Right",("Yes",
                                             "No",
                                           ), help = align_tip)
        smooth_win_value = form.slider("Select smoothing window value",100,2000,step = 20)
        xlim_value = form.text_input("X-axis limits: Separate by comman")
        ylim_value = form.text_input("Y-axis limits: Separate by comman")
        
        submit = form.form_submit_button('Plot')
        
    if submit:
        dva_data = []
        dva_cell_ids = []
        

        for ii, istep in enumerate(StepNumber):
                if st.session_state.Cycler_Name == "PEC": 
                      idx = 2
                      volt_val,step_volt = PEC_Step_Plot([istep],"Step Time (Seconds)","Voltage (V)","Secondary variable")
                      curr_val,step_current = PEC_Step_Plot([istep],"Step Time","Current (A)","Secondary variable")
                      step_current_item =  curr_val[0][:,1][4]
                     
                      if  step_current_item > 0:
                          cap_val,step_cap = PEC_Step_Plot([istep],"Step Time (Seconds)","Charge Capacity (Ah)","Secondary variable")

                      else:
                          cap_val,step_cap = PEC_Step_Plot([istep],"Step Time (Seconds)","Discharge Capacity (Ah)","Secondary variable")
                          
                
                elif st.session_state.Cycler_Name == "BioLogic": 
                    idx = 1
                    
                    if "Charge" in plot_type_yvalue:
                        state = "C"
                    else:
                        state = "D"
                    if "DVA" in  plot_type_yvalue:
                        plot_type_yvalue = "DVA"
                    else:
                        plot_type_yvalue = "ICA"
                   
                  
                    volt_val,step_volt = BioLogic_Step_Plot([istep],Count,state,"TestTime","Voltage (V)","Secondary variable")
                    cap_val,step_cap = BioLogic_Step_Plot([istep],Count,state,"TestTime","Capacity (Ah)","Secondary variable")
                    step_current = step_cap
                   
                else: 
                    idx = 1
                    volt_val,step_volt = Step_Plot([istep],"StepTime","Voltage (V)","Secondary variable")
                    cap_val,step_cap = Step_Plot([istep],"StepTime","Capacity (Ah)","Secondary variable")
                    step_current = step_cap
               
                  
                     
                        
                for ii_item in range(0,len(cap_val)):
                         volt_value = volt_val[ii_item][:,1]                          
                         cap_value = cap_val[ii_item][:,1]
                         cap = step_cap.iloc[ii_item][idx]
                         volt = step_volt
                         volt = step_volt.iloc[ii_item][idx]
                         if cap>100:
                             cap_value  = cap_value/1000
                         if volt>4.6:
                             volt_value = volt_value/1000
                             
                        
                         curr_Data =  np.column_stack((cap_value,volt_value))
                         dva_data.append(curr_Data)
                         curr_id = step_current.iloc[ii_item][0]
                         dva_cell_ids.append(curr_id)
              
                
        ylim_value = ylim_value.split(",")    
        ylim_value1 =float(ylim_value[0]) 
        ylim_value2 =float(ylim_value[1]) 
        ylim_value =[ylim_value1,ylim_value2]
        
        xlim_value = xlim_value.split(",") 
        xlim_value1 =float(xlim_value[0]) 
        xlim_value2 =float(xlim_value[1]) 
        xlim_value =[xlim_value1,xlim_value2]
        
        
        if Alighment == "Yes":
            align_state = "Align right"
        else:
            align_state = "Align left"
            
        if plot_type_yvalue == "DVA":
          
            DVA = DVA_SG(dva_data,dva_cell_ids, "Capacity", "DVA",align_state,smooth_win_value,xlim_value,ylim_value)
        else:
            ICA = DVA_SG(dva_data,dva_cell_ids, "Voltage", "ICA",align_state,smooth_win_value,xlim_value,ylim_value)
        
                 
    
    

       
                  
  
    
  


if  st.session_state.TestData == []:
    pass
elif st.session_state.EIS == "Yes":
    pass
elif st.session_state.Cycler_Name == "Other data file": 
    pass
else:

    with st.sidebar.expander("Step Operations"):
        form = st.form("Step operations")
       
    
        yvariable_name = form.selectbox("",("Charge Capacity (Ah)","Discharge Capacity (Ah)",
                                            ),index=None,placeholder="Choose variable",)
        
        if  st.session_state.Cycler_Name != "PEC": 
                                   
             col = 1
             if  yvariable_name == "Charge Capacity":
                   yvariable_name = "Capacity (Ah)"
                   state =  "C"
             elif yvariable_name == "Discharge Capacity":
                   yvariable_name = "Capacity (Ah)"
                   state =  "D"       
        else:
            col = 2


        
        operation_name = form.selectbox("",("Add","Multiply",
                                            "Substract",),index=None,placeholder="Choose operation type",)
       
        
        StepNumber_step_ops = form.multiselect("StepNumber",steps)
        Count_step_ops = form.multiselect("Select Count Number",counts)
        
        submit = form.form_submit_button('Ok')
        
    if submit:
            
            if  st.session_state.Cycler_Name == "PEC": 
                   step_val, ops_step_data = PEC_Step_Plot(StepNumber_step_ops,"Step Time (Seconds)",yvariable_name,
                                          "Secondary variable")
                   
            elif st.session_state.Cycler_Name == "BioLogic": 
            
                 step_val, ops_step_data = BioLogic_Step_Plot(StepNumber_step_ops,Count_step_ops,state,"TestTime",yvariable_name, "Secondary variable")
            else:
                 step_val, ops_step_data = Step_Plot(StepNumber_step_ops,"StepTime",yvariable_name, "Secondary variable")
            
            
            
            
            
            ops_id = ops_step_data["Cell Id"]
            ops_id = np.unique(ops_id)
            ops_col = list(ops_step_data.columns.values)
            
            
            ops_fin_value = []
            for ops_item in ops_id:
                ops_value = ops_step_data.loc[ops_step_data["Cell Id"]==ops_item,ops_col[col]]
                
                if operation_name == "Add":
                #ADD OTHER OPERATIONS AND ADD OPTIONS FOR USING RESULTS FOR FURTHER ANALYSIS
                    ops_value = sum(ops_value)
                elif operation_name == "Multiply":
              
                    ops_value = np.product(ops_value)
                    
                elif "Substract":
                    if len(StepNumber_step_ops)!= 2:
                        st.error("Only variables from two steps can be subtracted, select two steps for substraction")
                        
                    else:
                       #st.write(ops_value.iloc[0])
                       #ops_value = np.subtract(ops_value[0],ops_value[1])
                       ops_value = np.subtract(ops_value.iloc[0],ops_value.iloc[1])
                       ops_value = np.abs(ops_value)
                    
                    
                ops_fin_value.append(ops_value)
                
                
                
            
            ops_label = ops_item,ops_col[col].split("Max")
            ops_label = ops_label[1]
            user_ops_step_data = np.column_stack((ops_id,ops_fin_value))
            user_ops_step_data = pd.DataFrame(user_ops_step_data, columns = ["Cell Id",ops_label[-1]])
            
           
            with st.expander(" Step operations values"):
                 st.text("Step Operations Value for steps "+ str(StepNumber_step_ops))
                 st.write(user_ops_step_data)
            







if  st.session_state.TestData == []:
   pass 
elif st.session_state.EIS == "Yes":
    pass
elif st.session_state.Cycler_Name == "Other data file": 
    pass
else:
    max_cyc_num = np.max(counts)
    max_step_num = np.max(steps)
    if max_step_num > max_cyc_num:
        pass
    else:
        
        with st.sidebar.expander("Cycle Data Analysis and Plots"):
            st.session_state.Cycle_plot = "Yes"
            cyc_counts = list(counts)
            form = st.form("Cycle Data Plots")
            
    
            plot_type_yvalue = form.selectbox(" Cycle Plot - Y-axis value",("Charge Voltage"," Discharge Voltage","Charge Current","Discharge Current",
                                                                            "Charge Capacity","Discharge Capacity",
                                                                            "Charge Slippage","Discharge Slippage","Cycling Coulombic efficiency",
                                                " Charge Temperature"," Discharge Temperature",),index=None,placeholder="Choose y-axis variable",)
        
            plot_type_xvalue = form.selectbox(" Cycle Plot - X-axis value",("Time","Cycle Number","Charge Current","Discharge Current","Charge Capacity",
                                            "Discharge Capacity",),index=None,placeholder="Choose x-axis variable",)

            cycle_numbers = form.multiselect("Select Cycle Number",["All Cycles"] + cyc_counts)
            text = " Choose cycle numbers to plot or use this space to enter a range of two values: lower range and upper range sepearate by comma or space. "
            text2 = "If both range values and individual cycle numbers are selected, only the values within the range will be processed"
            cycle_numbers_range = form.text_input("Or enter range of two values separated by comma", 
                                                  help = text+ text2)
            normalise = form.checkbox("Use relative capacity in plots", value = False)
            slippage = "False"
            
           
            
            
            submit = form.form_submit_button('Plot')
            
        
        if submit:
             
               
               if cycle_numbers == ["All Cycles"]:

                   cycle_numbers  = cyc_counts 
                   
                   
               if cycle_numbers_range == "":
                   cycle_numbers =  cycle_numbers
                   
               else:
                   cycle_numbers = cycle_numbers_range.split(",")
                   cycle_numbers_1 =  int(cycle_numbers[0])
                   cycle_numbers_2 =  int(cycle_numbers[1])
                   cycle_numbers = []
                   for ii in range(cycle_numbers_1,cycle_numbers_2+1):
                       cycle_numbers.append(ii)
                   
                   
                  
                      
               if "Charge" in plot_type_yvalue or "Charge" in plot_type_xvalue :
                   
                    if st.session_state.Cycler_Name == "PEC":
                        state = "I Charge"
                        append = ''
                    else:
                        state = "C"
                    
                        append = "Charge"
                    
                   
               elif "Discharge" in plot_type_yvalue or "Discharge" in plot_type_xvalue:
                    
                    if st.session_state.Cycler_Name == "PEC":
                        state = "I Disch."
                        append = ''
                    else:
                            
                        state = "D"
                        append = "Discharge "
                   
                    
               if "Voltage" in  plot_type_yvalue:
                   plot_type_yvalue =  "Voltage (V)"
                       
               elif "Capacity" in plot_type_yvalue:
                     
                     if st.session_state.Cycler_Name == "PEC":
                         plot_type_yvalue =  plot_type_yvalue
                     else:
                         plot_type_yvalue = "Capacity (Ah)" 
                     
                    
                         
               elif "Current" in plot_type_yvalue:
                         plot_type_yvalue = "Current (A)"  
         
               elif "Temperature" in plot_type_yvalue:
                     plot_type_yvalue = "Temperature"
                
              
                
               if "Time" in plot_type_xvalue:
                      plot_type_xvalue = "StepTime"
               elif "Capacity" in plot_type_xvalue:
                   
                  
                   if st.session_state.Cycler_Name == "PEC":
                       plot_type_xvalue =  plot_type_xvalue
                   else:
                       plot_type_xvalue = "Capacity (Ah)" 
                        
                      
                           
                                                 
               elif "Current" in plot_type_xvalue:
                     plot_type_xvalue = "Current (A)"

               elif "Temperature" in plot_type_xvalue:
                       plot_type_xvalue = "Temperature"
                     
              
               if plot_type_xvalue == "Cycle Number":
                   #st.write("Here")
                   st.session_state.Allow_legend = "Yes"
                   
                   
                   
                   if plot_type_yvalue != "Cycling Coulombic efficiency":
                       
                                         
                       if  st.session_state.Cycler_Name == "BioLogic" and state == "C":  #Use charge capacity at end of CV for charge capacity
                                state = "CV"
                       elif st.session_state.Cycler_Name == "PEC" and state == "I Charge":
                               state = "V Charge" # PEC constinues to add continuos capacity during the CV charge phase
                   
                    
                    
                   if "Slippage" in plot_type_yvalue:   
                        slippage = "True"
                        
                        
                        if st.session_state.Cycler_Name == "PEC" :
                            
                                  if  "Charge" in plot_type_yvalue:
                                         plot_type_yvalue = "Charge Capacity (Ah)"
                                         append = "Charge"
                                  else:
                                         plot_type_yvalue = "Discharge Capacity (Ah)"
                                         append = "Discharge"
                                
                                  cyc_plot_val = PEC_Cycle_Plot("Cycle",plot_type_yvalue,state,"Secondary variable",cycle_numbers)
                                  
                        else:           
                                  cyc_plot_val = full_cycle_data_plot("Cycle","Capacity (Ah)",state,"Secondary variable", cycle_numbers) 
                           
                                  
                   elif   plot_type_yvalue == "Cycling Coulombic efficiency":
                          
                       
                          if st.session_state.Cycler_Name == "PEC" :
                              cyc_plot_val = PEC_Cycle_Plot("Cycle","Charge Capacity (Ah)","V Charge","Secondary variable",cycle_numbers)
                              dchar_cap = PEC_Cycle_Plot("Cycle","Discharge Capacity (Ah)","I Disch.","Secondary variable",cycle_numbers)
                             
                              
                          else:
                              
                              if  st.session_state.Cycler_Name == "BioLogic":  # Using CV for Biologic
                                 cyc_plot_val = full_cycle_data_plot("Cycle","Capacity (Ah)","CV","Secondary variable", cycle_numbers)
                              else:
                                  cyc_plot_val = full_cycle_data_plot("Cycle","Capacity (Ah)" ,"C","Secondary variable", cycle_numbers) 
                                  
                              dchar_cap = full_cycle_data_plot("Cycle","Capacity (Ah)" ,"D","Secondary variable", cycle_numbers) 
                              
                            
                   else:
                       
                         if st.session_state.Cycler_Name == "PEC":
                                if  plot_type_yvalue == "Charge Capacity":
                                    plot_type_yvalue = "Charge Capacity (Ah)"
                                    
                                elif plot_type_yvalue == "Discharge Capacity":
                                     plot_type_yvalue = "Discharge Capacity (Ah)"
                                    
                                
                                cyc_plot_val = PEC_Cycle_Plot("Cycle",plot_type_yvalue,state,"Secondary variable",cycle_numbers)
                                                                
                         else:
                                cyc_plot_val = full_cycle_data_plot("Cycle",plot_type_yvalue,state,"Secondary variable", cycle_numbers) 
                   
                    
                    
                   name_active_ids = cyc_plot_val.iloc[:,0]
                   name_active_ids = np.unique(name_active_ids)
                  

                   capacity_num_cyc = []
                   tit_cyc = []
                   ylim1 = []
                   xlim1 = []
                   ylim2 = []
                   xlim2 = []
                   ylim11 = []
                   xlim11 = []
                   ylim21 = []
                   xlim21 = []
                   
                   slippages = []
                   alt_cyc_plot = pd.DataFrame()
                   alt_slip_plot = pd.DataFrame()
                   alt_plot_lab = plot_type_yvalue.split("[")
                   alt_plot_lab = alt_plot_lab[0]
                   
                   
                 
               
                   
                   for ii_id in name_active_ids:
                       if slippage == "True":
                           ylabel = append + " Slippage"
                           alt_plot_lab = ylabel
                           #cyc_cap = cyc_plot_val.loc[cyc_plot_val["Cell Id"] == ii_id,"Capacity [Ah]"]
                           
                           cyc_cap = cyc_plot_val.loc[cyc_plot_val["Cell Id"] == ii_id,plot_type_yvalue]
                           name_curr_id = cyc_plot_val.loc[cyc_plot_val["Cell Id"] == ii_id,"Cell Id"]
                           num_cycles_id =  cyc_cap.index
                           num_cycles_id = num_cycles_id -  num_cycles_id[0]
                           
                           
                       elif  plot_type_yvalue ==  "Cycling Coulombic efficiency":
                              col_nam = cyc_plot_val.columns.values
                              plot_type_yvalu = col_nam[1]
                              cyc_plot_vall =   cyc_plot_val.loc[cyc_plot_val["Cell Id"] == ii_id,plot_type_yvalu]
                              
                              col_nam = dchar_cap.columns.values
                              plot_type_yvalu = col_nam[1]
                              cyc_cap_dchar =   dchar_cap.loc[dchar_cap["Cell Id"] == ii_id,plot_type_yvalu]
                              name_curr_id = cyc_plot_val.loc[cyc_plot_val["Cell Id"] == ii_id,"Cell Id"]
                              
                              #cyc_plot_vall = cyc_plot_vall.to_numpy()
                              
                             
                              charge_capacity = cyc_plot_vall.to_numpy()
                              discharge_capacity = cyc_cap_dchar.to_numpy()
                              
                             
                              ylabel = plot_type_yvalue
                              lenChg = len(charge_capacity)
                              lenDchg = len(discharge_capacity)
                          
                              if lenChg < lenDchg:
                                  #cyc_cap_dchar = cyc_cap_dchar[0:lenChg]
                                  discharge_capacity = discharge_capacity[0:lenChg]                                
                                  
                                  #cyc_cap =  discharge_capacity/charge_capacity
                                  
                                                                   
                              elif lenDchg < lenChg:
                                  
                                  charge_capacity = charge_capacity[0:lenDchg]
                                  #cyc_plot_vall  = cyc_plot_vall[0:lenDchg]
                                  name_curr_id = name_curr_id[0:lenDchg]
                                  #st.write("Got here instead")
                                  
                                  
                                                               
                              cyc_cap =  discharge_capacity/charge_capacity
                              num_cycles_id =  np.linspace(1,len(cyc_cap),len(cyc_cap))
                              #num_cycles_id = num_cycles_id -  num_cycles_id[0]
                              
                              #np.linspace(1,len(slip),len(slip))
                             
                                  
                                  
                       
                       else: 
                           col_nam = cyc_plot_val.columns.values
                           plot_type_yvalue = col_nam[1]
                           ylab = plot_type_yvalue.split("[")
                           ylab = ylab[0]
                           ylabel = "Remaining " + ylab
                           cyc_cap = cyc_plot_val.loc[cyc_plot_val["Cell Id"] == ii_id,plot_type_yvalue]
                           alt_plot_lab = plot_type_yvalue.split("[")
                           alt_plot_lab = alt_plot_lab[0]
                           name_curr_id = cyc_plot_val.loc[cyc_plot_val["Cell Id"] == ii_id,"Cell Id"]
                           num_cycles_id =  cyc_cap.index
                           num_cycles_id = num_cycles_id -  num_cycles_id[0]
                           
                           
                           
                         
            
                      
                       if "Capacity" in plot_type_yvalue or "Capacity" in plot_type_xvalue:
                    
                          if normalise == True:
                             
                              cyc_cap = cyc_cap/cyc_cap.iloc[0]
                              ylabel = "Relative capacity"
                              
                              if slippage == "True":
                                  ylabel = append + " Slippage"
                           
                           
                       ylim1.append(cyc_cap.min())
                       ylim2.append(cyc_cap.max())
                       xlim1.append(num_cycles_id.min())
                       xlim2.append(num_cycles_id.max())
                       
                       
                       dat  = np.column_stack((num_cycles_id,cyc_cap))
                       capacity_num_cyc.append(dat)
                       tit_cyc.append(ii_id)
                       alt_cyc_temp = pd.DataFrame({"Cycle Number":num_cycles_id,
                                                    ylabel:cyc_cap,
                                                    "Cell Id":name_curr_id })
                       alt_cyc_plot = pd.concat([alt_cyc_plot, alt_cyc_temp], axis = 0)
                       
                       
                       
                       slip = np.diff(cyc_cap)
                       slip = np.abs(slip)
                      
                       
                       slip_num = np.linspace(1,len(slip),len(slip))
                       curr_id_slip = name_curr_id[0:len(name_curr_id)-1]
                       #st.write(curr_id_slip)
                       slip_dat  = np.column_stack((slip_num,slip))
                       slippages.append(slip_dat)
                       ylim11.append(np.min(slip))
                       ylim21.append(np.max(slip))
                       xlim11.append(np.min(slip_num))
                       xlim21.append(np.max(slip_num))
                       
                       alt_slip_temp = pd.DataFrame({"Cycle Number":slip_num,
                                                     alt_plot_lab: slip,
                                                    "Cell Id":curr_id_slip })
                       alt_slip_plot = pd.concat([alt_slip_plot, alt_slip_temp], axis = 0)
                     
                       
                                                    
                   
                   
                   if slippage == "True":
                     
                      
                       ylim11 = np.min(ylim11)
                       ylim21 = np.max(ylim21)
                       ylim11 = ylim11 - (ylim11 *0.02)
                       ylim21 = ylim21 + (ylim21 *0.02)
                       ylim = [ylim11,ylim21]
                           
                       xlim11 = np.min(xlim11)
                       xlim21 = np.max(xlim21)
                       xlim11 = xlim11 - (xlim11 *0.02)
                       xlim21 = xlim21 + (xlim21 *0.02)
                       xlim = [xlim11,xlim21]
                       st.session_state.Current_plot_full_test_ylabel = ylabel
                       st.session_state.Current_plot_full_test_xlabel = plot_type_xvalue
                       st.session_state.Current_plot_full_test_legend = tit_cyc
                        
                       st.session_state.Current_plot_full_test_ylim = ylim
                       st.session_state.Current_plot_full_test_xlim = xlim
                       plot(slippages)   
                       plot_altair(alt_slip_plot,ylim,xlim)
                       
                   else:
                      
                       ylim1 = np.min(ylim1)
                       ylim2 = np.max(ylim2)
                       ylim1 = ylim1 - (ylim1 *0.02)
                       ylim2 = ylim2 + (ylim2 *0.02)
                       ylim = [ylim1,ylim2]
                           
                       xlim1 = np.min(xlim1)
                       xlim2 = np.max(xlim2)
                       xlim1 = xlim1 - (xlim1 *0.02)
                       xlim2 = xlim2 + (xlim2 *0.02)
                       xlim = [xlim1,xlim2]
                       
                       st.session_state.Current_plot_full_test_ylabel = ylabel
                       st.session_state.Current_plot_full_test_xlabel = plot_type_xvalue
                       st.session_state.Current_plot_full_test_legend = tit_cyc
                        
                       st.session_state.Current_plot_full_test_ylim = ylim
                       st.session_state.Current_plot_full_test_xlim = xlim
                       plot(capacity_num_cyc)   
                       plot_altair(alt_cyc_plot,ylim,xlim)
                       
                       

               else:
                   st.session_state.Allow_legend = "No"
                   if st.session_state.Cycler_Name == "PEC" :
                          
                          if  plot_type_yvalue == "Charge Capacity":
                               plot_type_yvalue = "Charge Capacity (Ah)"
                              
                          if plot_type_xvalue == "Charge Capacity" :
                               plot_type_xvalue = "Charge Capacity (Ah)" 
                        
                          if  plot_type_yvalue == "Discharge Capacity":
                              plot_type_yvalue = "Discharge Capacity (Ah)"
                             
                          if plot_type_xvalue == "Discharge Capacity" :
                             
                              plot_type_xvalue = "Discharge Capacity (Ah)" 
                          
                              
                              
                         
                          cyc_plot_val = PEC_Cycle_Plot(plot_type_xvalue,plot_type_yvalue,state,"Primary variable", cycle_numbers)
                         
                   else:
                          
                          cyc_plot_val = full_cycle_data_plot(plot_type_xvalue,plot_type_yvalue,state,"Primary variable", cycle_numbers)
       
               if "Capacity" in plot_type_yvalue:
                   st.write(append+plot_type_yvalue+ " Table")
                   st.write(cyc_plot_val)
               if "Slippage" in plot_type_yvalue:
                   st.write(plot_type_yvalue+ " Table")
                   st.write(alt_slip_plot)
                   

               if "Coulombic efficiency" in plot_type_yvalue:
                    st.write(plot_type_yvalue+ " Table")
                    st.write(alt_cyc_plot)



if st.session_state.Cycler_Name == "Other data file": 
    column_names = []
    for  active_id in st.session_state.Active_CellIds:     
           file_num = st.session_state.Cell_ids_and_file_nums[active_id]
           item =  st.session_state.TestData[file_num]
           col_name = item.columns.values
           column_names.append(col_name)
    column_names =  np.unique(column_names)
    with st.sidebar.expander("Select columns to plot"):
         form = st.form("Plot data selection")
         xAxis =  form.selectbox("Select x-axis value",column_names ,index=None,placeholder="Choose x-axis variable",)
         yAxis =  form.multiselect("Select y-axis value(s)",column_names,placeholder="Choose y-axis variables",)
         
         submit = form.form_submit_button('Plot')
         
    if submit:
        generic_Plot(xAxis,yAxis)
        
         
         
         
         





if  st.session_state.TestData == []:
    pass
elif st.session_state.EIS == "Yes":
    pass
elif st.session_state.Cycler_Name == "Other data file": 
    pass
else:
    with st.expander("Information extracted from data files"):    
           
           #st.text_area("Steps and Cycles numbers in this file",steps_and_counts)
         
           st.text("CC Charge Steps: "+ str(cc_charge_steps))
           if st.session_state.Cycler_Name == "PEC" or st.session_state.Cycler_Name == "BioLogic" : 
                st.text("CV Charge Steps: "+ str(cv_charge_steps))
           if st.session_state.Cycler_Name == "Maccor": 
                st.text("Maccor does not separate CC and CV charge steps")
           st.text("Discharge Steps: "+ str(discharge_steps))
           st.text("Rest Steps: "+ str(Rest_steps))
           if st.session_state.Cycler_Name == "PEC":
              st.text(" Climate Control Rest Steps: "+ str(Rest_steps_ccontrol))
           st.text("DCIR Steps: "+ str(DCIR_steps))
           st.text("OCV Steps: "+ str(OCV_steps))
           st.text("Steps and their respective cycle counts: " +steps_and_counts)  # go back to list to string and see how to represent each line





#Currently trying to read in the modified pouch cell data from cognition
#To compare them with the one tested here as as perform lifetime prediction
#Continue with this



# def Cycling_capacity_data(charge_StepNumber,discharge_StepNumber):
#     counts = 0
#     discharge_capacity_data = []
#     charge_capacity_data = []
#     ylim1_charge = []
#     ylim2_charge = []
#     ylim1_discharge = []
#     ylim2_discharge = []
#     titl = []
#     sumdisch = []
#     sumchr = []
    
    
#     for num, ifile in enumerate(st.session_state.TestData):
#         # This function assumes that all charge and discharge steps have the step number
#         # count = ifile.StepNumber.values
#         # uniq_count = np.unique(count)
#         # st.write(uniq_count)
#         charge_value = ifile.loc[(ifile['StepNumber'] == charge_StepNumber) & (ifile['State'] == 2),
#                               "StepCapacity"].values
#         charge_value = charge_value[1:]/charge_value[1]
        
#         ylim1_charge.append(np.min(charge_value))
#         ylim2_charge.append(np.max(charge_value))
        
#         chargeLength = np.linspace(0, len(charge_value)-1,len(charge_value))
       
#         chargedata = np.column_stack((chargeLength,charge_value))
#         charge_capacity_data.append(chargedata)
#         sumchr.append(charge_value)
        
        
        
        
#         discharge_value = ifile.loc[(ifile['StepNumber'] == discharge_StepNumber) & (ifile['State'] == 2),
#                               "StepCapacity"].values
#         discharge_value =  discharge_value/discharge_value[0]
#         sumdisch.append(discharge_value)
#         #st.write(len(discharge_value))
#         ylim1_discharge.append(np.min(np.abs(discharge_value)))
#         ylim2_discharge.append(np.max(np.abs(discharge_value)))
        
#         dischargeLength = np.linspace(0, len(discharge_value)-1,len(discharge_value))
#         dischargedata = np.column_stack((dischargeLength,np.abs(discharge_value)))
        
#         discharge_capacity_data.append(dischargedata)
#         titl.append(st.session_state.FileName[num])
   
#     xlabel = "Cycle Number"   
#     ylabel = "Relative discharge capacity"  
 
#     ylim = [np.min(ylim1_discharge),np.max(ylim2_discharge)] 
#     plot(discharge_capacity_data,ylim,xlabel,ylabel,titl)
    
#     ylabel = "Relative charge capacity"  
    
#     ylim = [np.min(ylim1_charge),np.max(ylim2_charge)] 
#     plot(charge_capacity_data,ylim,xlabel,ylabel,titl)
    
#     SumDischarge = 0
#     for k, item in enumerate(sumdisch):
#         SumDischarge = SumDischarge + item
#     SumDischarge = SumDischarge/(k+1)
    
#     st.write(k)
#     ylim = [np.min(SumDischarge),np.max(SumDischarge)]
#     ylabel = "Average relative discharge capacity"  
#     plotdata = [np.column_stack((dischargeLength,SumDischarge))]
#     plot(plotdata,ylim,xlabel,ylabel,["FF"])
#     #np.savetxt("DF_cells.csv",(plotdata[0]),delimiter=',')
    
    
    
# form = st.sidebar.form("Cycling Plots")

# chargeStepNumber = form.number_input("Charging Step Number")
# dischargeStepNumber = form.number_input("Discharging Step Number")


# submit = form.form_submit_button('Plot')



# if submit:
   
#     Cycling_capacity_data(chargeStepNumber,dischargeStepNumber)  
    
    


# def cells_cycling_Data_compared() :
#     FF = pd.read_csv("FF_cells.csv",comment="#", header=None).to_numpy()
#     FD = pd.read_csv("FD_cells.csv",comment="#", header=None).to_numpy()
#     DF = pd.read_csv("DF_cells.csv",comment="#", header=None).to_numpy()
#     DD = pd.read_csv("DD_cells.csv",comment="#", header=None).to_numpy()
#     plotdata = [FF,FD,DF,DD]
#     ylim1 = [np.min(FF[:,1]),np.min(FD[:,1]),np.min(DF[:,1]), np.min(DD[:,1])]
#     ylim2 = [np.max(FF[:,1]),np.max(FD[:,1]),np.max(DF[:,1]), np.max(DD[:,1])]
#     ylim = [np.min(ylim1),np.max(ylim2)]
#     ylabel = "Average relative discharge capacity"  
#     xlabel = "Cycle Number"
    
#     plot(plotdata,ylim,xlabel,ylabel,["FF","FD","DF","DD"])


# def grouped_bar_plot():
#     # for third project cells
#     Labels = ["DD","DF","FD","FF"]
#     width = 0.25  # the width of the bars
#     x = np.arange(len(Labels))
    
#     #Single layer cells third project, absolute capacity
#     # half_c = [0.200965501,0.209258803,0.187281681,0.182377304]
#     # one_c = [0.171466609,0.188401473,0.177099064,0.173511887]
#     # two_c = [0.083340469,0.106188942,0.132819638,0.145511261]
#     # three_c = [0.037992675,0.058715862,0.077401764,0.102281403]
#     # four_c = [0.014203033,0.021475474,0.028966383,0.054254222]
    
#     #Single layer cells third project, relative capacity
#     # half_c = [0.954367578,0.972976641,0.974765724,0.980200806]
#     # one_c = [0.814279922,0.87599771,0.921767126,0.932552943]
#     # two_c = [0.395776595,0.49373961,0.691301091,0.782061435]
#     # three_c = [0.18042389,0.273007211,0.40286154,0.549719245]
#     # four_c = [0.067448962,0.099853072,0.150764542,0.291593477]
    
#     # #Single layer cells third project, absolute capacity standard deviation
#     # half_c =   [0.010887719,	0.005074332,	0.013118003,	0.008649269]
#     # one_c =    [0.021895543,	0.005784169,	0.011141848,	0.008304493]
#     # two_c  =  [0.038517479,	0.013610194,	0.010994886,	0.013527838]
#     # three_c = [0.027456827,	0.014673535,	0.019045447,	0.003384954]
#     # four_c =  [0.010113354,	0.014942713,	0.009808614,0.00169844]
    
#     #Single layer cells third project, absolute resistance 
#     half_c =   [11.2253628,	11.70157128,13.49197858,14.02698813]
#     one_c =    [5.603743975,5.842726002,6.741933976,7.002745754]
#     two_c  =  [2.850307356,	2.934129578,	3.389161888,	4.245372387]
#     three_c = [1.894418679,	1.958472729,	2.26144786,	2.345415507]
#     four_c =  [1.322119398,	1.177371318,	1.361163873,	1.421700155]
    
#     #Single layer cells third project, standard deviation resistance 
#     half_c =   [1.298562642,	0.248263072,	1.107558501,	0.684279781]
#     one_c =    [0.643583994,	0.118317833,	0.551855053,	0.338393181]
#     two_c  =  [0.257963732,	0.055868843,	0.266906806,	1.701106293]
#     three_c = [0.185957561,	0.03297995,	0.176829736,	0.114233122]
#     four_c =  [0.221776027,	0.019535715,	0.103203826,	0.101820762]

    











#     fig, ax = plt.subplots()
#     rects1 = ax.bar(x - width/5, half_c, width, label='C/2')
#     rects2 = ax.bar(x + width/5, one_c, width, label='1C')
#     rects3 = ax.bar(x + width/5+width/5, two_c, width, label='2C')
#     rects4 = ax.bar(x + width/5+width/5+width/5, three_c, width, label='3C')
#     rects5 = ax.bar(x + width/5+width/5+width/5+width/5, four_c, width, label='4C')
    
    
    
    
   # for second project multi-layer cells
    # Labels = ["DD","DD-high-LL","FF"]
    # width = 0.3  # the width of the bars
    # x = np.arange(len(Labels))
    
    # #Multi layer cells second project, absolute capacity
    # # half_c = [1.144328535,0.1608053,0.982056813]
    # # one_c = [1.144328535, 0.061830087,0.435559133]
    # # two_c = [0.135313748,0.026795862,0.083166424]
    # # three_c = [0.080008609,0.012373802,0.04957838]
    # # four_c = [0.066074833,0.005032984,0.039750332]
    # # five_c = [0.066074833,0.00080418,0.032860544]
    
    # #Multi layer cells second project, relative capacity
    # half_c = [0.86903919, 0.440497593,0.776799189]
    # one_c = [0.86903919,0.169372556,0.344523837]
    # two_c = [0.102761529,0.073402511,0.065783985]
    # three_c = [0.060761062,0.033895837,0.039216107]
    # four_c = [0.050179313,0.013786966,0.031442199]
    # five_c = [0.050179313,0.00220291,0.025992431]
    
    
    
    
    
    
    # #Multi layer cells second project, stardard deviations capacity
    # half_c = [ 0.076712627,	0.09789485,	0.242194316]
    # one_c = [0.096661578,	0.025223629,	0.196591919]
    # two_c = [0,	0.008725068,	0.036318276]
    # three_c = [0,	0.004710868,	0.023017314]
    # four_c = [0,	0.002993471,	0.022309832]
    # five_c = [0,	0.001227969,	0.021734699]
    
    # #Multi layer cells second project, stardard resistance
    # half_c = [ 1.674538435,	1.712486157,	1.640709644]
    # one_c = [0.817591767,	0.859958282,	0.822876326]
    # two_c = [0.42300384,	0.431957024,	0.413387679]
    # three_c = [0.283287824,	0.289250023,	0.277004093]
    # four_c = [0.213278244,	0.2178454,	0.208439693]
    # five_c = [0.170936704,	0.179178688,	0.167034874]
    
    # #Multi layer cells second project, stardard deviations Resistance
    # half_c = [0.010714301,	0.024125517,	0.013679557,]
    # one_c = [0.034630334,	0.011181665,	0.007710947,]
    # two_c = [0,	0.00565493,	0.003113347]
    # three_c = [0,	0.003813061,	0.001946211]
    # four_c = [0, 0.002989667,	0.001539581]
    # five_c = [0,	0.007565561,	0.001197912]
    
    
    
    
       
    
    # div = 4
    # fig, ax = plt.subplots()
    # rects1 = ax.bar(x - width/div, half_c, width, label='C/2')
    # rects2 = ax.bar(x + width/div, one_c, width, label='1C')
    # rects3 = ax.bar(x + width/div+width/div, two_c, width, label='2C')
    # rects4 = ax.bar(x + width/div+width/div+width/div, three_c, width, label='3C')
    # rects5 = ax.bar(x + width/div+width/div+width/div+width/div, four_c, width, label='4C')
    # rects6 = ax.bar(x + width/div+width/div+width/div+width/div +width/div, five_c, width, label='5C')
    
    
    #ax.set_ylabel('Absolute capacity [Ah]')
#     #ax.set_ylabel('Resistance [Ohms]')
#     ax.set_ylabel('Standard Deviation [Ohms]')
#     ax.set_title('Discharge Rate Capability')
#     ax.set_xticks(x, Labels)
#     ax.legend(prop={'size': 6})

#     # To set labels on the bars
#     #ax.bar_label(rects1, padding=0.5)
#     #ax.bar_label(rects2, padding=0.5)
#     #ax.bar_label(rects3, padding=0.5)
#     #ax.bar_label(rects4, padding=0.5)
#     #ax.bar_label(rects5, padding=0.5)

#     #fig.tight_layout()
#     st.pyplot(fig)

# form = st.sidebar.form("Average Cycling Plots")

# submit = form.form_submit_button('Plot')
# if submit:
#     #cells_cycling_Data_compared()
#     grouped_bar_plot()
    

#Next steps
# Write the plot function
# Write the download data function
# Write plot variable widget
# May be use tab that contains current data variables that user can select
#x axis variables and one or more y axis variables to plot
# Write plot step number function
#   Write DVA/SOC/Capacity fade and other battery analysis
#st.write(time.time() - start_time )

# Removing the need to split column names removed 10s in the import time of PEC file
# Removing the tabs reduced import time to 15 s from 50s from the original time
# So, to improve the time, need to
# 1. Stop searching for column names in PEC plots: Achieve this by assigning correct column name 
    # importing files and in the selection box widget
# 2. Think of wether tab can be redesign to improve time or put it in submit widget so that only the
# time it calls that function is when it is actually needed
#3. try casheing again and see if any improvement can be acheieved
# without all the other functions, loading PEC files containtaining data would normally
#crash took 27 s. So, the app needs to be optimised with respect to the functions


#Things to come!!!
#characters like [], dots in the column names which altair does not recognise
#These characters must be removed or handled specially see: 
    #https://altair-viz.github.io/altair-viz-v4/user_guide/troubleshooting.html
    #under ecoding with special characters 
#1. Fix error with PEC column names -solved
#1. Arrange PEC data such that each variable is constant and consistent with oher cyclers - solved
#1. add another column in other cyclers to have cell IDc 
#1. Using () does not cause issue with Altair - So, all units in the future will be with ()
#1. Rewrite PEC so that all cell ids are in file numbers so that dict can be used to stop file number and
#cell id for easy and fast searching and operation- solved.
#1. Search for files with similar cell ids from PEC data file merge them - solved
#1. Time analysis of the app different sections to see why the slow performance
#1. Convert absolute time data to relative time stamps for merging data files
#1. Extract only required data for analysis to reduce running time - solved
#1. Clean up PEC functions for plotting
#1. include cycle numbers in non cycle number plots
#1. Use Step operation results for further analysis
#1. Analysis of GITT and HPPC - Check wether we can use Ferran's PyBaMM GITT
#1. Capability to import generic files and be able to plot column data and do some analysis with it   
#2. Extract more details from data - DVA/ICA steps, DCIR steps, 
#2. Add step data in tables and perform further analysis with it
#4. ECM for fitting EIS data -Add more prebuilt ECM models
#add more help in the EIS fitting widgets - plot the bode plots 
#of fitted ECM m
#5. Make Nyquist plot to be orthonormal scaled
#6. Upload file from url


#Current fixes
#Bugs associated with selcting and analysis files has been fixed
#Make altair plot have correct axis limits, 
#Slippages
#DVA and ICA added

#Rememeber to clear cache whenever you load new data files

#Allow multiple-variable plots within the Full test plot 


""" 


This app is in a trial stage. Please report any bugs/errors to:
Kenneth.Nwanoro@UKBIC.couk
"""


#st.image("Discharge_and_Charge_Process_of_a_Conventional_Lithium_Ion_Battery_Cell.gif")   
#st.image("How_a_Lithium_Ion_Battery_Actually_Works_Photorealistic_16_Month_Project.gif", width =800)

st.image("Image_play.gif", width = 850)

# Edit gif images using the link below
#https://ezgif.com/effects/ezgif-3-440923394d.gif

#was open

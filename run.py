# -*- coding: utf-8 -*-
"""
Created on Fri May 24 15:37:00 2019

@author: srm-jba
"""

import pandas as pd
import numpy as np
import python.read_vent as read_vent
import python.parse_inputs as pik


def calculate_n(building_type, building_age, apartment_quantity, apartment_size, n_50, x_vent):
    
    
    days = range(8)
    time_steps = range(24)
    
    clustered = {}
    clustered["weights"] = np.array([[27],[47],[49],[70],[48],[49],[20],[54]])
    clustered["temp_ambient"] = {}
    clustered["temp_ambient"] = np.array([   [-7.962,-8.567,-9.071,-9.474,-9.172,-9.575,-9.172,-9.575,-9.273,-3.830,
                                             -0.806,1.209,0.403,1.310,0.605,0.000,-1.613,-2.318,-2.822,-3.024,
                                             -3.225,-3.326,-3.124,-2.822],
                                             [3.024,2.016,2.117,3.528,4.233,5.543,4.838,4.435,4.233,8.164,	
                                              11.087,13.304,13.002,12.699,10.986,10.281,8.668,8.869,7.055,4.536,	
                                              3.427,3.024,2.721,3.830],
                                             [14.413,13.808,12.901,12.901,11.389,11.792,13.707,16.529,19.755,22.678,
                                              23.585,24.089,24.996,26.004,26.205,25.298,25.500,24.693,24.492,22.476,	
                                              20.763,19.352,17.638,17.537],
                                             [5.644,4.536,4.334,4.233,4.233,3.528,3.931,5.342,8.769,11.994,	
                                              14.211,14.514,15.522,15.925,15.522,15.320,14.010,12.599,10.281,8.265,	
                                              7.962,7.055,6.249,5.140],
                                             [8.970,9.071,9.071,8.668,8.769,8.063,8.567,9.474,12.296,14.211,	
                                              14.514,15.723,16.429,16.933,17.033,16.832,15.219,14.211,13.607,13.203,	
                                              12.800,12.397,12.196,11.692],
                                             [9.373,8.869,8.366,8.668,8.466,8.668,8.567,8.869,9.777,10.482,	
                                              11.288,11.288,11.591,10.885,11.490,11.591,11.389,11.087,10.986,9.575,	
                                              8.970,8.668,8.466,8.769],
                                             [0.706,0.504,-0.101,0.000,-0.706,-0.403,-0.302,-0.302,-0.101,0.101,
                                              0.302,0.706,1.310,1.310,1.008,0.907,0.907,0.403,0.605,0.605,	
                                              0.605,0.302,1.008,0.605],
                                             [-1.310,-1.310,-1.411,-1.814,-1.713,-1.512,-1.713,-1.713,-1.713,-1.613,	
                                              -1.713,-1.613,-1.411,-1.209,-1.109,-1.915,-2.318,-2.419,-2.520,-2.520,	
                                              -2.621,-2.520,-2.621,-2.822]])
    clustered["wind_speed"] = pd.read_csv("raw_inputs/vent/wind_speed.csv", sep=";", header=None, engine = "python")
    
    clustered["temp_delta"] ={}
    
    for d in days:
        for t in time_steps:
            clustered["temp_delta"][d,t] = np.maximum(0,(20-clustered["temp_ambient"][d,t]))
      
    
    
    vent, df_vent = read_vent.read_vent()
    
    buildings = pik.parse_building_parameters()
    
    building = {}
    building["dimensions"] = buildings[building_type][building_age]
    building["dimensions"]["Area"] = apartment_quantity * apartment_size
    building["quantity"] = apartment_quantity
    
    temp_array = np.asarray(clustered["temp_ambient"])
    temp_average = np.mean(temp_array, axis = 1)
    
    df_windows=pd.DataFrame()
    
    for d in days:
        if temp_average[d] <-5:
                df_windows[d]=df_vent["<-5"]
        elif temp_average[d] <0:
                df_windows[d]=df_vent["<0"]
        elif temp_average[d] <3:
                df_windows[d]=df_vent["<3"]
        elif temp_average[d] <6:
                df_windows[d]=df_vent["<6"]
        elif temp_average[d] <9:
                df_windows[d]=df_vent["<9"]
        elif temp_average[d] <12:
                df_windows[d]=df_vent["<12"]
        elif temp_average[d] <15:
                df_windows[d]=df_vent["<15"]
        elif temp_average[d] <18:
                df_windows[d]=df_vent["<18"]
        elif temp_average[d] <21:
                df_windows[d]=df_vent["<21"]
        elif temp_average[d] <24:
                df_windows[d]=df_vent["<24"]
        elif temp_average[d] <27:
                df_windows[d]=df_vent["<27"]
        else:
                df_windows[d]=df_vent[">27"]
            
    #Window profiles regarding daily average ambient temperature
    #% dicts 
    air_flow1 = {}                          # Zwischenwert für Maximum (linke Seite)
    air_flow2 = {}                          # Zwischenwert für MaximuM (rechte Seite)
    air_flow  = {}                          # Max von air_flow1 & 2
    
    for d in days:
        for t in time_steps:
            air_flow1[d,t] = (vent["sci"]["c_wnd"]*clustered["wind_speed"][t][d]**2)**0.5
            air_flow2[d,t] = (vent["sci"]["c_st"]*vent["tec"]["h_w_st"]*clustered["temp_delta"][d,t])**0.5
            
            if air_flow1[d,t] > air_flow2[d,t]:
                air_flow[d,t] = air_flow1[d,t]
                
            else:
                air_flow[d,t] = air_flow2[d,t]
    
    factor_q_v = 3600*building["dimensions"]["Area"]/(70)*vent["tec"]["A_w_tot"]/2         # ohne 3600 wie in Norm (mit 3600 ist der stündliche Volumenstrom)
    
    
    Q_window_stream = {}
    for d in days:                           # einströmender Luftmassenstrom
        for t in time_steps:
            Q_window_stream[d,t] = (factor_q_v*air_flow[d,t]*df_windows[d][t]) * clustered["weights"][d,0] * (clustered["temp_ambient"][d,t]+273.15)/(273.15+20)
            
    Q_window_total = sum(Q_window_stream[key] for key in Q_window_stream)
        
    n_window = Q_window_total/(364 * 24 * building["dimensions"]["Area"]*building["dimensions"]["Volume"])
    
    Q_window_heat = {}
    for d in days:
        for t in time_steps:
            Q_window_heat[d,t] = (Q_window_stream[d,t]*vent["sci"]["cp_air"]*clustered["temp_delta"][d,t])
    
    Q_vent_Inf_stream = {}
    for d in days:
        for t in time_steps:
            Q_vent_Inf_stream[d,t] = (vent["tec"]["e_z"] * n_50 * clustered["weights"][d,0] *
                                                         building["dimensions"]["Area"]*building["dimensions"]["Volume"])
    
    Q_Inf_total = sum(Q_vent_Inf_stream[key] for key in Q_vent_Inf_stream)
    
    n_inf = Q_Inf_total/(364 * 24 * building["dimensions"]["Area"]*building["dimensions"]["Volume"])
    
    Q_vent_Inf_heat = {}
    
    for d in days:
        for t in time_steps:
            Q_vent_Inf_heat[d,t] = Q_vent_Inf_stream[d,t] * vent["sci"]["cp_air"]*clustered["temp_delta"][d,t]
            
    
    Q_vent_loss = {}
    for d in days:
        for t in time_steps:
            Q_vent_loss[d,t] = ((1-vent["eco"]["phi_heat_recovery"]*x_vent)*Q_window_heat[d,t]+Q_vent_Inf_heat[d,t])
        
                                                     
    return (n_window, n_inf, temp_average, df_windows, clustered)


building_type = "ClusterB"
building_age = "0 1957"
apartment_quantity = 25
apartment_size = 80
n_50 = 4.5
x_vent = 0

n_window, n_inf, temp_average, df_windows, clustered = calculate_n(building_type, building_age, apartment_quantity, apartment_size, n_50, x_vent)
                                                     
import yaml
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from math import log
import spotpy
from spotpy.parameter import Uniform
from spotpy.objectivefunctions import nashsutcliffe, correlationcoefficient, lognashsutcliffe


with open("config.yml", "r", encoding='utf-8') as file:
    config = yaml.safe_load(file)


def main():
    spot_setup_instance = spot_setup()
    sampler = spotpy.algorithms.sceua(spot_setup_instance, dbname='model_analyser/green_ampt_model_lhs', dbformat='csv')
    sampler.sample(repetitions=3000)


class spot_setup(object):
    key_value = Uniform(low=0.1, high=0.99, optguess=0.2)
    Ksup = Uniform(low=4.8, high=240, optguess=55)
    Ksub = Uniform(low=4.8, high=240, optguess=100)
    Kperc = Uniform(low=240, high=1440, optguess=70)
    Kbase = Uniform(low=240, high=12000, optguess=10000)


    def simulation(self, x):
        df = pd.read_csv('input_green_ampt_model.csv', sep=',')
        fc_equation_value = green_ampt.fc_equation(config['n'], config['Wa'], config['b'])
        P_value = green_ampt.P(config['Wf'], config['n'], fc_equation_value)
        qsim = green_ampt().green_ampt_model(df, P_value, key_value = x[0], Ksup = x[1], Ksub = x[2], Kperc = x[3], Kbase = x[4])
        return qsim['qatrasado']
    

    def evaluation(self):
        qobs = pd.read_csv('input_green_ampt_model.csv', sep=',')
        return qobs['q_obs']


    def objectivefunction(self, simulation, evaluation):
        return correlationcoefficient(evaluation, simulation) + nashsutcliffe(evaluation, simulation)
    






class green_ampt():
    def __init__(self):
        self.ft = 0
        self.fc = 50
        self.fp_or_fs = 0

    def fc_equation(n, Wa, b):
        return n*(3400/Wa)**(-1/b)

    def P(Wf, n, fc_equation):
        return Wf*(n - fc_equation)


    # Function to solve Green-Ampt equation
    def equation(randon_value, time_list, ts_list, fp_or_fs_list, Ksat, P_value):
        equation_result = ((time_list + config['var_t']) - ts_list) - ((randon_value - fp_or_fs_list) / Ksat) - ((P_value / Ksat) * log((fp_or_fs_list + P_value) / (randon_value + P_value)))
        return equation_result

    # Function to find the zero of the Green-Ampt equation
    def find_zero(time_list, ts_list, fp_or_fs_list, Ksat, P_value):
        randon_value = 1

        def equation_to_solve(randon_value):
            return green_ampt.equation(randon_value, time_list,  ts_list, fp_or_fs_list, Ksat, P_value)

        N8_solution = fsolve(equation_to_solve, randon_value)[0]
        return N8_solution



    def green_ampt_model(self,df, P_value, key_value, Ksup, Ksub, Kperc, Kbase):
        time_list = []
        time_list_date = []
        incremetal_rainfall_list = []
        rainfall_intensity_list = []
        transpiration_list = []
        ft_list = []
        fc_list = []
        f_line_list = []
        fc_line_list = []
        fp_or_fs_list = []
        dt_line_list = []
        ts_list = []
        ft_var_t_list = []
        infiltration_list = []
        runoff_list = []
        rsuperficial_list = []
        esuperficial_list = []
        rsolo_list = []
        esubterranea_list = []
        rec_list = []
        rsubterranea_list = []
        ebase_list = []
        etotal_list = []
        qsup_list = []
        qsub_list = []
        qbase_list = []
        qtotal_list = []
        qobs_list = []

        for var_time in df['var_time_minutes']:
            time_list.append(var_time)
        for time_date in df['date']:
            time_list_date.append(time_date)
        for transpiration in df['transpiration']:
            transpiration_list.append(transpiration)
        for qobs in df['q_obs']:
            qobs_list.append(qobs)
        for index, value in enumerate(time_list):
            if index == 0:
                incremetal_rainfall_list.append(df['prec'][index])
                rainfall_intensity_list.append(incremetal_rainfall_list[index]/config['var_t'])
                ft_list.append(self.ft)
                fc_list.append(self.fc)
                if fc_list[index] > rainfall_intensity_list[index]:
                    f_line_list.append(ft_list[index] + incremetal_rainfall_list[index])
                else:
                    f_line_list.append(None)  
                if fc_list[index] > rainfall_intensity_list[index]:
                    fc_line_list.append(config['Ksat']*(1+(P_value/f_line_list[index])))
                else:
                    fc_line_list.append(None)
                fp_or_fs_list.append(self.fp_or_fs)
                if fc_list[index] > rainfall_intensity_list[index]:
                    if fc_line_list[index] is None or fc_line_list[index] < rainfall_intensity_list[index]:
                        dt_line_list.append((fp_or_fs_list[index] - ft_list[index])/rainfall_intensity_list[index])
                    else:
                        dt_line_list.append(None)
                else:
                    dt_line_list.append(0)
                if fc_list[index] < rainfall_intensity_list[index]:
                    ts_list.append(time_list[index])
                else:
                    if fc_line_list[index] is None or fc_line_list[index] < rainfall_intensity_list[index]:
                        ts_list.append(dt_line_list[index] + time_list[index])
                    else:
                        ts_list.append(None)
                if f_line_list[index] == None:
                    ft_var_t_list.append(green_ampt.find_zero(time_list[index], ts_list[index], fp_or_fs_list[index], config['Ksat'], P_value))
                else:
                    if fc_list[index] > rainfall_intensity_list[index]:
                        ft_var_t_list.append(f_line_list[index])
                    else:
                        ft_var_t_list.append(ft_var_t_list[index])
                infiltration_list.append(ft_var_t_list[index] - ft_list[index])
                runoff_list.append(incremetal_rainfall_list[index] - ft_var_t_list[index])
                rsuperficial_list.append(runoff_list[index])    
                esuperficial_list.append(rsuperficial_list[index]*(1-key_value**(1/Ksup)))      
                rsolo_list.append(infiltration_list[index] + config['initial_soil_water'])
                esubterranea_list.append(rsolo_list[index]*(1-key_value**(1/Ksub)))
                rec_list.append(rsolo_list[index]*(1-key_value**(1/Kperc)))
                rsubterranea_list.append(rec_list[index] + config['initial_rsub_water'])
                ebase_list.append(rsubterranea_list[index]*(1-key_value**(1/Kbase)))
                etotal_list.append(esuperficial_list[index] + esubterranea_list[index] + ebase_list[index])
                qsup_list.append((esuperficial_list[index]/1000)*(config['area_bacia_km']*1000000)/0.5/3600)
                qsub_list.append(((esubterranea_list[index]/1000)*(config['area_bacia_m2']))/(0.5*3600))
                qbase_list.append(((ebase_list[index]/1000)*(config['area_bacia_m2']))/(0.5*3600))
                qtotal_list.append(qsup_list[index] + qsub_list[index] + qbase_list[index])
             
            else:

                incremetal_rainfall_list.append(df['prec'][index])
                rainfall_intensity_list.append(incremetal_rainfall_list[index]/config['var_t'])
                ft_list.append(ft_var_t_list[index-1])
                fc_list.append(config['Ksat']*(1+P_value/ft_list[index]))
                if fc_list[index] > rainfall_intensity_list[index]:
                    f_line_list.append(ft_list[index] + incremetal_rainfall_list[index])
                else:
                    f_line_list.append(None) 
                if fc_list[index] > rainfall_intensity_list[index]:
                    fc_line_list.append(config['Ksat']*(1+(P_value/f_line_list[index])))
                else:
                    fc_line_list.append(None)
                if fc_list[index] < rainfall_intensity_list[index]:
                    fp_or_fs_list.append(ft_list[index])
                else:
                    if fc_line_list[index] is None or fc_line_list[index] < rainfall_intensity_list[index]:
                        fp_or_fs_list.append((config['Ksat']*P_value) / (rainfall_intensity_list[index] - config['Ksat']))
                    else:
                        fp_or_fs_list.append(None)
                if fc_list[index] > rainfall_intensity_list[index]:
                    if fc_line_list[index] is None or fc_line_list[index] < rainfall_intensity_list[index]:
                        dt_line_list.append((fp_or_fs_list[index] - ft_list[index])/rainfall_intensity_list[index])
                    else:
                        dt_line_list.append(None)
                else:
                    dt_line_list.append(0)
                if fc_list[index] < rainfall_intensity_list[index]:
                    ts_list.append(time_list[index])
                else:
                    if fc_line_list[index] is None or fc_line_list[index] < rainfall_intensity_list[index]:
                        ts_list.append(dt_line_list[index] + time_list[index])
                    else:
                        ts_list.append(None)
                if fc_line_list[index] is None or fc_line_list[index] < rainfall_intensity_list[index]:
                    ft_var_t_list.append(green_ampt.find_zero(time_list[index], ts_list[index], fp_or_fs_list[index], config['Ksat'], P_value))
                else:
                    if fc_list[index] > rainfall_intensity_list[index]:
                        ft_var_t_list.append(f_line_list[index])
                    else:
                        ft_var_t_list.append(ft_var_t_list[index])
                infiltration_list.append(ft_var_t_list[index] - ft_list[index])
                runoff_list.append((incremetal_rainfall_list[index] - (ft_var_t_list[index] - ft_var_t_list[index - 1])))
                rsuperficial_list.append(rsuperficial_list[index-1] + runoff_list[index] - esuperficial_list[index-1]) 
                esuperficial_list.append(rsuperficial_list[index]*(1-key_value**(1/Ksup)))
                if infiltration_list[index] + rsolo_list[index-1] - transpiration_list[index] - rec_list[index-1] > 0:
                    rsolo_list.append(infiltration_list[index] + rsolo_list[index-1] - transpiration_list[index] - rec_list[index-1])
                else:
                    rsolo_list.append(0)
                esubterranea_list.append(rsolo_list[index]*(1-key_value**(1/Ksub)))
                rec_list.append(rsolo_list[index]*(1-key_value**(1/Kperc)))
                rsubterranea_list.append(rsubterranea_list[index-1] + rec_list[index] - ebase_list[index-1])
                ebase_list.append(rsubterranea_list[index]*(1-key_value**(1/Kbase)))
                etotal_list.append(esuperficial_list[index] + esubterranea_list[index] + ebase_list[index])
                qsup_list.append((esuperficial_list[index]/1000)*(config['area_bacia_km']*1000000)/0.5/3600)
                qsub_list.append(((esubterranea_list[index]/1000)*(config['area_bacia_m2']))/(0.5*3600))
                qbase_list.append(((ebase_list[index]/1000)*(config['area_bacia_m2']))/(0.5*3600))
                qtotal_list.append(qsup_list[index] + qsub_list[index] + qbase_list[index])
                
        qatrasado_list = []
        for index, value in enumerate(qtotal_list):
            if index < 12:
                qatrasado_list.append(qbase_list[index])
            else:
                qatrasado_list.append(qtotal_list[index-12])
       

        data = {
                'date': time_list_date,
                'Time': time_list,
                'rainfall': incremetal_rainfall_list,
                'Rainfall Intensity': rainfall_intensity_list,
                'ft': ft_list,
                'fc': fc_list,
                'Fl': f_line_list,
                'fcl': fc_line_list,
                'fp_fs': fp_or_fs_list,
                'dt': dt_line_list,
                'ts': ts_list,
                'Ft_var': ft_var_t_list,
                'Infiltration': infiltration_list,
                'Runoff': runoff_list,
                'Rsuperficial': rsuperficial_list,
                'transpiration': transpiration_list,
                'Rsolo': rsolo_list,
                'Rec': rec_list,
                'Rsubterranea': rsubterranea_list,
                'Esup': esuperficial_list,
                'Esub': esubterranea_list,
                'Ebase': ebase_list,
                'Etotal': etotal_list,
                'qsup': qsup_list,
                'qsub': qsub_list,
                'qbase': qbase_list,
                'qtotal': qtotal_list,
                'qatrasado': qatrasado_list,
                'q_obs': qobs_list,
                }
                
        df = pd.DataFrame(data).round(3)
        return df

def plot_results(model):
    plt.figure(figsize=(12, 6))

    plt.plot(model['Time'], model['qatrasado'], label='qsim', color='blue')
    plt.plot(model['Time'], model['q_obs'], label='qobs', color='red')

    # Configurações do gráfico
    plt.xlabel('Data', fontsize=14)
    plt.ylabel('Vazão', fontsize=14)
    plt.title('Vazões em função do tempo', fontsize=16)
    plt.grid(True)
    plt.legend()


if __name__ == '__main__':
    main()

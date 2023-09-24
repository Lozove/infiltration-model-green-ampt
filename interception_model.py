import yaml
import pandas as pd
from math import log, exp

with open("config.yml", "r", encoding='utf-8') as file:
    config = yaml.safe_load(file)

def main():
    dataframe = pd.read_csv("data/input_interception_model.csv", sep=',')
    capc_dossel = interception.capc_dossel()
    ec = interception.ec()
    p_line = interception.p_line(capc_dossel)
    interception_model = interception().interception_model(dataframe, p_line, capc_dossel)
    interception_model.to_csv('results/output_interception_model.csv', sep=';', index=False)

class interception():
    def __init__(self):
        self.armazenamento_dossel_inicial = 0

    def capc_dossel():
        return config['Cd'] * config['Sc']
    
    def ec():
        return config['Emed'] / config['Cd']
    
    def p_line(capc_dossel):
        return -((config['Rmed'] * capc_dossel)/config['Emed']) * log(1-(config['Emed']/(config['Cd'] * config['Rmed'])))

    
    def interception_model(self, dataframe, p_line, capc_dossel):
        time_list = []
        date_list =[]
        prec_list = []
        prec_accumulated_list = []
        p_livre_list = []
        p_tronco_list = []
        prec_dossel_list = []
        drenagem_dossel_list = []
        evaporacao_pos_chuva_list = []
        armazenamento_dossel_list = []
        excesso_dossel_list = []
        prec_efetiva_list = []
        transpiracao_dossel_list = []


        for date_t in dataframe['t']:
            time_list.append(date_t)
        for prec in dataframe['prec']:
            prec_list.append(prec)
        for date_day in dataframe['data']:
            date_list.append(date_day)

        for index, value in enumerate(time_list):
            if index == 0:
                if prec_list[index] == 0:
                    prec_accumulated_list.append(0)
                else:
                    prec_accumulated_list.append(prec_list[index])
                p_livre_list.append(config['p']*prec_list[index])
                p_tronco_list.append(config['Cd']*config['pt']*prec_list[index])  
                prec_dossel_list.append(prec_list[index] - p_livre_list[index] - p_tronco_list[index])
                if self.armazenamento_dossel_inicial + prec_dossel_list[index] > capc_dossel:
                    drenagem_dossel_list.append(config['Ds'] * exp(config['bR']*(p_line - capc_dossel)))
                else:
                    drenagem_dossel_list.append(0)
                if prec_list[index] == 0:
                    if self.armazenamento_dossel_inicial - drenagem_dossel_list[index] < config['var_t_dossel'] * config['Emed']:
                        evaporacao_pos_chuva_list.append(self.armazenamento_dossel_inicial - drenagem_dossel_list[index])
                    else:
                        evaporacao_pos_chuva_list.append(config['Emed'] * config['var_t_dossel'])
                else:               
                    evaporacao_pos_chuva_list.append(0)
                if prec_dossel_list[index] + self.armazenamento_dossel_inicial - drenagem_dossel_list[index] - evaporacao_pos_chuva_list[index] > p_line:
                    armazenamento_dossel_list.append(p_line)
                else:
                    armazenamento_dossel_list.append(prec_dossel_list[index] + self.armazenamento_dossel_inicial - drenagem_dossel_list[index] - evaporacao_pos_chuva_list[index])
                if armazenamento_dossel_list[index] >= p_line:
                    excesso_dossel_list.append(prec_dossel_list[index] + self.armazenamento_dossel_inicial  - drenagem_dossel_list[index] - p_line)
                else:
                    excesso_dossel_list.append(0)
                prec_efetiva_list.append(excesso_dossel_list[index] + drenagem_dossel_list[index] + p_livre_list[index] + p_tronco_list[index])
                if prec_list[index] == 0:
                    transpiracao_dossel_list.append(config['Emed'] * config['var_t'] - evaporacao_pos_chuva_list[index])
                else:
                    transpiracao_dossel_list.append(0)
            else:
                if prec_list[index] == 0:
                    prec_accumulated_list.append(0)
                else:
                    prec_accumulated_list.append(prec_list[index])
                p_livre_list.append(config['p']*prec_list[index])
                p_tronco_list.append(config['Cd']*config['pt']*prec_list[index])  
                prec_dossel_list.append(prec_list[index] - p_livre_list[index] - p_tronco_list[index])
                if armazenamento_dossel_list[index-1] + prec_dossel_list[index] > capc_dossel:
                    drenagem_dossel_list.append(config['Ds'] * exp(config['bR']*(p_line - capc_dossel)))
                else:
                    drenagem_dossel_list.append(0)
                if prec_list[index] == 0:
                    if armazenamento_dossel_list[index-1] - drenagem_dossel_list[index] < config['var_t_dossel'] * config['Emed']:
                        evaporacao_pos_chuva_list.append(armazenamento_dossel_list[index-1] - drenagem_dossel_list[index])
                    else:
                        evaporacao_pos_chuva_list.append(config['Emed'] * config['var_t_dossel'])
                else:               
                    evaporacao_pos_chuva_list.append(0)
                if prec_dossel_list[index] + armazenamento_dossel_list[index-1] - drenagem_dossel_list[index] - evaporacao_pos_chuva_list[index] > p_line:
                    armazenamento_dossel_list.append(p_line)
                else:
                    armazenamento_dossel_list.append(prec_dossel_list[index] + armazenamento_dossel_list[index-1] - drenagem_dossel_list[index] - evaporacao_pos_chuva_list[index])
                if armazenamento_dossel_list[index] >= p_line:
                    excesso_dossel_list.append(prec_dossel_list[index] + armazenamento_dossel_list[index-1]  - drenagem_dossel_list[index] - p_line)
                else:
                    excesso_dossel_list.append(0)
                prec_efetiva_list.append(excesso_dossel_list[index] + drenagem_dossel_list[index] + p_livre_list[index] + p_tronco_list[index])
                if prec_list[index] == 0:
                    transpiracao_dossel_list.append(config['Emed'] * config['var_t'] - evaporacao_pos_chuva_list[index])
                else:
                    transpiracao_dossel_list.append(0)
                    
        data = {'date': date_list,
                't_var': time_list,
                'precipitaiton': prec_list,
                'evaporacao_pos_chuva': evaporacao_pos_chuva_list,
                'drengem_dossel': drenagem_dossel_list,
                'armazenamento_dossel': armazenamento_dossel_list,
                'excesso_dossel': excesso_dossel_list,
                'transpiracao_dossel': transpiracao_dossel_list,
                'prec_efetiva': prec_efetiva_list}

        df = pd.DataFrame(data).round(5)

        return df
                            
            
                




if __name__ == "__main__":
    main()



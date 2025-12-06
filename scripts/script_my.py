import json
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from datetime import datetime
import os  # Para criar diretórios, se necessário
import re  # Para usar expressões regulares

# Função para carregar os dados do arquivo JSON
def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['MySQL tpm']  # A chave onde estão os TPMs

# Função para processar os dados, extraindo tempos e TPMs
def extract_data(data):
    times = []
    tpm_values = []
    
    # Ordenando os dados pelas chaves (tempos) para garantir que a ordem seja cronológica
    for time, tpm in sorted(data.items()):
        times.append(time)
        tpm_values.append(int(tpm))  # Convertendo TPM para inteiro
    
    return times, tpm_values

# Função para converter a data em tempo relativo (em minutos desde o início do teste)
def convert_to_relative_time_in_minutes(times):
    # Converte a primeira data como referência e calcula o tempo relativo para todas as outras em minutos
    start_time = datetime.strptime(times[0], '%Y-%m-%d %H:%M:%S')
    relative_times = []
    
    for time_str in times:
        current_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        delta = current_time - start_time
        relative_times.append(delta.total_seconds() / 60)  # Calculando o tempo em minutos
    
    return relative_times

# Função para filtrar os dados até o ponto onde o TPM se torna 0 duas vezes consecutivas ou tempo > 16 minutos
def filter_data(times, tpm_values):
    filtered_times = []
    filtered_tpm_values = []
    
    zero_count = 0  # Contador para TPM igual a zero consecutivamente
    
    for time, tpm in zip(times, tpm_values):
        # Se o tempo ultrapassar 16 minutos, interrompe
        if time > 16:
            break
        
        if tpm == 0:
            zero_count += 1
        else:
            zero_count = 0  # Reseta o contador se o TPM não for zero
        
        # Se ocorrerem 2 zeros consecutivos, interrompemos
        if zero_count < 2:
            filtered_times.append(time)
            filtered_tpm_values.append(tpm)
        else:
            break
    
    return filtered_times, filtered_tpm_values

# Função para gerar o gráfico de comparação e salvar
def generate_comparison_plot(times_list, tpm_list, files, output_filename):
    plt.figure(figsize=(12, 6))

    # Para cada par de arquivos, processa e plota os dados
    for i in range(len(times_list)):
        # Convertendo os tempos para tempos relativos (minutos desde o início do teste)
        times_relative = convert_to_relative_time_in_minutes(times_list[i])

        # Filtrando os dados para parar quando TPM for 0 duas vezes consecutivas ou tempo > 16 minutos
        times_filtered, tpm_filtered = filter_data(times_relative, tpm_list[i])

        # Extrair número de VUs a partir do nome do arquivo (exemplo: '1Vu', '2Vu', etc.)
        match = re.search(r'(\d+)Vu', files[i])  # Encontrando o padrão 'XVu'
        if match:
            vu = match.group(1)  # Número de VUs (ex: '1', '2', etc.)
            label = f'{vu}Vu'  # Usando o número de VUs como rótulo

            # Plotando os dados
            plt.plot(times_filtered, tpm_filtered, label=label, marker='o', linestyle='-', markersize=6)

    # Ajustando o número de ticks no eixo X para ser de 1 em 1 minuto
    min_time = 0  # Começo do tempo (0 minutos)
    max_time = 16  # Tempo máximo (16 minutos)

    # Definindo os ticks no eixo X de 1 em 1 minuto, limitado a 16 minutos
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True, prune='both'))  # Limitar ticks a cada 1 minuto
    plt.xticks(range(min_time, max_time + 1, 1))  # 1 minuto por tick, até 16 minutos

    # Títulos e rótulos
    plt.title('Comparação de Performance - TPM vs Tempo', fontsize=14)
    plt.xlabel('Tempo (Minutos)', fontsize=12)
    plt.ylabel('TPM (Transactions per Minute)', fontsize=12)
    
    # Adicionando legenda
    plt.legend(loc='upper left')

    # Ajustando a rotação dos ticks no eixo X para legibilidade
    plt.xticks(rotation=45, ha='right')
    
    # Melhorando o layout para garantir que o gráfico esteja bem posicionado
    plt.tight_layout()
    
    # Adicionando a grade
    plt.grid(True)

    # Criar diretório 'graphs' se não existir
    if not os.path.exists('graphs'):
        os.makedirs('graphs')

    # Salvando o gráfico na pasta 'graphs'
    plt.savefig(f'graphs/{output_filename}.png')

    # Exibindo o gráfico
    plt.show()

# Caminhos para os arquivos JSON de exemplo (substitua com os seus arquivos reais)
files = [
     './results/rui/testA_my_1Vu_5Wh.json',
     './results/rui/testA_my_2Vu_10Wh.json',
     './results/rui/testA_my_4Vu_20Wh.json',
     './results/rui/testA_my_8Vu_40Wh.json',
     './results/rui/testA_my_10Vu_50Wh.json'
]
# files = [
#     './results/francisco/testA_my_1Vu_5Wh.json',
#     './results/francisco/testA_my_2Vu_10Wh.json',
#     './results/francisco/testA_my_4Vu_20Wh.json',
#     './results/francisco/testA_my_8Vu_40Wh.json',
#     './results/francisco/testA_my_10Vu_50Wh.json'
# ]

#TODO: FALTA TROCAR AQUI O TEST_B

# files = [
#     './results/francisco/testC_my_1Vu_5Wh.json',
#     './results/francisco/testC_my_2Vu_10Wh.json',
#     './results/francisco/testB_my_4Vu_20Wh.json',
#     './results/francisco/testC_my_8Vu_40Wh.json',
#     './results/francisco/testC_my_10Vu_50Wh.json'
# ]



# Carregar e extrair os dados dos arquivos
times_list = []
tpm_list = []

for file in files:
    data = load_data(file)
    times, tpm = extract_data(data)
    times_list.append(times)
    tpm_list.append(tpm)

# Gerar e exibir o gráfico de comparação, e salvar na pasta 'graphs'
generate_comparison_plot(times_list, tpm_list, files, 'testC_my_comparison')

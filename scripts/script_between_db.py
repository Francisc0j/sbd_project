import json
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from datetime import datetime

# Função para carregar os dados do arquivo JSON
def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data.get('MySQL tpm') or data.get('PostgreSQL tpm')  # A chave onde estão os TPMs

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

# Função para filtrar os dados até o ponto onde o TPM se torna 0 duas vezes consecutivas
def filter_data(times, tpm_values):
    filtered_times = []
    filtered_tpm_values = []
    
    zero_count = 0  # Contador para TPM igual a zero consecutivamente
    
    for time, tpm in zip(times, tpm_values):
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

# Função para gerar o gráfico de comparação
def generate_comparison_plot(times1, tpm1, times2, tpm2):
    plt.figure(figsize=(12, 6))

    # Convertendo os tempos para tempos relativos (minutos desde o início do teste)
    times1_relative = convert_to_relative_time_in_minutes(times1)
    times2_relative = convert_to_relative_time_in_minutes(times2)

    # Filtrando os dados para parar quando TPM for 0 duas vezes consecutivas
    times1_filtered, tpm1_filtered = filter_data(times1_relative, tpm1)
    times2_filtered, tpm2_filtered = filter_data(times2_relative, tpm2)

    # Plotando os dados dos dois testes
    plt.plot(times1_filtered, tpm1_filtered, label='MySQL', color='orange', marker='o', linestyle='-', markersize=6)
    plt.plot(times2_filtered, tpm2_filtered, label='PostgreSQL', color='blue', marker='o', linestyle='-', markersize=6)  # Usando círculos

    # Ajustando o número de ticks no eixo X para ser de 1 em 1 minuto
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True, prune='both'))  # Limitar ticks a cada 1 minuto
    plt.xticks(range(int(min(times1_filtered + times2_filtered)), int(max(times1_filtered + times2_filtered)) + 1, 1))  # 1 minuto por tick

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

    # Exibindo o gráfico
    plt.show()

# Caminhos para os arquivos JSON de exemplo
file1 = './results/francisco/testA_my_10Vu_50Wh.json'  # Substitua pelo caminho do seu primeiro arquivo JSON
file2 = './results/francisco/testA_pg_10Vu_50Wh.json'  # Substitua pelo caminho do seu segundo arquivo JSON

# Carregar e extrair os dados dos dois arquivos
data1 = load_data(file1)
data2 = load_data(file2)

# Extraindo os tempos e TPMs dos dois conjuntos de dados
times1, tpm1 = extract_data(data1)
times2, tpm2 = extract_data(data2)

# Gerar e exibir o gráfico de comparação
generate_comparison_plot(times1, tpm1, times2, tpm2)
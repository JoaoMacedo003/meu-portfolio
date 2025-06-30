"""
@author:
- Joao Macedo       2021220627
- Bruno Silva       2021232021
- Diogo Honório     2021232043
- Pedro Fernandes   2019218772
"""

import os
import librosa
import librosa.display
import sounddevice as sd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.fft as sf
import sounddevice
from scipy import stats
from functools import reduce
from scipy.stats import pearsonr
from sklearn.metrics import mean_squared_error


def extract_features(file_path):
    """
    Extrai várias características de áudio do arquivo fornecido e retorna estatísticas homogêneas e achatadas.
    As características incluem MFCCs, centroides espectrais, largura de banda espectral, e outros.

    Parâmetros:
        file_path (str): Caminho para o arquivo de áudio do qual as características serão extraídas.
        
    Retorna:
        dict: Dicionário contendo arrays de características extraídas.
        numpy.ndarray: Array contendo coeficiente de correlação de Pearson e RMSE entre centroides espectrais calculados e do librosa.
    """
    try:
        # Carrega o arquivo de áudio como um waveform mono com uma taxa de amostragem de 22050 Hz
        y, sr = librosa.load(file_path, sr=22050, mono=True)

        # Extração de múltiplas características do áudio
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)                                      # 91 colunas da matriz numpy 
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]                    # 7     "       " 
        # Cálculo da spectral_centroid de raiz com os valores inicias do load da librosa
        spectral_centroid_raiz = spectral_centroid_root(y=y, sr=sr) 

        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]                  # 7     "       " 
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr, n_bands = 6)          # 49     "       " 
        spectral_flatness = librosa.feature.spectral_flatness(y=y)[0]                           # 7     "       " 
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]                      # 7     "       " 
        rms = librosa.feature.rms(y=y)[0]                                                       # 7     "       " 
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y=y)[0]                         # 7     "       " 
        f0 = librosa.yin(y, fmin=20, fmax=sr/2, sr= sr)                                         # 7     "       " 
        # Ajuste para valores específicos de F0
        f0[f0 == 11025] = 0
        
        tempo = librosa.beat.beat_track(y=y, sr=sr)[0]                                          # 1     "       "
        
        _, filename = os.path.split(file_path)
        if filename.endswith("MT0040033011.mp3"):
            np.savetxt('Spectral Centroid MT0040033011.csv', spectral_centroid_raiz, fmt = "%f", delimiter=',')     # Validação de resultados para 2.2

        # Ajustando o deslocamento mencionado (librosa tem um atraso de 2 janelas)
        adjusted_spectral_centroid_librosa = spectral_centroid[2:]

        # Certificando que ambos arrays têm o mesmo tamanho
        min_length = min(len(spectral_centroid_raiz), len(adjusted_spectral_centroid_librosa))
        spectral_centroid_raiz = spectral_centroid_raiz[:min_length]
        adjusted_spectral_centroid_librosa = adjusted_spectral_centroid_librosa[:min_length]

        # Calcular o coeficiente de correlação de Pearson
        corr_coef, _ = pearsonr(spectral_centroid_raiz, adjusted_spectral_centroid_librosa)
        
        # Calcular o RMSE
        rmse = np.sqrt(mean_squared_error(spectral_centroid_raiz, adjusted_spectral_centroid_librosa))
        
        corr_coef_rmse = []
        corr_coef_rmse.append(corr_coef)
        corr_coef_rmse.append(rmse)

        # Armazena as características em um dicionário
        features = {
            'mfcc': mfcc,
            'spectral_centroid': spectral_centroid,
            'spectral_bandwidth': spectral_bandwidth,
            'spectral_contrast': spectral_contrast,
            'spectral_flatness': spectral_flatness,
            'spectral_rolloff': spectral_rolloff,
            'fundamental_frequency': f0,
            'rms': rms,
            'zero_crossing_rate': zero_crossing_rate,
            'tempo': tempo
        }

        return features, np.array(corr_coef_rmse)

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def spectral_centroid_root(y, sr, window_size=2048, hop_length=512):
    """
    Calcula o centroide espectral do sinal de áudio fornecido usando a transformada rápida de Fourier (FFT).
    O centroide espectral é uma medida que indica o centro de 'gravidade' do espectro de um som.

    Parâmetros:
        y (numpy.ndarray): O array de dados do sinal de áudio.
        sr (int): Taxa de amostragem do sinal de áudio.
        window_size (int): Tamanho da janela para aplicação da FFT, padrão é 2048.
        hop_length (int): Número de amostras entre início de janelas consecutivas, padrão é 512.

    Retorna:
        numpy.ndarray: Um array de valores de centroide espectral para cada janela processada do sinal.
    """
    
    # Numero de janelas a percorrer
    # Calcula o número total de janelas possíveis, dado o tamanho da janela e o passo (considerando sobreposição)
    if len(y) < window_size:
        num_windows = 1  # Se o sinal é menor que uma janela, apenas uma janela é necessária
    else:
        num_windows = (len(y) // hop_length) - 3     

    # Verifica se o final do sinal será capturado pela última janela
    # Isso acontece se a última posição inicial da janela + tamanho da janela ultrapassar o comprimento do sinal
    end_of_last_window = (num_windows - 1) * hop_length + window_size
    if end_of_last_window > len(y):
        padding = end_of_last_window - len(y)
        y = np.pad(y, (0, padding), mode='constant')

    # Prepara a função de janela
    window_function = np.hanning(window_size)

    # Frequências para cada bin do espectro de magnitude
    freqs = np.fft.rfftfreq(window_size, d=1/sr)

    # Agora y é garantido de ter um comprimento suficiente para calcular todas as janelas planejadas
    centroid_values = []


    for i in range(num_windows-1):   # Nota: perguntar ao stor, se retirar o -1  acrescenta um valor a mais ao np.array 
        # Define o índice inicial e final da janela atual
        start_index = int(i * hop_length)
        end_index = start_index + window_size

        # Extrai a janela atual do sinal
        window_signal = y[start_index:end_index] * window_function

        # Calcula o espectro de magnitude
        magnitude_spectrum = np.abs(sf.rfft(window_signal))

        SC = np.sum(magnitude_spectrum * freqs) / np.sum(magnitude_spectrum) if np.sum(magnitude_spectrum) > 0 else 0

        centroid_values.append(SC)  # Uso de append para adicionar cada valor calculado

    return np.array(centroid_values)
        




def calculateStatistics(features):
    """
    Calcula estatísticas resumidas para cada característica de áudio fornecida,
    garantindo que todas sejam achatadas em arrays 1D antes de calcular as estatísticas.
    
    Parâmetros:
        features (dict): Dicionário contendo as características de áudio, onde cada chave
                         é o nome da característica e o valor é o dado (pode ser array 1D, 2D ou escalar).
        
    Retorna:
        numpy.ndarray: Array do NumPy contendo todas as estatísticas calculadas de todas as características.
    """
    # Lista para armazenar as estatísticas de todas as características
    feature_stats = []
    
    for key, value in features.items():
        
        # Condições específicas para características complexas
        if key == 'mfcc' or key == 'spectral_contrast':
            # Essas características são arrays 2D onde cada linha precisa de estatísticas individuais
            for row in value:
                stats_values = compute_stats(row)
                feature_stats.extend(stats_values)

        elif key == 'tempo':
            # O tempo é um escalar, apenas adicione-o diretamente
            feature_stats.append(value)

        else:
            # Caso padrão para qualquer outro tipo de array de características
            stats_values = compute_stats(value)
            feature_stats.extend(stats_values)

    return np.array(feature_stats)  # Converte a lista para um array do NumPy antes de retornar



def compute_stats(value):
    """
    Calcula estatísticas descritivas para um conjunto de dados fornecido.
    
    Parâmetros:
        value (array_like): Conjunto de dados numéricos do qual as estatísticas serão calculadas.
        
    Retorna:
        list: Uma lista contendo as seguintes estatísticas do conjunto de dados:
              - Média
              - Desvio padrão
              - Assimetria (skewness)
              - Curtose
              - Mediana
              - Valor máximo
              - Valor mínimo
    """
    # Calcula as estatísticas descritivas e armazena em uma lista
    stats_values = [
        np.mean(value),  # Média dos valores
        np.std(value),   # Desvio padrão dos valores
        stats.skew(value),  # Assimetria dos valores
        stats.kurtosis(value),  # Curtose dos valores
        np.median(value),  # Mediana dos valores
        np.max(value),  # Valor máximo dos valores
        np.min(value)  # Valor mínimo dos valores
    ]

    return stats_values



def normalize_np(all_features, count):
    """
    Normaliza os dados de um array do NumPy para o intervalo [0, 1], inserindo os valores mínimos e máximos
    na primeira e segunda linha da matriz de retorno, respectivamente.
    
    Parâmetros:
        all_features (numpy.ndarray): O array do NumPy a ser normalizado, contendo as características extraídas.
        count (int): O número efetivo de arquivos processados.
        max_files (int): O número máximo de arquivos a serem processados.
        
    Retorna:
        numpy.ndarray: O array normalizado com os valores mínimos e máximos nas duas primeiras linhas.
    """

    # Inicializa a matriz normalizada com duas linhas adicionais para os valores mínimos e máximos
    all_features_normalized = np.zeros((count + 2, 190))  # Primeiras duas linhas para min e max
    
    # Evita a normalização se nenhum arquivo foi processado
    if count == 0:
        return all_features_normalized

    # Calcula os valores mínimos e máximos das características
    min_vals = np.min(all_features[:count], axis=0)
    max_vals = np.max(all_features[:count], axis=0)
    
    # Substitui o intervalo de 0 por 1 para evitar divisão por zero
    val_range = np.where(max_vals - min_vals == 0, 1, max_vals - min_vals)
    
    # Normaliza as características
    normalized_features = (all_features[:count] - min_vals) / val_range

    # Coloca os valores mínimos e máximos nas primeiras linhas da matriz normalizada
    all_features_normalized[0] = min_vals
    all_features_normalized[1] = max_vals

    # Coloca as características normalizadas após as duas primeiras linhas
    all_features_normalized[2:count+2] = normalized_features

    return all_features_normalized

        
def euclidean_distance(x, y):
    """
    Calcula a distância Euclidiana entre dois vetores.

    Parâmetros:
        x (numpy.ndarray): Primeiro vetor.
        y (numpy.ndarray): Segundo vetor.
    
    Retorna:
        float: A distância Euclidiana entre os vetores x e y.
    """
    return np.sqrt(np.sum((x - y) ** 2))


def manhattan_distance(x, y):
    """
    Calcula a distância Euclidiana entre dois vetores.

    Parâmetros:
        x (numpy.ndarray): Primeiro vetor.
        y (numpy.ndarray): Segundo vetor.
    
    Retorna:
        float: A distância Euclidiana entre os vetores x e y.
    """
    return np.sum(np.abs(x - y))        


def cosine_similarity(x, y):
    """
    Calcula a similaridade de cosseno entre dois vetores, que é o cosseno do ângulo entre eles.
    A similaridade é ajustada para ser uma medida de distância ao subtrair a similaridade do valor 1.

    Parâmetros:
        x (numpy.ndarray): Primeiro vetor.
        y (numpy.ndarray): Segundo vetor.
    
    Retorna:
        float: A medida de distância baseada na similaridade de cosseno (1 - similaridade de cosseno).
    """
    dot_product = np.dot(x, y)
    norm_x = np.linalg.norm(x)
    norm_y = np.linalg.norm(y)
    cos_similarity = dot_product / (norm_x * norm_y)
    return 1 - cos_similarity 


def calculate_distance_rankings(query_features_normalized, all_features_normalized, audio_dir, count):
    """
    Calcula as distâncias entre as características de uma consulta e todas as outras características,
    gerando rankings baseados nas distâncias Euclidiana, Manhattan e Cosseno.

    Parâmetros:
        query_features_normalized (numpy.ndarray): Características normalizadas do arquivo de consulta.
        all_features_normalized (numpy.ndarray): Matriz de características normalizadas de todos os arquivos.
        audio_dir (str): Caminho do diretório onde estão localizados os arquivos de áudio.
        count (int): Número de arquivos processados.
    
    Retorna:
        tuple: Contém diversos elementos detalhando os resultados das distâncias calculadas e rankings formados:
            - Arrays das distâncias mais próximas para cada medida de distância.
            - Listas completas de distâncias calculadas para cada medida.
            - Arrays dos rankings dos arquivos de áudio, indicando os arquivos mais próximos com base em cada medida.
    """

    # Listas para armazenar as distâncias
    euclidean_distances = []
    manhattan_distances = []
    cosine_distances = []

    # Calcular distâncias
    for i in range(count-1):
        # Calcular a distância Euclidiana
        euclidean_dist = euclidean_distance(query_features_normalized[:190], all_features_normalized[(i+2), :])
        euclidean_distances.append(euclidean_dist)
        
        # Calcular a distância de Manhattan
        manhattan_dist = manhattan_distance(query_features_normalized[:190], all_features_normalized[(i+2), :])
        manhattan_distances.append(manhattan_dist)
        
        # Calcular a distância de Cosseno
        cosine_dist = cosine_similarity(query_features_normalized[:190], all_features_normalized[(i+2), :])
        cosine_distances.append(cosine_dist)

    # Calcular rankings para cada distância
    euclidean_index_ranking = np.argsort(euclidean_distances)[:11].astype('int16')
    manhattan_index_ranking = np.argsort(manhattan_distances)[:11].astype('int16')
    cosine_index_ranking = np.argsort(cosine_distances)[:11].astype('int16')

    # Obter os valores correspondentes das distâncias
    closest_euclidean_dists = [euclidean_distances[i] for i in euclidean_index_ranking]
    closest_manhattan_dists = [manhattan_distances[i] for i in manhattan_index_ranking]
    closest_cosine_sims = [cosine_distances[i] for i in cosine_index_ranking]

    euclidean_ranking = [None] * 11
    manhattan_ranking = [None] * 11
    cosine_ranking = [None] * 11

    # Obtém a lista de arquivos no diretório de áudio
    audio_files = os.listdir(audio_dir)
    for i in range(11):
        euclidean_ranking[i] = audio_files[euclidean_index_ranking[i]]
        manhattan_ranking[i] = audio_files[manhattan_index_ranking[i]]
        cosine_ranking[i] = audio_files[cosine_index_ranking[i]]

    return np.array(closest_euclidean_dists), np.array(closest_manhattan_dists), np.array(closest_cosine_sims), euclidean_distances, manhattan_distances, cosine_distances, np.array(euclidean_ranking), np.array(manhattan_ranking), np.array(cosine_ranking)


def metadata_objective(query_metadata, target, target_metadata):  
    """
    Avalia a relevância de uma música alvo em relação a uma música de consulta,
    com base em gêneros, emoções e artistas associados.

    Parâmetros:
        query_metadata (DataFrame): DataFrame contendo os metadados da música de consulta.
        target (str): Nome do arquivo da música alvo (com extensão .mp3).
        target_metadata (DataFrame): DataFrame contendo os metadados das músicas alvo.

    Retorna:
        int: Pontuação indicando o número de critérios coincidentes entre a música alvo e a consulta.
    """

    # Remove a extensão do nome do arquivo de destino
    target_sample = target[:-4]
    
    # Filtra a linha correspondente ao arquivo de destino pelo nome do arquivo (sem a extensão .mp3)
    target_filename = target_metadata.loc[target_metadata['Song'] == target_sample]
    
    # Inicializa a pontuação da qualidade da música alvo
    count = 0
    
    if not target_filename.empty:
        # Filtra a linha correspondente ao arquivo de consulta pelo nome do arquivo (sem a extensão .mp3)
        query = query_metadata.loc[query_metadata['Song'] == "MT0000414517"]

        # Verifica se algum dos gêneros da música alvo corresponde ao gênero da consulta
        target_genres = target_filename['GenresStr'].values[0].split('; ')
        query_genres = query['GenresStr'].values[0].split('; ')
        count += sum(genre in target_genres for genre in query_genres)


        # Verifica se a emoção da música alvo corresponde à emoção da consulta
        target_moods = target_filename['MoodsStrSplit'].values[0].split('; ')
        query_moods = query['MoodsStrSplit'].values[0].split('; ')
        count += sum(mood in target_moods for mood in query_moods)

        # Verifica se o artista da música alvo corresponde ao artista da consulta
        target_artist = target_filename['Artist'].values[0]
        query_artist = query['Artist'].values[0]
        count += float(query_artist == target_artist)


    return count


def calcular_precisao(metadata, euclidean_ranking, manhattan_ranking, cosine_ranking):
    """
    Calcula a precisão dos rankings de distâncias (Euclidiana, Manhattan e Cosseno),
    verificando a presença de itens recomendados nos metadados e excluindo um item específico.

    Parâmetros:
        metadata (list): Lista de referências válidas para comparação.
        euclidean_ranking (list): Lista de recomendações baseadas na distância Euclidiana.
        manhattan_ranking (list): Lista de recomendações baseadas na distância Manhattan.
        cosine_ranking (list): Lista de recomendações baseadas na similaridade de Cosseno.

    Retorna:
        tuple: Contém as precisões calculadas para cada método de distância em percentual.
    """

    # Contagem de recomendações corretas nos rankings de distância
    count_euclidiana = sum(1 for recomendação in euclidean_ranking if recomendação in metadata and recomendação != "MT0000414517.mp3")
    count_manhattan = sum(1 for recomendação in manhattan_ranking if recomendação in metadata and recomendação != "MT0000414517.mp3")
    count_cosine = sum(1 for recomendação in cosine_ranking if recomendação in metadata and recomendação != "MT0000414517.mp3")
    
    # Precisão para cada método
    precisao_euclidiana = count_euclidiana / (len(euclidean_ranking)-1) * 100
    precisao_manhattan = count_manhattan / (len(manhattan_ranking)-1) * 100
    precisao_cosine = count_cosine / (len(cosine_ranking)-1) * 100
    
    return np.array(precisao_euclidiana), np.array(precisao_manhattan), np.array(precisao_cosine)


def process_mp3_files(audio_dir, query_file_name, panda_metadata_dir, query_metadata_dir, max_files=900):
    """
    Processa arquivos MP3 para extrair características de áudio, realiza análise estatística,
    e salva os resultados em estruturas de dados NumPy e arquivos CSV.
    
    Parâmetros:
        audio_dir (str): Diretório contendo arquivos MP3.
        query_file_name (str): Nome do arquivo específico para consulta dentro do diretório.
        panda_metadata_dir (str): Caminho para o arquivo CSV com metadados do panda.
        query_metadata_dir (str): Caminho para o arquivo CSV com metadados da consulta.
        max_files (int): Número máximo de arquivos MP3 para processar.
        
    Retorna:
        numpy.ndarray: Matriz com as estatísticas das características de áudio dos arquivos processados.
    """
        
    index_stats_query_features = 0
    
    # Assume que cada arquivo preencherá exatamente uma linha da matriz 'all_features'.
    all_features = np.zeros((max_files, 190))  # Ajusta o tamanho assumindo 190 características por arquivo, nossa matriz numpy
    FM_Q = np.zeros((3, 190))
    notNormFM_Q = np.zeros((1, 190))
    

    corr_coef_rmse_values = []
    
    # Variáveis para armazenar as distâncias
    euclidean_distances = []
    manhattan_distances = []
    cosine_distances = []

    # Avaliacao Objetiva 
    top10_objective = dict()                # NomeFicheiro: Count 
    
    # Leitura files
    panda_metadata = pd.read_csv(panda_metadata_dir)
    query_metadata = pd.read_csv(query_metadata_dir)


    count = 0
    for filename in os.listdir(audio_dir):

        if filename.endswith(".mp3"):
            file_path = os.path.join(audio_dir, filename)
            features, corr_coef_rmse = extract_features(file_path)
            
            # Avaliacao Objetiva
            count_metadata = metadata_objective(query_metadata, filename, panda_metadata)
            top10_objective[filename] = count_metadata


            if not features:
                print(f"Erro ao extrair características de {file_path}.")
                continue
            
            if filename.endswith(query_file_name):
                index_stats_query_features =  count;
            
            corr_coef_rmse_values.append(corr_coef_rmse)

            stats_features = calculateStatistics(features)  # Calcula estatísticas a partir das características
            

            if stats_features.size > 0:  # Verifica se as características foram extraídas e as estatísticas calculadas
                all_features[count, :] = stats_features[:190]  # Garante que apenas 190 características sejam armazenadas
                count += 1
                if count >= max_files:
                    break
                

    all_features_normalized = normalize_np(all_features, count)

    # Extrai a linha especificada e mantém como uma matriz de uma linha
    notNormFM_Q = all_features[index_stats_query_features:index_stats_query_features+1, :]

    # Selecionando as duas primeiras linhas de all_features_normalized
    top_two_rows = all_features_normalized[:2, :]
    query_features_normalized = all_features_normalized[index_stats_query_features+2, :]
    # Concatenando as duas primeiras linhas com a linha de query_features_normalized
    FM_Q = np.vstack((top_two_rows, query_features_normalized))
    
    closest_euclidean_dists, closest_manhattan_dists, closest_cosine_sims, euclidean_distances, manhattan_distances, cosine_distances, euclidean_ranking_np, manhattan_ranking_np, cosine_ranking_np = calculate_distance_rankings(query_features_normalized, all_features_normalized, audio_dir, count)

    # Converter valores do dicionário para um array NumPy
    values = np.array(list(top10_objective.values()))
    top10 = np.argsort(values)[::-1][:11].astype('int16')
    # Converter índices NumPy de volta para as chaves do dicionário
    sorted_keys = [list(top10_objective.keys())[index] for index in top10]
    sorted_items = [values[index] for index in top10]
    
    top10_objective_filename = [item for item in sorted_keys] 
    top10_objective_count_metadata = [item for item in sorted_items] 

    precisao_euclidiana, precisao_manhattan, precisao_cosine = calcular_precisao(sorted_keys, euclidean_ranking_np, manhattan_ranking_np, cosine_ranking_np)

    np.savetxt('features.csv', all_features, fmt = "%f", delimiter=',')                             # Validação de resultados para 2.1
    np.savetxt('features_normalized.csv', all_features_normalized, fmt = "%f", delimiter=',')       # Validação de resultados para 2.1
    np.savetxt('metricsSpectralCentroid.csv', np.array(corr_coef_rmse_values), fmt = "%f", delimiter=',')       # Validação de resultados para 2.2
    np.savetxt('euclidean_distances.csv', euclidean_distances, fmt = "%f", delimiter=',')        # Validação de resultados para 3.2
    np.savetxt('manhattan_distances.csv', manhattan_distances, fmt = "%f", delimiter=',')        # Validação de resultados para 3.2
    np.savetxt('cosine_distances.csv', cosine_distances, fmt = "%f", delimiter=',')        # Validação de resultados para 3.2
    np.savetxt('query_features.csv', notNormFM_Q, fmt = "%f", delimiter=',')        # Validação de resultados para 3.2
    np.savetxt('query_features_normalized.csv', FM_Q, fmt = "%f", delimiter=',')        # Validação de resultados para 3.2

    #Rankings
    print("- Rankings:\n")

    # Recomendação baseada na classificação euclidiana
    print("Ranking: Euclidean-------------")
    print(euclidean_ranking_np)
    formatted_array = [f"{x:.6e}" for x in closest_euclidean_dists]
    print(np.array(formatted_array))

    # Recomendação baseada na classificação de Manhattan
    print("\nRanking: Manhattan-------------")
    print(manhattan_ranking_np)
    formatted_array = [f"{x:.7e}" for x in closest_manhattan_dists]
    print(np.array(formatted_array))

    # Recomendação baseada na classificação de Cosseno
    print("\nRanking: Cosine-------------")
    print(cosine_ranking_np)
    print(closest_cosine_sims)

    print("\nRanking: Metadata-------------")
    print(np.array(top10_objective_filename))
    print(np.array(top10_objective_count_metadata))

    # Printing the precision values
    print("\nPrecision de:  " + str(precisao_euclidiana))
    print("Precision dm:  " + str(precisao_manhattan))
    print("Precision dc:  " + str(precisao_cosine))




if __name__ == "__main__":
    # Diretório onde os arquivos de áudio estão armazenados - Alterar aqui
    audio_dir = r"C:\Users\joaod\Universidade\3ªano\2ªsemestre 2023-2024\Multimédia\Laboratorial\TP2\Queries"
    
    query_file_name = "MT0000414517.mp3"

    panda_metadata_dir = r"C:\Users\joaod\Universidade\3ªano\2ªsemestre 2023-2024\Multimédia\Laboratorial\TP2\panda_dataset_taffc_metadata.csv"
    
    query_metadata_dir = r"C:\Users\joaod\Universidade\3ªano\2ªsemestre 2023-2024\Multimédia\Laboratorial\TP2\query_metadata.csv"
    
    # Extração de características
    process_mp3_files(audio_dir, query_file_name, panda_metadata_dir, query_metadata_dir)
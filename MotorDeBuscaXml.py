import os
import xml.etree.ElementTree as ET
import time

class Item:
    def __init__(self, id, ocorrencias_titulo, ocorrencias_texto, palavras_texto, peso, titulo, texto):
        self.id = id
        self.ocorrencias_titulo = ocorrencias_titulo
        self.ocorrencias_texto = ocorrencias_texto
        self.palavras_texto = palavras_texto
        self.peso = peso
        self.titulo = titulo
        self.texto = texto

class Pesquisa:
    def __init__(self, pesquisa, resultado_da_pesquisa):
        self.pesquisa = pesquisa
        self.resultado_da_pesquisa = resultado_da_pesquisa

# Cache para armazenar resultados de pesquisa
cache = {}

def filtrar_palavras(texto):
    """
    Filtra palavras menores que 4 caracteres de um texto.
    """
    return [palavra for palavra in texto.split() if len(palavra) >= 4]

def parse_xml(file_path, search):
    """
    Processa o arquivo XML e realiza a busca pelo termo.
    """
    lista_de_resultados = []
    tree = ET.parse(file_path)
    root = tree.getroot()
    search = search.lower()

    # Realizar busca no arquivo XML
    for page in root.findall('page'):
        page_id = page.find('id').text
        page_title = page.find('title').text or ""
        page_text = page.find('text').text or ""

        # Filtrar palavras do título e texto
        words_in_title = filtrar_palavras(page_title.lower())
        words_in_text = filtrar_palavras(page_text.lower())

        # Contar ocorrências no título e no texto
        ocorrencias_titulo = words_in_title.count(search)
        ocorrencias_texto = words_in_text.count(search)

        # Verificar se a palavra aparece no título ou texto
        if ocorrencias_titulo > 0 or ocorrencias_texto > 0:
            # Cálculo de pesos balanceado (densidade de ocorrência)
            peso_titulo = (ocorrencias_titulo / len(words_in_title)) if len(words_in_title) > 0 else 0.0
            peso_texto = (ocorrencias_texto / len(words_in_text)) if len(words_in_text) > 0 else 0.0

            # Atribuindo pesos para título e texto, com 70% para o título e 30% para o texto
            relevancia = (0.1 * peso_titulo) + (0.3 * peso_texto)
            
            lista_de_resultados.append(Item(
                id=page_id,
                ocorrencias_titulo=ocorrencias_titulo,
                ocorrencias_texto=ocorrencias_texto,
                palavras_texto=len(words_in_text),
                peso=relevancia,
                titulo=page_title,
                texto=page_text
            ))

    # Ordenar resultados por peso em ordem decrescente
    resultado = sorted(lista_de_resultados, key=lambda item: item.peso, reverse=True)

    # Armazenar resultados no cache para uso futuro
    cache[search] = resultado
    return resultado

def buscar_arquivos_xml():
    """
    Busca automaticamente todos os arquivos XML no diretório atual.
    """
    directory_path = os.getcwd()  # Diretório atual do script
    arquivos_xml = [os.path.join(directory_path, filename) for filename in os.listdir(directory_path) if filename.endswith(".xml")]

    if not arquivos_xml:
        print("Nenhum arquivo XML encontrado no diretório.")
        return

    print(f"Arquivos XML encontrados: {len(arquivos_xml)}")
    for file_path in arquivos_xml:
        print(f"Processando arquivo: {file_path}")

        while True:
            search = input("\nDigite o termo de pesquisa (ou 'sair' para encerrar): ").strip()
            if search.lower() == "sair":
                print("Encerrando busca neste arquivo.")
                break

            # Validar termos de entrada (ignorar palavras menores que 4 caracteres)
            if len(search) < 4:
                print("Digite uma palavra com pelo menos 4 caracteres.")
                continue

            # Verificar se a pesquisa já foi realizada anteriormente e está no cache
            if search in cache:
                print(f"Resultado para '{search}' encontrado no cache!")
                resultados = cache[search]
            else:
                # Medir o tempo de busca pela primeira vez
                start_time = time.time()
                resultados = parse_xml(file_path, search)
                end_time = time.time()
                print(f"Tempo de busca pela primeira vez: {end_time - start_time:.4f} segundos")

            if resultados:
                print("\nResultados mais relevantes (em ordem de relevância):")
                for idx, item in enumerate(resultados[:5], 1):  # Exibe os 5 primeiros resultados
                    print(f"\nResultado {idx}:")
                    print(f"ID: {item.id}")
                    print(f"Título: {item.titulo}")
                    print(f"Número de Palavras no Texto: {item.palavras_texto}")
                    print(f"Ocorrências no Título: {item.ocorrencias_titulo}")
                    print(f"Ocorrências no Texto: {item.ocorrencias_texto}")
                    print(f"Peso (Relevância): {item.peso:.4f}")
                print("-" * 100)
            else:
                print("Nenhum resultado relevante encontrado para essa busca.")


try:
    buscar_arquivos_xml()
except Exception as e:
    print(f"Erro: {e}")

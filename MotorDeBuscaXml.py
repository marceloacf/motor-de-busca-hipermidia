import xml.etree.ElementTree as ET
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

class BuscaXML:
    def __init__(self, caminho_arquivo):
        self.paginas=self.carregar_xml(caminho_arquivo)
        self.vectorizer=TfidfVectorizer(stop_words="english")
        self.tfidf_matrix=None
        self.documentos=[]
        self.preprocessar()

    def carregar_xml(self, caminho_arquivo):
        tree=ET.parse(caminho_arquivo)
        root=tree.getroot()
        paginas=[]
        for page in root.findall('page'):
            id=page.find('id').text
            title=page.find('title').text
            text=page.find('text').text or ""
            paginas.append({"id":id,"title":title,"text":text})
        return paginas

    def preprocessar(self):
        self.documentos=[f"{page['title']} {page['text']}" for page in self.paginas]
        self.tfidf_matrix=self.vectorizer.fit_transform(self.documentos)

    def buscar(self, palavra, limite=10):
        query_vec=self.vectorizer.transform([palavra])
        similaridades=cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        resultados=sorted(zip(similaridades, self.paginas),
            key=lambda x: x[0],
            reverse=True
        )
        resultados_relevantes=[
            {"id": res[1]["id"], "title": res[1]["title"], "score": res[0]}
            for res in resultados if res[0] > 0
        ]
        return resultados_relevantes[:limite]
    
    

def encontrar_arquivo_xml(pasta="."):
        diretorio=Path(pasta)
        arquivos_xml=list(diretorio.glob("*.xml"))
        
        if not arquivos_xml:
            raise FileNotFoundError("Nenhum arquivo XML encontrado na pasta especificada.")
        
        return arquivos_xml[0]

try:
    caminho=encontrar_arquivo_xml()
    busca=BuscaXML(caminho)

    while True:
        palavra=input("Digite a palavra para buscar (ou 'sair' para encerrar): ").strip()
        if palavra.lower() == "sair":
            print("Encerrando o programa.")
            break
        
        resultados=busca.buscar(palavra,limite=5)
        if resultados:
            print("\nResultados mais relevantes:")
            for res in resultados:
                print(f"ID: {res['id']}, Título: {res['title']}, Relevância: {res['score']:.4f}")
        else:
            print("Nenhum resultado encontrado para essa busca.")
except FileNotFoundError as e:
    print(e)

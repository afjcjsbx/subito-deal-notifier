import re
import httpx
from bs4 import BeautifulSoup
import json

class SubitoAd:
    def __init__(self, url: str):
        self.url = url
        self.product_title = None
        self.product_description = None
        self.product_price = None
        self.product_features = []

    def to_json(self):
        """ Converte l'oggetto in formato JSON """

        # Assicura che self.product_price sia sempre un valore float valido
        price = float(self.product_price[0]) if isinstance(self.product_price, tuple) else 0.0

        annuncio_dict = {
            "title": self.product_title,
            "description": self.product_description,
            "price": price,
            "features": self.product_features
        }
        return json.dumps(annuncio_dict, ensure_ascii=False, indent=4)

    def extract_data(self):
        """ Estrae i dati dall'annuncio """
        try:
            response = httpx.get(self.url)
            if response.status_code == 200:
                html_content = response.text
                self.product_title = self.extract_title(html_content)
                self.product_description = self.extract_description(html_content)
                self.product_price = self.extract_price(html_content)
                self.product_features = self.extract_features(html_content)
            else:
                print(f"Errore nel recupero dei dati per {self.url}")
        except Exception as e:
            print(f"Errore durante l'estrazione dei dati: {e}")

    def extract_title(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        title_tag = soup.find('h1', class_='AdInfo_title__KwKRY')
        if title_tag:
            return title_tag.get_text(strip=True)

        return 'N/A'

    def extract_description(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        description_tag = soup.find('p', class_='AdDescription_description__154FP')
        if description_tag:
            return description_tag.get_text(strip=True)

        return 'N/A'

    def extract_price(self, html_content: str) -> float:
        """ Estrae il prezzo in modo universale e preserva la valuta """
        soup = BeautifulSoup(html_content, 'html.parser')

        price_tag = soup.find('p', class_='AdInfo_price__flXgp')
        price_text = price_tag.get_text(strip=True) if price_tag else ''

        if not price_text:
            return 0.0

        valuta = re.search(r'€|£|\$', price_text)
        valuta_symbol = valuta.group(0) if valuta else ''

        price_cleaned = re.sub(r'[^\d,]', '', price_text)
        price_cleaned = price_cleaned.replace('.', '')

        if ',' in price_cleaned:
            price_cleaned = price_cleaned.replace(',', '.')

        try:
            price = float(price_cleaned)
        except ValueError:
            price = 0.0

        return price


    def extract_features(self, html_content: str) -> list:
        soup = BeautifulSoup(html_content, 'html.parser')
        features = []
        features_section = soup.find('div', class_='main-data_main-features-container__Ghc7I')
        if features_section:
            feature_tags = features_section.find_all('div', class_='main-data_main-feature__NujTP')
            for tag in feature_tags:
                feature_name = tag.find('p', class_='caption')
                if feature_name:
                    features.append(feature_name.get_text(strip=True))

        add_feature = soup.find_all('span', class_='feature-list_value__SZDpz')
        for feature in add_feature:
            features.append(feature.get_text(strip=True))

        # if not features:
            # features.append('Nessuna caratteristica trovata')

        return features



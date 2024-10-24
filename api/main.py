from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Fonction pour scraper les données
def scrape_audio_data(page):
    url = f"https://vetso.serasera.org/audio?page={page}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        
        titles_seen = set()  # Pour éviter les doublons
        audio_data = []  # Liste pour stocker les résultats
        
        # Rechercher toutes les sections de poèmes (chaque poème a une structure en row)
        rows = soup.find_all('div', class_='row')

        for row in rows:
            # Vérifier que la colonne contenant le titre existe
            title_column = row.find('div', class_='col-md-8')
            if title_column:
                # Extraire le titre du premier lien dans la colonne de gauche
                title_tag = title_column.find('a')
                title = title_tag.text.strip() if title_tag else None

                # Extraire l'auteur du lien suivant (celui entre parenthèses)
                author_tag = title_tag.find_next('a') if title_tag else None
                author = author_tag.text.strip() if author_tag else None
            else:
                title = None
                author = None

            # Vérifier que la colonne contenant l'audio existe
            audio_column = row.find('div', class_='col-md-4')
            if audio_column:
                # Extraire l'URL de l'audio depuis l'élément <audio>
                audio_tag = audio_column.find('audio')
                audio_src = audio_tag.get('src') if audio_tag else None
            else:
                audio_src = None

            # Ajouter les résultats seulement si toutes les données sont présentes et sans doublons
            if title and author and audio_src and title not in titles_seen:
                audio_data.append({
                    'title': title,
                    'author': author,
                    'audio_url': audio_src
                })
                titles_seen.add(title)
        
        return audio_data
    else:
        return []

# Route pour la recherche avec pagination
@app.route('/recherche', methods=['GET'])
def recherche():
    question = request.args.get('question')
    page = request.args.get('page', default=1, type=int)

    if question == 'audio':
        # Scrape les données en fonction de la page demandée
        audio_data = scrape_audio_data(page)
        
        if audio_data:
            return jsonify(audio_data), 200
        else:
            return jsonify({"error": "No data found for this page."}), 404
    else:
        return jsonify({"error": "Invalid query parameter. Use 'audio' as question."}), 400

# Lancer l'application sur le host 0.0.0.0 et port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

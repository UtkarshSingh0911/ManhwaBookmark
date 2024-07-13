from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comics.db'
db = SQLAlchemy(app)

class Comic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    chapter_num = db.Column(db.String(20), nullable=False)
    chapter_date = db.Column(db.String(30), nullable=False)
    url = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f"<Comic {self.title}>"

def extract_info_from_link(link):
    chapter_num = link.find('span', class_='chapternum').text.strip()
    chapter_date = link.find('span', class_='chapterdate').text.strip()
    return chapter_num, chapter_date

def get_first_link_info(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        target_div = soup.find('div', id='chapterlist')
        if not target_div:
            return None

        first_link = target_div.find('a')
        if not first_link:
            return None

        chapter_num, chapter_date = extract_info_from_link(first_link)

        infox_div = soup.find('div', class_='infox')
        if not infox_div:
            return None

        title_header = infox_div.find('h1', class_='entry-title')
        if not title_header:
            return None

        title = title_header.text.strip()

        return {
            'chapter_num': chapter_num,
            'chapter_date': chapter_date,
            'title': title
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

@app.route('/')
def index():
    comics = Comic.query.all()
    return render_template('index.html', comics=comics)

@app.route('/add', methods=['GET', 'POST'])
def add_comic():
    if request.method == 'POST':
        url = request.form['url']
        comic_info = get_first_link_info(url)
        if comic_info:
            new_comic = Comic(
                title=comic_info['title'],
                chapter_num=comic_info['chapter_num'],
                chapter_date=comic_info['chapter_date'],
                url=url
            )
            db.session.add(new_comic)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('add_comic.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

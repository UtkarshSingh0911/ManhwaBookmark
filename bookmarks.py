import requests
from bs4 import BeautifulSoup

def extract_info_from_link(link):
    # Extract chapter number and date from the link
    chapter_num = link.find('span', class_='chapternum').text.strip()
    chapter_date = link.find('span', class_='chapterdate').text.strip()
    return chapter_num, chapter_date

def get_first_link_info(url):
    try:
        response = requests.get(url)
        response.raise_for_status() 

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        #search chapterlist
        target_div = soup.find('div', id='chapterlist')
        if not target_div:
            return None

        # find latest chapter link
        first_link = target_div.find('a')
        if not first_link:
            return None

        # Get chapter number, and date from the first link
        chapter_num, chapter_date = extract_info_from_link(first_link)

        # Find div storing title
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
            'title' : title
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

#add all the comics to track
urls = [
        ]


for url in urls:
    first_link_info = get_first_link_info(url)

    if first_link_info:
        print(f" {first_link_info['title']}-{first_link_info['chapter_num']} on {first_link_info['chapter_date']}")
    
    else:
        print("No link found in the specified div.")

#do check for the ids and classes of divs and spans everytime using on different website.
#currently following classes and ids are being used
#line 6 - chapternum(class)
#line 7 - chapterdate(class)
#line 19 - chapterlist(id)
#line 32 - infox(class)
#line 36 - entry-title(class)
from services import default_request, get_pagination_number
from bs4 import BeautifulSoup


def parse_data_from_chapter(chapter_link: str) -> dict:
    """parse all novels from category link"""
    response = default_request(chapter_link)
    if response.status_code == 200:
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        chapter_content = soup.find('div', class_='chapter-content')
        number = get_pagination_number(chapter_link)
        if not chapter_content:
            return {}
        chapter_content_list = chapter_content.find_all('p')
        return {'chapter_id': number, 'data': [p.text for p in chapter_content_list]}
    else:
        print('Error executing the GET request:', response.status_code)
        return {}
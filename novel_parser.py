from services import default_request, get_pagination_number
from bs4 import BeautifulSoup


def generate_chapters_link_list(novel_link: str) -> dict:
    """parse basic data and generate list of links"""
    response = default_request(novel_link)
    if response.status_code == 200:
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        name = soup.find('h1', class_='novel-title').text
        number_of_chapter = soup.find('div', class_='header-stats').find('strong').text
        chapter_links = [f"{novel_link[:-5]}_{num}.html" for num in range(1, int(number_of_chapter))]
        return {"name": name, "chapters": chapter_links}
    else:
        print('Error executing the GET request:', response.status_code)
        return {}

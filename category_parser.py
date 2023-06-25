from services import default_request, get_pagination_number
from bs4 import BeautifulSoup


def parse_novels_from_category(category_link: str) -> list:
    """parse all novels from category link"""
    response = default_request(category_link)
    if response.status_code == 200:
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        articles = soup.find('article', id='explore')
        if not articles:
            return []
        article_list = articles.find('ul', class_='novel-list')
        final_list = article_list.find_all('li', class_='novel-item')
        links_list = [f"https://www.readwn.com{link.find('a')['href']}" for link in final_list]
        return links_list
    else:
        print('Error executing the GET request:', response.status_code)
        return []


def create_category_links_list(link):
    response = default_request(link)
    if response.status_code == 200:
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        articles = soup.find('article', id='explore')
        pages = articles.find('ul', class_='pagination')
        last_page = pages.find_all('li')[-1].find('a')['href']
        first_num, last_num = get_pagination_number(link), get_pagination_number(last_page)
        links = [link.replace(str(first_num), str(i)) for i in range(int(first_num), int(last_num) +1)]
        return links

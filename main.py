from bs4 import BeautifulSoup
import os
import pathlib
import pathvalidate
import requests
from urllib.parse import urljoin


def download_books(url, books_id):
    for book_number in books_id:
        response = requests.get(f'{url}b{book_number}/',
                                allow_redirects=True,
                                timeout=3)

        try:
            check_for_redirect(response)
            response.raise_for_status()
        except requests.HTTPError:
            continue

        title, author, image_url = get_book_info(response)

        try:
            download_txt(url, book_number, title)
            download_image(image_url)
        except requests.HTTPError:
            continue

def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()
 

def get_book_info(response):
    soup = BeautifulSoup(response.text, 'lxml')
    info = soup.find('body').find('h1').text
    title, author = info.split('::')
    
    image = soup.find('div', class_='bookimage').find('img')['src']
    image_url = urljoin(url, image)

    return title, author, image_url


def download_txt(url, book_number, title, folder='books/'):
    filename = f'{book_number}.{title}'
    filepath = os.path.join(folder, filename.strip() + '.txt')
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    params = {'id': book_number}
    response = requests.get(f'{url}txt.php',
                            params=params,
                            allow_redirects=True,
                            timeout=3)
    response.raise_for_status()
    
    filename = pathvalidate.sanitize_filename(filename)

    with open(filepath, 'wb') as file:
        file.write(response.content)
    
    return filepath
    

def download_image(image_url, folder='images/'):
    filename = os.path.basename(image_url)
    filepath = os.path.join(folder, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    response = requests.get(image_url)

    with open(filepath, 'wb') as file:
        file.write(response.content)
    
    return filepath


if __name__ == '__main__':
    url = 'https://tululu.org/'
    book_ids = range(1, 11)
    download_books(url, book_ids)
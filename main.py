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

        book_info = parse_book_page(BeautifulSoup(response.text, 'lxml'))

        try:
            download_txt(url, book_number, book_info['title'])
            download_image(book_info['image_url'])
        except requests.HTTPError:
            continue


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def parse_book_page(html):
    info = html.find('body').find('h1').text

    title, author = info.split('::')

    image = html.find('div', class_='bookimage').find('img')['src']
    image_url = urljoin(url, image)

    raw_comments = html.find_all('div', class_='texts')
    comments = [comment.find(
        'span', class_='black').text for comment in raw_comments]

    raw_genres = html.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in raw_genres]

    return {'title': title,
            'author': author,
            'image_url': image_url,
            'comments': comments,
            'genres': genres}


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
    books_ids = range(1, 11)
    download_books(url, books_ids)

from bs4 import BeautifulSoup
import os
import pathlib
import pathvalidate
import requests


def download_books(url, books_id):
    for book_number in books_id:
        response = requests.get(f'{url}{book_number}/',
                                allow_redirects=True,
                                timeout=3)

        try:
            check_for_redirect(response)
            response.raise_for_status()
        except requests.HTTPError:
            continue

        title, author = get_book_info(response)

        try:
            download_txt(book_number, f'{book_number}.{title}')
        except requests.HTTPError:
            continue

def check_for_redirect(response):
    if response.url != response.request.url or response.url == 'https://tululu.org/':
        raise requests.HTTPError()

        

def get_book_info(response):
    soup = BeautifulSoup(response.text, 'lxml')
    info = soup.find('body').find('h1').text
    title, author = info.split('::')
    return title, author


def download_txt(book_number, filename, folder='books/'):
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

    params = {'id': book_number}
    response = requests.get('https://tululu.org/txt.php',
                            params=params,
                            allow_redirects=True,
                            timeout=3)
    check_for_redirect(response)
    response.raise_for_status()
    
    filename = pathvalidate.sanitize_filename(filename)

    filepath = os.path.join(folder, filename.strip() + '.txt')
    with open(filepath, 'wb') as file:
        file.write(response.content)
    
    return filepath
    


if __name__ == '__main__':
    url = 'https://tululu.org/b'
    book_id = range(1, 11)

    download_books(url, book_id)
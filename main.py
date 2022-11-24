import requests
import pathlib

def download_book(folderpath, url):
    pathlib.Path(folderpath).mkdir(parents=True, exist_ok=True) 

    for book_number in range(1, 11):
        params = {'id': book_number}
        response = requests.get(url, params=params)
        response.raise_for_status()

        with open(f'{folderpath}/id{book_number}', 'wb') as file:
            file.write(response.content)

if __name__ == '__main__':
    url = 'https://tululu.org/txt.php'
    folderpath = 'books'
    download_book(folderpath, url)

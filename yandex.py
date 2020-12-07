import requests
from http.client import responses

ya_token = ''

class YaUploader:
    def __init__(self, token: str):
        self.TOKEN = {'Authorization': 'OAuth ' + token}
        self.HOST_API = 'https://cloud-api.yandex.net:443'
        self.UPLOAD_SCHEME = '/v1/disk/resources/upload'
        self.LIST_SCHEME = '/v1/disk/resources/files'
        self.USER_AGENT = {"User-Agent": "Godexd"}
        self.HEADERS = {**self.USER_AGENT, **self.TOKEN}

    def __do_request(self, method='get', url=None, params=None, headers=None, files=None):
        if headers is None:
            headers = self.HEADERS
        if params is None:
            params = {}
        if url is None:
            url = self.LIST_SCHEME
        if method == 'get':
            return requests.get(url, params=params, headers=headers)
        if method == 'put':
            return requests.put(url, params=params, headers=headers, files=files)
        if method == 'post':
            return requests.post(url, params=params, headers=headers)
        return 'method not defined'

    def upload(self, file_path: str):
        upload_link = self.__do_request('get', self.HOST_API + self.UPLOAD_SCHEME, params={'path': file_path})
        files = {'file': open(file_path, 'rb')}
        request = self.__do_request('put', upload_link.json()['href'], params={'path': file_path}, files=files)
        if not (200 <= request.status_code < 300):
            return f'\nError while uploading file. Error code: ' \
                   f'{request.status_code} ({responses[request.status_code]})'
        return f'\nFile uploaded. Code: {request.status_code} ({responses[request.status_code]})'

    def list_files(self, limit=20):
        result = []
        offset = 0
        try:
            while True:
                print('requesting ' + str(limit) + ' files with offset ' + str(offset) + '...')
                request = self.__do_request('get',
                                            self.HOST_API + self.LIST_SCHEME,
                                            params={'limit': limit, 'fields': 'path, size', 'offset': offset})
                if not (200 <= request.status_code < 300):
                    return [f'\nError while listing directories. Error code: '
                            f'{request.status_code} ({responses[request.status_code]})']
                items = request.json()['items']
                if len(items) < 1:
                    break
                result += [f'\n- {x["path"].lstrip("disk:/")} ({str(int(x["size"] / 1024))} kB)'
                           for x in request.json()['items']]
                if len(items) < limit:
                    break
                offset += limit
        except:
            pass
        return result


while ya_token == '':
    ya_token = input('Please enter your Yandex OAuth token: ')
print('File uploading, please wait...')

uploader = YaUploader(ya_token)
print('\nFiles in Yandex disk:')
print(*uploader.list_files(5))
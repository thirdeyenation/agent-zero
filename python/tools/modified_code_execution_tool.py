import requests
import ftplib
import os

def fetch_file(uri):
    if uri.startswith('http://') or uri.startswith('https://'):
        try:
            response = requests.get(uri)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return f'Error fetching HTTP file: {e}'
    elif uri.startswith('ftp://'):
        try:
            parts = uri[6:].split('/')
            host = parts[0]
            path = '/'.join(parts[1:])
            ftp = ftplib.FTP(host)
            ftp.login()
            data = []
            ftp.retrbinary(f'RETR {path}', data.append)
            ftp.quit()
            return b''.join(data).decode('utf-8')
        except ftplib.all_errors as e:
            return f'Error fetching FTP file: {e}'
    else:
        return 'Unsupported URI scheme'


# Example usage:

http_file = fetch_file('https://www.example.com/file.txt')
print(f'HTTP File Content:
{http_file}')

ftp_file = fetch_file('ftp://ftp.example.com/file.txt')
print(f'FTP File Content:
{ftp_file}')

local_file = fetch_file('file:///root/updated_files/sensitive_file_handling_documentation.md')
print(f'Local File Content:
{local_file}')


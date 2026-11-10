"""구글 시트 API 공통 도우미.
토큰: 환경변수 GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / GOOGLE_REFRESH_TOKEN 로 자동 발급.
(클라우드 기본 환경에는 저장돼 있음. 노트북에서 직접 돌릴 땐 같은 값을 환경변수로 넣어야 함)
"""
import json, os, urllib.request, urllib.parse

ID = '1Sr8ut3Vtw2lleVVxAPgarrVijcXrJok-WtiKSz6RDLY'  # 26년 11월 결산 (기본값)

def _token():
    body = urllib.parse.urlencode({
        'client_id': os.environ['GOOGLE_CLIENT_ID'],
        'client_secret': os.environ['GOOGLE_CLIENT_SECRET'],
        'refresh_token': os.environ['GOOGLE_REFRESH_TOKEN'],
        'grant_type': 'refresh_token'}).encode()
    return json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token', body))['access_token']

TOK = _token()

def req(url, body=None, method=None):
    r = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                               method=method or ('POST' if body is not None else 'GET'),
                               headers={'Authorization': 'Bearer ' + TOK, 'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(r))

def get(ranges, render='FORMATTED_VALUE', sid=ID):
    q = urllib.parse.urlencode([('ranges', x) for x in ranges] + [('valueRenderOption', render)])
    return {v['range']: v.get('values', []) for v in
            req(f'https://sheets.googleapis.com/v4/spreadsheets/{sid}/values:batchGet?' + q)['valueRanges']}

def put(data, sid=ID):
    return req(f'https://sheets.googleapis.com/v4/spreadsheets/{sid}/values:batchUpdate',
               {'valueInputOption': 'USER_ENTERED', 'data': [{'range': r, 'values': v} for r, v in data]})

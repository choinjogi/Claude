import sys,json; sys.path.insert(0,'.'); from gs import *
D=json.load(open('master_data.json'))
tabs={
 '안내':None,
 '직원':D['staff'],
 '계약조건':D['con'],
 '스케줄':[["날짜","직원번호","이름(자동)","코드","확정 시각","비고"]],
 '근태':[["근태번호","근무 날짜","직원번호","이름(자동)","예외 출근","퇴근","근무 유형","대타 대상(직원번호)","특이사항","제출 시각","출처","상태"]],
 '매출':[["날짜","매출","메모"]],
 '변경이력':[["시각","누가","표","대상","항목","전","후","사유"]],
 '코드표':None,
}
codes=[["분류","코드","뜻"],
 ["스케줄 코드","O","근무 (저녁 18~22시)"],["스케줄 코드","오전","주말 오전 근무 (12~15시)"],["스케줄 코드","오전+오후","주말 오전+저녁"],
 ["스케줄 코드","X","휴무/불가"],["스케줄 코드","연차","연차(유급)"],["스케줄 코드","무급","무급 휴무"],["스케줄 코드","미배정","배정 안 됨"],
 ["구분","정직원","월급제"],["구분","알바","시급제"],
 ["그룹","정","스케줄 정 그룹(고정 근무)"],["그룹","알","스케줄 알바 그룹"],
 ["급여형태","월급",""],["급여형태","시급",""],
 ["주휴수당","지급","주 15시간 이상이면 지급 (주차=달력 1~7일 단위)"],["주휴수당","없음","계약상 주휴 없음"],["주휴수당","해당없음","월급제"],
 ["상태(직원)","재직",""],["상태(직원)","퇴사",""],
 ["근무 유형","정상",""],["근무 유형","대타","다른 사람 대신"],["근무 유형","추가","스케줄 외 추가 근무"],
 ["출처","폼","퇴근 폼 제출"],["출처","수기","사장님이 직접 입력"],["출처","Claude","Claude가 입력"],
 ["상태(근태)","정상",""],["상태(근태)","중복제외","같은 날 중복 제출로 제외"],["상태(근태)","삭제","잘못 제출"]]
guide=[["산성식육점 마스터DB"],[""],
 ["이 파일은 매달 복사하지 않고 계속 쌓는 '원본 데이터' 파일입니다. (앱 전환의 바탕)"],
 ["· 한 줄 = 한 건. 사람은 이름 대신 직원번호(S001…)로 연결합니다."],
 ["· 직원: 사람 1명당 1줄. 계약조건: 급여·출근·주휴 조건을 기간별로 1줄 (조건이 바뀌면 새 줄 추가, 이전 줄 '적용 종료' 입력)."],
 ["· 스케줄/근태/매출/변경이력: 2-2단계에서 과거 데이터를 옮기고, 2-3단계부터 자동으로 쌓입니다."],
 ["· 코드표: 각 칸에 쓰는 값의 뜻."],
 ["· 주민번호는 이 파일에 넣지 않습니다 (→ 인사카드(비공개))."],
 ["· 현재 월 결산 파일·스케줄 파일은 그대로 쓰고 있으며, 이 파일은 아직 '참고용 사본' 단계입니다."],
 [""],["만든 날: 2026-11-10 / 계약조건 시작일 중 '월 파일 기준'이라 적힌 것은 그 달 결산 파일에 처음 나온 달이라 정확한 날짜는 아닙니다."]]
tabs['안내']=guide; tabs['코드표']=codes
props=[{'properties':{'title':t,'gridProperties':{'rowCount':(2000 if t in('스케줄','근태') else 200),'columnCount':max(len(v[0]) for v in [tabs[t]]) if t!='안내' else 2,'frozenRowCount':0 if t=='안내' else 1}}} for t in tabs]
ss=req('https://sheets.googleapis.com/v4/spreadsheets',{'properties':{'title':'산성식육점 마스터DB','locale':'ko_KR','timeZone':'Asia/Seoul'},'sheets':props})
NID=ss['spreadsheetId']; open('master_id','w').write(NID)
sh={s['properties']['title']:s['properties']['sheetId'] for s in ss['sheets']}
reqs=[]
TEXT=lambda t,c0,c1:{'repeatCell':{'range':{'sheetId':sh[t],'startRowIndex':1,'startColumnIndex':c0,'endColumnIndex':c1},'cell':{'userEnteredFormat':{'numberFormat':{'type':'TEXT'}}},'fields':'userEnteredFormat.numberFormat'}}
NUM=lambda t,c0,c1,p:{'repeatCell':{'range':{'sheetId':sh[t],'startRowIndex':1,'startColumnIndex':c0,'endColumnIndex':c1},'cell':{'userEnteredFormat':{'numberFormat':{'type':'NUMBER' if 'yyyy' not in p and 'hh' not in p else ('DATE' if 'yyyy' in p and 'hh' not in p else ('TIME' if 'yyyy' not in p else 'DATE_TIME')),'pattern':p}}},'fields':'userEnteredFormat.numberFormat'}}
reqs+= [TEXT('직원',9,14), TEXT('직원',7,8), NUM('직원',6,7,'yyyy-mm-dd'), NUM('직원',8,9,'yyyy-mm-dd'),
        NUM('계약조건',3,5,'yyyy-mm-dd'), NUM('계약조건',6,7,'#,##0'), NUM('계약조건',7,8,'hh:mm'),
        NUM('스케줄',0,1,'yyyy-mm-dd'), NUM('스케줄',4,5,'yyyy-mm-dd hh:mm'),
        NUM('근태',1,2,'yyyy-mm-dd'), NUM('근태',4,6,'hh:mm'), NUM('근태',9,10,'yyyy-mm-dd hh:mm:ss'),
        NUM('매출',0,1,'yyyy-mm-dd'), NUM('매출',1,2,'#,##0'), NUM('변경이력',0,1,'yyyy-mm-dd hh:mm')]
for t in tabs:
    if t=='안내': continue
    reqs.append({'repeatCell':{'range':{'sheetId':sh[t],'startRowIndex':0,'endRowIndex':1},'cell':{'userEnteredFormat':{'textFormat':{'bold':True},'backgroundColor':{'red':0.88,'green':0.92,'blue':0.98}}},'fields':'userEnteredFormat(textFormat,backgroundColor)'}})
reqs.append({'repeatCell':{'range':{'sheetId':sh['안내'],'startRowIndex':0,'endRowIndex':1},'cell':{'userEnteredFormat':{'textFormat':{'bold':True,'fontSize':14}}},'fields':'userEnteredFormat.textFormat'}})
def dv(t,col,vals):
    return {'setDataValidation':{'range':{'sheetId':sh[t],'startRowIndex':1,'startColumnIndex':col,'endColumnIndex':col+1},'rule':{'condition':{'type':'ONE_OF_LIST','values':[{'userEnteredValue':v} for v in vals]},'showCustomUi':True,'strict':False}}}
reqs+=[dv('직원',3,['정직원','알바']),dv('직원',4,['정','알']),dv('직원',5,['재직','퇴사']),
       dv('계약조건',5,['월급','시급']),dv('계약조건',8,['지급','없음','해당없음']),
       dv('스케줄',3,['O','오전','오전+오후','X','연차','무급','미배정']),
       dv('근태',6,['정상','대타','추가']),dv('근태',10,['폼','수기','Claude']),dv('근태',11,['정상','중복제외','삭제'])]
req(f'https://sheets.googleapis.com/v4/spreadsheets/{NID}:batchUpdate',{'requests':reqs})
NM="IF({c}2:{c}=\"\",\"\",IFERROR(VLOOKUP({c}2:{c},'직원'!$A:$B,2,FALSE),\"❓없는 번호\"))"
data=[]
for t,v in tabs.items():
    data.append({'range':f"'{t}'!A1",'values':v})
put_raw=lambda d: req(f'https://sheets.googleapis.com/v4/spreadsheets/{NID}/values:batchUpdate',{'valueInputOption':'USER_ENTERED','data':d})
# text-ish columns first as RAW to keep exact strings for 계좌 etc
req(f'https://sheets.googleapis.com/v4/spreadsheets/{NID}/values:batchUpdate',{'valueInputOption':'RAW','data':[d for d in data if d['range'].startswith("'안내'") or d['range'].startswith("'코드표'")]})
put_raw([d for d in data if not (d['range'].startswith("'안내'") or d['range'].startswith("'코드표'"))])
put_raw([{'range':"'계약조건'!C1",'values':[["={\"이름(자동)\";ARRAYFORMULA("+NM.format(c='B')+")}"]]},
         {'range':"'스케줄'!C1",'values':[["={\"이름(자동)\";ARRAYFORMULA("+NM.format(c='B')+")}"]]},
         {'range':"'근태'!D1",'values':[["={\"이름(자동)\";ARRAYFORMULA("+NM.format(c='C')+")}"]]}])
for t in tabs:
    req(f'https://sheets.googleapis.com/v4/spreadsheets/{NID}:batchUpdate',{'requests':[{'autoResizeDimensions':{'dimensions':{'sheetId':sh[t],'dimension':'COLUMNS','startIndex':0,'endIndex':15}}}]})
print(NID)

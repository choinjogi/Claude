import sys,json,calendar,datetime; sys.path.insert(0,'.'); from gs import *
M=json.load(open('months.json'))
# --- roster per month (active section only for Oct/Nov) ---
hist={}
for m,sid in M.items():
    st='직원DB' if m=='2026-03' else '직원명부'
    v=list(get([f"'{st}'!A1:F80"],sid=sid).values())[0]; rows={}
    for r in v[1:]:
        r=(r+['']*6)[:6]
        if r[0]=='퇴사자': break
        if r[0] and r[1] and r[3]: rows[r[0]]=('정직원' if r[1]=='직원' else r[1], r[2].zfill(5) if r[2] else '', int(r[3].replace('₩','').replace(',','').replace(' ','')))
    hist[m]=rows
cur=list(get(["'직원명부'!A1:S60"]).values())[0]
hdr=cur[0]; now={}; order11=[]; sec='재직'
for r in cur[1:]:
    r=(r+['']*19)[:19]
    if r[0]=='퇴사자': sec='퇴사'; continue
    if not r[0]: continue
    now[r[0]]=dict(구분='정직원' if r[1]=='직원' else r[1],출근=r[2],금액=r[3],퇴사일=r[4],은행=r[5],계좌=r[6],이메일=r[7].strip(),표시=r[11],그룹=r[12],고정휴무=r[13],최소=r[14],우선=r[15],비고=r[16],주휴=r[18],상태=sec)
    order11.append(r[0])
first={}
for m in M:
    for n in hist[m]: first.setdefault(n,m)
names=sorted(order11,key=lambda n:(first.get(n,'9999'),order11.index(n)))
sid_of={n:f"S{i+1:03d}" for i,n in enumerate(names)}
def ymd(s):
    s=s.replace(' ','').strip('.')
    try: y,mo,d=[int(x) for x in s.split('.')]; return f"{y:04d}-{mo:02d}-{d:02d}"
    except Exception: return ''
staff=[["직원번호","이름","표시이름","구분","그룹","상태","입사일","명부 첫 등장(월)","퇴사일","은행","계좌번호","이메일","연락처","카카오ID","메모"]]
for n in names:
    x=now[n]; memo=[]
    if x['비고']: memo.append(x['비고'])
    if x['상태']=='퇴사' and not ymd(x['퇴사일']): memo.append('퇴사일 미상')
    if first.get(n)=='2026-01': memo.append('1월 이전부터 근무 가능')
    staff.append([sid_of[n],n,x['표시'],x['구분'],x['그룹'] or ('알' if x['구분']=='알바' else ''),x['상태'],'',first.get(n,''),ymd(x['퇴사일']),x['은행'],x['계좌'],x['이메일'],'','',' / '.join(memo)])
# --- contracts ---
mons=list(M)
def mstart(m): return m+'-01'
def mend(m): y,mo=map(int,m.split('-')); return f"{m}-{calendar.monthrange(y,mo)[1]:02d}"
def dminus(d): return (datetime.date.fromisoformat(d)-datetime.timedelta(days=1)).isoformat()
con=[["조건번호","직원번호","이름(자동)","적용 시작","적용 종료","급여형태","금액","기본출근","주휴수당","고정휴무","최소출근일","우선배정","메모"]]
rows=[]
for n in names:
    segs=[]
    for m in mons:
        c=hist[m].get(n)
        if not c: continue
        if segs and segs[-1]['v']==c: segs[-1]['last']=m
        else: segs.append({'v':c,'first':m,'last':m,'start':mstart(m)})
    if n=='김세희':
        # 10/12부터 월급제 (근무기록부 반직원 처리), 11월 명부 정직원
        segs=[s for s in segs]
        for s in segs:
            if s['v'][0]=='알바': s['last']='2026-10'; s['endfix']='2026-10-11'
            if s['v'][0]=='정직원': s['start']='2026-10-12'; s['memo']='10/12~10/31은 반직원(일할 계산), 11월부터 정직원'
    for i,s in enumerate(segs):
        if i+1<len(segs): end=dminus(segs[i+1]['start'])
        elif now[n]['상태']=='퇴사': end=ymd(now[n]['퇴사일']) or mend(s['last'])
        else: end=''
        end=s.get('endfix',end)
        g,ch,amt=s['v']; kind='월급' if g=='정직원' else '시급'
        ju='해당없음' if kind=='월급' else ('없음' if now[n]['주휴']=='없음' else '지급')
        memo=[s.get('memo','')]
        if s['first']=='2026-01' and i==0: memo.append('시작일=1월 파일 기준(그 전부터일 수 있음)')
        elif i>0 or s['start'].endswith('-01'): memo.append('시작일=월 파일 기준(정확한 날짜 확인 필요)' if not s.get('memo') else '')
        if now[n]['상태']=='퇴사' and not ymd(now[n]['퇴사일']) and i+1==len(segs): memo.append('종료일=마지막 등장 월말(퇴사일 미상)')
        last=(i+1==len(segs) and now[n]['상태']=='재직')
        rows.append([sid_of[n],s['start'],end,kind,amt,ch,ju,now[n]['고정휴무'] if last else '',now[n]['최소'] if last else '',now[n]['우선'] if last else '',' / '.join(x for x in memo if x)])
for i,r in enumerate(rows): con.append([f"C{i+1:03d}",r[0],'']+r[1:])
json.dump({'staff':staff,'con':con,'sid_of':sid_of},open('master_data.json','w'),ensure_ascii=False)
print(len(staff)-1,'staff',len(con)-1,'contracts')
for r in con[1:]: print(r[:2],r[3:9],r[12][:50])

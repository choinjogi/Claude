import sys,json; sys.path.insert(0,'.'); from gs import *
def cn(s):
    n=0
    for ch in s: n=n*26+ord(ch)-64
    return n
def cl(n):
    s=''
    while n: n,r=divmod(n-1,26); s=chr(65+r)+s
    return s
EX="COUNTIFS('직원명부'!$A:$A,{name},'직원명부'!$S:$S,\"없음\")>0"
LIST="IFERROR(FILTER('직원명부'!$A$2:$A,'직원명부'!$S$2:$S=\"없음\"),\"\")"
data=[]
data.append(("'직원명부'!S1",[["주휴수당"]]))
data.append(("'직원명부'!S7",[["없음"]]))
# 월말근무내역 주휴 rows
for fc in ['O','R','U','X','AA','AD','AG','AJ','AM','AS','AV']:
    n=cn(fc); nm=cl(n-1)+'$1'; h=cl(n+1)
    for k in range(5):
        r=36+k
        f=(f"=ARRAYFORMULA(IF({EX.format(name=nm)}, 0, LET(주분, SUMPRODUCT((INT((IFERROR(DAY($A$3:$A$33),99)-1)/7)={k})*IF(ISNUMBER({h}$3:{h}$33),ROUND({h}$3:{h}$33*60),0)), "
           f"IF(주분 >= 900, (MIN(주분, 2400) / 60) * {fc}$35 * 0.2, 0))))")
        data.append((f"'월말근무내역'!{fc}{r}",[[f]]))
# 요약데이터 E
data.append(("'요약데이터'!E3:E80",[[f"=IF($B{r}=\"\", \"\", IF({EX.format(name='$B'+str(r))}, 0, IF($C{r}>=15, (MIN($C{r}, 40)/5) * $D{r}, 0)))"] for r in range(3,81)]))
F=get(["'요약데이터'!J3:J33","'요약데이터'!T12","'요약데이터'!T21"],'FORMULA')
J=[row[0] for row in F["'요약데이터'!J3:J33"]]
newJ=[]
for f in J:
    assert 'b<>"리티카"' in f
    f=f.replace("LET(b, ","LET(ex_, "+LIST+", b, ",1).replace('b<>"리티카"','ISNA(MATCH(b, ex_, 0))')
    newJ.append([f])
data.append(("'요약데이터'!J3:J33",newJ))
t12=F["'요약데이터'!T12"][0][0]; assert t12.count('nm<>"리티카"')==1
t12=t12.replace("LET(y, ","LET(ex_, "+LIST+", y, ",1).replace('nm<>"리티카"','ISNA(MATCH(nm, ex_, 0))')
data.append(("'요약데이터'!T12",[[t12]]))
t21=F["'요약데이터'!T21"][0][0]; assert t21.count('nm="리티카"')==2
t21=t21.replace("LET(y, ","LET(ex_, "+LIST+", y, ",1).replace('nm="리티카"','ISNUMBER(MATCH(nm, ex_, 0))')
data.append(("'요약데이터'!T21",[[t21]]))
# 대시보드
data.append(("'대시보드'!C3",[["=SUM(ARRAYFORMULA(IF(('월말근무내역'!$A$42:$AV$42=\"주휴포함총급여\")*(IFERROR(VLOOKUP('월말근무내역'!$A$1:$AV$1,'직원명부'!$A:$B,2,FALSE),\"\")=\"알바\")*ISNUMBER('월말근무내역'!$B$42:$AW$42),'월말근무내역'!$B$42:$AW$42,0)))"]]))
data.append(("'대시보드'!C5",[["='요약데이터'!U7"]]))
data.append(("'대시보드'!C7",[["='요약데이터'!U8"]]))
# 월말결제
AL="(IFERROR(VLOOKUP($B$3:$B$14,'직원명부'!$A:$B,2,FALSE),\"\")=\"알바\")"
data.append(("'월말결제'!C16",[[f"=SUM(ARRAYFORMULA(IF(($B$3:$B$14<>\"\")*{AL}*ISNUMBER($C$3:$C$14),$C$3:$C$14,0)))"]]))
data.append(("'월말결제'!C17",[[f"=SUM(ARRAYFORMULA(IF(($B$3:$B$14<>\"\")*NOT{AL}*ISNUMBER($C$3:$C$14),$C$3:$C$14,0)))"]]))
data.append(("'월말결제'!B17",[[f"=\"정직원 (\"&IFERROR(TEXTJOIN(\", \",TRUE,FILTER($B$3:$B$14,$B$3:$B$14<>\"\",NOT{AL})),\"없음\")&\")\""]]))
# 근무기록부
data.append(("'근무기록부'!G2",[["=ARRAYFORMULA(IF($B2:B=\"\", \"\", VLOOKUP($B2:B, '직원명부'!$A:$D, 2, FALSE)))"]]))
data.append(("'근무기록부'!L2",[["=ARRAYFORMULA(IF($B2:B=\"\", \"\", IF($J2:J<>\"\", $J2:J, IF($E2:E<>\"\", $E2:E, $H2:H))))"]]))
json.dump(data,open('newformulas.json','w'),ensure_ascii=False,indent=0)
if len(sys.argv)>1 and sys.argv[1]=='go':
    r=put(data); print('updated cells',r.get('totalUpdatedCells'))
else: print(len(data),'ranges prepared'); print(data[2][1][0][0]); print(newJ[0][0][:300])

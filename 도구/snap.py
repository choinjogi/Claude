import sys,json; sys.path.insert(0,'.'); from gs import *
R=["'대시보드'!A1:F16","'월말결제'!A1:O18","'요약데이터'!A1:Z48","'월말근무내역'!A34:AW42","'근무기록부'!A1:Q120","'직원명부'!R1:S20"]
json.dump(get(R),open(sys.argv[1],'w'),ensure_ascii=False)
F=get(["'월말근무내역'!A36:AW40","'요약데이터'!E3:E80","'요약데이터'!J3:J33","'요약데이터'!T12","'요약데이터'!T21","'대시보드'!C3:C7","'월말결제'!B16:C18","'근무기록부'!G2","'근무기록부'!L2"],'FORMULA')
json.dump(F,open(sys.argv[1]+'.formulas','w'),ensure_ascii=False)
print('ok')

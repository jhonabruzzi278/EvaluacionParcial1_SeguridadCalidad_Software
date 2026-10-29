import json,subprocess,re,sys,tempfile,pathlib
SCR=pathlib.Path(tempfile.gettempdir())/'atlas_informe'
pdf=sys.argv[1]
heads=json.load(open(SCR/'headings.json')); tables=json.load(open(SCR/'tables.json'))
n=int(re.search(r'Pages:\s+(\d+)',subprocess.run(['pdfinfo',pdf],capture_output=True,text=True).stdout).group(1))
pages={}
for pg in range(4,n+1):
    t=subprocess.run(['pdftotext','-f',str(pg),'-l',str(pg),'-layout',pdf,'-'],capture_output=True,text=True).stdout
    lines=[l.strip() for l in t.splitlines()]
    for h in heads:
        if h not in pages and h in lines: pages[h]=pg
    for i in range(1,len(tables)+1):
        k=f'T{i}'
        if k not in pages and any(l.startswith(f'Tabla {i}. ') for l in lines): pages[k]=pg
miss=[h for h in heads if h not in pages]+[f'T{i}' for i in range(1,len(tables)+1) if f'T{i}' not in pages]
print('missing',miss,'pages',n)
json.dump(pages,open(SCR/'pages.json','w'),ensure_ascii=False)

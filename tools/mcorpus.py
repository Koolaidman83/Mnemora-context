#!/usr/bin/env python3
import argparse,json,re,subprocess,sys,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
BASE='https://mnemora-context.netlify.app/'
def git(*a): subprocess.run(['git','--no-pager','-C',str(R),*a],check=True)
LEGACY_IDS = {'index': 'knowledge/README.md', 'nursing.study': 'knowledge/nursing/study-architecture.md', 'nursing.ob_peds_ontology': 'knowledge/nursing/ob-peds-nclex-ontology.md', 'nursing.assessment': 'knowledge/nursing/assessment-patterns.md', 'ems.workflow': 'knowledge/ems/workflow-architecture.md', 'clinicals.competencies': 'knowledge/clinicals/competency-mapping.md', 'mathematics.learning': 'knowledge/mathematics/learning-architecture.md', 'engineering.learning': 'knowledge/engineering/learning-architecture.md', 'interoperability.provenance': 'knowledge/interoperability/source-provenance.md', 'llms': 'llms.txt', 'llms.full': 'llms-full.txt'}

def registry(write=False):
 import hashlib
 from urllib.parse import quote
 p=R/'knowledge-index.json'
 data=json.loads(p.read_text())
 old={d['path']:d for d in data['documents']}
 docs=[]
 paths=set()
 aliases=LEGACY_IDS
 candidates=list((R/'knowledge').rglob('*'))
 candidates += [R/'llms.txt', R/'llms-full.txt']
 for f in sorted(candidates):
  if f.is_symlink():
   raise ValueError(f'Symlink forbidden: {f}')
  if not f.is_file():
   continue
  if f.suffix.lower() not in ('.md','.txt','.json'):
   continue
  rel=f.relative_to(R).as_posix()
  if not re.fullmatch(r'[A-Za-z0-9_./ -]+',rel):
   raise ValueError(f'Unsupported path: {rel}')
  content=f.read_text(encoding='utf-8')
  if f.suffix.lower()=='.json':
   json.loads(content)
  if re.search(r'-----BEGIN [A-Z ]*PRIVATE KEY-----|\\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}|\\bghp_[A-Za-z0-9]{20,}',content):
   raise ValueError(f'Possible credential: {rel}')
  d=dict(old.get(rel,{}))
  legacy=next((k for k,v in aliases.items() if v==rel),None)
  stable='doc.'+hashlib.sha256(rel.encode()).hexdigest()[:24]
  d['id']=legacy or d.get('id') or stable
  d['path']=rel
  d['title']=d.get('title') or f.stem.replace('-',' ').replace('_',' ').title()
  d['description']=d.get('description') or 'Public knowledge document'
  d['category']=str(Path(rel).parent)
  d['visibility']='public'
  d['url']=BASE+quote(rel)
  d['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
  docs.append(d)
  paths.add(rel)
 ids=[d['id'] for d in docs]
 if len(ids)!=len(set(ids)):
  raise ValueError('Duplicate document IDs')
 data['documents']=docs
 data['visibility']='public'
 if write:
  tmp=p.with_suffix('.tmp')
  tmp.write_text(json.dumps(data,indent=2)+'\n')
  tmp.replace(p)
 print(f'{len(docs)} documents discovered recursively.')
 print('Basic validation passed. Manual privacy review required.')

def main():
 p=argparse.ArgumentParser(); p.add_argument('command',choices=['add','validate','index','sync','publish','ai','status']); p.add_argument('source',nargs='?'); p.add_argument('--category',default='general'); a=p.parse_args()
 if a.command=='add':
  if not a.source: p.error('add requires a file')
  src=Path(a.source).expanduser(); cat=Path(a.category)
  if cat.is_absolute() or '..' in cat.parts or src.suffix.lower() not in ('.md','.txt','.json'): p.error('Invalid category or file type')
  dest=R/'knowledge'/cat/src.name
  if not dest.resolve().is_relative_to(R/'knowledge') or dest.exists(): p.error('Unsafe or existing destination')
  if input(f'Copy {src} to PUBLIC corpus {dest}? [y/N] ').lower()!='y': return
  dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dest); print('Imported locally; not published.')
 elif a.command=='validate': registry()
 elif a.command=='index': registry(True)
 elif a.command=='sync': git('pull','--ff-only','origin','editor-test')
 elif a.command=='status': git('status','--short','--branch')
 elif a.command=='ai': print((R/'AI-IMPORT.md').read_text())
 elif a.command=='publish':
  if subprocess.check_output(['git','-C',str(R),'branch','--show-current'],text=True).strip()!='editor-test': raise ValueError('Wrong branch')
  if subprocess.check_output(['git','-C',str(R),'diff','--cached','--name-only'],text=True).strip(): raise ValueError('Unstage existing changes first')
  registry(True); git('status','--short'); git('diff','--','knowledge','knowledge-index.json')
  if input('Reviewed ALL public files, including untracked files, for privacy and rights? Publish corpus? [y/N] ').lower()!='y': return
  git('add','--','knowledge','knowledge-index.json'); git('diff','--cached','--stat')
  if input('Commit and push these files? [y/N] ').lower()!='y': return
  git('commit','-m','Update public Mnemora corpus'); git('push','origin','editor-test')
if __name__=='__main__': main()

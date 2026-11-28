#!/usr/bin/env python3
import argparse,json,re,subprocess,sys,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
BASE='https://mnemora-context.netlify.app/'
def git(*a): subprocess.run(['git','-C',str(R),*a],check=True)
def registry(write=False):
 p=R/'knowledge-index.json'; data=json.loads(p.read_text()); docs=data['documents']; known={d['path'] for d in docs}
 for f in sorted((R/'knowledge').rglob('*')):
  if f.is_symlink(): raise ValueError(f'Symlink forbidden: {f}')
  if not f.is_file() or f.suffix.lower() not in ('.md','.txt','.json'): continue
  rel=f.relative_to(R).as_posix(); content=f.read_text(encoding='utf-8')
  if f.suffix=='.json': json.loads(content)
  if re.search(r'-----BEGIN [A-Z ]*PRIVATE KEY-----|\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}|\bghp_[A-Za-z0-9]{20,}',content): raise ValueError(f'Possible credential: {rel}')
  if rel not in known: docs.append(dict(title=f.stem.replace('-',' ').title(),path=rel,description='Public knowledge document',url=BASE+rel)); known.add(rel)
 for d in docs:
  f=(R/d['path']).resolve()
  if not f.is_relative_to(R) or not f.is_file(): raise ValueError('Invalid registry path: '+d['path'])
 if write: p.write_text(json.dumps(data,indent=2)+'\n')
 print(f'{len(docs)} registered documents; basic validation passed. Manual privacy review still required.')
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

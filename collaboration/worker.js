const s={type:'string',minLength:1,maxLength:16000}, id={type:'string',maxLength:100}, rev={type:'integer',minimum:0};
const specs={task_create:{instructions:s},task_list:{},task_get:{id},task_claim:{id,revision:rev},task_submit:{id,revision:rev,result:s},task_review:{id,revision:rev,review:s}};
const tools=Object.entries(specs).map(([name,properties])=>({name,description:name.replaceAll('_',' '),inputSchema:{type:'object',properties,required:Object.keys(properties),additionalProperties:false}}));
export default {async fetch(req,env){
 const json=(x,status=200)=>Response.json(x,{status});
 if(new URL(req.url).pathname!='/mcp')return json({error:'Not found'},404);
 const auth=req.headers.get('Authorization')||'';
 const actors=[['chatgpt',env.CHATGPT_TOKEN],['claude',env.CLAUDE_TOKEN],['owner',env.OWNER_TOKEN]];
 const matches=actors.filter(([_,token])=>typeof token==='string'&&token.length>=32&&auth==='Bearer '+token);
 if(matches.length!==1)return json({error:'Unauthorized'},401);
 const actor=matches[0][0];
 if(req.method!=='POST')return json({error:'Method not allowed'},405);
 let m;try{const raw=await req.text();if(raw.length>100000)return json({error:'Too large'},413);m=JSON.parse(raw)}catch{return json({error:'Invalid JSON'},400)}
 const reply=result=>json({jsonrpc:'2.0',id:m.id,result});
 const err=(code,message)=>json({jsonrpc:'2.0',id:m.id??null,error:{code,message}});
 if(m.jsonrpc!=='2.0')return err(-32600,'Invalid request');
 if(m.method==='initialize')return reply({protocolVersion:'2025-03-26',capabilities:{tools:{}},serverInfo:{name:'mnemora-collaboration',version:'0.1.0'}});
 if(m.method==='notifications/initialized')return new Response(null,{status:202});
 if(m.method==='ping')return reply({});
 if(m.method==='tools/list')return reply({tools});
 if(m.method!=='tools/call')return err(-32601,'Unknown method');
 const name=m.params?.name,a=m.params?.arguments||{};
 if(!Object.hasOwn(specs,name))return err(-32602,'Unknown tool');
 for(const [k,v] of Object.entries(specs[name])){if(v.type==='string'?(typeof a[k]!=='string'||!a[k].trim()||a[k].length>v.maxLength):(!Number.isSafeInteger(a[k])||a[k]<0))return err(-32602,'Invalid '+k)}
 const q=(sql,...args)=>env.DB.prepare(sql).bind(...args);
 const out=(value,isError=false)=>reply({content:[{type:'text',text:JSON.stringify(value)}],isError});
 try{
 if(name==='task_list')return out((await q('SELECT id,creator,claimant,status,revision,updated FROM tasks ORDER BY updated DESC LIMIT 100').all()).results);
 if(name==='task_get')return out(await q('SELECT * FROM tasks WHERE id=?',a.id).first());
 if(name==='task_create'){const key=crypto.randomUUID();await q('INSERT INTO tasks(id,instructions,creator) VALUES(?,?,?)',key,a.instructions,actor).run();return out({id:key,revision:0,status:'open'})}
 let r;
 if(name==='task_claim')r=await q("UPDATE tasks SET claimant=?,status='claimed',revision=revision+1,updated=CURRENT_TIMESTAMP WHERE id=? AND revision=? AND status='open' AND creator<>?",actor,a.id,a.revision,actor).run();
 if(name==='task_submit')r=await q("UPDATE tasks SET result=?,status='submitted',revision=revision+1,updated=CURRENT_TIMESTAMP WHERE id=? AND revision=? AND status='claimed' AND claimant=?",a.result,a.id,a.revision,actor).run();
 if(name==='task_review')r=await q("UPDATE tasks SET review=?,status='reviewed',revision=revision+1,updated=CURRENT_TIMESTAMP WHERE id=? AND revision=? AND status='submitted' AND creator=?",a.review,a.id,a.revision,actor).run();
 return r.meta.changes===1?out({id:a.id,revision:a.revision+1}):out({error:'Conflict or unauthorized transition'},true);
 }catch{return out({error:'Database unavailable or schema not initialized'},true)}
}};

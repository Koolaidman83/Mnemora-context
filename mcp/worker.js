// Mnemora Public Knowledge MCP v1.0
// Read-only MCP over Streamable HTTP, deployed as a Cloudflare Worker.
// No private memory, device controls, or arbitrary URL fetching.
const BASE = 'https://raw.githubusercontent.com/Koolaidman83/Mnemora-context/editor-test/';
const DOCUMENTS = Object.freeze({
  'index': 'knowledge/README.md',
  'nursing.study': 'knowledge/nursing/study-architecture.md',
  'nursing.ob_peds_ontology': 'knowledge/nursing/ob-peds-nclex-ontology.md',
  'nursing.assessment': 'knowledge/nursing/assessment-patterns.md',
  'ems.workflow': 'knowledge/ems/workflow-architecture.md',
  'clinicals.competencies': 'knowledge/clinicals/competency-mapping.md',
  'mathematics.learning': 'knowledge/mathematics/learning-architecture.md',
  'engineering.learning': 'knowledge/engineering/learning-architecture.md',
  'interoperability.provenance': 'knowledge/interoperability/source-provenance.md',
  'llms': 'llms.txt',
  'llms.full': 'llms-full.txt'
});
const TOOLS = [
  {name:'knowledge_list', description:'List public Mnemora knowledge documents and IDs.', inputSchema:{type:'object',properties:{},additionalProperties:false}},
  {name:'knowledge_get', description:'Read one allowlisted public Mnemora document by ID.', inputSchema:{type:'object',properties:{id:{type:'string',description:'ID from knowledge_list'}},required:['id'],additionalProperties:false}},
  {name:'knowledge_search', description:'Case-insensitive text search across public Mnemora documents. Returns matching excerpts and document IDs.', inputSchema:{type:'object',properties:{query:{type:'string',minLength:2,maxLength:120}},required:['query'],additionalProperties:false}}
];
const HEADERS = {'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','Access-Control-Allow-Origin':'*','Access-Control-Allow-Methods':'GET,POST,OPTIONS','Access-Control-Allow-Headers':'Content-Type,Accept,MCP-Protocol-Version,Mcp-Session-Id','Access-Control-Expose-Headers':'MCP-Protocol-Version'};
function json(data,status=200,extra={}) {return new Response(JSON.stringify(data),{status,headers:{...HEADERS,...extra}});}
function rpc(id,result) {return {jsonrpc:'2.0',id,result};}
function err(id,code,message) {return {jsonrpc:'2.0',id,error:{code,message}};}
async function read(id) {
  if (!Object.hasOwn(DOCUMENTS,id)) throw new Error('Unknown document ID');
  const response = await fetch(BASE+DOCUMENTS[id], {headers:{'Accept':'text/plain'},cf:{cacheTtl:60,cacheEverything:true}});
  if (!response.ok) throw new Error('Document unavailable ('+response.status+'): '+id);
  const content=await response.text();
  if (content.length>150000) throw new Error('Document exceeds size limit');
  return content;
}
async function toolCall(name,args) {
  if (name==='knowledge_list') return {content:[{type:'text',text:JSON.stringify(Object.entries(DOCUMENTS).map(([id,path])=>({id,path,url:BASE+path})),null,2)}]};
  if (name==='knowledge_get') {
    if (typeof args?.id!=='string'||!Object.hasOwn(DOCUMENTS,args.id)) return {isError:true,content:[{type:'text',text:'Unknown document ID. Call knowledge_list first.'}]};
    const content=await read(args.id);
    return {content:[{type:'text',text:'Source: '+BASE+DOCUMENTS[args.id]+'\n\n'+content}]};
  }
  if (name==='knowledge_search') {
    const q=typeof args?.query==='string'?args.query.trim().toLowerCase():'';
    if (q.length<2||q.length>120) return {isError:true,content:[{type:'text',text:'Query must be 2–120 characters.'}]};
    const hits=[];
    for (const id of Object.keys(DOCUMENTS)) {
      let content;
      try {content=await read(id);} catch(e) {continue;}
      const lower=content.toLowerCase();let pos=0,count=0;
      while ((pos=lower.indexOf(q,pos))!==-1 && count<3 && hits.length<24) {
        hits.push({id,url:BASE+DOCUMENTS[id],excerpt:content.slice(Math.max(0,pos-140),Math.min(content.length,pos+q.length+220))});
        pos+=q.length;count++;
      }
      if(hits.length>=24)break;
    }
    return {content:[{type:'text',text:JSON.stringify({query:args.query,matches:hits},null,2)}]};
  }
  return {isError:true,content:[{type:'text',text:'Unknown tool'}]};
}
export default {
  async fetch(request) {
    const url=new URL(request.url);
    if(request.method==='OPTIONS') return new Response(null,{status:204,headers:HEADERS});
    if(url.pathname==='/' && request.method==='GET') return json({service:'Mnemora Public Knowledge MCP',status:'online',mcp_endpoint:'/mcp',read_only:true,source:'public GitHub editor-test'});
    if(url.pathname!=='/mcp') return json({error:'Not found'},404);
    if(request.method==='GET') return new Response('SSE sessions are not used by this stateless MCP server.',{status:405,headers:{...HEADERS,'Allow':'POST, OPTIONS'}});
    if(request.method!=='POST') return json({error:'Method not allowed'},405);
    let msg;
    try {msg=await request.json();} catch {return json(err(null,-32700,'Invalid JSON'),400);}
    if(!msg || Array.isArray(msg) || msg.jsonrpc!=='2.0'||typeof msg.method!=='string') return json(err(msg?.id??null,-32600,'Invalid JSON-RPC request'),400);
    if(msg.id===undefined) return new Response(null,{status:202,headers:HEADERS});
    try {
      switch(msg.method) {
        case 'initialize': return json(rpc(msg.id,{protocolVersion:'2025-03-26',capabilities:{tools:{listChanged:false}},serverInfo:{name:'mnemora-public-knowledge',version:'1.0.0'}}),200,{'MCP-Protocol-Version':'2025-03-26'});
        case 'ping': return json(rpc(msg.id,{}));
        case 'tools/list': return json(rpc(msg.id,{tools:TOOLS}));
        case 'tools/call': {
          const name=msg.params?.name;
          if(!TOOLS.some(t=>t.name===name)) return json(err(msg.id,-32602,'Unknown tool'),400);
          return json(rpc(msg.id,await toolCall(name,msg.params?.arguments??{})));
        }
        default: return json(err(msg.id,-32601,'Method not found'),404);
      }
    } catch(e) {return json(rpc(msg.id,{isError:true,content:[{type:'text',text:'Request failed: '+String(e.message||e)}]}));}
  }
};

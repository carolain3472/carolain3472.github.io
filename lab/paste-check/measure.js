const {mask}=require('./mask.js'),M=require('./messages.json'),R={};let fp=[];
for(const m of M){const {out,key}=mask(m.text);const masked=Object.values(key);
 for(const e of m.entities){R[e.type]=R[e.type]||{n:0,ok:0};R[e.type].n++;if(!out.includes(e.text))R[e.type].ok++;}
 for(const v of masked)if(!m.entities.some(e=>e.text.includes(v.replace(/^.*?(\d)/,'$1'))||v.includes(e.text)))fp.push(v)}
console.log(JSON.stringify(R));console.log('false',fp);
const ex=M.slice(0,6).map(m=>[m.text,mask(m.text).out]);console.log(JSON.stringify(ex,null,1));require('fs').writeFileSync('results.json',JSON.stringify({recall:R,false_positives:fp,examples:ex},null,1))

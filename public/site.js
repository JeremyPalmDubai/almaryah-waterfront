'use strict';
// Official Tally embed loader; no test submissions or unverified attribution parameters.
if(document.querySelector('iframe[data-tally-src]')){
 var d=document,w='https://tally.so/widgets/embed.js',v=function(){
  if(typeof Tally!=='undefined')Tally.loadEmbeds();
  else d.querySelectorAll('iframe[data-tally-src]:not([src])').forEach(function(el){el.src=el.dataset.tallySrc;});
 };
 if(typeof Tally!=='undefined')v();
 else if(d.querySelector('script[src="'+w+'"]')==null){var s=d.createElement('script');s.src=w;s.onload=v;s.onerror=v;d.body.appendChild(s);}
}
const data=document.getElementById('calc-data');
if(data){
 const c=JSON.parse(data.textContent),p=c.payment;
 const fmt=(n,currency)=>currency+' '+new Intl.NumberFormat(c.locale,{maximumFractionDigits:0}).format(n);
 const calc=document.getElementById('calculator');
 calc.addEventListener('submit',event=>{
  event.preventDefault();const price=Number(document.getElementById('price').value),error=document.getElementById('calc-error');
  if(!Number.isSafeInteger(price)||price<=0||price>1000000000){error.textContent=c.error;return;}
  error.textContent='';
  const booking=Math.round(price*p.bookingPercent/100),each=Math.round(price*p.installmentPercent/100);
  const rows=[booking,...Array(p.constructionInstallments).fill(each)];rows.push(price-rows.reduce((a,b)=>a+b,0));
  const totalUsd=Math.round(price/Number(c.fx)),usd=rows.slice(0,-1).map(a=>Math.round(a/Number(c.fx)));usd.push(totalUsd-usd.reduce((a,b)=>a+b,0));
  const stages=[rows[0],rows.slice(1,-1).reduce((a,b)=>a+b,0),rows.at(-1)];const dollars=[usd[0],usd.slice(1,-1).reduce((a,b)=>a+b,0),usd.at(-1)];
  stages.forEach((n,i)=>{document.querySelector('[data-amount="'+i+'"]').textContent=fmt(n,'AED');document.querySelector('[data-usd="'+i+'"]').textContent=c.approx+' '+fmt(dollars[i],'USD');});
  rows.forEach((n,i)=>{document.querySelector('[data-row-aed="'+i+'"]').textContent=fmt(n,'AED');document.querySelector('[data-row-usd="'+i+'"]').textContent=fmt(usd[i],'USD');});
  document.getElementById('total-aed').textContent=fmt(price,'AED');document.getElementById('total-usd').textContent=fmt(totalUsd,'USD');
 });
}
// Reveal the local brochure only after the official submission event from this iframe.
// No answers are logged, stored or forwarded by this handler.
const brochureResult=document.getElementById('brochure-success');
const enquiryFrame=document.querySelector('iframe[data-form-id]');
if(brochureResult&&enquiryFrame){
 window.addEventListener('message',event=>{
  if(event.origin!=='https://tally.so'||event.source!==enquiryFrame.contentWindow)return;
  let message;
  try{message=typeof event.data==='string'?JSON.parse(event.data):event.data;}catch{return;}
  if(message?.event!=='Tally.FormSubmitted'||message.payload?.formId!==enquiryFrame.dataset.formId||!message.payload?.id)return;
  brochureResult.hidden=false;
  const heading=brochureResult.querySelector('h3');heading.focus({preventScroll:true});
  brochureResult.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'center'});
 });
}

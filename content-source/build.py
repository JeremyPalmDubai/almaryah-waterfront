from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
from html import escape as e
import json,re,calendar,datetime,shutil
from urllib.parse import urlparse
from content import C,LANGS,NAMES
from types_content import IDS,CATEGORY,IMAGES
BASE=Path(__file__).resolve().parent
P=json.loads((BASE/'project.json').read_text()); A=json.loads((BASE/'assets.json').read_text()); OUT=BASE/'dist';O=P['origin'].rstrip('/');DOMAIN=urlparse(O).netloc
PRICE=P['categories'][0]['fromAed'];FX=Decimal(P['fx']['aedPerUsd']);PAY=P['payment']
assert sum(PAY[x] for x in ['bookingPercent','constructionPercent','handoverPercent'])==100
assert PAY['constructionInstallments']*PAY['installmentPercent']==PAY['constructionPercent']

def amounts(price):
 total=int(price);rnd=lambda n:int(n.quantize(Decimal(1),rounding=ROUND_HALF_UP));b=rnd(Decimal(total)*PAY['bookingPercent']/100);cs=[rnd(Decimal(total)*PAY['installmentPercent']/100)]*PAY['constructionInstallments'];h=total-b-sum(cs)
 usdTotal=int((Decimal(total)/FX).quantize(Decimal(1),rounding=ROUND_HALF_UP));vals=[b,*cs,h];u=[int((Decimal(x)/FX).quantize(Decimal(1),rounding=ROUND_HALF_UP)) for x in vals[:-1]];u.append(usdTotal-sum(u));assert sum(vals)==total and sum(u)==usdTotal
 return vals,u
AM,UM=amounts(PRICE)
def money(n,cur,l):
 s=f'{n:,}'.replace(',',{'en':',','fr':'\u202f','es':'.','nl':'.','de':'.','pt':' ' }[l]);return f'{cur} {s}'
def handover(l):return ('T' if l in ['fr','es','pt'] else 'Q')+str(P['handover']['quarter'])+' '+str(P['handover']['year'])
def date(l):return datetime.date.fromisoformat(P['asOf']).strftime('%d/%m/%Y' if l not in ['de','nl'] else '%d.%m.%Y')
def shortPrice(l):
 val=str(Decimal(PRICE)/1000000).rstrip('0').rstrip('.')
 if l!='en':val=val.replace('.',',')
 return val
def txt(l,k):
 s=C[l][k]
 if not isinstance(s,str):return s
 return s.format(booking=PAY['bookingPercent'],construction=PAY['constructionPercent'],handoverPart=PAY['handoverPercent'],count=PAY['constructionInstallments'],part=PAY['installmentPercent'],interval=PAY['intervalMonths'],duration=PAY['constructionInstallments']*PAY['intervalMonths'],shortAed=shortPrice(l),aed=money(PRICE,'AED',l),usd=money(sum(UM),'USD',l),handover=handover(l),rate=str(FX),date=date(l))
def img(name,l,altidx,hero=False,cls=''):
 a=A[name];vs=a['variants'];w=vs[-1];h=round(a['height']*w/a['width']);alt=C[l]['imageAlts'][altidx]
 return f'<figure class="visual {cls}"><img src="/assets/{name}-{w}.webp" srcset="'+', '.join(f'/assets/{name}-{v}.webp {v}w' for v in vs)+f'" sizes="'+('(max-width: 640px) 1100px, 100vw' if hero else '(max-width: 640px) 100vw, 60vw')+f'" width="{w}" height="{h}" alt="{e(alt)}" '+('fetchpriority="high" loading="eager"' if hero else 'loading="lazy" decoding="async"')+f'><span class="watermark" aria-hidden="true">{DOMAIN}</span></figure>'
def head(l,kind,title,desc,faq=None):
 path=C[l][kind];canon=O+path
 links=''.join(f'<link rel="alternate" hreflang="{ll}" href="{O+C[ll][kind]}">' for ll in LANGS)+f'<link rel="alternate" hreflang="x-default" href="{O+C["en"][kind]}">'
 schema=[{'@context':'https://schema.org','@type':'WebPage','name':title,'description':desc,'url':canon,'inLanguage':l}]
 if kind=='home':schema.append({'@context':'https://schema.org','@type':'ApartmentComplex','name':P['name'],'address':{'@type':'PostalAddress','addressLocality':'Al Maryah Island, Abu Dhabi','addressCountry':'AE'},'numberOfAccommodationUnits':P['residenceCount'],'amenityFeature':[{'@type':'LocationFeatureSpecification','name':v,'value':True} for v in C[l]['amenities']]})
 if faq:schema.append({'@context':'https://schema.org','@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in faq]})
 if kind!='home':schema.append({'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':C[l]['navHomes'],'item':O+C[l]['home']},{'@type':'ListItem','position':2,'name':title,'item':canon}]})
 favicon='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 64 64%22%3E%3Crect width=%2264%22 height=%2264%22 fill=%22%23172925%22/%3E%3Ctext x=%2232%22 y=%2244%22 text-anchor=%22middle%22 fill=%22white%22 font-family=%22Georgia%22 font-size=%2240%22%3EM%3C/text%3E%3C/svg%3E'
 return f'<!doctype html><html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(desc)}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{canon}">{links}<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{canon}"><meta property="og:type" content="website"><meta name="theme-color" content="#172925"><link rel="icon" href="{favicon}"><link rel="stylesheet" href="/site.css"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace("<","&lt;")}</script><script src="/site.js" defer></script><script src="/motion.js" defer></script></head><body><a class="skip" href="#main">{txt(l,"skip")}</a>'
def header(l,kind):
 c=C[l];nav=''.join(f'<a class="nav-link" href="{c["home"]}#{id}">{c[k]}</a>' for id,k in [('residences','navHomes'),('lifestyle','navLife'),('payment','navPlan'),('location','navLocation')]);opts=''.join(f'<a class="language-option" href="{C[ll][kind]}" lang="{ll}" hreflang="{ll}" '+('aria-current="page"' if ll==l else '')+f'><span>{ll.upper()}</span><span>{NAMES[i]}</span><span aria-hidden="true" class="language-check">'+('✓' if ll==l else '')+'</span></a>' for i,ll in enumerate(LANGS))
 return f'<header><a href="{c["home"]}" aria-label="{e(P["name"])}"><img class="logo" width="209" height="129" src="/assets/ritz-carlton-logo.svg" alt="{e(P["name"])}"></a><nav aria-label="{c["footerExplore"]}">{nav}<details class="language-switch"><summary aria-label="{c["language"]}: {NAMES[LANGS.index(l)]}"><span>{l.upper()}</span><svg width="12" height="8" viewBox="0 0 12 8" aria-hidden="true"><path d="M1 1.5 6 6.5 11 1.5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg></summary><div class="language-panel" aria-label="{c["language"]}">{opts}</div></details><a class="button" href="'+('#enquire' if kind!='legal' else c['home']+'#enquire')+f'">{c["ctaShort"]}</a></nav></header>'
def footer(l):
 c=C[l];links=''.join(f'<a href="{c["home"]}#{id}">{c[k]}</a>' for id,k in [('residences','navHomes'),('lifestyle','navLife'),('payment','navPlan'),('location','navLocation')]);langs=''.join(f'<a href="{C[ll]["guide"]}" lang="{ll}">{C[ll]["guideTitle"]}</a>' for ll in LANGS)
 links+=''.join(f'<a href="{c[id]}">{c["typeNames"][i]}</a>' for i,id in enumerate(IDS))
 return f'<footer class="footer"><div class="footer-top"><div><img class="logo" src="/assets/ritz-carlton-logo.svg" width="209" height="129" alt="{e(P["name"])}"><p class="brand-name">Al Maryah Waterfront</p><p class="note">{c["independent"]}<br>Al Maryah Island · Abu Dhabi</p></div><div><h3>{c["footerExplore"]}</h3>{links}</div><div><h3>{c["footerInternational"]}</h3>{langs}</div><div><h3>{c["footerInfo"]}</h3><a href="{c["home"]}#faq">FAQ</a><a href="{c["guide"]}#visa">{c["visaTitle"]}</a><a href="{c["legal"]}">{c["legalTitle"]}</a><a href="/sitemap.xml">Sitemap</a></div></div><p class="legal-note">{c["legalIntro"]} {c["termsBody"]}</p><div class="footer-bottom"><span>© {P["asOf"][:4]} Al Maryah Waterfront</span><span>{c["rights"]}</span></div></footer>'
def form(l,type_name=None):
 c=C[l];url=f'https://tally.so/embed/{P["tally"]["id"]}?alignLeft=1&hideTitle=1&transparentBackground=1&dynamicHeight=1'
 return f'<section class="section blue enquire" id="enquire"><div><p class="eyebrow">Al Maryah Waterfront</p><h2>{c["brochureTitle"]}</h2><p>{c["brochureIntro"]}</p><p class="note">{c["independent"]}</p></div><div class="form-wrap"><p class="form-note">{c["formLanguage"]}</p><iframe data-tally-src="{e(url)}" loading="lazy" width="100%" height="448" title="{e(c["formTitle"]+(" — "+type_name if type_name else ""))}" data-form-id="{P["tally"]["id"]}" lang="en" frameborder="0" marginheight="0" marginwidth="0"></iframe><div class="brochure-success" id="brochure-success" role="status" aria-live="polite" hidden><h3 tabindex="-1">{c["brochureReady"]}</h3><a class="button" href="/downloads/ritz-carlton-al-maryah-brochure.pdf" download="Ritz-Carlton-Al-Maryah-Brochure.pdf">{c["brochureDownload"]}</a></div><p class="note">{c["formPrivacy"]} <a href="{c["legal"]}">{c["legalTitle"]}</a></p></div></section>'
def mobile(l,category=None):
 cat=category if category is not None else P['categories'][0]
 label=(txt(l,'from')+' '+money(cat['fromAed'],'AED',l)) if cat['fromAed'] else txt(l,'onRequest')
 return f'<div class="mobile-cta"><span>{label}</span><a href="#enquire" class="button">{txt(l,"brochureCta")}</a></div>' 
def faqs(l):
 c=C[l];ans=[c['locationBody'],txt(l,'faqPrice'),c['paymentBody']+' '+txt(l,'sixPayments')+'. '+txt(l,'scheduleNote'),txt(l,'faqHandover'),c['remoteBody'],c['visaBody'],c['risk']];return list(zip(c['faqQs'],ans))
def faqSection(l,fs):return f'<section class="section faq" id="faq"><div><p class="eyebrow">FAQ</p><h2>{C[l]["faqTitle"]}</h2></div><div>'+''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q,a in fs)+'</div></section>'
def payment(l):
 c=C[l];vals=[AM[0],sum(AM[1:-1]),AM[-1]];uv=[UM[0],sum(UM[1:-1]),UM[-1]];pcs=[PAY['bookingPercent'],PAY['constructionPercent'],PAY['handoverPercent']]
 cards=''.join(f'<article class="payment-card"><strong>{pcs[i]}<span style="font-size:.42em">%</span></strong><h3>{c["stages"][i]}</h3><p class="amount" data-amount="{i}">{money(vals[i],"AED",l)}</p><p class="usd" data-usd="{i}">{c["approx"]} {money(uv[i],"USD",l)}</p>'+ (f'<p class="note">{txt(l,"sixPayments")}</p>' if i==1 else '')+'</article>' for i in range(3))
 labels=[c['stages'][0]]+[c['instalment']+' '+str(i+1) for i in range(PAY['constructionInstallments'])]+[c['stages'][2]];pcts=[pcs[0]]+[PAY['installmentPercent']]*PAY['constructionInstallments']+[pcs[-1]]
 rows=''.join(f'<tr><td>{labels[i]}</td><td>{pcts[i]}%</td><td data-row-aed="{i}">{money(a,"AED",l)}</td><td data-row-usd="{i}">{money(UM[i],"USD",l)}</td></tr>' for i,a in enumerate(AM))
 calcjson=json.dumps({"payment":PAY,"fx":str(FX),"locale":l,"approx":c["approx"],"error":c["calcError"]},ensure_ascii=False)
 return f'<section class="section blue" id="payment"><p class="eyebrow">03 / {c["navPlan"]}</p><div class="section-head"><h2>{c["paymentTitle"]}</h2><p>{c["paymentBody"]}</p></div><div class="payment-grid" aria-live="polite">{cards}</div><form class="payment-toolbar" id="calculator"><label for="price">{c["calcLabel"]}</label><input type="number" id="price" min="1" max="1000000000" step="1" value="{PRICE}" inputmode="numeric" required><button class="button" type="submit">{c["recalculate"]}</button><span id="calc-error" class="error" aria-live="polite"></span></form><details class="schedule"><summary>{c["scheduleTitle"]}</summary><div style="overflow-x:auto"><table><thead><tr><th scope="col">{c["navPlan"]}</th><th scope="col">{c["percent"]}</th><th scope="col">AED</th><th scope="col">USD</th></tr></thead><tbody>{rows}<tr><th scope="row">{c["total"]}</th><td>100%</td><td id="total-aed">{money(PRICE,"AED",l)}</td><td id="total-usd">{money(sum(UM),"USD",l)}</td></tr></tbody></table></div></details><p class="note">{txt(l,"scheduleNote")}</p><p class="note">{txt(l,"fxNote")}</p><p class="note">{c["priceNote"]}</p><script type="application/json" id="calc-data">{calcjson}</script></section>'
def home(l):
 c=C[l];fs=faqs(l);s=head(l,'home',c['title'],txt(l,'description'),fs)+header(l,'home')+'<main id="main">'
 s+=f'<section class="hero">{img("aerial",l,0,True)}<span class="hero-marker">{c["heroMarker"]}</span><div class="hero-copy"><p class="eyebrow">Al Maryah Island · Abu Dhabi</p><h1><span class="sr-only">{e(P["name"])} — </span>{c["hero"]}</h1><div class="hero-bottom"><p>{c["heroSub"]}</p><div class="hero-actions"><a class="button light" href="#enquire">{c["cta"]}</a><a class="button outline" href="#residences">{c["explore"]}</a></div></div></div></section>'
 facts=[(c['oneFrom'],money(PRICE,'AED',l),c['approx']+' '+money(sum(UM),'USD',l)),(c['navPlan'],' / '.join(str(PAY[k]) for k in ['bookingPercent','constructionPercent','handoverPercent']),c['stages'][0]+' / '+c['stages'][2]),(c['handover'],handover(l),''),(c['furnishing'],c['furnished'],'')]
 s+='<section class="facts">'+''.join(f'<div class="fact"><span>{x}</span><strong>{y}</strong><small>{z}</small></div>' for x,y,z in facts)+'</section>'
 s+=f'<section class="section"><div class="intro"><p class="eyebrow">{c["introLabel"]}</p><div><h2>{c["intro"]}</h2><p class="large-copy">{c["introBody"]}</p></div></div><div class="split">{img("architecture",l,1)}<div><span class="index">KILLA DESIGN</span><h2>{c["architectureTitle"]}</h2><p>{c["architectureBody"]}</p><a class="text-link" href="#residences">{c["explore"]}</a></div></div><div class="split reverse">{img("living",l,2)}<div><span class="index">TARA BERNERD & PARTNERS</span><h2>{c["interiorTitle"]}</h2><p>{c["interiorBody"]}</p><a class="text-link" href="#enquire">{c["plansRequest"]}</a></div></div></section>'
 s+=f'<section class="dark section" id="residences"><div class="section-head"><div><p class="eyebrow">02 / {c["navHomes"]}</p><h2>{c["collection"]}</h2></div><p>{c["collectionBody"]}</p></div><div class="residence-list">'
 for i,id in enumerate(IDS):
  cat=P['categories'][CATEGORY[i]]
  price=(c['from']+' '+money(cat['fromAed'],'AED',l)) if cat['fromAed'] else c['onRequest']
  s+=f'<div class="residence-row"><span class="index">0{i+1}</span><h3><a href="{c[id]}">{c["typeNames"][i]}</a></h3><p>{price}</p><a href="{c[id]}" class="text-link">{c["viewType"]}</a></div>'
 s+=f'</div><p class="note">{c["priceNote"]}</p><div class="gallery">{img("dining",l,3)}{img("bedroom",l,4)}</div></section>'
 s+=f'<section class="section" id="lifestyle"><div class="section-head"><div><p class="eyebrow">{c["navLife"]}</p><h2>{c["amenityTitle"]}</h2></div><p>{c["amenityBody"]}</p></div><div class="gallery">{img("indoor-pool",l,5)}{img("outdoor-pool",l,6)}</div><div class="amenities">'+''.join(f'<div><span>{i+1:02}</span>{a}</div>' for i,a in enumerate(c['amenities']))+f'</div><div class="gallery">{img("cinema",l,7)}{img("fitness",l,8)}</div></section>'
 s+=f'<section class="fullbleed">{img("lobby",l,9,False)}<p class="image-caption">{c["render"]}</p></section><section class="section intro"><p class="eyebrow">THE RITZ-CARLTON</p><div><h2>{c["services"]}</h2><p class="large-copy">{c["servicesBody"]}</p></div></section>'
 s+=f'<section class="brand-partners"><img src="/assets/saas-logo.svg" width="132" height="85" alt="SAAS Properties" loading="lazy"><span>Killa Design</span><span>Tara Bernerd & Partners</span></section>'
 s+=payment(l)
 s+=f'<section class="section" id="location"><div class="split reverse">{img("district",l,10)}<div><p class="eyebrow">AL MARYAH ISLAND</p><h2>{c["locationTitle"]}</h2><p>{c["locationBody"]}</p></div></div><div class="benefits">'+''.join(f'<article><span class="index">0{i+1}</span><h3>{a}</h3><p>{c["benefitBodies"][i]}</p></article>' for i,a in enumerate(c['benefitTitles']))+'</div></section>'
 s+=f'<section class="section dark"><div class="section-head"><h2>{c["remoteTitle"]}</h2><p>{c["remoteBody"]}</p></div><a class="button light" href="{c["guide"]}">{c["guideTitle"]}</a></section>'+faqSection(l,fs)+form(l)+'</main>'+footer(l)+mobile(l)+'</body></html>';return s

def guide(l):
 c=C[l];title=c['guideTitle']+' | Al Maryah Waterfront';s=head(l,'guide',title,c['guideIntro'])+header(l,'guide')+f'<main id="main"><section class="article-hero"><p class="eyebrow">AL MARYAH WATERFRONT</p><h1>{c["guideTitle"]}</h1><p class="large-copy">{c["guideIntro"]}</p><a class="text-link" href="{c["home"]}">{c["back"]}</a></section><section class="fullbleed">{img("aerial",l,0,True)}<p class="image-caption">{c["render"]}</p></section><article class="article-content"><h2>{c["stepsTitle"]}</h2><ol class="steps">'+''.join(f'<li>{e(v)}</li>' for v in c['steps'])+f'</ol><h2>{c["remoteTitle"]}</h2><p>{c["remoteBody"]}</p><h2 id="visa">{c["visaTitle"]}</h2><p>{c["visaBody"]}</p><h2>{c["navPlan"]}</h2><p>{txt(l,"faqPrice")}</p><p>{c["paymentBody"]}</p><p>{txt(l,"sixPayments")}</p><p>{txt(l,"scheduleNote")}</p><a class="text-link" href="{c["home"]}#payment">{c["scheduleTitle"]}</a><h2>{c["benefitTitles"][2]}</h2><p>{c["risk"]}</p><h2>{c["sources"]}</h2><p>{txt(l,"sourceBody")}</p><p class="note">Abu Dhabi Residents Office · ICP · Central Bank of the UAE</p><a class="button" href="#enquire">{c["cta"]}</a></article>'+form(l)+'</main>'+footer(l)+mobile(l)+'</body></html>';return s

def legal(l):
 c=C[l];s=head(l,'legal',c['legalTitle']+' | Al Maryah Waterfront',c['legalIntro'])+header(l,'legal')+f'<main id="main"><section class="article-hero"><p class="eyebrow">AL MARYAH WATERFRONT</p><h1>{c["legalTitle"]}</h1><p>{c["legalIntro"]}</p><a class="text-link" href="{c["home"]}">{c["back"]}</a></section><article class="article-content"><h2>{c["operatorTitle"]}</h2><p>{c["operatorMissing"]}</p><h2>{c["dataTitle"]}</h2><p>{c["dataBody"]}</p><h2>{c["termsTitle"]}</h2><p>{c["termsBody"]}</p><p>{c["priceNote"]}</p><p>{txt(l,"fxNote")}</p><h2>{c["sources"]}</h2><p>{txt(l,"sourceBody")}</p></article></main>'+footer(l)+'</body></html>';return s

def type_page(l,i):
 c=C[l];id=IDS[i];name=c['typeNames'][i];cat=P['categories'][CATEGORY[i]];heroImage,alt=IMAGES[i]
 price=(c['from']+' '+money(cat['fromAed'],'AED',l)) if cat['fromAed'] else c['onRequest']
 priceBody=txt(l,'faqPrice') if cat['fromAed'] else c['typePriceUnknown']
 questions=[(c['faqQs'][1],priceBody),(c['confirmTitle'],c['confirmBody']),(c['faqQs'][3],txt(l,'faqHandover'))]
 title=name+' Ritz-Carlton Abu Dhabi | '+c['typeTitleSuffix']
 desc=c['typeIntros'][i].split('. ')[0]+'. '+price+'. '+c['brochureCta']+'.'
 s=head(l,id,title,desc,questions)+header(l,id)+f'<main id="main"><section class="type-hero"><div class="type-hero-copy"><a class="back text-link" href="{c["home"]}#residences">{c["back"]}</a><p class="eyebrow">THE RITZ-CARLTON RESIDENCES · AL MARYAH ISLAND</p><h1>{name}<span>Abu Dhabi</span></h1><p>{c["typeIntros"][i]}</p><p class="type-price">{price}</p><a class="button" href="#enquire">{c["brochureCta"]}</a></div>{img(heroImage,l,alt,True)}</section><p class="type-image-note note">{c["illustrationType"]}</p>'
 s+=f'<section class="section type-details"><div><p class="eyebrow">{name}</p><h2>{c["typeFacts"]}</h2><p class="large-copy">{priceBody}</p><p class="note">{c["priceNote"]}</p></div><dl class="spec-list"><div><dt>{c["navHomes"]}</dt><dd>{name}</dd></div><div><dt>{c["area"]}</dt><dd>{c["areaUnknown"]}</dd></div><div><dt>{c["handover"]}</dt><dd>{handover(l)}</dd></div><div><dt>{c["furnishing"]}</dt><dd>{c["furnished"]}</dd></div></dl></section>'
 s+=f'<section class="section dark"><div class="split reverse">{img("dining" if heroImage!="dining" else "living",l,3 if heroImage!="dining" else 2)}<div><h2>{c["confirmTitle"]}</h2><p>{c["confirmBody"]}</p><a class="button light" href="#enquire">{c["brochureCta"]}</a></div></div><p class="note">{c["illustrationType"]}</p></section>'
 if cat['fromAed']:s+=payment(l)
 else:s+=f'<section class="section blue"><div class="intro"><h2>{c["navPlan"]}</h2><div><p class="large-copy">{txt(l,"typePlanNote")}</p><p>{txt(l,"sixPayments")}</p><p class="note">{txt(l,"scheduleNote")}</p></div></div></section>'
 s+=f'<section class="section"><div class="section-head"><h2>{c["amenityTitle"]}</h2><p>{c["amenityBody"]}</p></div><div class="gallery">{img("indoor-pool",l,5)}{img("fitness",l,8)}</div><div class="amenities">'+''.join(f'<div><span>{j+1:02}</span>{a}</div>' for j,a in enumerate(c['amenities']))+'</div></section>'
 s+=faqSection(l,questions)+form(l,name)
 s+=f'<section class="section"><h2>{c["otherTypes"]}</h2><div class="type-related">'+''.join(f'<a href="{c[other]}"><span>{c["typeNames"][j]}</span><small>{c["viewType"]}</small></a>' for j,other in enumerate(IDS) if j!=i)+'</div></section></main>'+footer(l)+mobile(l,cat)+'</body></html>'
 return s

routes=[]
for l in LANGS:
 for kind,fn in [('home',home),('guide',guide),('legal',legal)]+[(id,lambda lang,i=i:type_page(lang,i)) for i,id in enumerate(IDS)]:
  path=C[l][kind];f=OUT/path.strip('/')/'index.html';f.parent.mkdir(parents=True,exist_ok=True);f.write_text(fn(l));routes.append({'lang':l,'kind':kind,'path':path})
# Localised alternates on each sitemap URL.
ns='xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml"'
xml='<?xml version="1.0" encoding="UTF-8"?><urlset '+ns+'>'
for r in routes:
 xml+=f'<url><loc>{O+r["path"]}</loc><lastmod>{P["asOf"]}</lastmod>'+''.join(f'<xhtml:link rel="alternate" hreflang="{ll}" href="{O+C[ll][r["kind"]]}"/>' for ll in LANGS)+f'<xhtml:link rel="alternate" hreflang="x-default" href="{O+C["en"][r["kind"]]}"/></url>'
(OUT/'sitemap.xml').write_text(xml+'</urlset>')
xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'
for r in routes:
 if r['kind']=='legal':continue
 page=(OUT/r['path'].strip('/')/'index.html').read_text();imgs=list(dict.fromkeys(re.findall(r'<img src="([^"]+\.webp)"',page)))
 xml+=f'<url><loc>{O+r["path"]}</loc>'+''.join(f'<image:image><image:loc>{O+u}</image:loc></image:image>' for u in imgs)+'</url>'
(OUT/'sitemap-images.xml').write_text(xml+'</urlset>')
(OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {O}/sitemap.xml\nSitemap: {O}/sitemap-images.xml\n')
(OUT/'_redirects').write_text(f'http://{DOMAIN}/* {O}/:splat 301\nhttp://www.{DOMAIN}/* {O}/:splat 301\nhttps://www.{DOMAIN}/* {O}/:splat 301\n/en/ / 301\n')
(OUT/'_headers').write_text('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n/assets/*\n  Cache-Control: public, max-age=2592000\n')
(OUT/'404.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="robots" content="noindex"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/site.css"><title>Page not found | Al Maryah Waterfront</title><main class="article-hero"><p>404</p><h1>Page not found</h1><a class="button" href="/">Al Maryah Waterfront</a></main></html>')
(BASE/'routes.json').write_text(json.dumps(routes,indent=2));print(f'Created {len(routes)} pages, sitemaps and robots.txt for {O}. Not deployed.')

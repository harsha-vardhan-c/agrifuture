import React, { useEffect, useState } from 'react';

const API = import.meta.env.VITE_API_BASE_URL || '';
const money = (value, maximumFractionDigits = 0) => `₹${new Intl.NumberFormat('en-IN', { maximumFractionDigits }).format(Number(value) || 0)}`;
const monthLabel = (value, options = { month: 'long', year: 'numeric' }) => {
  const s = value?.length === 7 ? `${value}-01` : value;
  return new Intl.DateTimeFormat('en-IN', { timeZone: 'UTC', ...options }).format(new Date(`${s}T00:00:00Z`));
};

function Icon({ name, size = 20, ...rest }) {
  const shapes = {
    arrow: <><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></>,
    left: <><path d="M19 12H5"/><path d="m11 18-6-6 6-6"/></>,
    leaf: <><path d="M20 4c-9 0-15 5-15 11a5 5 0 0 0 5 5c6 0 11-6 10-16Z"/><path d="M5 20c2-5 6-9 12-12"/></>,
    chart: <><path d="M4 19h16"/><path d="M5 15l5-5 4 3 5-7"/></>,
    calendar: <><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/></>,
    pin: <><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></>,
    sun: <><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></>,
    cloud: <><path d="M7 18h12a4 4 0 0 0 0-8h-1a7 7 0 0 0-13-2 5 5 0 0 0 2 10Z"/></>,
    alert: <><path d="M12 3 2 20h20L12 3Z"/><path d="M12 9v5m0 3h.01"/></>,
    check: <><path d="m5 12 5 5L20 7"/></>,
    chevron: <><path d="m6 9 6 6 6-6"/></>,
    calendarClock: <><rect x="3" y="4" width="18" height="17" rx="2"/><path d="M8 2v4m8-4v4M3 10h18"/><circle cx="13" cy="15" r="3"/></>,
    info: <><circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-9h.01"/></>,
    sprout: <><path d="M12 21v-9"/><path d="M12 14C7 14 4 11 4 6c5 0 8 3 8 8Z"/><path d="M12 12c0-5 3-8 8-8 0 5-3 8-8 8Z"/></>,
    refresh: <><path d="M20 11a8 8 0 0 0-14-5L4 8"/><path d="M4 3v5h5"/><path d="M4 13a8 8 0 0 0 14 5l2-2"/><path d="M20 21v-5h-5"/></>,
    up: <><path d="M12 19V5m-6 6 6-6 6 6"/></>,
    down: <><path d="M12 5v14m-6-6 6 6 6-6"/></>,
    equals: <><path d="M5 9h14M5 15h14"/></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...rest}>{shapes[name] || shapes.info}</svg>;
}

function Brand({ onClick }) {
  return <button className="brand" onClick={onClick} aria-label="Go to AgriFuture home">
    <span className="brand-icon"><Icon name="sprout" size={22}/></span>
    <span>agri<span className="brand-highlight">future</span><span className="brand-dot">.</span></span>
  </button>;
}

function Header({ onHome, onPredict, page }) {
  return <header className="site-header">
    <div className="container header-inner">
      <Brand onClick={onHome}/>
      <nav className="main-nav" aria-label="Main navigation">
        <button className={page === 'home' ? 'nav-active' : ''} onClick={onHome}>Home</button>
        <button className={page !== 'home' ? 'nav-active' : ''} onClick={onPredict}>Price outlook</button>
        <a href="#method" onClick={page !== 'home' ? onHome : undefined}>How it works</a>
      </nav>
      <button className="header-cta" onClick={onPredict}>Explore prices <Icon name="arrow" size={17}/></button>
    </div>
  </header>;
}

function GrowingScene() {
  return <div className="hero-art" aria-hidden="true">
    <div className="scene-orbit scene-orbit-one"/><div className="scene-orbit scene-orbit-two"/>
    <div className="scene-card scene-price">
      <span className="scene-mini">District price overview</span>
      <div className="scene-card-title">Vegetables</div>
      <div className="scene-bars"><i/><i/><i/><i/><i/><i/><i/><i/><i/></div>
      <span className="scene-meta"><span className="scene-green-dot"/> Historical trends</span>
    </div>
    <svg className="scene-plant" viewBox="0 0 390 420" fill="none">
      <ellipse cx="185" cy="371" rx="135" ry="21" fill="#245144" opacity=".1"/>
      <path d="M191 369c-3-85 1-197-19-282" stroke="#194D35" strokeWidth="9" strokeLinecap="round"/>
      <path d="M191 317c-16-78-77-118-139-134 4 76 67 141 139 134Z" fill="#5DA476"/>
      <path d="M188 248c24-92 95-127 163-120-9 78-64 135-163 120Z" fill="#2F7A56"/>
      <path d="M175 172c-44-67-39-117-13-160 43 45 52 97 13 160Z" fill="#88BB7C"/>
      <path d="M188 319c-34-54-75-84-111-105M191 246c37-46 80-72 126-92M177 155c-8-36-11-66-13-114" stroke="#D4E7AC" strokeWidth="3" strokeLinecap="round" opacity=".75"/>
      <circle cx="254" cy="309" r="56" fill="#E9A76A"/><circle cx="269" cy="294" r="47" fill="#F8BE7C"/>
      <path d="M264 251c5-21 22-29 33-29" stroke="#225D41" strokeWidth="7" strokeLinecap="round"/>
      <path d="M266 249c-10-25-30-30-44-25 4 19 19 27 44 25Z" fill="#2F8058"/>
      <circle cx="116" cy="357" r="33" fill="#C9B174"/><circle cx="105" cy="351" r="23" fill="#E4D398"/>
    </svg>
    <div className="scene-pill"><Icon name="leaf" size={15}/> Rooted in real data</div>
  </div>;
}

function Home({ onStart, meta }) {
  return <main>
    <section className="hero-section">
      <div className="container hero-grid">
        <div className="hero-copy">
          <div className="eyebrow"><span className="eyebrow-dot"/> KARNATAKA CROP PRICE OUTLOOKS</div>
          <h1>Better crop decisions start with <em>better price insights.</em></h1>
          <p>Explore historical vegetable prices and get a thoughtful outlook for the months ahead. Built around real district-level agricultural market data.</p>
          <div className="hero-actions">
            <button className="button button-primary button-lg" onClick={onStart}>Explore price outlooks <Icon name="arrow"/></button>
            <span className="hero-side-note"><Icon name="check" size={17}/> No account needed</span>
          </div>
          <div className="source-strip"><Icon name="info" size={17}/> Based on AGMARKNET wholesale market price data.</div>
        </div>
        <GrowingScene/>
      </div>
    </section>
    <section className="stats-section">
      <div className="container stat-grid">
        <div className="stat"><b>{meta?.observed_price_rows?.toLocaleString('en-IN') || '13,552'}</b><span>Real price observations</span></div>
        <div className="stat"><b>5 years</b><span>Historical monthly data</span></div>
        <div className="stat"><b>District-wise</b><span>Location-specific insights</span></div>
        <div className="stat"><b>12 months</b><span>Maximum forecast period</span></div>
      </div>
    </section>
    <section className="process-section" id="method">
      <div className="container">
        <div className="section-heading"><span className="section-kicker">SIMPLE BY DESIGN</span><h2>From curiosity to clarity in three steps.</h2><p>Just a few selections. We'll handle the price history and forecasting calculations.</p></div>
        <div className="step-grid">
          <div className="step-card"><span className="step-number">01</span><div className="step-icon"><Icon name="leaf" size={25}/></div><h3>Choose your crop</h3><p>Start with the vegetable you want to understand, from tomatoes to green chillies.</p></div>
          <div className="step-card"><span className="step-number">02</span><div className="step-icon"><Icon name="pin" size={25}/></div><h3>Select your district</h3><p>See only the locations where usable official historical records are available.</p></div>
          <div className="step-card"><span className="step-number">03</span><div className="step-icon"><Icon name="chart" size={25}/></div><h3>Explore the outlook</h3><p>Read a monthly price estimate, a price range, trends and simple explanations.</p></div>
        </div>
      </div>
    </section>
    <section className="trust-section">
      <div className="container trust-grid">
        <div><span className="section-kicker section-kicker-light">WHY DATA MATTERS</span><h2>Real market prices.<br/><em>Clear future trends.</em></h2><p>We use past wholesale prices to estimate future price trends for vegetables across Karnataka.</p></div>
        <div className="trust-points"><div><Icon name="check"/><span>Historical prices from government market reports</span></div><div><Icon name="check"/><span>Models tested using past market prices</span></div><div><Icon name="check"/><span>Weather details shown where available</span></div><div><Icon name="check"/><span>Easy-to-read price charts and trends</span></div></div>
      </div>
    </section>
    <section className="bottom-cta"><div className="container bottom-content"><div><span className="section-kicker">GET STARTED</span><h2>See what the data says about your crop.</h2></div><button className="button button-primary button-lg" onClick={onStart}>Start exploring <Icon name="arrow"/></button></div></section>
  </main>;
}

function ChoosePage({ meta, error, crop, setCrop, district, setDistrict, month, setMonth, onSubmit, loading }) {
  const available = (meta?.crop_options || []).filter(c => c.available);
  const cropEntry = available.find(c => c.crop === crop);
  return <main className="work-page"><div className="container">
    <div className="page-top"><span className="section-kicker">PRICE OUTLOOK</span><h1>Let's explore your crop.</h1><p>Choose what you'd like to forecast. We'll use the latest available monthly price history.</p></div>
    <div className="predict-layout">
      <form className="form-card" onSubmit={onSubmit}>
        <div className="form-title"><div className="form-title-icon"><Icon name="chart" size={22}/></div><div><h2>Your forecast details</h2><p>Three quick selections</p></div></div>
        <div className="form-field"><label htmlFor="crop">Vegetable</label><div className="field-wrapper"><Icon name="leaf" size={20}/><select id="crop" value={crop} onChange={e => { setCrop(e.target.value); const item = available.find(x=>x.crop===e.target.value); setDistrict(item?.districts?.[0] || ''); }} disabled={!available.length} required><option value="" disabled>Select a vegetable</option>{available.map(x=><option key={x.crop} value={x.crop}>{x.crop}</option>)}</select><Icon name="chevron" size={17}/></div></div>
        <div className="form-field"><label htmlFor="district">District</label><div className="field-wrapper"><Icon name="pin" size={20}/><select id="district" value={district} onChange={e => setDistrict(e.target.value)} disabled={!cropEntry} required><option value="" disabled>Choose a district</option>{(cropEntry?.districts || []).map(d=><option key={d} value={d}>{d}</option>)}</select><Icon name="chevron" size={17}/></div><p className="field-hint">Only locations with enough recent reported prices are shown.</p></div>
        <div className="form-field"><label htmlFor="month">Future month</label><div className="field-wrapper"><Icon name="calendar" size={20}/><select id="month" value={month} onChange={e=>setMonth(e.target.value)} disabled={!meta?.available_months?.length} required><option value="" disabled>Select a month</option>{(meta?.available_months || []).map(m=><option key={m} value={m}>{monthLabel(m)}</option>)}</select><Icon name="chevron" size={17}/></div><p className="field-hint">Forecast months begin after the last available price record.</p></div>
        {error && <div className="error-message" role="alert"><Icon name="alert" size={18}/>{error}</div>}
        <button className="button button-primary button-block" disabled={loading || !crop || !district || !month}>{loading ? 'Calculating forecast…' : 'View price outlook'} {!loading && <Icon name="arrow"/>}</button>
      </form>
      <aside className="form-aside">
        <div className="aside-badge"><Icon name="leaf" size={18}/> PRICE DATA</div><h2>Real prices.<br/><em>Real context.</em></h2>
        <p>Each estimate is tied to a crop, a district, a forecast month and a known historical price period.</p>
        <div className="aside-separator"/>
        <div className="aside-fact"><Icon name="calendarClock"/><div><strong>Data last available</strong><span>{meta?.latest_price_month ? monthLabel(meta.latest_price_month) : 'Loading…'}</span></div></div>
        <div className="aside-fact"><Icon name="chart"/><div><strong>How forecasts are evaluated</strong><span>Separate errors for each month ahead</span></div></div>
        <div className="aside-fact"><Icon name="info"/><div><strong>Long-range estimates</strong><span>Price estimates for the months ahead</span></div></div>
      </aside>
    </div>
  </div></main>;
}

function PriceChart({ history, outlook, selectedMonth }) {
  const [hovered, setHovered] = useState(null);
  const hist = (history || []).slice(-18).map(p=>({ ...p, kind:'actual' }));
  const pred = (outlook || []).map(p=>({date: `${p.month}-01`,price:p.predicted_rs_per_quintal,low:p.indicative_low_rs_per_quintal,high:p.indicative_high_rs_per_quintal,kind:'forecast'}));
  const all = [...hist, ...pred];
  if (all.length < 2) return <p>No chart data for this selection.</p>;
  const W=840, H=315, L=58, R=20, T=19, B=51;
  const values = all.flatMap(p=>[p.price, ...(p.kind === 'forecast' ? [p.low,p.high] : [])]);
  const max = Math.max(...values,1)*1.12, min=Math.max(0,Math.min(...values)*0.75);
  const x=i=>L+(i/(all.length-1))*(W-L-R);
  const y=v=>T+(1-(v-min)/(max-min))*(H-T-B);
  const lastActual=hist.length-1;
  const historicalPoints=hist.map((p,i)=>`${x(i)},${y(p.price)}`).join(' ');
  const predictedPoints=[hist[lastActual],...pred].map((p,j)=>`${x(lastActual+j)},${y(p.price)}`).join(' ');
  const upper=pred.map((p,i)=>`${x(hist.length+i)},${y(p.high)}`).join(' ');
  const lower=pred.slice().reverse().map((p,i)=>`${x(all.length-1-i)},${y(p.low)}`).join(' ');
  const band=`${upper} ${lower}`;
  const selectedIndex=all.findIndex(p=>p.kind==='forecast' && p.date===`${selectedMonth}-01`);
  const selected=all[selectedIndex];
  return <div className="chart-wrap">
    <div className="chart-legend"><span><i className="legend-real"/> Published prices</span><span><i className="legend-pred"/> Forecast</span><span><i className="legend-band"/> Price range</span></div>
    <svg className="price-chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Historic monthly prices and up to twelve months of forecast prices, shown with a price range">
      {[0,.25,.5,.75,1].map(p=>{const v=min+(max-min)*p;return <g key={p}><line x1={L} x2={W-R} y1={y(v)} y2={y(v)} stroke="#E4ECE7" strokeWidth="1"/><text x={L-10} y={y(v)+5} fill="#71877A" fontSize="13" textAnchor="end">{Math.round(v/1000)}k</text></g>})}
      <polygon points={band} fill="#BCEAD2" opacity=".63"/>
      <line x1={x(lastActual)+9} x2={x(lastActual)+9} y1={T} y2={H-B} stroke="#8FAE9B" strokeDasharray="4 5"/>
      <polyline points={historicalPoints} fill="none" stroke="#1F503D" strokeWidth="3.5" strokeLinejoin="round" strokeLinecap="round"/>
      <polyline points={predictedPoints} fill="none" stroke="#0FA772" strokeWidth="3.5" strokeDasharray="7 6" strokeLinejoin="round" strokeLinecap="round"/>
      {selected && <><circle cx={x(selectedIndex)} cy={y(selected.price)} r="9" fill="#0FA772" opacity=".15"/><circle cx={x(selectedIndex)} cy={y(selected.price)} r="5.5" fill="#0FA772" stroke="white" strokeWidth="2"/></>}
      {all.map((p,i)=>(i%3===0 || i===all.length-1) && <text key={p.date+i} x={x(i)} y={H-20} fontSize="12" textAnchor="middle" fill="#7D9183">{monthLabel(p.date,{month:'short',year:'2-digit'})}</text>)}
      <text x={x(lastActual)-5} y={T+7} fontSize="12" textAnchor="end" fill="#627C6B">Observed</text><text x={x(lastActual)+22} y={T+7} fontSize="12" textAnchor="start" fill="#179164">Outlook</text>
      {all.map((p,i)=><circle key={p.date+i} cx={x(i)} cy={y(p.price)} r="10" fill="transparent" onMouseEnter={()=>setHovered({p,i})} onMouseLeave={()=>setHovered(null)}><title>{`${monthLabel(p.date)}: ${money(p.price)} per quintal (${p.kind})`}</title></circle>)}
      {hovered && <g pointerEvents="none"><rect x={Math.min(W-163,Math.max(4,x(hovered.i)-65))} y={Math.max(4,y(hovered.p.price)-63)} rx="8" width="161" height="48" fill="#173B2B"/><text x={Math.min(W-163,Math.max(4,x(hovered.i)-65))+12} y={Math.max(4,y(hovered.p.price)-63)+19} fill="#C9E8D6" fontSize="12">{monthLabel(hovered.p.date)}</text><text x={Math.min(W-163,Math.max(4,x(hovered.i)-65))+12} y={Math.max(4,y(hovered.p.price)-63)+38} fill="white" fontSize="15" fontWeight="600">{money(hovered.p.price)} / q</text></g>}
    </svg>
  </div>;
}

function Results({ result, onBack }) {
  const selected=result.selected, explanation=result.explanation;
  const isUp=explanation.direction==='rise', isDown=explanation.direction==='fall';
  return <main className="results-page"><div className="container">
    <div className="results-heading"><div><button className="back-button" onClick={onBack}><Icon name="left" size={17}/> Modify selection</button><div className="section-kicker">PRICE OUTLOOK RESULTS</div><h1>{result.crop} in {result.district}</h1><p>{monthLabel(selected.month)} forecast • {selected.horizon} month{selected.horizon===1?'':'s'} after the last recorded price ({monthLabel(result.origin_month)})</p></div><span className="experimental-badge"><Icon name="info" size={16}/> Price forecast</span></div>
    <div className="results-grid">
      <div className="result-primary">
        <div className="forecast-summary"><div><div className="summary-kicker">PROJECTED DISTRICT WHOLESALE PRICE</div><div className="price-display">{money(selected.predicted_rs_per_quintal)}</div><div className="price-conversion">per quintal (100 kg) <span>≈ {money(selected.predicted_rs_per_kg,2)} per kg</span></div></div><div className={`direction-chip ${isUp?'rise':isDown?'fall':'steady'}`}><Icon name={isUp?'up':isDown?'down':'equals'} size={18}/>{Math.abs(explanation.change_pct_vs_last_observed)}% {isUp?'higher':isDown?'lower':'difference'}</div></div>
        <div className="range-panel"><div><span>Estimated price range</span><strong>{money(selected.indicative_low_rs_per_quintal)} – {money(selected.indicative_high_rs_per_quintal)}</strong></div></div>
        <div className="chart-card"><div className="card-head"><div><h2>Past prices and future forecasts</h2><p>Last recorded month: {monthLabel(result.origin_month)}. The dashed line shows predicted prices after that.</p></div><span className="small-pill">₹ per quintal</span></div><PriceChart history={result.history} outlook={result.outlook} selectedMonth={selected.month}/></div>
        <div className="insight-card"><div className="card-head"><div><span className="section-kicker">UNDERSTANDING THE OUTLOOK</span><h2>{explanation.headline}</h2></div><div className="insight-mark"><Icon name="leaf"/></div></div><div className="reason-list">{explanation.reasons.map((r,i)=><div className="reason" key={i}><span className="reason-icon"><Icon name={r.type==='festival'?'calendar':r.type==='season'?'sun':'chart'} size={20}/></span><div><strong>{r.title}</strong><p>{r.message}</p><small>{r.evidence}</small></div></div>)}</div></div>
      </div>
      <aside className="results-aside">
        <div className="context-card">
          <div className="context-top"><Icon name="calendarClock"/><span>Last Recorded Market Price</span></div>
          <strong>{monthLabel(result.origin_month)}</strong>
          <p>Wholesale price: <b>{money(result.last_observed_price_rs_per_quintal)} / quintal</b></p>
        </div>
      </aside>
    </div>
  </div></main>;
}

function Footer({ onHome, onStart, meta }) {
  return <footer className="site-footer"><div className="container footer-grid"><div><Brand onClick={onHome}/><p>Vegetable price history and future price trends for Karnataka.</p></div><div className="footer-links"><button onClick={onHome}>Home</button><button onClick={onStart}>Price outlooks</button><a href="https://agmarknet.gov.in/" target="_blank" rel="noreferrer">AGMARKNET data source</a><a href="https://open-meteo.com/en/docs/historical-weather-api" target="_blank" rel="noreferrer">Weather methodology</a></div></div><div className="container footer-bottom"><span>© 2026 AgriFuture · Vegetable Price Forecasting</span><span>Observed price data through {meta?.latest_price_month ? monthLabel(meta.latest_price_month) : 'the latest available month'}</span></div></footer>;
}

export default function App() {
  const [page,setPage] = useState('home');
  const [meta,setMeta] = useState(null);
  const [metaError,setMetaError] = useState('');
  const [crop,setCrop] = useState('');
  const [district,setDistrict] = useState('');
  const [month,setMonth] = useState('');
  const [result,setResult] = useState(null);
  const [error,setError] = useState('');
  const [loading,setLoading] = useState(false);

  useEffect(()=>{
    let done=false;
    fetch(`${API}/api/metadata`).then(r=>{if(!r.ok)throw Error('The prediction service is unavailable.');return r.json()})
      .then(data=>{if(done)return;setMeta(data);const first=data.crop_options.find(c=>c.available);setCrop(first?.crop||'');setDistrict(first?.districts?.[0]||'');setMonth(data.available_months?.[0]||'');})
      .catch(err=>{if(!done)setMetaError(`Could not connect to the AgriFuture backend. Start FastAPI and refresh. ${err.message}`)});
    return ()=>{done=true};
  },[]);
  useEffect(()=>{window.scrollTo({top:0,behavior:'instant'});},[page]);
  const goHome=()=>{setPage('home');setError('')};
  const goPredict=()=>{setPage('predict');setError('')};
  async function submit(e){
    e.preventDefault();setError('');setLoading(true);
    try{
      const response=await fetch(`${API}/api/predict`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({crop,district,month})});
      const data=await response.json();
      if(!response.ok)throw Error(typeof data.detail==='string'?data.detail:'Unable to generate a price outlook for that selection.');
      setResult(data);setPage('results');
    }catch(err){setError(err.message || 'Prediction failed. Try again.');}
    finally{setLoading(false)}
  }
  return <div className="app-shell"><Header onHome={goHome} onPredict={goPredict} page={page}/>
    {metaError && <div className="global-error" role="alert"><Icon name="alert" size={18}/>{metaError}</div>}
    {page==='home' && <Home onStart={goPredict} meta={meta}/>} 
    {page==='predict' && <ChoosePage meta={meta} error={error} crop={crop} setCrop={setCrop} district={district} setDistrict={setDistrict} month={month} setMonth={setMonth} onSubmit={submit} loading={loading}/>}
    {page==='results' && result && <Results result={result} onBack={goPredict}/>} 
    <Footer onHome={goHome} onStart={goPredict} meta={meta}/>
  </div>;
}

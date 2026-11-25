// Replaces personal data with codes before you paste a text into an AI tool. Runs only in your browser.
// It catches patterns (emails, phones, ID and account numbers, addresses with a street word). It does NOT know names well.
const RULES = [
  ['EMAIL', /[\w.+-]+@[\w-]+(?:\.[\w-]+)+/g],
  ['NIT', /\b(?:NIT\.?:?\s*)?\d{3}\.?\d{3}\.?\d{3}\s?-\s?\d\b/gi],
  ['CUENTA', /\b(?:cuenta|cta\.?|account)(?:\s+(?:de\s+)?(?:ahorros|corriente|savings|checking))?(?:\s+(?:n[oº°]\.?|número|number|#))?\s*:?\s*\d[\d -]{6,20}\d/gi],
  ['TEL', /(?:\+?57\s?)?\b3\d{2}[\s.-]?\d{3}[\s.-]?\d{4}\b|\(?\b60\d\)?[\s.-]?\d{3}[\s.-]?\d{4}\b/g],
  ['CC', /\b(?:C\.?\s?C\.?|cédula|cedula|c[eé]dula de ciudadan[ií]a|documento|ID)(?:\s+(?:es|n[oº°]\.?|número|#)){0,2}\s*:?\s*\d{1,3}(?:[.\s]?\d{3}){2,3}\b/gi],
  ['DIR', /\b(?:calle|cl\.?|carrera|cra\.?|kr\.?|avenida|av\.?|diagonal|dg\.?|transversal|tv\.?)\s*\d+[a-z]?\s*(?:bis)?\s*(?:#|n[oº°]\.?)\s*\d+[a-z]?\s*-\s*\d+\b/gi],
  ['NOMBRE', /\b(?:Sr\.?|Sra\.?|Señor|Señora|Don|Doña|Dr\.?|Dra\.?)\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,2}/g]];
function mask(text) {
  const key = {}, n = {}; let out = text;
  for (const [tag, re] of RULES) out = out.replace(re, m => {
    if (/^\[\w+-\d+\]$/.test(m)) return m;
    const hit = Object.entries(key).find(([, v]) => v === m); if (hit) return hit[0];
    n[tag] = (n[tag] || 0) + 1; const code = `[${tag}-${n[tag]}]`; key[code] = m; return code; });
  return { out, key };
}
function unmask(text, key) { return text.replace(/\[\w+-\d+\]/g, c => key[c] ?? c); }
if (typeof module !== 'undefined') module.exports = { mask, unmask, RULES };

import { Customer } from '@/types'

export const CUSTOMERS: Record<string, Customer> = {
  A: { key: 'A', name: 'Customer A', address: '123 Main St' },
  B: { key: 'B', name: 'Customer B', address: '456 Elm St' },
  C: { key: 'C', name: 'Customer C', address: '789 Oak St' },
}

export const INITIAL_PRODUCTS = [
  'நாட்டு சக்கரை (Country sugar)',
  'ராகி (Ragi)',
  'ராகி மாவு (Ragi flour)',
  'நாட்டு கம்பு (Country kambu)',
  'நாட்டு கம்பு மாவு (Country kambu flour)',
  'சத்து மாவு (Sattu flour)',
  'மட்ட சம்பா அரிசி (Matta Samba rice)',
  'சிவப்பு கவுணி அரிசி (Red parboiled rice)',
  'சிவப்பு சோளம் (Red corn)',
  'சம்பா அவுள் (Samba bran)',
  'உளுந்தங்களி மாவு (Ulundhu kali flour)',
  'நாட்டு கொண்க்கடலை (Country chickpea)',
  'இடியாப்ப மாவு (Idiyappam flour)',
  'வெள்ளை புட்டு மாவு (White puttu flour)',
  'வெள்ளை நைஸ் அவுள் (White rice bran)',
  'Corn flakes (Corn flakes)',
  'ராகி அவுள் (Ragi bran)',
  'கம்பு அவுள் (Kambu bran)',
  'சோள அவுள் (Corn bran)',
  'கோதுமை அவுள் (Wheat bran)',
  'Red rice அவுள் (Red rice bran)',
  'கொள்ளு அவுள் (Horse gram bran)',
  'வெள்ளை சோளம் (White corn)',
  'சிவப்பு கொள்ளு (Red cowpea)',
  'கருப்பு கொள்ளு (Black cowpea)',
  'உடைத்த கருப்பு உளுந்து (Split black gram)',
  'தட்டைப் பயறு (Thataipayyir)',
  'மாப்பிள்ளை சம்பா அரிசி (Mappillai samba rice)',
  'கைக்குத்தல் அரிசி (Handan sown rice)',
  'அச்சு வெள்ளம் (Palm jaggery)',
  'சிவப்பு அரிசி புட்டு மாவு (Red rice flour for puttu)',
  'சிவப்பு அரிசி இடியாப்ப மாவு (Red rice flour for idiappam)',
  'சிவப்பு அரிசி குருனை (Red rice - Kuruvai variety)',
  'மட்ட சம்பா குருனை (Matta Samba rice - Kuruvai variety)',
  'சிவப்பு நைஸ் அவுள் (Red rice bran)',
  'வெள்ளை கெட்டி அவுள் (White parboiled rice)',
  'சுண்ட வத்தல் (Dried ginger)',
  'மனத்தக்காலி வத்தல் (Bird\'s eye chili)',
  'மோர் மிளகாய் (Yogurt chilies)',
  'மிதுக்கு வத்தல் (Guntur chili)',
  'பட் அப்பளம் (Batten appalam)',
  'Heart Appalam (Heart appalam)',
  'வெங்காய வடகம் (Onion vadai)',
  'கொத்தவரங்காய் வத்தல் (Cluster beans sundried)',
  'அடை மிக்ஸ் (Adai mix)',
  'கடலை மாவு (Gram flour)',
  'மூங்கில் அரிசி (Foxtail millet)',
  'வருத்த வெள்ளை ரவை (Roasted semolina)',
  'கொள்ளுக்கஞ்சி மாவு (Horse gram kanji flour)',
  'கொள்ளு மாவு (Horse gram flour)',
  'பச்சைப் பயறு (Green Gram)',
]

export const API_ENDPOINTS = {
  handwritingRecognition: '/api/v1/handwriting/recognize',
  invoiceAnalysis: '/api/v1/invoice/analyze',
  translation: '/api/v1/translate',
} as const

export const COMPANY_INFO = {
  name: 'SADHASIVA AGENCIES',
  address: '4/53, Bhairavi Nagar, Puliyankulam,',
  city: 'Inamreddiyapatti Post, Virudhunagar - 626 003.',
  phone: 'Cell: 88258 08813, 91596 84261',
} as const

export const DEFAULT_PAGINATION = {
  page: 1,
  limit: 10,
} as const

export const FUZZY_SEARCH_THRESHOLD = 40
export const DEBOUNCE_DELAY = 300
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Wheat, Loader2, AlertTriangle, CheckCircle, TrendingUp, TrendingDown,
  Minus, Thermometer, CloudRain, Wind, ShieldAlert, Lightbulb,
  FlaskConical, Droplets, Bug, BarChart3, Target, Activity,
  ChevronDown, ChevronUp, TriangleAlert, Info, Zap
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer
} from 'recharts';

const dynamicTranslations = {
  // Explanation Keys
  temperature_low: {
    en: "Temperature is below ideal for the crop. Cold stress may reduce yield.",
    hi: "तापमान आदर्श से कम है। ठंड के तनाव से उपज कम हो सकती है।",
    mr: "तापमान आदर्शापेक्षा कमी आहे. थंडीच्या ताणामुळे उत्पादन कमी होऊ शकते."
  },
  temperature_high: {
    en: "Temperature is above the ideal maximum. Heat stress may reduce grain filling.",
    hi: "तापमान आदर्श अधिकतम से ऊपर है। गर्मी के तनाव से दाने भरने में कमी आ सकती है।",
    mr: "तापमान आदर्श कमाल मर्यादेच्या वर आहे. उष्णतेच्या ताणामुळे दाणे भरण्यात अडथळा येऊ शकतो."
  },
  temperature_optimal: {
    en: "Temperature is within the optimal range.",
    hi: "तापमान इष्टतम है।",
    mr: "तापमान अनुकूल मर्यादेत आहे."
  },
  rainfall_low: {
    en: "Rainfall deficit detected. Supplemental irrigation is critical.",
    hi: "वर्षा की कमी। पूरक सिंचाई आवश्यक है।",
    mr: "पावसाची कमतरता. पूरक सिंचन आवश्यक आहे."
  },
  rainfall_high: {
    en: "Excess rainfall may cause waterlogging and increase disease pressure.",
    hi: "अत्यधिक वर्षा से बीमारियों का खतरा बढ़ सकता है।",
    mr: "जास्त पावसामुळे पाणी साचून रोगाचा धोका वाढू शकतो."
  },
  rainfall_optimal: {
    en: "Rainfall is adequate for crop requirements.",
    hi: "वर्षा फसल के लिए पर्याप्त है।",
    mr: "पाऊस पिकाच्या गरजेसाठी पुरेसा आहे."
  },
  humidity_low: {
    en: "Low humidity may cause water stress.",
    hi: "कम आर्द्रता जल तनाव पैदा कर सकती है।",
    mr: "कमी आर्द्रतेमुळे पाण्याचा ताण येऊ शकतो."
  },
  humidity_high: {
    en: "High humidity increases fungal disease risk.",
    hi: "उच्च आर्द्रता फंगल रोगों के जोखिम को बढ़ाती है।",
    mr: "जास्त आर्द्रतेमुळे बुरशीजन्य आजारांचा धोका वाढतो."
  },
  humidity_optimal: {
    en: "Humidity is within the acceptable range.",
    hi: "आर्द्रता स्वीकार्य है।",
    mr: "आर्द्रता योग्य मर्यादेत आहे."
  },
  season_optimal: {
    en: "The current season is highly suitable.",
    hi: "वर्तमान मौसम उपयुक्त है।",
    mr: "सध्याचा हंगाम अनुकूल आहे."
  },
  season_suboptimal: {
    en: "The selected season is not ideal for this crop.",
    hi: "चयनित मौसम आदर्श नहीं है।",
    mr: "निवडलेला हंगाम योग्य नाही."
  },
  season_unknown: {
    en: "No strong season preference data available.",
    hi: "कोई मौसम डेटा उपलब्ध नहीं है।",
    mr: "हंगामाच्या पसंतीचा कोणताही डेटा उपलब्ध नाही."
  },
  year_trend_optimal: {
    en: "Recent year benefits from modern cultivar adoption.",
    hi: "आधुनिक खेती अपनाने से लाभ।",
    mr: "आधुनिक लागवड पद्धतींचा फायदा."
  },
  year_trend_neutral: {
    en: "Moderate technology adoption expected.",
    hi: "मध्यम तकनीक अपनाने की उम्मीद है।",
    mr: "मध्यम तंत्रज्ञानाचा वापर अपेक्षित आहे."
  },

  // Alert Keys
  LOW_RAINFALL: {
    en: "Low rainfall detected. Drought risk elevated.",
    hi: "कम वर्षा। सूखे का जोखिम बढ़ा।",
    mr: "कमी पाऊस. दुष्काळाचा धोका."
  },
  SEVERE_DROUGHT_RISK: {
    en: "Severe drought risk. Immediate irrigation required.",
    hi: "गंभीर सूखे का जोखिम। तत्काल सिंचाई आवश्यक है।",
    mr: "तीव्र दुष्काळाचा धोका. तातडीने सिंचन आवश्यक."
  },
  HIGH_HEAT_STRESS: {
    en: "Extreme heat warning. Yield reduction possible.",
    hi: "अत्यधिक गर्मी की चेतावनी। उपज में कमी संभव है।",
    mr: "अति उष्णतेचा इशारा. उत्पादनात घट शक्य."
  },
  MILD_HEAT_STRESS: {
    en: "Mild heat stress. Use mulching if possible.",
    hi: "हल्की गर्मी का तनाव।",
    mr: "सौम्य उष्णतेचा ताण."
  },
  FROST_WARNING: {
    en: "Frost warning. Cold stress likely.",
    hi: "पाले की चेतावनी। ठंड का तनाव संभव है।",
    mr: "दव पडण्याची चेतावणी. थंडीचा ताण येण्याची शक्यता."
  },
  HIGH_DISEASE_RISK: {
    en: "High humidity indicates possible fungal disease.",
    hi: "उच्च आर्द्रता से फंगल बीमारी की संभावना।",
    mr: "जास्त आर्द्रतेमुळे बुरशीजन्य आजाराची शक्यता."
  },
  ELEVATED_DISEASE_RISK: {
    en: "Elevated disease risk detected.",
    hi: "बढ़ी हुई बीमारी का जोखिम।",
    mr: "रोगाचा धोका वाढला आहे."
  },
  WATERLOGGING_WARNING: {
    en: "Waterlogging risk. Improve drainage.",
    hi: "जलभराव का जोखिम। जल निकासी में सुधार करें।",
    mr: "पाणी साचण्याचा धोका. निचरा सुधारा."
  },
  YIELD_BELOW_REGIONAL_AVERAGE: {
    en: "Predicted yield is below the regional average.",
    hi: "तुलनात्मक उपज क्षेत्रीय औसत से कम है।",
    mr: "अपेक्षित उत्पादन प्रादेशिक सरासरीपेक्षा कमी आहे."
  },
  HIGH_PRODUCTION_RISK: {
    en: "High production risk. Consider immediate mitigations.",
    hi: "उच्च उत्पादन जोखिम। तत्काल शमन पर विचार करें।",
    mr: "उच्च उत्पादन जोखीम. तातडीच्या उपाययोजना करा."
  },
  YIELD_ABOVE_REGIONAL_AVERAGE: {
    en: "Yield is tracking above regional averages.",
    hi: "उपज क्षेत्रीय औसत से ऊपर है।",
    mr: "उत्पादन प्रादेशिक सरासरीच्या वर आहे."
  }
};

// ─── Data ───────────────────────────────────────────────────────────────────

const CROPS = [
  'Rice', 'Wheat', 'Maize', 'Barley', 'Bajra', 'Jowar', 'Sugarcane',
  'Cotton(lint)', 'Groundnut', 'Soyabean', 'Sunflower', 'Potato',
  'Onion', 'Banana', 'Coconut', 'Arhar/Tur', 'Gram', 'Jute',
  'Turmeric', 'Ginger', 'Ragi', 'Linseed', 'Sesamum'
];

const STATES = [
  'Andhra Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Gujarat',
  'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir', 'Jharkhand',
  'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan',
  'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh',
  'Uttarakhand', 'West Bengal'
];

const SEASONS = ['Kharif', 'Rabi', 'Whole Year', 'Autumn', 'Summer', 'Winter'];

// ─── Helper components ────────────────────────────────────────────────────────

const SectionLabel = ({ icon: Icon, text, color = 'text-amber-500' }) => (
  <h3 className={`text-[10px] font-bold uppercase tracking-[0.2em] mb-4 flex items-center gap-2 ${color}`}>
    <Icon className="w-3.5 h-3.5" /> {text}
  </h3>
);

const StatPill = ({ label, value, color }) => (
  <div className="flex flex-col gap-1">
    <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500">{label}</span>
    <span className={`text-xs font-bold ${color}`}>{value}</span>
  </div>
);

const yieldColor = (level) => ({
  HIGH:   { text: 'text-emerald-400', border: 'border-emerald-500/40', bg: 'bg-emerald-500/15', glow: 'rgba(52,211,153,0.3)' },
  MEDIUM: { text: 'text-amber-400',   border: 'border-amber-500/40',   bg: 'bg-amber-500/15',   glow: 'rgba(251,191,36,0.3)' },
  LOW:    { text: 'text-rose-400',    border: 'border-rose-500/40',    bg: 'bg-rose-500/15',    glow: 'rgba(251,113,133,0.3)'  },
}[level] || { text: 'text-slate-400', border: 'border-white/10', bg: 'bg-white/5', glow: 'transparent' });

const riskColor = (level) => ({
  HIGH:   'text-rose-400',
  MEDIUM: 'text-amber-400',
  LOW:    'text-emerald-400',
}[level] || 'text-slate-400');

const severityStyle = (s) => ({
  CRITICAL: 'border-rose-500/40 bg-rose-500/10 text-rose-300',
  WARNING:  'border-amber-500/40 bg-amber-500/10 text-amber-300',
  INFO:     'border-sky-500/40 bg-sky-500/10 text-sky-300',
}[s] || 'border-white/10 bg-white/5 text-slate-300');

const SeverityIcon = ({ s }) => ({
  CRITICAL: <TriangleAlert className="w-4 h-4 shrink-0 text-rose-400" />,
  WARNING:  <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />,
  INFO:     <Info className="w-4 h-4 shrink-0 text-sky-400" />,
}[s] || null);

const factorStatusDot = (status) => ({
  optimal:    'bg-emerald-400',
  low:        'bg-rose-400',
  high:       'bg-amber-400',
  suboptimal: 'bg-orange-400',
  unknown:    'bg-slate-500',
}[status] || 'bg-slate-500');

// ─── Custom Tooltip for Recharts ─────────────────────────────────────────────
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-card !rounded-xl !p-3 text-xs !bg-slate-900/90">
      <p className="text-slate-400 mb-1 uppercase tracking-wider">{label}</p>
      <p className="text-amber-400 font-bold">{Number(payload[0].value).toLocaleString()} hg/ha</p>
    </div>
  );
};

// ─── Sub-cards ────────────────────────────────────────────────────────────────

const YieldHeroCard = ({ result }) => {
  const c = yieldColor(result.yield_level);
  const yieldTons = (result.predicted_yield / 10000).toFixed(2);
  const { t } = useTranslation();
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-card p-8 relative overflow-hidden"
      style={{ boxShadow: `0 0 60px ${c.glow}` }}
    >
      <div className={`absolute inset-0 blur-[80px] pointer-events-none opacity-20`}
        style={{ background: c.glow }} />
      <div className="relative z-10 flex flex-col sm:flex-row items-center gap-8">
        {/* Yield number */}
        <div className="flex-1 text-center sm:text-left">
          <div className="flex items-center justify-center sm:justify-start gap-2 mb-3 text-amber-500">
            <CheckCircle className="w-4 h-4" />
            <span className="text-[10px] font-bold uppercase tracking-[0.2em]">{t('yield_ready_badge')}</span>
          </div>
          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">{t('yield_estimated')}</p>
          <div className="flex items-baseline gap-3 justify-center sm:justify-start">
            <span className="text-7xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-amber-200 tabular-nums">
              {Number(result.predicted_yield).toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </span>
            <span className="text-lg font-bold text-amber-500/60 tracking-widest">HG/HA</span>
          </div>
          <p className="text-slate-400 text-sm mt-1">≈ <span className="text-white font-semibold">{yieldTons}</span> {t('yield_tonnes')}</p>
        </div>

        <div className="w-px h-28 bg-white/10 hidden sm:block" />

        {/* Meta */}
        <div className="flex flex-col gap-5 min-w-[160px]">
          <div>
            <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-2">{t('yield_level')}</p>
            <span className={`inline-flex px-3 py-1.5 rounded-lg text-xs font-black tracking-widest uppercase border ${c.bg} ${c.border} ${c.text}`}>
              {result.yield_level}
            </span>
          </div>
          <div>
            <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-2">Crop · State</p>
            <p className="text-white text-sm font-semibold">{result.crop}</p>
            <p className="text-slate-400 text-xs">{result.area}</p>
          </div>
          <div>
            <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-2">Season · Year</p>
            <p className="text-white text-sm font-semibold">{result.season} {result.year}</p>
          </div>
        </div>
      </div>

      {/* Weather strip */}
      <div className="relative z-10 mt-8 pt-6 border-t border-white/5 flex flex-wrap gap-6">
        <div className="flex items-center gap-2 text-slate-300">
          <Thermometer className="w-4 h-4 text-orange-400" />
          <span className="text-xs">{result.weather?.temperature}°C</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <CloudRain className="w-4 h-4 text-sky-400" />
          <span className="text-xs">{result.weather?.rainfall} mm rainfall</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <Wind className="w-4 h-4 text-teal-400" />
          <span className="text-xs">{result.weather?.humidity}% humidity</span>
        </div>
        <span className="ml-auto text-[9px] text-slate-600 uppercase tracking-widest">
          {t('yield_weather_src')}: {result.weather?.source}
        </span>
      </div>
    </motion.div>
  );
};

const ComparisonCard = ({ comparison }) => {
  const { t } = useTranslation();
  if (!comparison) return null;
  const isAbove = comparison.status === 'ABOVE_AVERAGE';
  const isBelow = comparison.status === 'BELOW_AVERAGE';
  const TrendIcon = isAbove ? TrendingUp : isBelow ? TrendingDown : Minus;
  const color = isAbove ? 'text-emerald-400' : isBelow ? 'text-rose-400' : 'text-amber-400';
  const pct = Math.abs(comparison.difference_percent);
  const barFill = Math.min(100, 50 + (comparison.difference_percent / 2));

  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
      className="glass-card p-6">
      <SectionLabel icon={BarChart3} text={t('section_comparison')} />
      <div className="flex items-center gap-3 mb-5">
        <TrendIcon className={`w-8 h-8 ${color}`} />
        <div>
          <p className={`text-lg font-black ${color}`}>
            {isAbove ? '+' : isBelow ? '-' : ''}{pct.toFixed(1)}%
          </p>
          <p className="text-xs text-slate-400">{comparison.label}</p>
        </div>
      </div>
      {/* Visual bar */}
      <div className="relative h-2 bg-white/5 rounded-full overflow-hidden mb-4">
        <div className="absolute top-1/2 -translate-y-1/2 left-1/2 w-px h-4 bg-white/20" />
        <motion.div
          initial={{ width: '50%' }}
          animate={{ width: `${barFill}%` }}
          transition={{ delay: 0.3, duration: 0.8, ease: 'easeOut' }}
          className={`h-full rounded-full ${isAbove ? 'bg-emerald-500' : isBelow ? 'bg-rose-500' : 'bg-amber-500'}`}
        />
      </div>
      <div className="flex justify-between text-[9px] text-slate-600 uppercase tracking-wider mb-4">
        <span>{t('comparison_below_avg')}</span><span>{t('comparison_region_avg')}</span><span>{t('comparison_above_avg')}</span>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <StatPill label={t('comparison_your_yield')} value={`${Number(comparison.difference + comparison.region_average).toLocaleString()}`} color="text-white" />
        <StatPill label={t('comparison_difference')} value={comparison.difference > 0 ? `+${Number(comparison.difference).toLocaleString()}` : Number(comparison.difference).toLocaleString()} color={color} />
        <StatPill label={t('comparison_avg')} value={Number(comparison.region_average).toLocaleString()} color="text-slate-300" />
      </div>
    </motion.div>
  );
};

const TrendCard = ({ trend }) => {
  const { t } = useTranslation();
  if (!trend?.data) return null;
  const chartData = trend.data.years.map((y, i) => ({ year: y, yield: trend.data.yields[i] }));
  const insightColor = {
    IMPROVING: 'text-emerald-400', DECLINING: 'text-rose-400',
    STABLE: 'text-amber-400', VOLATILE: 'text-orange-400'
  }[trend.insight] || 'text-slate-400';
  const InsightIcon = {
    IMPROVING: TrendingUp, DECLINING: TrendingDown, STABLE: Minus, VOLATILE: Activity
  }[trend.insight] || Activity;

  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
      className="glass-card p-6">
      <div className="flex items-center justify-between mb-5">
        <SectionLabel icon={TrendingUp} text={t('section_trend')} />
        <div className="flex items-center gap-2">
          <InsightIcon className={`w-4 h-4 ${insightColor}`} />
          <span className={`text-xs font-bold uppercase tracking-wider ${insightColor}`}>{trend.insight}</span>
        </div>
      </div>
      <div className="h-52">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 5, right: 10, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
            <XAxis dataKey="year" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} dy={8} />
            <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false}
              tickFormatter={v => `${(v / 1000).toFixed(0)}k`} width={36} />
            <Tooltip content={<CustomTooltip />} />
            <Area type="monotone" dataKey="yield" stroke="#f59e0b" strokeWidth={2.5}
              fill="url(#trendGrad)" dot={{ fill: '#f59e0b', r: 4, strokeWidth: 0 }}
              activeDot={{ r: 6, fill: '#fbbf24' }} animationDuration={1500} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 flex gap-6 text-[10px] text-slate-500">
        <span>{t('trend_change')}: <span className={insightColor}>{trend.change_pct > 0 ? '+' : ''}{trend.change_pct?.toFixed(1)}%</span></span>
        <span>{t('trend_recent')}: <span className={insightColor}>{trend.recent_trend}</span></span>
        <span className="ml-auto">{trend.data.source === 'state' ? t('trend_state_data') : t('trend_national_est')}</span>
      </div>
    </motion.div>
  );
};

const AlertsCard = ({ alerts }) => {
  const { t, i18n } = useTranslation();
  if (!alerts?.length) return null;
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
      className="glass-card p-6">
      <SectionLabel icon={Zap} text={`${t('section_alerts')} (${alerts.length})`} color="text-rose-400" />
      <div className="flex flex-col gap-2">
        {alerts.map((a, i) => {
          const dynamicMsg = dynamicTranslations[a.code] ? dynamicTranslations[a.code][i18n.language] : a.message;
          return (
          <div key={i}
            className={`flex items-start gap-3 p-3 rounded-xl border text-sm ${severityStyle(a.severity)}`}>
            <SeverityIcon s={a.severity} />
            <div className="flex-1 min-w-0">
              <span className="text-[9px] font-bold uppercase tracking-widest opacity-60 block">{a.severity}</span>
              <p className="text-xs leading-relaxed">{dynamicMsg}</p>
            </div>
          </div>
        )})}
      </div>
    </motion.div>
  );
};

const ExplanationCard = ({ explanation }) => {
  const { t, i18n } = useTranslation();
  const [open, setOpen] = useState(false);
  if (!explanation) return null;
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}
      className="glass-card p-6">
      <div className="flex items-center justify-between cursor-pointer" onClick={() => setOpen(o => !o)}>
        <SectionLabel icon={Lightbulb} text={t('section_explanation')} color="text-sky-400" />
        {open ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
      </div>
      <p className="text-sm text-slate-300 mb-4 leading-relaxed">{explanation.summary}</p>
      <AnimatePresence>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
            <div className="flex flex-col gap-2 mt-2">
              {explanation.factors?.map((f, i) => {
                 const key = `${f.factor.toLowerCase().replace(' ', '_')}_${f.status}`;
                 const dynamicMsg = dynamicTranslations[key] ? dynamicTranslations[key][i18n.language] : f.message;
                 return (
                <div key={i}
                  className="flex items-start gap-3 p-3 bg-white/3 rounded-xl border border-white/5 hover:border-sky-500/20 transition-colors">
                  <span className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${factorStatusDot(f.status)}`} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between flex-wrap gap-2 mb-0.5">
                      <span className="text-xs font-bold text-slate-200">{f.factor}</span>
                      <span className="text-[9px] text-slate-500">{f.value} · ideal {f.ideal}</span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed">{dynamicMsg}</p>
                  </div>
                </div>
              )})}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const RecommendationsCard = ({ recommendations }) => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  if (!recommendations) return null;
  const { fertilizer, irrigation, pest_disease, best_practices, priority } = recommendations;
  const priorityColor = { IMMEDIATE: 'text-rose-400', MODERATE: 'text-amber-400', ROUTINE: 'text-emerald-400' }[priority] || 'text-slate-400';

  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
      className="glass-card p-6">
      <div className="flex items-center justify-between cursor-pointer" onClick={() => setOpen(o => !o)}>
        <SectionLabel icon={FlaskConical} text={t('section_recommendations')} color="text-emerald-400" />
        <div className="flex items-center gap-2">
          <span className={`text-[9px] font-bold uppercase tracking-widest ${priorityColor}`}>{priority}</span>
          {open ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
        </div>
      </div>

      {/* Best practices always visible */}
      <div className="grid sm:grid-cols-2 gap-2 mb-2">
        {best_practices?.slice(0, 4).map((p, i) => (
          <div key={i} className="flex gap-2 text-xs text-slate-400 bg-white/3 p-3 rounded-xl border border-white/5">
            <span className="text-emerald-500 text-base leading-none">•</span>
            <span>{p}</span>
          </div>
        ))}
      </div>

      <AnimatePresence>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
            <div className="mt-4 space-y-4">
              {/* Fertilizer */}
              <div className="bg-white/3 rounded-xl p-4 border border-white/5">
                <div className="flex items-center gap-2 mb-3">
                  <FlaskConical className="w-3.5 h-3.5 text-amber-400" />
                  <span className="text-[9px] font-bold text-amber-400 uppercase tracking-widest">{t('rec_fertilizer')}</span>
                </div>
                <div className="flex gap-4 mb-2">
                  {[['N', fertilizer?.N_kg_per_ha], ['P', fertilizer?.P_kg_per_ha], ['K', fertilizer?.K_kg_per_ha]].map(([k, v]) => (
                    <div key={k} className="text-center">
                      <p className="text-lg font-black text-white">{v}</p>
                      <p className="text-[9px] text-slate-500">{k} kg/ha</p>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-slate-400">{fertilizer?.timing}</p>
                <p className="text-xs text-slate-500 mt-1 italic">{fertilizer?.note}</p>
              </div>

              {/* Irrigation */}
              <div className="bg-white/3 rounded-xl p-4 border border-white/5">
                <div className="flex items-center gap-2 mb-2">
                  <Droplets className="w-3.5 h-3.5 text-sky-400" />
                  <span className="text-[9px] font-bold text-sky-400 uppercase tracking-widest">{t('rec_irrigation')}</span>
                  <span className={`ml-auto text-[9px] uppercase font-bold ${
                    irrigation?.status === 'deficit' ? 'text-rose-400' :
                    irrigation?.status === 'surplus' ? 'text-amber-400' : 'text-emerald-400'
                  }`}>{irrigation?.status}</span>
                </div>
                <p className="text-xs text-slate-400">{irrigation?.advice}</p>
              </div>

              {/* Pest watch */}
              {pest_disease?.length > 0 && (
                <div className="bg-white/3 rounded-xl p-4 border border-white/5">
                  <div className="flex items-center gap-2 mb-3">
                    <Bug className="w-3.5 h-3.5 text-orange-400" />
                    <span className="text-[9px] font-bold text-orange-400 uppercase tracking-widest">{t('rec_pest')}</span>
                  </div>
                  <div className="flex flex-col gap-1.5">
                    {pest_disease.map((p, i) => (
                      <div key={i} className="flex items-center justify-between text-xs">
                        <span className="text-slate-300 font-medium">{p.name}</span>
                        <span className={`text-[9px] uppercase font-bold px-2 py-0.5 rounded-full ${
                          p.risk === 'high' ? 'bg-rose-500/20 text-rose-400' :
                          p.risk === 'moderate' ? 'bg-amber-500/20 text-amber-400' :
                          'bg-slate-700 text-slate-400'
                        }`}>{p.risk}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const RiskCard = ({ risk }) => {
  const { t } = useTranslation();
  if (!risk) return null;
  const score = risk.risk_score ?? 0;
  const color = riskColor(risk.overall_risk);
  const barColor = risk.overall_risk === 'HIGH' ? 'bg-rose-500' : risk.overall_risk === 'MEDIUM' ? 'bg-amber-500' : 'bg-emerald-500';

  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }}
      className="glass-card p-6">
      <SectionLabel icon={ShieldAlert} text="Risk Assessment" color="text-rose-400" />
      <div className="flex items-center gap-4 mb-5">
        <div className="relative w-20 h-20 shrink-0">
          <svg viewBox="0 0 36 36" className="w-20 h-20 -rotate-90">
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="3" />
            <circle cx="18" cy="18" r="15.9" fill="none"
              stroke={risk.overall_risk === 'HIGH' ? '#f43f5e' : risk.overall_risk === 'MEDIUM' ? '#f59e0b' : '#10b981'}
              strokeWidth="3" strokeDasharray={`${score} ${100 - score}`}
              strokeLinecap="round" className="transition-all duration-1000" />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-lg font-black ${color}`}>{score}</span>
            <span className="text-[8px] text-slate-500">/100</span>
          </div>
        </div>
        <div>
          <p className={`text-2xl font-black ${color}`}>{risk.overall_risk}</p>
          <p className="text-xs text-slate-400 mt-1">{t('risk_overall')}</p>
        </div>
      </div>

      {/* Risk bar */}
      <div className="h-1.5 bg-white/5 rounded-full overflow-hidden mb-5">
        <motion.div initial={{ width: 0 }} animate={{ width: `${score}%` }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className={`h-full rounded-full ${barColor}`} />
      </div>

      {/* Factor breakdown */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        {risk.risk_factors?.map((f, i) => (
          <div key={i} className="flex items-center justify-between text-xs bg-white/3 px-3 py-2 rounded-lg border border-white/5">
            <span className="text-slate-400">{f.risk}</span>
            <span className={
              f.severity === 'HIGH' ? 'text-rose-400 font-bold' :
              f.severity === 'MEDIUM' ? 'text-amber-400 font-bold' : 'text-emerald-400'
            }>{f.severity}</span>
          </div>
        ))}
      </div>

      {/* Mitigation */}
      {risk.mitigation?.length > 0 && (
        <div>
          <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-2">{t('risk_mitigation')}</p>
          <div className="flex flex-col gap-2">
            {risk.mitigation.map((m, i) => (
              <div key={i} className="flex gap-2 text-xs text-slate-400">
                <Target className="w-3 h-3 shrink-0 mt-0.5 text-rose-400" />
                <span>{m}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
};

// ─── Main Component ────────────────────────────────────────────────────────────

const Yield = () => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({ crop: 'Rice', state: 'Punjab', season: 'Kharif', year: 2022 });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const val = e.target.name === 'year' ? parseInt(e.target.value, 10) : e.target.value;
    setFormData(p => ({ ...p, [e.target.name]: val }));
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch('http://127.0.0.1:8000/predict-yield-v2/full', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail?.message || data?.detail || 'Prediction failed');
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to connect to AI API.');
    } finally {
      setLoading(false);
    }
  };

  const intel = result?.intelligence || {};

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -30 }}
      className="p-6 lg:p-10 max-w-7xl mx-auto text-slate-100 relative z-10 space-y-10 pb-24"
    >
      {/* Header */}
      <div className="text-center">
        <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
          className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-[0_0_30px_rgba(245,158,11,0.5)]">
          <Wheat className="w-8 h-8 text-white" />
        </motion.div>
        <h1 className="text-4xl font-extrabold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">
          {t('yield_page_title')}
        </h1>
        <p className="text-slate-500 text-xs uppercase tracking-[0.2em]">
          {t('yield_page_subtitle')}
        </p>
      </div>

      <div className="grid lg:grid-cols-12 gap-6">

        {/* ── Input Form ──────────────────────────────────────── */}
        <motion.div initial={{ opacity: 0, x: -40 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}
          className="lg:col-span-4">
          <div className="glass-card p-7 h-full relative overflow-hidden">
            <div className="absolute inset-0 bg-amber-500/5 blur-[60px] pointer-events-none" />
            <form onSubmit={handlePredict} className="relative z-10 space-y-5">
              <SectionLabel icon={Wheat} text={t('yield_form_title')} />

              {[
                { label: t('yield_form_crop'), name: 'crop', options: CROPS },
                { label: t('yield_form_state'), name: 'state', options: STATES },
                { label: t('yield_form_season'), name: 'season', options: SEASONS },
              ].map(({ label, name, options }) => (
                <div key={name}>
                  <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-2">{label}</label>
                  <select name={name} value={formData[name]} onChange={handleChange}
                    className="glowing-input !py-3 !text-sm focus:ring-amber-500/50 appearance-none bg-slate-900">
                    {options.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                </div>
              ))}

              <div>
                <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-widest mb-2">{t('yield_form_year')}</label>
                <input type="number" name="year" value={formData.year} onChange={handleChange}
                  min="2000" max="2030"
                  className="glowing-input !py-3 !text-sm focus:ring-amber-500/50 font-mono" />
              </div>

              <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                type="submit" disabled={loading}
                className={`w-full py-4 mt-2 bg-gradient-to-r from-amber-600 to-orange-500 text-white rounded-xl 
                  shadow-[0_10px_20px_rgba(245,158,11,0.3)] hover:shadow-[0_15px_30px_rgba(245,158,11,0.5)] 
                  transition-all font-bold uppercase tracking-widest text-xs flex items-center justify-center gap-3 
                  border border-amber-400/30 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}>
                {loading ? <Loader2 className="animate-spin w-4 h-4" /> : <Wheat className="w-4 h-4" />}
                {loading ? t('yield_btn_loading') : t('yield_btn_predict')}
              </motion.button>
            </form>
          </div>
        </motion.div>

        {/* ── Right: Results ──────────────────────────────────── */}
        <div className="lg:col-span-8 flex flex-col gap-6">

          {/* Error */}
          <AnimatePresence>
            {error && (
              <motion.div key="error" initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="glass-card !bg-rose-500/10 !border-rose-500/30 p-5 flex gap-3 text-rose-200">
                <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-wider mb-1">{t('error_prediction')}</p>
                  <p className="text-sm">{error}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Placeholder */}
          {!result && !loading && !error && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="glass-card p-12 flex flex-col items-center justify-center text-center border-dashed !bg-white/2 min-h-[280px]">
              <Wheat className="w-12 h-12 text-slate-700 mb-4" />
              <p className="text-slate-500 text-xs uppercase tracking-widest max-w-xs">
                {t('yield_placeholder')}
              </p>
            </motion.div>
          )}

          {/* Results */}
          <AnimatePresence>
            {result && (
              <motion.div key="result" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col gap-5">

                {/* Row 1: Yield hero */}
                <YieldHeroCard result={result} />

                {/* Row 2: Comparison + Trend side by side on large screens */}
                <div className="grid md:grid-cols-2 gap-5">
                  <ComparisonCard comparison={result.comparison} />
                  <TrendCard trend={result.trend} />
                </div>

                {/* Row 3: Alerts (full width) */}
                <AlertsCard alerts={result.alerts} />

                {/* Row 4: Explanation + Risk side by side */}
                <div className="grid md:grid-cols-2 gap-5">
                  <ExplanationCard explanation={intel.explanation} />
                  <RiskCard risk={intel.risk} />
                </div>

                {/* Row 5: Recommendations (full width) */}
                <RecommendationsCard recommendations={intel.recommendations} />

              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
};

export default Yield;

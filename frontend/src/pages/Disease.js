import React, { useState, useRef } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import {
    UploadCloud, Leaf, Activity, Loader2, AlertTriangle, CheckCircle,
    ShieldCheck, ShieldAlert, ShieldX, Info, Beaker, Bug,
    ThermometerSun, Eye, Layers, Image as ImageIcon, ChevronRight,
    Zap, Heart, Microscope, Pill, TreeDeciduous, AlertOctagon,
    Lightbulb, TriangleAlert
} from 'lucide-react';

/* ═══════════════════════════════════════════════════
   HELPER: Severity color mapping
   ═══════════════════════════════════════════════════ */
const getSeverityColor = (level) => {
    const l = (level || '').toLowerCase();
    if (l.includes('severe') || l.includes('high')) return { bg: 'from-red-500/20 to-red-600/10', border: 'border-red-500/40', text: 'text-red-400', bar: 'from-red-600 to-red-400', glow: 'rgba(239,68,68,0.4)' };
    if (l.includes('moderate')) return { bg: 'from-amber-500/20 to-amber-600/10', border: 'border-amber-500/40', text: 'text-amber-400', bar: 'from-amber-600 to-amber-400', glow: 'rgba(245,158,11,0.4)' };
    return { bg: 'from-emerald-500/20 to-emerald-600/10', border: 'border-emerald-500/40', text: 'text-emerald-400', bar: 'from-emerald-600 to-emerald-400', glow: 'rgba(16,185,129,0.4)' };
};

const getConfidenceColor = (conf) => {
    if (conf >= 75) return 'text-emerald-400';
    if (conf >= 50) return 'text-amber-400';
    return 'text-red-400';
};

const getRiskIcon = (level) => {
    const l = (level || '').toLowerCase();
    if (l.includes('high')) return <ShieldX className="w-5 h-5 text-red-400 drop-shadow-[0_0_6px_currentColor]" />;
    if (l.includes('moderate')) return <ShieldAlert className="w-5 h-5 text-amber-400 drop-shadow-[0_0_6px_currentColor]" />;
    return <ShieldCheck className="w-5 h-5 text-emerald-400 drop-shadow-[0_0_6px_currentColor]" />;
};

/* ═══════════════════════════════════════════════════
   STAGGER ANIMATION VARIANTS
   ═══════════════════════════════════════════════════ */
const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.12, delayChildren: 0.1 } }
};

const itemVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.97 },
    visible: { opacity: 1, y: 0, scale: 1, transition: { type: 'spring', stiffness: 300, damping: 24 } }
};

/* ═══════════════════════════════════════════════════
   SUB-COMPONENT: Section Card
   ═══════════════════════════════════════════════════ */
const SectionCard = ({ icon: Icon, title, iconColor = 'text-brand-400', children, className = '' }) => (
    <motion.div variants={itemVariants} className={`relative bg-white/[0.04] backdrop-blur-xl border border-white/10 rounded-2xl p-5 overflow-hidden group hover:border-white/20 transition-all duration-500 ${className}`}>
        <div className="absolute inset-0 bg-gradient-to-br from-brand-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
        <div className="flex items-center gap-3 mb-4 relative z-10">
            <div className="w-9 h-9 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0">
                <Icon className={`w-4.5 h-4.5 ${iconColor} drop-shadow-[0_0_6px_currentColor]`} />
            </div>
            <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest">{title}</h3>
        </div>
        <div className="relative z-10">{children}</div>
    </motion.div>
);

/* ═══════════════════════════════════════════════════
   SUB-COMPONENT: Severity Progress Bar
   ═══════════════════════════════════════════════════ */
const SeverityBar = ({ percentage = 0, level = '' }) => {
    const colors = getSeverityColor(level);
    return (
        <div className="space-y-2">
            <div className="flex justify-between items-center">
                <span className="text-xs text-slate-400 font-semibold uppercase tracking-widest">Infection Area</span>
                <span className={`text-sm font-bold ${colors.text} drop-shadow-[0_0_5px_currentColor]`}>
                    {percentage.toFixed(1)}%
                </span>
            </div>
            <div className="h-2.5 rounded-full bg-white/10 overflow-hidden shadow-inner">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(percentage, 100)}%` }}
                    transition={{ duration: 1.5, delay: 0.3, ease: 'easeOut' }}
                    className={`h-full bg-gradient-to-r ${colors.bar} rounded-full`}
                    style={{ boxShadow: `0 0 15px ${colors.glow}` }}
                />
            </div>
            <div className="flex justify-between items-center">
                <span className={`text-xs font-semibold ${colors.text}`}>{level}</span>
                <span className={`text-xs font-semibold ${colors.text}`}>Risk: {level}</span>
            </div>
        </div>
    );
};

/* ═══════════════════════════════════════════════════
   SUB-COMPONENT: Treatment Tab Panel
   ═══════════════════════════════════════════════════ */
const TreatmentPanel = ({ treatment }) => {
    const [activeTab, setActiveTab] = useState('immediate');
    const tabs = [
        { key: 'immediate', label: 'Immediate', icon: Zap, color: 'text-red-400' },
        { key: 'prevention', label: 'Prevention', icon: ShieldCheck, color: 'text-blue-400' },
        { key: 'organic', label: 'Organic', icon: Leaf, color: 'text-emerald-400' },
    ];
    const items = treatment?.[activeTab] || [];

    return (
        <div>
            <div className="flex gap-1 mb-4 bg-white/5 rounded-xl p-1 border border-white/5">
                {tabs.map(tab => (
                    <button
                        key={tab.key}
                        onClick={() => setActiveTab(tab.key)}
                        className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-semibold tracking-wide transition-all duration-300 ${activeTab === tab.key
                            ? 'bg-white/10 text-white border border-white/10 shadow-lg'
                            : 'text-slate-400 hover:text-slate-300'
                            }`}
                    >
                        <tab.icon className={`w-3.5 h-3.5 ${activeTab === tab.key ? tab.color : ''}`} />
                        {tab.label}
                    </button>
                ))}
            </div>
            <AnimatePresence mode="wait">
                <motion.ul
                    key={activeTab}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    className="space-y-2"
                >
                    {items.map((step, i) => (
                        <li key={i} className="flex gap-3 items-start text-sm text-slate-300 leading-relaxed">
                            <ChevronRight className="w-4 h-4 mt-0.5 text-brand-400 flex-shrink-0" />
                            <span>{step}</span>
                        </li>
                    ))}
                    {items.length === 0 && (
                        <li className="text-sm text-slate-500 italic">No steps available for this category.</li>
                    )}
                </motion.ul>
            </AnimatePresence>
        </div>
    );
};

/* ═══════════════════════════════════════════════════
   SUB-COMPONENT: Top Predictions Mini-Chart
   ═══════════════════════════════════════════════════ */
const TopPredictions = ({ predictions = [] }) => (
    <div className="space-y-2.5">
        {predictions.slice(0, 5).map((pred, i) => (
            <div key={i} className="group/pred">
                <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-medium text-slate-300 truncate max-w-[200px]">{pred.name || pred.disease}</span>
                    <span className={`text-xs font-bold font-mono ${getConfidenceColor(pred.confidence)}`}>
                        {pred.confidence?.toFixed(1)}%
                    </span>
                </div>
                <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${pred.confidence}%` }}
                        transition={{ duration: 1, delay: 0.5 + i * 0.15 }}
                        className={`h-full rounded-full ${i === 0 ? 'bg-gradient-to-r from-brand-600 to-brand-400' : 'bg-white/15'}`}
                        style={i === 0 ? { boxShadow: '0 0 10px rgba(76,175,80,0.5)' } : {}}
                    />
                </div>
            </div>
        ))}
    </div>
);


/* ═══════════════════════════════════════════════════
   MAIN COMPONENT: Disease Analysis Page
   ═══════════════════════════════════════════════════ */
const Disease = () => {
    const { t } = useTranslation();
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [imageView, setImageView] = useState('original');
    const fileRef = useRef(null);

    const handleFileChange = (e) => {
        const selected = e.target.files[0];
        if (selected) {
            setFile(selected);
            setPreview(URL.createObjectURL(selected));
            setResult(null);
            setError(null);
            setImageView('original');
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        const selected = e.dataTransfer.files[0];
        if (selected) {
            setFile(selected);
            setPreview(URL.createObjectURL(selected));
            setResult(null);
            setError(null);
            setImageView('original');
        }
    };

    const handleAnalyze = async () => {
        if (!file) return;
        setLoading(true);
        setError(null);
        setResult(null);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const { data } = await axios.post('http://127.0.0.1:8000/plant-doctor', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                timeout: 30000,
            });
            setResult(data);
            setImageView('original');
        } catch (err) {
            setError(err.response?.data?.detail?.message || err.response?.data?.error || err.message || 'Analysis failed. Ensure the AI server is running.');
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        setFile(null);
        setPreview(null);
        setResult(null);
        setError(null);
        setImageView('original');
    };

    const severity = result?.severity || {};
    const risk = result?.risk || {};
    const explanation = result?.explanation || {};
    const treatment = result?.treatment || {};

    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            className="p-6 lg:p-10 max-w-[1400px] mx-auto text-slate-100 relative z-10"
        >
            {/* ════ HEADER ════ */}
            <div className="mb-10 text-center">
                <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-brand-500 to-emerald-600 flex items-center justify-center shadow-[0_0_30px_rgba(76,175,80,0.5)]"
                >
                    <Microscope className="w-8 h-8 text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]" />
                </motion.div>
                <h1 className="text-4xl font-extrabold mb-3 tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">
                    {t('disease_title')}
                </h1>
                <p className="text-slate-400 font-light tracking-widest text-sm uppercase">
                    {t('disease_subtitle')}
                </p>
            </div>

            {/* ════ MAIN GRID: LEFT + RIGHT ════ */}
            <div className="grid lg:grid-cols-5 gap-8">

                {/* ════════════════════════════════════
                   LEFT PANEL — AI VISUALIZATION (2 cols)
                   ════════════════════════════════════ */}
                <motion.div
                    initial={{ opacity: 0, x: -40 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.15 }}
                    className="lg:col-span-2 flex flex-col gap-5"
                >
                    {/* Section Title */}
                    <div className="mb-1">
                        <h2 className="text-lg font-bold tracking-wide flex items-center gap-2">
                            <Eye className="w-5 h-5 text-brand-400 drop-shadow-[0_0_6px_currentColor]" />
                            {t('disease_localization')}
                        </h2>
                        <p className="text-xs text-slate-500 mt-1 tracking-wide">{t('disease_highlighted')}</p>
                    </div>

                    {/* Image View Toggle (visible only after analysis) */}
                    {result && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex gap-1 bg-white/5 rounded-xl p-1 border border-white/5"
                        >
                            {[
                                { key: 'original', label: 'Original', icon: ImageIcon },
                                { key: 'overlay', label: 'Heatmap Overlay', icon: Layers },
                            ].map(tab => (
                                <button
                                    key={tab.key}
                                    onClick={() => setImageView(tab.key)}
                                    className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-semibold tracking-wide transition-all duration-300 ${imageView === tab.key
                                        ? 'bg-brand-500/20 text-brand-300 border border-brand-500/30 shadow-[0_0_15px_rgba(76,175,80,0.2)]'
                                        : 'text-slate-400 hover:text-white hover:bg-white/5'
                                        }`}
                                >
                                    <tab.icon className="w-3.5 h-3.5" />
                                    {tab.label}
                                </button>
                            ))}
                        </motion.div>
                    )}

                    {/* Image Container */}
                    <div
                        className={`glass-card !rounded-2xl overflow-hidden flex flex-col items-center justify-center relative group cursor-pointer ${!preview ? 'border-2 border-dashed !border-white/20 hover:!border-brand-500' : ''}`}
                        style={{ minHeight: '380px' }}
                        onDragOver={(e) => e.preventDefault()}
                        onDrop={handleDrop}
                        onClick={() => !preview && fileRef.current?.click()}
                    >
                        <input
                            ref={fileRef}
                            type="file"
                            className="hidden"
                            accept="image/*"
                            onChange={handleFileChange}
                        />

                        <AnimatePresence mode="wait">
                            {!preview ? (
                                /* Upload Placeholder */
                                <motion.div
                                    key="upload"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    className="flex flex-col items-center justify-center p-10 text-center"
                                >
                                    <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-5 shadow-[inset_0_0_20px_rgba(255,255,255,0.05)] border border-white/10 group-hover:scale-110 transition-transform duration-300">
                                        <UploadCloud className="w-10 h-10 text-slate-400 group-hover:text-brand-400 drop-shadow-[0_0_10px_currentColor] transition-colors duration-300" />
                                    </div>
                                    <h3 className="text-lg font-bold mb-2 tracking-wide">{t('disease_upload_placeholder')}</h3>
                                    <p className="text-slate-500 text-sm max-w-[260px] font-light leading-relaxed">
                                        {t('disease_upload_desc')}
                                    </p>
                                </motion.div>
                            ) : (
                                /* Image Preview */
                                <motion.div
                                    key={imageView}
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.95 }}
                                    transition={{ duration: 0.3 }}
                                    className="relative w-full h-full"
                                >
                                    <img
                                        src={imageView === 'overlay' && result?.visual_output 
                                            ? `${result.visual_output}?t=${Date.now()}` 
                                            : preview}
                                        alt="Plant leaf analysis"
                                        className="w-full h-full object-contain transition-opacity duration-500"
                                        style={{ minHeight: '350px', maxHeight: '450px' }}
                                    />

                                    {/* Heatmap Info Overlay */}
                                    {imageView === 'overlay' && result && (
                                        <div className="absolute bottom-0 left-0 right-0 p-3 pointer-events-none">
                                            <div className="bg-black/60 backdrop-blur-sm rounded-xl px-4 py-2 text-xs text-slate-300 flex items-center justify-between border border-white/10 shadow-lg">
                                                <div className="flex items-center gap-2">
                                                    <ThermometerSun className="w-4 h-4 text-brand-400" />
                                                    <span className="font-semibold tracking-wide capitalize">Grad-CAM++ Analysis</span>
                                                </div>
                                                <span className="text-brand-300 font-bold">
                                                    Infection Intensity: {severity.percentage?.toFixed(1) || 0}%
                                                </span>
                                            </div>
                                        </div>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Loading Overlay */}
                        {loading && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="absolute inset-0 bg-slate-950/80 backdrop-blur-md flex flex-col items-center justify-center z-20"
                            >
                                <div className="relative mb-5">
                                    <div className="w-16 h-16 rounded-full border-4 border-brand-500/20 border-t-brand-400 animate-spin" />
                                    <Leaf className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 text-brand-400 drop-shadow-[0_0_8px_currentColor]" />
                                </div>
                                <p className="text-brand-300 font-semibold tracking-widest text-sm animate-pulse">{t('disease_analyzing')}</p>
                            </motion.div>
                        )}
                    </div>

                    {/* Heatmap Legend (visible after analysis) */}
                    {result && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.5 }}
                            className="bg-white/[0.03] rounded-xl p-3 border border-white/5"
                        >
                            <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-2 font-semibold">Disease Probability</p>
                            <div className="h-2 rounded-full bg-gradient-to-r from-emerald-500 via-yellow-500 to-red-500" />
                            <div className="flex justify-between mt-1.5">
                                <span className="text-[10px] text-emerald-500 font-semibold">0% Low</span>
                                <span className="text-[10px] text-yellow-500 font-semibold">50%</span>
                                <span className="text-[10px] text-red-500 font-semibold">100% High</span>
                            </div>
                        </motion.div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex gap-3">
                        <motion.button
                            whileHover={{ scale: file && !loading ? 1.02 : 1 }}
                            whileTap={{ scale: file && !loading ? 0.98 : 1 }}
                            disabled={!file || loading}
                            onClick={handleAnalyze}
                            className={`btn-primary flex-1 flex items-center justify-center gap-3 uppercase tracking-widest text-sm ${(!file || loading) && 'opacity-40 cursor-not-allowed !shadow-none'}`}
                        >
                            {loading
                                ? <Loader2 className="animate-spin w-5 h-5" />
                                : <Activity className="w-5 h-5 drop-shadow-[0_0_5px_currentColor]" />
                            }
                            {loading ? t('disease_analyzing') : t('disease_btn_analyze')}
                        </motion.button>

                        {result && (
                            <motion.button
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={handleReset}
                                className="px-5 py-4 rounded-2xl bg-white/5 border border-white/10 text-slate-400 hover:text-white hover:bg-white/10 transition-all text-sm font-semibold tracking-widest uppercase"
                            >
                                {t('disease_btn_new')}
                            </motion.button>
                        )}
                    </div>
                </motion.div>

                {/* ════════════════════════════════════
                   RIGHT PANEL — DIAGNOSTIC REPORT (3 cols)
                   ════════════════════════════════════ */}
                <motion.div
                    initial={{ opacity: 0, x: 40 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.25 }}
                    className="lg:col-span-3"
                >
                    <AnimatePresence mode="wait">

                        {/* ── ERROR STATE ── */}
                        {error && (
                            <motion.div
                                key="error"
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className="glass-card !bg-red-500/10 !border-red-500/30 p-6 flex gap-4 text-red-200 shadow-[0_0_30px_rgba(239,68,68,0.15)]"
                            >
                                <AlertTriangle className="w-6 h-6 shrink-0 drop-shadow-[0_0_5px_currentColor]" />
                                <div>
                                    <h3 className="font-bold tracking-wide mb-1">Analysis Failed</h3>
                                    <p className="text-sm text-red-300/80">{error}</p>
                                </div>
                            </motion.div>
                        )}

                        {/* ── EMPTY PLACEHOLDER ── */}
                        {!result && !error && !loading && (
                            <motion.div
                                key="placeholder"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="glass-card p-14 flex flex-col items-center justify-center text-center border-dashed !bg-white/[0.03]"
                                style={{ minHeight: '500px' }}
                            >
                                <div className="w-24 h-24 rounded-full bg-white/5 flex items-center justify-center mb-6 shadow-[inset_0_0_20px_rgba(255,255,255,0.05)] border border-white/10">
                                    <Leaf className="w-12 h-12 text-slate-600 drop-shadow-[0_0_5px_rgba(255,255,255,0.1)]" />
                                </div>
                                <h3 className="text-xl font-bold mb-3 tracking-wide text-slate-400">{t('disease_report_placeholder_title')}</h3>
                                <p className="text-slate-500 font-light max-w-xs leading-relaxed">
                                    {t('disease_report_placeholder_desc')}
                                </p>
                            </motion.div>
                        )}

                        {/* ── LOADING STATE ── */}
                        {loading && !result && (
                            <motion.div
                                key="loading"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="glass-card p-14 flex flex-col items-center justify-center text-center"
                                style={{ minHeight: '500px' }}
                            >
                                <div className="relative mb-8">
                                    <div className="w-20 h-20 rounded-full border-4 border-brand-500/20 border-t-brand-400 animate-spin" />
                                    <Microscope className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 text-brand-400 drop-shadow-[0_0_10px_currentColor]" />
                                </div>
                                <h3 className="text-lg font-bold text-brand-300 tracking-widest mb-2 animate-pulse">
                                    Analyzing Plant Health
                                </h3>
                                <p className="text-slate-500 text-sm tracking-wide">Running CNN model + Grad-CAM + severity estimation...</p>
                            </motion.div>
                        )}

                        {/* ════════════════════════════════
                           RESULTS — DIAGNOSTIC REPORT
                           ════════════════════════════════ */}
                        {result && (
                            <motion.div
                                key="results"
                                variants={containerVariants}
                                initial="hidden"
                                animate="visible"
                                className="flex flex-col gap-5"
                            >
                                {/* ── 1. DISEASE HEADLINE CARD ── */}
                                <motion.div
                                    variants={itemVariants}
                                    className="glass-card p-6 relative overflow-hidden"
                                >
                                    <div className="absolute top-0 right-0 w-40 h-40 bg-brand-500/10 rounded-full blur-[60px] pointer-events-none" />

                                    <div className="flex items-start gap-5 relative z-10">
                                        {/* Status Icon */}
                                        <motion.div
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            transition={{ type: 'spring', bounce: 0.5, delay: 0.2 }}
                                            className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-500/20 to-brand-600/10 border border-brand-500/30 flex items-center justify-center flex-shrink-0 shadow-[0_0_20px_rgba(76,175,80,0.2)]"
                                        >
                                            {result.disease?.toLowerCase() === 'healthy'
                                                ? <Heart className="w-8 h-8 text-emerald-400 drop-shadow-[0_0_8px_currentColor]" />
                                                : <Bug className="w-8 h-8 text-amber-400 drop-shadow-[0_0_8px_currentColor]" />
                                            }
                                        </motion.div>

                                        {/* Disease Info */}
                                        <div className="flex-1 min-w-0">
                                            <p className="text-xs text-slate-500 uppercase tracking-widest font-semibold mb-1">{result.plant || 'Unknown Plant'}</p>
                                            <h2 className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 mb-2 truncate">
                                                {result.disease || 'Unknown Disease'}
                                            </h2>
                                            <p className="text-sm text-slate-400 leading-relaxed line-clamp-2">
                                                {result.disease_description || ''}
                                            </p>
                                        </div>
                                    </div>

                                    {/* Meta Badges */}
                                    <div className="flex flex-wrap gap-2 mt-5 relative z-10">
                                        {/* Confidence Badge */}
                                        <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-bold tracking-wide ${getConfidenceColor(result.confidence)} bg-white/5 border-white/10`}>
                                            <CheckCircle className="w-3.5 h-3.5" />
                                            {result.confidence?.toFixed(1)}% — {result.confidence_label || ''}
                                        </span>

                                        {/* Source Badge */}
                                        <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs font-bold tracking-wide text-slate-400">
                                            <Beaker className="w-3.5 h-3.5 text-blue-400" />
                                            {result.final_source || 'CNN Model'}
                                        </span>

                                        {/* Status Badge */}
                                        <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs font-bold tracking-wide ${result.status === 'Known' ? 'text-emerald-400' : 'text-amber-400'}`}>
                                            {result.status === 'Known' ? <ShieldCheck className="w-3.5 h-3.5" /> : <ShieldAlert className="w-3.5 h-3.5" />}
                                            {result.status}
                                        </span>
                                    </div>
                                </motion.div>

                                {/* ── 2. SEVERITY & RISK ── */}
                                <SectionCard icon={ThermometerSun} title={t('disease_severity_level')} iconColor={getSeverityColor(severity.level).text}>
                                    <SeverityBar percentage={severity.percentage || 0} level={severity.level || 'Unknown'} />
                                    <div className="mt-4 flex items-center gap-3 bg-white/[0.03] rounded-xl p-3 border border-white/5">
                                        {getRiskIcon(risk.level)}
                                        <div className="flex-1">
                                            <p className="text-xs font-bold text-slate-300">{risk.meaning || ''}</p>
                                            <p className="text-[11px] text-slate-500 mt-0.5">{risk.urgency || ''}</p>
                                        </div>
                                    </div>
                                </SectionCard>

                                {/* ── 3. SUMMARY ── */}
                                {result.summary && (
                                    <SectionCard icon={Info} title={t('disease_summary')} iconColor="text-blue-400">
                                        <p className="text-sm text-slate-300 leading-relaxed">{result.summary}</p>
                                    </SectionCard>
                                )}

                                {/* ── 4. FINAL ADVICE (HIGHLIGHT) ── */}
                                {result.final_advice && (
                                    <motion.div
                                        variants={itemVariants}
                                        className={`relative rounded-2xl p-5 overflow-hidden border bg-gradient-to-r ${getSeverityColor(severity.level).bg} ${getSeverityColor(severity.level).border}`}
                                    >
                                        <div className="flex items-start gap-4">
                                            <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center flex-shrink-0">
                                                <Lightbulb className={`w-5 h-5 ${getSeverityColor(severity.level).text} drop-shadow-[0_0_6px_currentColor]`} />
                                            </div>
                                            <div>
                                                <h3 className="text-sm font-bold uppercase tracking-widest text-slate-300 mb-2">{t('disease_recommended_action')}</h3>
                                                <p className="text-sm text-slate-200 leading-relaxed font-medium">{result.final_advice}</p>
                                            </div>
                                        </div>
                                    </motion.div>
                                )}

                                {/* ── 5. EXPLANATION ── */}
                                {explanation.causes && explanation.causes.length > 0 && (
                                    <SectionCard icon={Microscope} title={t('disease_why_happened')} iconColor="text-purple-400">
                                        <div className="flex flex-wrap gap-2 mb-4">
                                            {explanation.type && (
                                                <span className="text-[11px] px-2.5 py-1 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-300 font-semibold tracking-wide">
                                                    {explanation.type}
                                                </span>
                                            )}
                                            {explanation.pathogen && (
                                                <span className="text-[11px] px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-slate-400 font-semibold italic tracking-wide">
                                                    {explanation.pathogen}
                                                </span>
                                            )}
                                        </div>
                                        <ul className="space-y-2.5">
                                            {explanation.causes.map((cause, i) => (
                                                <li key={i} className="flex gap-3 items-start text-sm text-slate-300 leading-relaxed">
                                                    <div className="w-1.5 h-1.5 rounded-full bg-purple-400 mt-2 flex-shrink-0 shadow-[0_0_5px_rgba(168,85,247,0.6)]" />
                                                    <span>{cause}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </SectionCard>
                                )}

                                {/* ── 6. TREATMENT ── */}
                                {(treatment.immediate?.length > 0 || treatment.prevention?.length > 0 || treatment.organic?.length > 0) && (
                                    <SectionCard icon={Pill} title={t('disease_treatment_plan')} iconColor="text-teal-400">
                                        <TreatmentPanel treatment={treatment} />
                                    </SectionCard>
                                )}

                                {/* ── 7. TOP PREDICTIONS ── */}
                                {result.top_predictions?.length > 0 && (
                                    <SectionCard icon={Activity} title={t('disease_differential_diagnosis')} iconColor="text-sky-400">
                                        <TopPredictions predictions={result.top_predictions} />
                                    </SectionCard>
                                )}

                                {/* ── 8. SIMILAR CASES ── */}
                                {result.similar_cases?.length > 0 && (
                                    <SectionCard icon={TreeDeciduous} title={t('disease_similar_cases')} iconColor="text-green-400">
                                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                            {result.similar_cases.map((c, i) => (
                                                <div key={i} className="bg-white/[0.03] rounded-xl p-3 border border-white/5 text-center">
                                                    <p className="text-sm font-semibold text-slate-300 truncate mb-1">{c.disease || c.label}</p>
                                                    <p className="text-xs text-brand-400 font-bold">{c.similarity_score || `${c.similarity_value?.toFixed(1)}%`}</p>
                                                </div>
                                            ))}
                                        </div>
                                    </SectionCard>
                                )}

                                {/* ── 9. CLIP PREDICTIONS (Unknown fallback) ── */}
                                {result.clip_predictions?.length > 0 && (
                                    <SectionCard icon={Eye} title="CLIP Open-World Analysis" iconColor="text-indigo-400">
                                        <p className="text-xs text-slate-500 mb-3">Zero-shot CLIP predictions for unrecognized disease</p>
                                        <div className="space-y-2">
                                            {result.clip_predictions.map((pred, i) => (
                                                <div key={i} className="flex items-center justify-between bg-white/[0.03] rounded-lg p-3 border border-white/5">
                                                    <span className="text-sm text-slate-300 capitalize">{pred.label}</span>
                                                    <span className="text-sm font-bold text-indigo-400">{pred.confidence?.toFixed(1)}%</span>
                                                </div>
                                            ))}
                                        </div>
                                    </SectionCard>
                                )}

                                {/* ── 10. UNKNOWN MESSAGE ── */}
                                {result.message && (
                                    <motion.div
                                        variants={itemVariants}
                                        className="rounded-2xl p-4 bg-amber-500/10 border border-amber-500/30 flex gap-3 items-start"
                                    >
                                        <AlertOctagon className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5 drop-shadow-[0_0_5px_currentColor]" />
                                        <p className="text-sm text-amber-200 leading-relaxed">{result.message}</p>
                                    </motion.div>
                                )}

                                {/* ── 11. WARNINGS ── */}
                                {result.warnings?.length > 0 && (
                                    <motion.div variants={itemVariants} className="space-y-2">
                                        {result.warnings.map((w, i) => (
                                            <div key={i} className="rounded-xl p-3 bg-amber-500/5 border border-amber-500/20 flex gap-3 items-center">
                                                <TriangleAlert className="w-4 h-4 text-amber-500 flex-shrink-0" />
                                                <p className="text-xs text-amber-300/80">{w}</p>
                                            </div>
                                        ))}
                                    </motion.div>
                                )}

                                {/* ── 12. DIAGNOSIS TIME ── */}
                                <motion.div
                                    variants={itemVariants}
                                    className="text-center py-3"
                                >
                                    <p className="text-[11px] text-slate-600 tracking-widest uppercase">
                                        Diagnosis completed in <span className="text-brand-500 font-bold">{result.diagnosis_time_ms?.toFixed(0)}ms</span>
                                    </p>
                                </motion.div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>
            </div>
        </motion.div>
    );
};

export default Disease;

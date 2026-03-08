import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Droplets, CheckCircle, AlertTriangle, Loader2, Brain, Leaf, Sun, CloudRain, FlaskConical, Layers, Hexagon, Sprout } from 'lucide-react';

const Crop = () => {
    const [formData, setFormData] = useState({
        Nitrogen: 90,
        Phosphorus: 40,
        Potassium: 40,
        Temperature: 28,
        Humidity: 70,
        pH: 6.5,
        Rainfall: 200
    });
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: parseFloat(e.target.value) });
    };

    const handlePredict = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const { data } = await axios.post('http://localhost:5000/api/crop', formData);
            setResult(data);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to initialize array.');
        } finally {
            setLoading(false);
        }
    };

    const fields = [
        { name: 'Nitrogen', icon: Layers, unit: 'kg/ha', color: 'text-soil-400' },
        { name: 'Phosphorus', icon: Hexagon, unit: 'kg/ha', color: 'text-brand-400' },
        { name: 'Potassium', icon: Leaf, unit: 'kg/ha', color: 'text-harvest-400' },
        { name: 'Temperature', icon: Sun, unit: '°C', color: 'text-amber-500' },
        { name: 'Humidity', icon: Droplets, unit: '%', color: 'text-sky-400' },
        { name: 'pH', icon: FlaskConical, unit: 'level', color: 'text-brand-300' },
        { name: 'Rainfall', icon: CloudRain, unit: 'mm', color: 'text-blue-400' }
    ];

    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            className="p-8 lg:p-12 max-w-5xl mx-auto h-full text-slate-100 relative z-10"
        >
            <div className="mb-12 text-center">
                <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-soil-500 to-soil-700 flex items-center justify-center shadow-[0_0_30px_rgba(109,76,65,0.5)]"
                >
                    <Sprout className="w-8 h-8 text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]" />
                </motion.div>
                <h1 className="text-4xl font-extrabold mb-3 tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">Smart Crop Recommendation</h1>
                <p className="text-slate-400 font-light tracking-widest text-sm uppercase">Identify the best crops for your soil and climate.</p>
            </div>

            <div className="grid lg:grid-cols-2 gap-10">
                {/* Form */}
                <motion.div
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="glass-card p-10 relative overflow-hidden group"
                >
                    {/* Subtle glow behind form */}
                    <div className="absolute inset-0 bg-brand-500/10 blur-[80px] pointer-events-none opacity-50 group-hover:opacity-100 transition-opacity duration-1000" />

                    <form onSubmit={handlePredict} className="grid grid-cols-2 gap-6 relative z-10">
                        {fields.map(f => (
                            <div key={f.name} className={f.name === 'Rainfall' ? 'col-span-2' : ''}>
                                <label className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">
                                    <f.icon className={`w-4 h-4 ${f.color} drop-shadow-[0_0_5px_currentColor]`} /> {f.name} <span className="text-slate-500 lowercase opacity-50 ml-auto">({f.unit})</span>
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    name={f.name}
                                    value={formData[f.name]}
                                    onChange={handleChange}
                                    required
                                    className="glowing-input font-mono text-lg tracking-wider"
                                />
                            </div>
                        ))}
                        <div className="col-span-2 pt-6 mt-2 border-t border-white/10">
                            <button
                                type="submit"
                                disabled={loading}
                                className={`btn-primary w-full py-4 rounded-xl transition-all duration-300 font-bold uppercase tracking-widest text-sm flex items-center justify-center gap-3 ${loading && 'opacity-50 cursor-not-allowed shadow-none border-t border-white/5'}`}
                            >
                                {loading ? <Loader2 className="animate-spin w-5 h-5 drop-shadow-[0_0_5px_currentColor]" /> : <Sprout className="w-5 h-5 drop-shadow-[0_0_5px_currentColor]" />}
                                {loading ? 'Analyzing Soil...' : 'Get Recommendation'}
                            </button>
                        </div>
                    </form>
                </motion.div>

                {/* Results */}
                <motion.div
                    initial={{ opacity: 0, x: 50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 }}
                    className="h-full relative"
                >
                    <AnimatePresence mode="wait">
                        {error && (
                            <motion.div
                                key="error"
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.9 }}
                                className="glass-card !bg-red-500/10 !border-red-500/30 p-6 flex gap-4 text-red-200 shadow-[0_0_30px_rgba(239,68,68,0.2)] mb-6"
                            >
                                <AlertTriangle className="w-6 h-6 shrink-0 drop-shadow-[0_0_5px_currentColor]" />
                                <p className="font-medium tracking-wide">{error}</p>
                            </motion.div>
                        )}

                        {!result && !error && !loading && (
                            <motion.div
                                key="placeholder"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="glass-card p-10 flex flex-col items-center justify-center text-center h-[500px] border-dashed !bg-white/5"
                            >
                                <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-6 shadow-[inset_0_0_20px_rgba(255,255,255,0.05)] border border-white/10">
                                    <Sprout className="w-10 h-10 text-slate-500 drop-shadow-[0_0_5px_rgba(255,255,255,0.1)]" />
                                </div>
                                <p className="text-slate-400 font-light tracking-wide max-w-[200px]">Awaiting soil and climate data to generate recommendation.</p>
                            </motion.div>
                        )}

                        {result && (
                            <motion.div
                                key="result"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="glass-card overflow-hidden h-full flex flex-col p-8 relative group overflow-y-auto"
                            >
                                <div className="absolute inset-0 bg-brand-500/10 blur-[80px] pointer-events-none opacity-50 group-hover:opacity-80 transition-opacity" />

                                <div className="flex flex-col items-center justify-center mb-6">
                                    <motion.div
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        transition={{ type: "spring", bounce: 0.5, delay: 0.1 }}
                                        className="w-20 h-20 bg-white/10 rounded-full flex items-center justify-center mb-4 backdrop-blur-md shadow-[0_0_30px_rgba(76,175,80,0.3)] border border-brand-500/50 relative z-10"
                                    >
                                        <CheckCircle className="w-10 h-10 text-brand-400 drop-shadow-[0_0_10px_currentColor]" />
                                    </motion.div>

                                    <div className="w-full text-center relative z-10">
                                        <p className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-2">Recommended Crop</p>
                                        <motion.div
                                            initial={{ opacity: 0, scale: 0.9 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            transition={{ delay: 0.3 }}
                                            className="text-4xl lg:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-brand-300 capitalize drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]"
                                        >
                                            {result.recommended_crop}
                                        </motion.div>
                                    </div>

                                    {result.confidence && (
                                        <div className="w-full max-w-xs relative z-10 mt-4">
                                            <div className="flex justify-between items-end mb-1">
                                                <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Confidence Score</p>
                                                <span className="font-bold text-brand-300 drop-shadow-[0_0_5px_currentColor] text-sm">{result.confidence.toFixed(1)}%</span>
                                            </div>
                                            <div className="h-1.5 rounded-full bg-white/10 overflow-hidden shadow-inner">
                                                <motion.div
                                                    initial={{ width: 0 }}
                                                    animate={{ width: `${result.confidence}%` }}
                                                    transition={{ duration: 1.5, delay: 0.5, ease: "easeOut" }}
                                                    className="h-full bg-gradient-to-r from-brand-500 to-brand-400 rounded-full shadow-[0_0_15px_rgba(76,175,80,0.8)]"
                                                />
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {result.top_recommendations && result.top_recommendations.length > 0 && (
                                    <div className="mt-4 relative z-10 w-full mb-6">
                                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 border-b border-white/10 pb-2">Top Alternatives</h4>
                                        <div className="space-y-3">
                                            {result.top_recommendations.map((rec, i) => (
                                                <div key={i} className="flex items-center justify-between text-sm bg-white/5 p-3 rounded-lg border border-white/5 shadow-sm">
                                                    <span className="font-semibold text-brand-200 capitalize">{rec.crop}</span>
                                                    <span className="text-brand-400 font-mono tracking-widest">{rec.confidence}%</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {result.agronomic_advice && result.agronomic_advice.length > 0 && (
                                    <div className="mt-2 relative z-10 w-full mb-4">
                                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 border-b border-white/10 pb-2">Agronomic Advice</h4>
                                        <ul className="space-y-3">
                                            {result.agronomic_advice.map((advice, i) => (
                                                <li key={i} className="flex gap-3 text-sm text-slate-300 leading-relaxed bg-brand-900/10 p-3 rounded-lg border border-brand-500/10 hover:border-brand-500/30 transition-colors">
                                                    <span className="text-brand-400 shrink-0 mt-0.5">•</span>
                                                    <span>{advice}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {result.ai_advice && (
                                    <motion.div
                                        initial={{ opacity: 0, scale: 0.95 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        transition={{ delay: 0.6 }}
                                        className="mt-6 relative z-10 w-full mb-4"
                                    >
                                        <h4 className="flex items-center gap-2 text-xs font-bold text-amber-300 uppercase tracking-widest mb-3 border-b border-amber-500/20 pb-2 drop-shadow-[0_0_5px_currentColor]">
                                            <Brain className="w-4 h-4 text-amber-400" /> AI Farming Advisor
                                        </h4>
                                        <div className="text-sm text-amber-100/80 leading-relaxed bg-gradient-to-br from-amber-500/10 to-transparent p-5 rounded-xl border border-amber-500/20 shadow-[0_0_20px_rgba(245,158,11,0.05)] whitespace-pre-wrap font-light tracking-wide">
                                            {result.ai_advice}
                                        </div>
                                    </motion.div>
                                )}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>
            </div>
        </motion.div>
    );
};

export default Crop;

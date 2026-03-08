import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Map, CheckCircle, AlertTriangle, Loader2, Thermometer, CloudRain, Sun, TrendingUp, Info, Wheat } from 'lucide-react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area
} from 'recharts';

const Yield = () => {
    const [formData, setFormData] = useState({
        Area: 'India',
        Crop: 'Rice',
        Year: 2024,
        Temperature: 25,
        Rainfall: 1000,
        Season: 'Kharif'
    });
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [trends, setTrends] = useState(null);
    const [error, setError] = useState(null);

    // Fetch trends whenever Area or Crop changes
    useEffect(() => {
        const fetchTrends = async () => {
            if (!formData.Area || !formData.Crop) return;
            try {
                const { data } = await axios.post('http://localhost:5000/api/yield-trends', {
                    Area: formData.Area,
                    Crop: formData.Crop
                });
                if (data.success && data.trends) {
                    setTrends(data.trends.sort((a, b) => a.Year - b.Year));
                }
            } catch (err) {
                console.error("Failed to fetch trends", err);
            }
        };
        fetchTrends();
    }, [formData.Area, formData.Crop]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        const val = (name === 'Area' || name === 'Crop' || name === 'Season') ? value : parseFloat(value);
        setFormData({ ...formData, [name]: val });
    };

    const handlePredict = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const { data } = await axios.post('http://localhost:5000/api/yield', formData);
            setResult(data);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to initialize forecast.');
        } finally {
            setLoading(false);
        }
    };

    const seasons = ['Kharif', 'Rabi', 'Whole Year', 'Autumn', 'Summer', 'Winter'];

    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            className="p-8 lg:p-12 max-w-7xl mx-auto h-full text-slate-100 relative z-10 space-y-12 pb-24"
        >
            <div className="text-center">
                <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-[0_0_30px_rgba(245,158,11,0.5)]"
                >
                    <Wheat className="w-8 h-8 text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]" />
                </motion.div>
                <h1 className="text-4xl font-extrabold mb-3 tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 font-display">Yield Prediction</h1>
                <p className="text-slate-400 font-light tracking-widest text-sm uppercase italic">Forecast seasonal yields using spatial and climate data.</p>
            </div>

            <div className="grid lg:grid-cols-12 gap-8">
                {/* Form Section */}
                <motion.div
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="lg:col-span-4 lg:row-span-2"
                >
                    <div className="glass-card p-8 h-full relative overflow-hidden group">
                        <div className="absolute inset-0 bg-amber-500/5 blur-[60px] pointer-events-none group-hover:bg-amber-500/10 transition-colors" />

                        <form onSubmit={handlePredict} className="space-y-6 relative z-10">
                            <h3 className="text-xs font-bold text-amber-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                                <Map className="w-4 h-4" /> Location & Crop
                            </h3>

                            <div className="grid grid-cols-1 gap-6">
                                <div>
                                    <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">Geographic Area</label>
                                    <input
                                        type="text"
                                        name="Area"
                                        value={formData.Area}
                                        onChange={handleChange}
                                        required
                                        className="glowing-input !py-3 !text-sm focus:ring-amber-500/50"
                                        placeholder="e.g. India"
                                    />
                                </div>
                                <div>
                                    <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">Crop Specifier</label>
                                    <input
                                        type="text"
                                        name="Crop"
                                        value={formData.Crop}
                                        onChange={handleChange}
                                        required
                                        className="glowing-input !py-3 !text-sm focus:ring-amber-500/50"
                                        placeholder="e.g. Rice"
                                    />
                                </div>
                            </div>

                            <div className="pt-4 border-t border-white/5" />

                            <h3 className="text-xs font-bold text-amber-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                                <Sun className="w-4 h-4" /> Climate & Timing
                            </h3>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">Temp (°C)</label>
                                    <input
                                        type="number"
                                        name="Temperature"
                                        value={formData.Temperature}
                                        onChange={handleChange}
                                        required
                                        className="glowing-input !py-3 !text-sm focus:ring-amber-500/50"
                                    />
                                </div>
                                <div>
                                    <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">Rainfall (mm)</label>
                                    <input
                                        type="number"
                                        name="Rainfall"
                                        value={formData.Rainfall}
                                        onChange={handleChange}
                                        required
                                        className="glowing-input !py-3 !text-sm focus:ring-amber-500/50"
                                    />
                                </div>
                                <div className="col-span-2">
                                    <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">Cycle Season</label>
                                    <select
                                        name="Season"
                                        value={formData.Season}
                                        onChange={handleChange}
                                        className="glowing-input !py-3 !text-sm focus:ring-amber-500/50 appearance-none bg-slate-900"
                                    >
                                        {seasons.map(s => <option key={s} value={s}>{s}</option>)}
                                    </select>
                                </div>
                                <div className="col-span-2">
                                    <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">Target Year</label>
                                    <input
                                        type="number"
                                        name="Year"
                                        value={formData.Year}
                                        onChange={handleChange}
                                        required
                                        min="2000"
                                        max="2035"
                                        className="glowing-input !py-3 !text-sm focus:ring-amber-500/50 font-mono"
                                    />
                                </div>
                            </div>

                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                type="submit"
                                disabled={loading}
                                className={`w-full py-4 mt-6 bg-gradient-to-r from-amber-600 to-orange-500 text-white rounded-xl shadow-[0_10px_20px_rgba(245,158,11,0.3)] hover:shadow-[0_15px_30px_rgba(245,158,11,0.5)] transition-all duration-300 font-bold uppercase tracking-widest text-xs flex items-center justify-center gap-3 border border-amber-400/30 ${loading && 'opacity-50 cursor-not-allowed'}`}
                            >
                                {loading ? <Loader2 className="animate-spin w-4 h-4" /> : <Wheat className="w-4 h-4" />}
                                {loading ? 'Computing Forecast...' : 'Predict Yield'}
                            </motion.button>
                        </form>
                    </div>
                </motion.div>

                {/* Main Results Display */}
                <motion.div
                    initial={{ opacity: 0, x: 50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 }}
                    className="lg:col-span-8 flex flex-col gap-8"
                >
                    <AnimatePresence mode="wait">
                        {error && (
                            <motion.div
                                key="error"
                                initial={{ opacity: 0, y: -20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                className="glass-card !bg-red-500/10 !border-red-500/30 p-6 flex gap-4 text-red-200 shadow-[0_0_30px_rgba(239,68,68,0.2)]"
                            >
                                <AlertTriangle className="w-6 h-6 shrink-0 drop-shadow-[0_0_5px_currentColor]" />
                                <div className="space-y-1">
                                    <p className="font-bold uppercase tracking-wider text-xs">Calibration Error</p>
                                    <p className="text-sm font-light">{error}</p>
                                </div>
                            </motion.div>
                        )}

                        {result ? (
                            <motion.div
                                key="result"
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="glass-card p-10 relative group overflow-hidden"
                            >
                                <div className="absolute inset-0 bg-amber-500/10 blur-[100px] pointer-events-none" />

                                <div className="flex flex-col lg:flex-row items-center gap-12 relative z-10">
                                    <div className="flex-1 text-center lg:text-left space-y-4">
                                        <div className="flex items-center justify-center lg:justify-start gap-3 text-amber-500 mb-2">
                                            <CheckCircle className="w-5 h-5" />
                                            <span className="text-xs font-bold uppercase tracking-[0.2em]">Yield Prediction Ready</span>
                                        </div>
                                        <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Estimated Crop Yield</h2>
                                        <div className="flex items-baseline justify-center lg:justify-start gap-4">
                                            <span className="text-6xl lg:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-amber-200 tabular-nums drop-shadow-[0_0_20px_rgba(255,255,255,0.2)]">
                                                {result.predicted_yield?.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                                            </span>
                                            <span className="text-2xl font-bold text-amber-500/60 tracking-widest">HG/HA</span>
                                        </div>
                                    </div>

                                    <div className="w-px h-32 bg-white/10 hidden lg:block" />

                                    <div className="space-y-6 min-w-[200px]">
                                        <div>
                                            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Yield Level</p>
                                            <span className={`inline-flex px-4 py-2 rounded-lg text-xs font-black tracking-widest uppercase border ${result.yield_level === 'HIGH' ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400' :
                                                result.yield_level === 'MEDIUM' ? 'bg-amber-500/20 border-amber-500/40 text-amber-400' :
                                                    'bg-rose-500/20 border-rose-500/40 text-rose-300'
                                                }`}>
                                                {result.yield_level} Level
                                            </span>
                                        </div>
                                        {result.yield_uncertainty && (
                                            <div>
                                                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 flex items-center gap-2">
                                                    Data Variance <Info className="w-3 h-3 cursor-help text-slate-600" />
                                                </p>
                                                <span className="text-xl font-mono text-slate-300">± {result.yield_uncertainty} <span className="text-xs text-slate-500">hg/ha</span></span>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {result.agronomic_advice && (
                                    <div className="mt-10 pt-8 border-t border-white/5 relative z-10">
                                        <h4 className="text-[10px] font-bold text-amber-500 uppercase tracking-widest mb-4">Farming Insights</h4>
                                        <div className="grid md:grid-cols-2 gap-4">
                                            {result.agronomic_advice.map((advice, i) => (
                                                <div key={i} className="flex gap-3 text-sm text-slate-400 bg-white/5 p-4 rounded-xl border border-white/5 hover:border-amber-500/20 transition-colors">
                                                    <span className="text-amber-500 text-lg leading-none">•</span>
                                                    <span>{advice}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </motion.div>
                        ) : (
                            <motion.div
                                key="placeholder"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="glass-card p-12 flex flex-col items-center justify-center text-center h-[350px] border-dashed !bg-white/2"
                            >
                                <div className="w-20 h-20 rounded-full bg-slate-900 flex items-center justify-center mb-6 shadow-2xl border border-white/5">
                                    <Wheat className="w-10 h-10 text-slate-700" />
                                </div>
                                <p className="text-slate-500 font-light tracking-widest max-w-sm uppercase text-xs">System ready. Enter location and climate details to generate yield forecast.</p>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Trends Visualization - Always visible if data exists */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                        className="glass-card p-8 min-h-[400px] flex flex-col"
                    >
                        <div className="flex items-center justify-between mb-8 relative z-10">
                            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-3">
                                <TrendingUp className="w-4 h-4 text-amber-500" /> Historical Yield Trends
                            </h3>
                            <div className="flex gap-4">
                                <span className="flex items-center gap-2 text-[10px] text-slate-500 uppercase tracking-tighter">
                                    <span className="w-2 h-2 rounded-full bg-amber-500" /> Yield (hg/ha)
                                </span>
                            </div>
                        </div>

                        <div className="flex-1 w-full min-h-[300px] relative z-10">
                            {trends && trends.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={trends}>
                                        <defs>
                                            <linearGradient id="colorYield" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                                                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                        <XAxis
                                            dataKey="Year"
                                            stroke="#475569"
                                            fontSize={10}
                                            tickLine={false}
                                            axisLine={false}
                                            dy={10}
                                        />
                                        <YAxis
                                            stroke="#475569"
                                            fontSize={10}
                                            tickLine={false}
                                            axisLine={false}
                                            tickFormatter={(val) => `${val / 1000}k`}
                                        />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: '#0f172a',
                                                border: '1px solid rgba(255,255,255,0.1)',
                                                borderRadius: '12px',
                                                fontSize: '12px',
                                                boxShadow: '0 10px 25px -5px rgba(0,0,0,0.5)'
                                            }}
                                            itemStyle={{ color: '#f59e0b', fontWeight: 'bold' }}
                                        />
                                        <Area
                                            type="monotone"
                                            dataKey="Yield"
                                            stroke="#f59e0b"
                                            strokeWidth={3}
                                            fillOpacity={1}
                                            fill="url(#colorYield)"
                                            animationDuration={2000}
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="h-full flex flex-col items-center justify-center text-slate-600 space-y-4">
                                    <p className="text-[10px] uppercase tracking-[0.3em]">No Historical Data for {formData.Area}/{formData.Crop}</p>
                                    <div className="w-1/2 h-px bg-white/5" />
                                </div>
                            )}
                        </div>
                    </motion.div>
                </motion.div>
            </div>
        </motion.div>
    );
};

export default Yield;

import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, CheckCircle, AlertTriangle, Loader2, UploadCloud, Map, Droplets } from 'lucide-react';

const Report = () => {
    const [formData, setFormData] = useState({
        Nitrogen: 90,
        Phosphorus: 40,
        Potassium: 40,
        Temperature: 28,
        Humidity: 70,
        pH: 6.5,
        Rainfall: 200,
        Area: 'India',
        Crop: 'rice',
        Year: 2024
    });
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        const { name, value, type } = e.target;
        setFormData({
            ...formData,
            [name]: type === 'number' ? parseFloat(value) : value
        });
    };

    const handleFileChange = (e) => {
        const selected = e.target.files[0];
        if (selected) {
            setFile(selected);
            setPreview(URL.createObjectURL(selected));
        }
    };

    const handlePredict = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        const payload = new FormData();
        if (file) payload.append('file', file);

        for (const key in formData) {
            payload.append(key, formData[key]);
        }

        try {
            const { data } = await axios.post('http://localhost:5000/api/report', payload, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setResult(data.smart_report);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to initialize system core.');
        } finally {
            setLoading(false);
        }
    };

    const sectionVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: (i) => ({
            opacity: 1,
            y: 0,
            transition: { delay: i * 0.1, type: "spring", bounce: 0.4 }
        })
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            className="p-8 lg:p-12 max-w-6xl mx-auto h-full text-slate-100 relative z-10 w-full"
        >
            <div className="mb-12 text-center w-full">
                <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-fuchsia-500 to-purple-600 flex items-center justify-center shadow-[0_0_30px_rgba(168,85,247,0.5)] border border-fuchsia-400/50"
                >
                    <FileText className="w-8 h-8 text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]" />
                </motion.div>
                <h1 className="text-4xl font-extrabold mb-3 tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">Core Telemetry Report</h1>
                <p className="text-slate-400 font-light tracking-widest text-sm uppercase">Generate full AI synthesis analysis.</p>
            </div>

            <div className="grid lg:grid-cols-2 gap-10 items-start">
                {/* Form Container */}
                <motion.div
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="glass-card p-8 lg:p-10 relative overflow-hidden group w-full"
                >
                    <div className="absolute inset-0 bg-fuchsia-500/10 blur-[80px] pointer-events-none opacity-50 group-hover:opacity-100 transition-opacity duration-1000" />

                    <form onSubmit={handlePredict} className="space-y-8 relative z-10">

                        {/* Image Upload */}
                        <div className="bg-white/5 p-6 rounded-2xl border border-white/10 shadow-inner">
                            <h3 className="text-xs font-bold text-slate-400 tracking-widest uppercase mb-4 flex items-center gap-3">
                                <UploadCloud className="w-4 h-4 text-brand-400" />
                                Optic Sensor Data
                            </h3>
                            <div
                                className="border border-dashed border-white/20 bg-slate-900/50 rounded-xl p-6 flex flex-col items-center justify-center text-center hover:border-brand-500 hover:bg-white/10 transition-colors cursor-pointer shadow-inner"
                                onClick={() => document.getElementById('report-file').click()}
                            >
                                <input id="report-file" type="file" className="hidden" accept="image/*" onChange={handleFileChange} />
                                {preview ? (
                                    <motion.img
                                        initial={{ scale: 0.9, opacity: 0 }}
                                        animate={{ scale: 1, opacity: 1 }}
                                        src={preview} alt="Leaf" className="h-32 object-contain rounded-lg drop-shadow-[0_0_15px_rgba(255,255,255,0.2)]"
                                    />
                                ) : (
                                    <p className="text-sm text-slate-400 font-bold uppercase tracking-widest drop-shadow-[0_0_5px_rgba(0,0,0,0.5)]">Load Diagnostic Image Array</p>
                                )}
                            </div>
                        </div>

                        {/* Biosphere Inputs */}
                        <div className="grid grid-cols-2 gap-5">
                            <div className="col-span-2">
                                <h3 className="text-xs font-bold text-slate-400 tracking-widest uppercase border-b border-white/10 pb-3 mb-2 flex items-center gap-2">
                                    <Droplets className="w-4 h-4 text-indigo-400" /> Biosphere Metrics
                                </h3>
                            </div>
                            {[
                                { name: 'Nitrogen', type: 'number' },
                                { name: 'Phosphorus', type: 'number' },
                                { name: 'Potassium', type: 'number' },
                                { name: 'Temperature', type: 'number' },
                                { name: 'Humidity', type: 'number' },
                                { name: 'pH', type: 'number' },
                                { name: 'Rainfall', type: 'number' },
                            ].map(f => (
                                <div key={f.name}>
                                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 px-1">{f.name}</label>
                                    <input
                                        type={f.type} step="any" name={f.name} value={formData[f.name]}
                                        onChange={handleChange} required
                                        className="glowing-input font-mono text-center tracking-wider focus:ring-fuchsia-400 focus:shadow-[0_0_20px_rgba(168,85,247,0.2)] bg-slate-900/40 py-3"
                                    />
                                </div>
                            ))}
                        </div>

                        {/* Spatial Targets */}
                        <div className="grid grid-cols-2 gap-5 pt-4">
                            <div className="col-span-2">
                                <h3 className="text-xs font-bold text-slate-400 tracking-widest uppercase border-b border-white/10 pb-3 mb-2 flex items-center gap-2">
                                    <Map className="w-4 h-4 text-amber-400" /> Spatial Target
                                </h3>
                            </div>
                            {['Area', 'Crop', 'Year'].map(f => (
                                <div key={f}>
                                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 px-1">{f}</label>
                                    <input
                                        type={f === 'Year' ? 'number' : 'text'} name={f} value={formData[f]}
                                        onChange={handleChange} required
                                        className="glowing-input font-mono tracking-wider focus:ring-fuchsia-400 focus:shadow-[0_0_20px_rgba(168,85,247,0.2)] bg-slate-900/40 py-3 text-center uppercase"
                                    />
                                </div>
                            ))}
                        </div>

                        <div className="pt-8">
                            <motion.button
                                whileHover={{ scale: !loading ? 1.02 : 1 }}
                                whileTap={{ scale: !loading ? 0.98 : 1 }}
                                type="submit"
                                disabled={loading}
                                className={`w-full py-5 bg-gradient-to-r from-fuchsia-600 to-purple-500 text-white rounded-xl shadow-[0_0_20px_rgba(168,85,247,0.4)] hover:shadow-[0_0_40px_rgba(168,85,247,0.6)] transition-all duration-300 font-bold uppercase tracking-widest text-sm flex items-center justify-center gap-3 border border-fuchsia-400/50 ${loading && 'opacity-50 cursor-not-allowed shadow-none'}`}
                            >
                                {loading ? <Loader2 className="animate-spin w-5 h-5 drop-shadow-[0_0_5px_currentColor]" /> : <FileText className="w-5 h-5 drop-shadow-[0_0_5px_currentColor]" />}
                                {loading ? 'Synthesizing Data Streams...' : 'Initiate Full Telemetry Report'}
                            </motion.button>
                        </div>
                    </form>
                </motion.div>

                {/* Results Area */}
                <motion.div
                    initial={{ opacity: 0, x: 50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 }}
                    className="h-full relative w-full"
                >
                    <AnimatePresence mode="wait">
                        {error && (
                            <motion.div
                                key="error"
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.9 }}
                                className="glass-card !bg-red-500/10 !border-red-500/30 p-6 flex gap-4 text-red-200 shadow-[0_0_30px_rgba(239,68,68,0.2)] mb-6 absolute top-0 w-full z-20"
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
                                className="glass-card p-10 flex flex-col items-center justify-center text-center h-[500px] border-dashed !bg-white/5 w-full"
                            >
                                <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-6 shadow-[inset_0_0_20px_rgba(255,255,255,0.05)] border border-white/10">
                                    <FileText className="w-10 h-10 text-slate-500 drop-shadow-[0_0_5px_rgba(255,255,255,0.1)]" />
                                </div>
                                <p className="text-slate-400 font-light tracking-wide max-w-[250px] uppercase text-sm leading-relaxed">
                                    Connect data uplinks to generate integrated synthesis report.
                                </p>
                            </motion.div>
                        )}

                        {result && (
                            <motion.div
                                key="result"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="glass-card overflow-hidden w-full relative group"
                            >
                                <div className="absolute inset-0 bg-fuchsia-500/10 blur-[80px] pointer-events-none opacity-50 group-hover:opacity-80 transition-opacity" />

                                <div className="bg-slate-900/60 p-8 border-b border-white/5 shadow-inner backdrop-blur-md relative z-10 flex flex-col items-center text-center">
                                    <motion.div
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        transition={{ type: "spring", bounce: 0.5, delay: 0.1 }}
                                        className="flex items-center justify-center w-16 h-16 rounded-full bg-white/10 border border-brand-400/50 shadow-[0_0_20px_rgba(16,185,129,0.3)] mb-4"
                                    >
                                        <CheckCircle className="w-8 h-8 text-brand-400 drop-shadow-[0_0_5px_currentColor]" />
                                    </motion.div>
                                    <h3 className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-300 uppercase tracking-widest drop-shadow-[0_0_10px_rgba(255,255,255,0.2)]">Synthesis Complete</h3>
                                    <p className="text-slate-400 text-sm tracking-widest font-bold mt-2 font-mono uppercase text-brand-300 drop-shadow-[0_0_5px_currentColor]">System Link Active</p>
                                </div>

                                <div className="p-8 space-y-6 relative z-10">

                                    {/* Visual Condition Render */}
                                    <motion.div custom={1} variants={sectionVariants} initial="hidden" animate="visible" className="glass-card !bg-white/5 !rounded-2xl p-6 border !border-white/10 shadow-inner group/card hover:!border-rose-400/50 transition-colors">
                                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-3">
                                            <span className="w-3 h-3 rounded-full bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.8)] animate-pulse"></span> Visual Diagnostic Core
                                        </h4>
                                        {result.disease_prediction ? (
                                            result.disease_prediction.error ? (
                                                <p className="text-rose-400 tracking-wide font-mono text-sm">{result.disease_prediction.error}</p>
                                            ) : (
                                                <div className="flex justify-between items-end">
                                                    <div>
                                                        <p className="text-2xl font-extrabold text-white capitalize mb-1 tracking-wide drop-shadow-[0_0_5px_rgba(255,255,255,0.3)]">
                                                            {result.disease_prediction.disease}
                                                        </p>
                                                        <p className="text-xs text-rose-300 font-bold uppercase tracking-widest">Detected Signature</p>
                                                    </div>
                                                    <div className="text-right">
                                                        <p className="text-2xl font-extrabold text-rose-400 drop-shadow-[0_0_10px_rgba(244,63,94,0.5)] mb-1">
                                                            {result.disease_prediction.confidence?.toFixed(1)}%
                                                        </p>
                                                        <p className="text-xs text-slate-400 font-bold uppercase tracking-widest">Certainty</p>
                                                    </div>
                                                </div>
                                            )
                                        ) : (
                                            <p className="text-slate-500 font-mono text-sm tracking-wide">No optic data uplink established.</p>
                                        )}
                                    </motion.div>

                                    {/* Crop Array Render */}
                                    {result.crop_recommendation && (
                                        <motion.div custom={2} variants={sectionVariants} initial="hidden" animate="visible" className="glass-card !bg-white/5 !rounded-2xl p-6 border !border-white/10 shadow-inner group/card hover:!border-indigo-400/50 transition-colors">
                                            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-3">
                                                <span className="w-3 h-3 rounded-full bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.8)] animate-pulse"></span> Optimal Biosphere Array
                                            </h4>
                                            {result.crop_recommendation.error ? (
                                                <p className="text-red-400 tracking-wide font-mono text-sm">{result.crop_recommendation.error}</p>
                                            ) : (
                                                <div className="flex justify-between items-end">
                                                    <div>
                                                        <p className="text-2xl font-extrabold text-indigo-300 capitalize mb-1 tracking-wide drop-shadow-[0_0_10px_rgba(99,102,241,0.5)]">
                                                            {result.crop_recommendation.recommended_crop}
                                                        </p>
                                                        <p className="text-xs text-indigo-400 font-bold uppercase tracking-widest">Primary Vector</p>
                                                    </div>
                                                    {result.crop_recommendation.confidence && (
                                                        <div className="text-right">
                                                            <p className="text-xl font-extrabold text-slate-200 mb-1 drop-shadow-[0_0_5px_rgba(255,255,255,0.3)]">
                                                                {result.crop_recommendation.confidence.toFixed(1)}%
                                                            </p>
                                                            <p className="text-xs text-slate-400 font-bold uppercase tracking-widest">Match</p>
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </motion.div>
                                    )}

                                    {/* Spatial Forecast Render */}
                                    {result.yield_prediction && (
                                        <motion.div custom={3} variants={sectionVariants} initial="hidden" animate="visible" className="glass-card !bg-white/5 !rounded-2xl p-6 border !border-white/10 shadow-inner group/card hover:!border-amber-400/50 transition-colors">
                                            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-3">
                                                <span className="w-3 h-3 rounded-full bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.8)] animate-pulse"></span> Spatial Densities Target
                                            </h4>
                                            {result.yield_prediction.error ? (
                                                <p className="text-red-400 tracking-wide font-mono text-sm">{result.yield_prediction.error}</p>
                                            ) : (
                                                <div className="flex justify-between items-end">
                                                    <div>
                                                        <p className="text-2xl font-extrabold text-amber-400 mb-1 drop-shadow-[0_0_10px_rgba(245,158,11,0.5)]">
                                                            {result.yield_prediction.predicted_yield?.toFixed(2)} <span className="text-lg text-amber-400/70 font-mono tracking-widest">t/ha</span>
                                                        </p>
                                                        <p className="text-xs text-amber-500 font-bold uppercase tracking-widest">Forecast Plot</p>
                                                    </div>
                                                    <div className="text-right">
                                                        <p className={`text-xl font-extrabold mb-1 tracking-widest uppercase shadow-sm ${result.yield_prediction.yield_level === 'HIGH' ? 'text-brand-400 drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]' :
                                                            result.yield_prediction.yield_level === 'MEDIUM' ? 'text-amber-400 drop-shadow-[0_0_8px_rgba(245,158,11,0.8)]' :
                                                                'text-rose-400 drop-shadow-[0_0_8px_rgba(244,63,94,0.8)]'
                                                            }`}>
                                                            {result.yield_prediction.yield_level}
                                                        </p>
                                                        <p className="text-xs text-slate-400 font-bold uppercase tracking-widest">Classification</p>
                                                    </div>
                                                </div>
                                            )}
                                        </motion.div>
                                    )}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>
            </div>
        </motion.div>
    );
};

export default Report;

import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, CheckCircle, AlertTriangle, Loader2, Activity } from 'lucide-react';

const Disease = () => {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        const selected = e.target.files[0];
        if (selected) {
            setFile(selected);
            setPreview(URL.createObjectURL(selected));
            setResult(null);
            setError(null);
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
        }
    };

    const handleAnalyze = async () => {
        if (!file) return;

        setLoading(true);
        setError(null);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const { data } = await axios.post('http://localhost:5000/api/disease', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setResult(data);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to connect to backend.');
        } finally {
            setLoading(false);
        }
    };

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
                    className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-rose-500 to-red-600 flex items-center justify-center shadow-[0_0_30px_rgba(244,63,94,0.5)]"
                >
                    <Activity className="w-8 h-8 text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]" />
                </motion.div>
                <h1 className="text-4xl font-extrabold mb-3 tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">Diagnostics Hub</h1>
                <p className="text-slate-400 font-light tracking-widest text-sm uppercase">Identify anomalies in realtime.</p>
            </div>

            <div className="grid lg:grid-cols-2 gap-10">
                {/* Upload Area */}
                <motion.div
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="flex flex-col gap-6 relative"
                >
                    {/* Dark glow background */}
                    <div className="absolute inset-0 bg-brand-500/10 blur-[100px] z-0 pointer-events-none rounded-full" />

                    <div
                        className="glass-card !bg-white/5 border-2 border-dashed !border-white/20 p-10 flex flex-col items-center justify-center text-center hover:!border-brand-500 hover:!bg-white/10 transition-colors cursor-pointer group h-[400px] relative z-10"
                        onDragOver={(e) => e.preventDefault()}
                        onDrop={handleDrop}
                        onClick={() => document.getElementById('file-upload').click()}
                    >
                        <input
                            id="file-upload"
                            type="file"
                            className="hidden"
                            accept="image/*"
                            onChange={handleFileChange}
                        />

                        {preview ? (
                            <motion.img
                                initial={{ scale: 0.9, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                src={preview} alt="Telemetry" className="w-full h-full object-contain rounded-xl drop-shadow-[0_0_15px_rgba(16,185,129,0.2)]"
                            />
                        ) : (
                            <>
                                <div className="w-24 h-24 rounded-full bg-white/5 flex items-center justify-center mb-6 shadow-[inset_0_0_20px_rgba(255,255,255,0.05)] border border-white/10 group-hover:scale-110 transition-transform">
                                    <UploadCloud className="w-12 h-12 text-slate-300 group-hover:text-brand-400 drop-shadow-[0_0_10px_currentColor] transition-colors" />
                                </div>
                                <h3 className="text-xl font-bold mb-2 tracking-wide">Upload Telemetry View</h3>
                                <p className="text-slate-400 text-sm max-w-[250px] font-light">
                                    Drag and drop visual data mapping, or click to initialize link.
                                </p>
                            </>
                        )}
                    </div>

                    <motion.button
                        whileHover={{ scale: file && !loading ? 1.02 : 1 }}
                        whileTap={{ scale: file && !loading ? 0.98 : 1 }}
                        disabled={!file || loading}
                        onClick={handleAnalyze}
                        className={`btn-primary w-full flex items-center justify-center gap-3 uppercase tracking-widest text-sm ${(!file || loading) && 'opacity-50 cursor-not-allowed shadow-none'}`}
                    >
                        {loading ? <Loader2 className="animate-spin w-5 h-5 drop-shadow-[0_0_5px_currentColor]" /> : <Activity className="w-5 h-5 drop-shadow-[0_0_5px_currentColor]" />}
                        {loading ? 'Processing Array...' : 'Run Diagnostics'}
                    </motion.button>
                </motion.div>

                {/* Results Area */}
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
                                className="glass-card p-10 flex flex-col items-center justify-center text-center h-[400px] border-dashed !bg-white/5"
                            >
                                <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-6 shadow-[inset_0_0_20px_rgba(255,255,255,0.05)] border border-white/10">
                                    <Activity className="w-10 h-10 text-slate-500 drop-shadow-[0_0_5px_rgba(255,255,255,0.1)]" />
                                </div>
                                <p className="text-slate-400 font-light tracking-wide max-w-[200px]">Awaiting telemetry link to process model data.</p>
                            </motion.div>
                        )}

                        {result && (
                            <motion.div
                                key="result"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="glass-card overflow-hidden h-full flex flex-col items-center justify-center p-10 relative group"
                            >
                                {/* Inner Glow */}
                                <div className="absolute inset-0 bg-brand-500/20 blur-[80px] pointer-events-none opacity-50 group-hover:opacity-80 transition-opacity" />

                                <div className="flex flex-col items-center justify-center w-full relative z-10 text-center mb-6">
                                    <motion.div
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        transition={{ type: "spring", bounce: 0.5, delay: 0.1 }}
                                        className="w-20 h-20 bg-white/10 rounded-full flex items-center justify-center mb-4 backdrop-blur-md shadow-[0_0_30px_rgba(16,185,129,0.3)] border border-brand-500/50 relative z-10 mx-auto"
                                    >
                                        <CheckCircle className="w-10 h-10 text-brand-400 drop-shadow-[0_0_10px_currentColor]" />
                                    </motion.div>

                                    <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-1 relative z-10">Detected Anomaly</h3>
                                    <motion.p
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        transition={{ delay: 0.3 }}
                                        className="text-3xl lg:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-brand-200 capitalize text-center drop-shadow-[0_0_10px_rgba(255,255,255,0.3)] relative z-10 pb-2"
                                    >
                                        {result.disease || result.condition || 'Healthy'}
                                    </motion.p>
                                </div>

                                <div className="w-full max-w-sm relative z-10 mb-4">
                                    <div className="flex justify-between items-end mb-1">
                                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Confidence Index</p>
                                        <span className="font-bold text-brand-300 drop-shadow-[0_0_5px_currentColor] text-sm">{result.confidence?.toFixed(1)}%</span>
                                    </div>
                                    <div className="h-1.5 rounded-full bg-white/10 overflow-hidden shadow-inner flex-shrink-0">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${result.confidence}%` }}
                                            transition={{ duration: 1.5, delay: 0.5, ease: "easeOut" }}
                                            className="h-full bg-gradient-to-r from-brand-600 to-brand-400 rounded-full shadow-[0_0_15px_rgba(16,185,129,0.8)]"
                                        />
                                    </div>
                                </div>

                                {result.top_predictions && result.top_predictions.length > 0 && (
                                    <div className="mt-2 relative z-10 w-full mb-4">
                                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 border-b border-white/10 pb-2">Top Alternatives</h4>
                                        <div className="space-y-2">
                                            {result.top_predictions.map((pred, i) => (
                                                <div key={i} className="flex items-center justify-between text-sm bg-white/5 p-2 rounded-lg border border-white/5 shadow-sm">
                                                    <span className="font-semibold text-brand-100 capitalize truncate max-w-[200px]">{pred.disease}</span>
                                                    <span className="text-brand-300 font-mono tracking-widest">{pred.confidence}%</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {result.plant && (
                                    <motion.div
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        transition={{ delay: 1 }}
                                        className="pt-8 w-full flex justify-center gap-4 relative z-10"
                                    >
                                        <span className="inline-flex px-4 py-2 border border-white/20 bg-white/5 backdrop-blur-sm text-slate-200 rounded-xl text-xs font-bold tracking-widest uppercase shadow-[0_2px_10px_rgba(0,0,0,0.2)]">
                                            Source: {result.plant}
                                        </span>
                                        <span className={`inline-flex px-4 py-2 border rounded-xl border-white/20 backdrop-blur-sm text-white text-xs font-bold tracking-widest uppercase shadow-[0_2px_10px_rgba(0,0,0,0.2)] ${result.confidence_level === 'HIGH' ? 'bg-brand-500/20' :
                                            result.confidence_level === 'MODERATE' ? 'bg-amber-500/20' :
                                                'bg-rose-500/20'
                                            }`}>
                                            Level: {result.confidence_level || 'Unknown'}
                                        </span>
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

export default Disease;

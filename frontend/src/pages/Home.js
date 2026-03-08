import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Leaf, Sprout, Wheat, ArrowRight } from 'lucide-react';

const FeatureCard = ({ icon: Icon, title, desc, to, bgGlow, textColor, hoverTextColor, delay }) => (
    <motion.div
        initial={{ opacity: 0, y: 50, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.8, delay, type: "spring", bounce: 0.4 }}
        className="glass-card p-10 flex flex-col items-start group relative z-10 hover:shadow-[0_0_50px_rgba(255,255,255,0.1)] transition-all overflow-hidden"
    >
        {/* Glow behind icon */}
        <div className={`absolute -top-10 -left-10 w-40 h-40 ${bgGlow} blur-[80px] opacity-20 group-hover:opacity-40 transition-opacity`} />

        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-8 bg-white/10 shadow-[inset_0_0_20px_rgba(255,255,255,0.2)] border border-white/20 relative z-10 group-hover:scale-110 transition-transform`}>
            <Icon className={`w-8 h-8 ${textColor} drop-shadow-[0_0_10px_rgba(255,255,255,0.8)]`} />
        </div>

        <h3 className="text-2xl font-bold mb-4 text-white tracking-wide relative z-10">{title}</h3>

        <p className="text-slate-400 mb-10 flex-1 leading-relaxed text-sm relative z-10">
            {desc}
        </p>

        <Link
            to={to}
            className={`mt-auto flex items-center text-sm font-semibold ${textColor} ${hoverTextColor} relative z-10 uppercase tracking-widest`}
        >
            Initialize <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform drop-shadow-[0_0_5px_currentColor]" />
        </Link>
    </motion.div>
);

const Home = () => {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="p-8 lg:p-12 max-w-7xl mx-auto flex flex-col items-center justify-center min-h-[calc(100vh-8rem)] relative z-10"
        >
            {/* Hero Section */}
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 1, type: "spring" }}
                className="mb-24 text-center relative z-10"
            >
                <motion.div
                    animate={{ boxShadow: ["0 0 10px rgba(76,175,80,0.3)", "0 0 30px rgba(76,175,80,0.7)", "0 0 10px rgba(76,175,80,0.3)"] }}
                    transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                    className="inline-block px-6 py-2 rounded-full bg-brand-500/10 text-brand-300 font-bold tracking-widest text-xs mb-8 border border-brand-500/30 backdrop-blur-md uppercase"
                >
                    AI Intelligence // Precision Agriculture
                </motion.div>

                <h1 className="text-5xl md:text-7xl font-extrabold text-white leading-tight mb-8 tracking-tighter">
                    Grow Smarter with <br className="hidden md:block" />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-300 via-emerald-200 to-emerald-600 drop-shadow-[0_0_30px_rgba(76,175,80,0.4)]">
                        AI Agriculture.
                    </span>
                </h1>

                <p className="text-lg md:text-xl text-slate-400 mb-12 max-w-2xl mx-auto leading-relaxed font-light">
                    Predict Crop Health, Optimize Yield, and Grow Smarter with our AI-Powered Smart Agriculture Platform.
                </p>

                <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="inline-block"
                >
                    <Link to="/report" className="btn-primary flex items-center gap-3">
                        <Leaf className="w-5 h-5 drop-shadow-[0_0_5px_currentColor]" />
                        <span>Launch Farm Intelligence Report</span>
                    </Link>
                </motion.div>
            </motion.div>

            {/* Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full">
                <FeatureCard
                    icon={Leaf}
                    title="Crop Disease Detection"
                    desc="Upload plant leaf images to identify diseases instantly using AI-powered image classification."
                    to="/disease"
                    bgGlow="bg-brand-500"
                    textColor="text-brand-400"
                    hoverTextColor="hover:text-brand-300"
                    delay={0.2}
                />
                <FeatureCard
                    icon={Sprout}
                    title="Smart Crop Recommendation"
                    desc="Calibrate soil chemistry and atmospheric conditions to identify optimal crops for your field."
                    to="/crop"
                    bgGlow="bg-soil-500"
                    textColor="text-soil-400"
                    hoverTextColor="hover:text-soil-300"
                    delay={0.4}
                />
                <FeatureCard
                    icon={Wheat}
                    title="Yield Prediction"
                    desc="Project season yields using historical data models fused with spatial and climate region analysis."
                    to="/yield"
                    bgGlow="bg-harvest-500"
                    textColor="text-harvest-400"
                    hoverTextColor="hover:text-harvest-400"
                    delay={0.6}
                />
            </div>
        </motion.div>
    );
};

export default Home;

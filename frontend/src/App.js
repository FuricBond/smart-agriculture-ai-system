import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Leaf, Sprout, Wheat, FileText, Menu, X, BrainCircuit } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import Home from './pages/Home';
import Disease from './pages/Disease';
import Crop from './pages/Crop';
import Yield from './pages/Yield';
import Report from './pages/Report';
import FarmAssistant from './pages/FarmAssistant';

// Floating Particle System Component
const ParticleBackground = () => {
  const [particles, setParticles] = useState([]);

  useEffect(() => {
    // Generate 30 random particles
    const newParticles = Array.from({ length: 30 }).map((_, i) => ({
      id: i,
      left: `${Math.random() * 100}vw`,
      width: `${Math.random() * 4 + 2}px`,
      height: `${Math.random() * 4 + 2}px`,
      animationDuration: `${Math.random() * 20 + 20}s`,
      animationDelay: `${Math.random() * 10}s`,
    }));
    setParticles(newParticles);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-brand-900 via-emerald-950 to-soil-900 animate-gradient-xy opacity-90" />
      {particles.map((p) => (
        <div
          key={p.id}
          className="particle"
          style={{
            left: p.left,
            width: p.width,
            height: p.height,
            animationDuration: p.animationDuration,
            animationDelay: p.animationDelay
          }}
        />
      ))}
    </div>
  );
};

// Nav Item with Glowing effect
const NavItem = ({ icon: Icon, label, path, active, onClick }) => (
  <Link
    to={path}
    onClick={onClick}
    className={`relative flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-300 overflow-hidden group ${active
      ? 'text-brand-300 font-semibold'
      : 'text-slate-300 hover:text-white'
      }`}
  >
    {active && (
      <motion.div
        layoutId="activeNavIndicator"
        className="absolute inset-0 bg-brand-500/20 rounded-xl border border-brand-500/30 shadow-[0_0_15px_rgba(76,175,80,0.3)]"
        initial={false}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
      />
    )}
    <Icon className={`w-5 h-5 relative z-10 ${active ? 'text-brand-400' : 'text-slate-400 group-hover:text-brand-400'} transition-colors duration-300 drop-shadow-[0_0_8px_rgba(76,175,80,0.5)]`} />
    <span className="relative z-10 tracking-wide text-sm">{label}</span>
  </Link>
);

const Navbar = () => {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const menuItems = [
    { icon: Leaf, label: 'Disease Analysis', path: '/disease' },
    { icon: Sprout, label: 'Crop Recommendations', path: '/crop' },
    { icon: Wheat, label: 'Yield Forecast', path: '/yield' },
    { icon: FileText, label: 'Farm Intelligence', path: '/report' },
    { icon: BrainCircuit, label: 'Farm AI Assistant', path: '/farm-assistant' },
  ];

  return (
    <nav className="fixed top-4 left-4 right-4 z-50 flex justify-center">
      <motion.div
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, type: "spring", bounce: 0.4 }}
        className="glass-card !rounded-full px-6 py-3 flex items-center justify-between w-full max-w-6xl !bg-slate-900/60 !border-white/10"
      >
        <Link to="/" className="flex items-center gap-3 mr-8 group relative z-10" onClick={() => setMobileOpen(false)}>
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-[0_0_20px_rgba(76,175,80,0.4)] group-hover:shadow-[0_0_30px_rgba(76,175,80,0.6)] transition-shadow duration-300">
            <Leaf className="text-white w-6 h-6 drop-shadow-[0_0_5px_rgba(255,255,255,0.8)]" />
          </div>
          <div className="hidden sm:block">
            <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 tracking-wider">
              AGRI<span className="text-brand-400">BRAIN</span>
            </h1>
          </div>
        </Link>

        {/* Desktop Nav */}
        <div className="hidden lg:flex items-center gap-2 relative">
          {menuItems.map((item) => (
            <NavItem
              key={item.path}
              {...item}
              active={location.pathname === item.path}
            />
          ))}
        </div>

        {/* Mobile Toggle */}
        <button
          className="lg:hidden p-2 rounded-full bg-white/10 border border-white/20 text-white shadow-[0_0_15px_rgba(255,255,255,0.1)] hover:bg-white/20 transition-all z-10"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          {mobileOpen ? <X /> : <Menu />}
        </button>

        {/* Mobile Dropdown */}
        <AnimatePresence>
          {mobileOpen && (
            <motion.div
              initial={{ opacity: 0, y: -20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              className="absolute top-full left-0 right-0 mt-4 p-4 glass-card flex flex-col gap-2 lg:hidden bg-slate-900/90"
            >
              {menuItems.map((item) => (
                <NavItem
                  key={item.path}
                  {...item}
                  active={location.pathname === item.path}
                  onClick={() => setMobileOpen(false)}
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </nav>
  );
};

const Layout = ({ children }) => {
  // Parallax effect on mouse move
  useEffect(() => {
    const handleMouseMove = (e) => {
      requestAnimationFrame(() => {
        const x = (window.innerWidth / 2 - e.pageX) / 50;
        const y = (window.innerHeight / 2 - e.pageY) / 50;
        document.documentElement.style.setProperty('--mouse-x', `${x}px`);
        document.documentElement.style.setProperty('--mouse-y', `${y}px`);
      });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 font-sans text-slate-100 relative selection:bg-brand-500/30 selection:text-white">
      <ParticleBackground />
      <Navbar />

      {/* 2) Parallax Container applied to Main Content */}
      <main
        className="relative z-10 pt-28 pb-12 w-full min-h-screen flex flex-col"
        style={{ transform: 'translate(var(--mouse-x, 0px), var(--mouse-y, 0px))', transition: 'transform 0.1s ease-out' }}
      >
        <AnimatePresence mode="wait">
          {children}
        </AnimatePresence>
      </main>
    </div>
  );
};

function App() {
  const location = useLocation();
  return (
    <Layout>
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Home />} />
        <Route path="/disease" element={<Disease />} />
        <Route path="/crop" element={<Crop />} />
        <Route path="/yield" element={<Yield />} />
        <Route path="/report" element={<Report />} />
        <Route path="/farm-assistant" element={<FarmAssistant />} />
      </Routes>
    </Layout>
  );
}

const AppWrapper = () => (
  <Router>
    <App />
  </Router>
);

export default AppWrapper;

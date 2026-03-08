import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { BrainCircuit, Send, User, Bot, Loader2, Sparkles } from 'lucide-react';

const FarmAssistant = () => {
    const [messages, setMessages] = useState([
        {
            id: 1,
            sender: 'ai',
            text: 'Hello! I am your Farm AI Assistant powered by Gemini. Ask me any questions about crop health, soil management, fertilizers, or dealing with pests and diseases.'
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();

        if (!inputValue.trim()) return;

        const userMsg = { id: Date.now(), sender: 'user', text: inputValue };
        setMessages(prev => [...prev, userMsg]);
        setInputValue('');
        setLoading(true);

        try {
            const { data } = await axios.post('http://localhost:5000/api/farm-assistant', {
                question: userMsg.text
            });

            const aiMsg = {
                id: Date.now() + 1,
                sender: 'ai',
                text: data.answer || "I'm sorry, I couldn't process that request."
            };
            setMessages(prev => [...prev, aiMsg]);
        } catch (err) {
            const errorMsg = {
                id: Date.now() + 1,
                sender: 'error',
                text: err.response?.data?.error || "AI assistant is currently unavailable. Please try again later."
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            className="p-4 lg:p-8 max-w-5xl mx-auto h-[calc(100vh-8rem)] text-slate-100 relative z-10 flex flex-col"
        >
            <div className="mb-6 flex-shrink-0 text-center relative z-10">
                <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center shadow-[0_0_30px_rgba(245,158,11,0.5)]"
                >
                    <BrainCircuit className="w-8 h-8 text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]" />
                </motion.div>
                <h1 className="text-3xl lg:text-4xl font-extrabold mb-2 tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">Farm AI Assistant</h1>
                <p className="text-slate-400 font-light tracking-widest text-sm uppercase flex items-center justify-center gap-2">
                    <Sparkles className="w-4 h-4 text-amber-400" /> Powered by Gemini
                </p>
            </div>

            <div className="glass-card flex-1 flex flex-col relative overflow-hidden group shadow-[0_0_50px_rgba(0,0,0,0.5)] border border-white/10">
                {/* Subtle glow behind chat */}
                <div className="absolute inset-0 bg-amber-500/5 blur-[100px] pointer-events-none opacity-50 group-hover:opacity-100 transition-opacity duration-1000" />

                {/* Chat History Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6 relative z-10 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                    <AnimatePresence initial={false}>
                        {messages.map((msg) => (
                            <motion.div
                                key={msg.id}
                                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                className={`flex items-start gap-4 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}
                            >
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-lg border ${msg.sender === 'user'
                                    ? 'bg-brand-600 border-brand-400/50'
                                    : msg.sender === 'error'
                                        ? 'bg-red-500/20 border-red-500/50 text-red-400'
                                        : 'bg-amber-500/20 border-amber-500/50 text-amber-400 backdrop-blur-md'
                                    }`}>
                                    {msg.sender === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                                </div>
                                <div className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${msg.sender === 'user'
                                    ? 'bg-brand-600/80 border border-brand-500/50 text-white rounded-tr-sm backdrop-blur-sm'
                                    : msg.sender === 'error'
                                        ? 'bg-red-950/50 border border-red-500/30 text-red-200 rounded-tl-sm'
                                        : 'bg-slate-800/60 border border-slate-700/50 text-slate-200 rounded-tl-sm backdrop-blur-md'
                                    }`}>
                                    {msg.sender === 'error' ? (
                                        <p className="text-sm font-medium tracking-wide">{msg.text}</p>
                                    ) : (
                                        <div
                                            className="text-sm leading-relaxed tracking-wide font-light whitespace-pre-wrap markdown-content"
                                            dangerouslySetInnerHTML={{ __html: msg.text.replace(/\*\*(.*?)\*\*/g, '<strong class="text-amber-300 font-bold">$1</strong>').replace(/\*(.*?)\*/g, '<em class="text-amber-100 italic">$1</em>').replace(/\n/g, '<br/>') }}
                                        />
                                    )}
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {loading && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex items-start gap-4"
                        >
                            <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-lg border bg-amber-500/20 border-amber-500/50 text-amber-400 backdrop-blur-md animate-pulse">
                                <Bot className="w-5 h-5" />
                            </div>
                            <div className="bg-slate-800/60 border border-slate-700/50 text-slate-200 rounded-2xl p-4 rounded-tl-sm backdrop-blur-md flex items-center gap-3 w-fit">
                                <Loader2 className="w-4 h-4 animate-spin text-amber-400" />
                                <span className="text-sm font-medium text-slate-400 uppercase tracking-widest text-xs">Analyzing...</span>
                            </div>
                        </motion.div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 bg-slate-900/50 border-t border-white/10 relative z-10 shrink-0">
                    <form onSubmit={handleSend} className="relative flex items-center">
                        <input
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            placeholder="Ask about crop diseases, fertilizers, or soil..."
                            disabled={loading}
                            className="w-full bg-black/40 border border-slate-700 rounded-xl py-4 pl-6 pr-14 text-white placeholder:text-slate-500 focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/50 transition-all font-light tracking-wide shadow-inner disabled:opacity-50"
                        />
                        <button
                            type="submit"
                            disabled={!inputValue.trim() || loading}
                            className="absolute right-2 p-2 rounded-lg bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-[0_0_15px_rgba(245,158,11,0.3)] hover:shadow-[0_0_25px_rgba(245,158,11,0.5)] disabled:opacity-50 disabled:shadow-none transition-all disabled:cursor-not-allowed"
                        >
                            <Send className="w-5 h-5 drop-shadow-[0_0_5px_rgba(255,255,255,0.5)]" />
                        </button>
                    </form>
                    <p className="text-center text-[10px] text-slate-500 uppercase tracking-widest mt-3">
                        AI can make mistakes. Verify agricultural advice before applying.
                    </p>
                </div>
            </div>
        </motion.div>
    );
};

export default FarmAssistant;

import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";

export default function Navigation() {
    const location = useLocation();
    const [ipAddress, setIpAddress] = useState("192.168.1.100");

    useEffect(() => {
        // Simulate real IP fetching or random gen for cyber feel
        const generateFakeIP = () => {
            return `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;
        };
        const interval = setInterval(() => {
            if (Math.random() > 0.95) setIpAddress(generateFakeIP());
        }, 2000);
        return () => clearInterval(interval);
    }, []);

    return (
        <motion.header
            initial={{ y: -50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="sticky top-0 z-50 h-[72px] bg-page-bg/40 backdrop-blur-xl border-b border-neon-blue/20 flex items-center px-6 sm:px-12 justify-between select-none"
        >
            {/* Left: Logo & IP */}
            <div className="flex items-center space-x-8">
                <Link to="/" className="flex items-center space-x-3 interactive" data-tauri-drag-region>
                    <div className="w-10 h-10 flex items-center justify-center">
                        <img src="/kalpai_logo.png" alt="KalpAI Logo" className="w-full h-full object-contain filter drop-shadow-[0_0_10px_rgba(0,240,255,0.8)]" />
                    </div>
                    <div className="flex flex-col">
                        <span className="text-xl font-bold tracking-widest text-white font-display uppercase leading-tight neon-text">KalpAI</span>
                        <span className="text-[0.65rem] tracking-[0.2em] text-neon-blue uppercase">Cognitive Core</span>
                    </div>
                </Link>
                <div className="hidden lg:flex flex-col border-l border-neon-blue/30 pl-4">
                    <span className="text-[0.55rem] font-mono tracking-[0.2em] text-cyan-500/70">REMOTE_ADDRESS</span>
                    <span className="text-xs font-mono font-bold text-neon-blue tracking-widest">{ipAddress}</span>
                </div>
            </div>

            {/* Center: Navigation Links */}
            <nav className="hidden md:flex items-center space-x-2 bg-black/40 p-1 rounded-lg border border-neon-blue/10 backdrop-blur-md">
                {[
                    { name: "System Status", path: "/" },
                    { name: "Telemetry Capture", path: "/capture" },
                    { name: "Context Memory", path: "/memory" },
                    { name: "Reasoning Engine", path: "/reasoning" },
                ].map((link) => {
                    const isActive = location.pathname === link.path || (link.path !== '/' && location.pathname.startsWith(link.path));

                    return (
                        <Link
                            key={link.name}
                            to={link.path}
                            data-text={link.name}
                            className={`relative px-5 py-2 text-xs font-bold tracking-wider uppercase transition-all duration-300 font-mono interactive glitch-hover ${isActive ? "text-page-bg" : "text-cyber-gray hover:text-white"
                                }`}
                        >
                            {isActive && (
                                <motion.div
                                    layoutId="navIndicator"
                                    className="absolute inset-0 bg-neon-blue rounded-md shadow-[0_0_15px_rgba(0,240,255,0.6)]"
                                    initial={false}
                                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                />
                            )}
                            <span className="relative z-10">{link.name}</span>
                        </Link>
                    )
                })}
            </nav>

            {/* Right: Status Indicator */}
            <div className="flex items-center space-x-3">
                <div className="flex flex-col items-end">
                    <span className="text-[0.65rem] text-cyber-gray uppercase tracking-widest">Network Link</span>
                    <span className="text-xs text-green-400 font-mono">SECURE</span>
                </div>
                <div className="w-3 h-3 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.8)] animate-pulse" />
            </div>
        </motion.header>
    );
}

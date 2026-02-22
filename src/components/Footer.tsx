import { Link } from "react-router-dom";

export default function Footer() {
    return (
        <footer className="bg-page-bg border-t border-neon-blue/20 py-12 px-6 sm:px-12 mt-auto relative overflow-hidden">

            <div className="absolute inset-0 bg-neon-blue/5 pointer-events-none" />

            <div className="max-w-[1200px] mx-auto flex flex-col md:flex-row items-center justify-between gap-8 relative z-10">

                {/* Left: Logo */}
                <Link to="/" className="flex items-center space-x-3">
                    <div className="w-8 h-8 flex items-center justify-center">
                        <img src="/kalpai_logo.png" alt="KalpAI Logo" className="w-full h-full object-contain filter drop-shadow-[0_0_8px_rgba(0,240,255,0.8)]" />
                    </div>
                    <div className="flex flex-col">
                        <span className="text-lg font-bold tracking-widest text-white font-display uppercase leading-tight neon-text">KalpAI</span>
                        <span className="text-[0.55rem] tracking-[0.2em] text-neon-blue uppercase">Cognitive Framework</span>
                    </div>
                </Link>

                {/* Center: Links */}
                <nav className="flex flex-wrap justify-center gap-6">
                    {["Documentation", "GitHub", "Architecture"].map((link) => (
                        <Link
                            key={link}
                            to="#"
                            className="text-xs font-mono uppercase tracking-widest text-cyber-gray hover:text-neon-blue transition-colors"
                        >
                            {link}
                        </Link>
                    ))}
                </nav>

                {/* Right: Copyright */}
                <div className="text-xs font-mono text-neon-blue/40 uppercase tracking-widest">
                    &copy; {new Date().getFullYear()} KalpAI Research Initiative
                </div>

            </div>
        </footer>
    );
}

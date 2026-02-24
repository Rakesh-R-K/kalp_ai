import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { motion } from "framer-motion";
import CyberBackground from "../components/CyberBackground";

export default function Capture() {
    const [greetMsg, setGreetMsg] = useState("");
    const [name, setName] = useState("");

    async function testLink() {
        try {
            const result = await invoke("process_nmap_file", { filePath: name });
            setGreetMsg(result as string);
        } catch (error) {
            setGreetMsg(`ERROR: ${error}`);
        }
    }

    return (
        <div className="relative w-full min-h-[calc(100vh-72px)] text-white font-sans flex flex-col items-center justify-center p-6">
            <CyberBackground />

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-[800px] glass-panel p-8 md:p-12 relative"
            >
                <div className="absolute top-0 right-8 px-4 py-1 bg-neon-blue text-black font-mono text-[0.65rem] font-bold tracking-widest uppercase">
                    Status: AWAITING_TELEMETRY
                </div>

                <div className="flex items-center space-x-4 mb-4">
                    <svg className="w-8 h-8 text-neon-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                    <h2 className="text-3xl font-display font-bold text-white tracking-widest uppercase neon-text">Telemetry Capture</h2>
                </div>

                <p className="text-cyber-gray font-mono text-sm leading-relaxed mb-10 pb-8 border-b border-white/10">
                    Module active. Listening for structured Nmap/Nikto/Gobuster outputs. Raw strings will be rejected. Only normalized entities (SOSM) will pass to the Context Matrix.
                </p>

                <h3 className="text-lg font-mono text-white mb-4 uppercase tracking-widest flex items-center">
                    <span className="w-2 h-2 bg-neon-blue rounded-full mr-3 animate-pulse"></span>
                    Parse Nmap XML
                </h3>

                <form
                    className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 w-full"
                    onSubmit={(e) => { e.preventDefault(); testLink(); }}
                >
                    <input
                        onChange={(e) => setName(e.currentTarget.value)}
                        placeholder="ENTER ABSOLUTE NMAP XML PATH..."
                        className="flex-1 bg-black/50 border border-neon-blue/30 rounded-none px-4 py-3 text-sm text-neon-blue font-mono uppercase focus:outline-none focus:border-neon-blue focus:shadow-[0_0_15px_rgba(0,240,255,0.3)] transition-all placeholder:text-neon-blue/30"
                    />
                    <button
                        type="submit"
                        className="bg-neon-blue/10 text-neon-blue border border-neon-blue px-8 py-3 text-sm font-mono font-bold tracking-widest uppercase transition-all hover:bg-neon-blue hover:text-black hover:shadow-[0_0_20px_rgba(0,240,255,0.6)]"
                    >
                        PROCESS
                    </button>
                </form>

                {greetMsg && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-8 w-full p-4 bg-green-900/20 border-l-2 border-green-500 text-green-400 text-sm font-mono flex items-start"
                    >
                        <span className="opacity-50 mr-3 text-green-500/50">{'>'}</span>
                        <span className="uppercase tracking-wide break-all">{greetMsg}</span>
                    </motion.div>
                )}
            </motion.div>
        </div>
    );
}

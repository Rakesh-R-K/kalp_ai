import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { motion } from "framer-motion";
import CyberBackground from "../components/CyberBackground";

export default function Memory() {
    const [greetMsg, setGreetMsg] = useState("");

    async function testLink() {
        try {
            const result = await invoke("get_memory_context");
            setGreetMsg(JSON.stringify(result, null, 2));
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
                <div className="absolute top-0 right-8 px-4 py-1 bg-neon-purple text-white font-mono text-[0.65rem] font-bold tracking-widest uppercase shadow-[0_0_10px_rgba(176,38,255,0.8)]">
                    Status: SYNCED (SURREAL_DB)
                </div>

                <div className="flex items-center space-x-4 mb-4">
                    <svg className="w-8 h-8 text-neon-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" /></svg>
                    <h2 className="text-3xl font-display font-bold text-white tracking-widest uppercase" style={{ textShadow: "0 0 10px rgba(176,38,255,0.5), 0 0 20px rgba(176,38,255,0.3)" }}>Context Memory</h2>
                </div>

                <p className="text-cyber-gray font-mono text-sm leading-relaxed mb-10 pb-8 border-b border-white/10">
                    State matrix bound to local SurrealDB graph instance. Persistent environmental relationships, operational history, and active hypotheses are maintained here.
                </p>

                <h3 className="text-lg font-mono text-white mb-4 uppercase tracking-widest flex items-center">
                    <span className="w-2 h-2 bg-neon-purple rounded-full mr-3 animate-pulse"></span>
                    Memory Synchronization
                </h3>

                <div className="flex w-full">
                    <button
                        onClick={testLink}
                        className="w-full bg-neon-purple/10 text-neon-purple border border-neon-purple px-8 py-3 text-sm font-mono font-bold tracking-widest uppercase transition-all hover:bg-neon-purple hover:text-white hover:shadow-[0_0_20px_rgba(176,38,255,0.6)]"
                    >
                        FETCH CONTEXT (SOSM)
                    </button>
                </div>

                {greetMsg && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-8 w-full p-4 bg-neon-purple/10 border-l-2 border-neon-purple text-neon-purple text-xs font-mono flex items-start overflow-auto max-h-[300px]"
                    >
                        <pre className="whitespace-pre-wrap">{greetMsg}</pre>
                    </motion.div>
                )}
            </motion.div>
        </div>
    );
}

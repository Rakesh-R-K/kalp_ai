import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { motion } from "framer-motion";
import CyberBackground from "../components/CyberBackground";

export default function Reasoning() {
    const [greetMsg, setGreetMsg] = useState("");
    const [name, setName] = useState("");

    async function testLink() {
        setGreetMsg(await invoke("greet", { name }));
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
                <div className="absolute top-0 right-8 px-4 py-1 bg-yellow-400 text-black font-mono text-[0.65rem] font-bold tracking-widest uppercase shadow-[0_0_10px_rgba(250,204,21,0.8)]">
                    Status: ONNX_INFERENCE_READY
                </div>

                <div className="flex items-center space-x-4 mb-4">
                    <svg className="w-8 h-8 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
                    <h2 className="text-3xl font-display font-bold text-white tracking-widest uppercase" style={{ textShadow: "0 0 10px rgba(250,204,21,0.5), 0 0 20px rgba(250,204,21,0.3)" }}>SLM Reasoning Core</h2>
                </div>

                <p className="text-cyber-gray font-mono text-sm leading-relaxed mb-10 pb-8 border-b border-white/10">
                    Local Phi-3-mini inference active via ONNX Runtime. Context is drawn directly from the Memory Matrix to generate high-value hypotheses without autonomous execution.
                </p>

                <h3 className="text-lg font-mono text-white mb-4 uppercase tracking-widest flex items-center">
                    <span className="w-2 h-2 bg-yellow-400 rounded-full mr-3 animate-pulse"></span>
                    SLM Prompt Test
                </h3>

                <form
                    className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 w-full"
                    onSubmit={(e) => { e.preventDefault(); testLink(); }}
                >
                    <input
                        onChange={(e) => setName(e.currentTarget.value)}
                        placeholder="ENTER CONTEXT FRAGMENT..."
                        className="flex-1 bg-black/50 border border-yellow-400/30 rounded-none px-4 py-3 text-sm text-yellow-400 font-mono uppercase focus:outline-none focus:border-yellow-400 focus:shadow-[0_0_15px_rgba(250,204,21,0.3)] transition-all placeholder:text-yellow-400/30"
                    />
                    <button
                        type="submit"
                        className="bg-yellow-400/10 text-yellow-400 border border-yellow-400 px-8 py-3 text-sm font-mono font-bold tracking-widest uppercase transition-all hover:bg-yellow-400 hover:text-black hover:shadow-[0_0_20px_rgba(250,204,21,0.6)]"
                    >
                        INFER
                    </button>
                </form>

                {greetMsg && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-8 w-full p-4 bg-yellow-400/10 border-l-2 border-yellow-400 text-yellow-400 text-sm font-mono flex items-start"
                    >
                        <span className="opacity-50 mr-3 text-yellow-400/50">{'>'}</span>
                        <span className="uppercase tracking-wide">{greetMsg}</span>
                    </motion.div>
                )}
            </motion.div>
        </div>
    );
}

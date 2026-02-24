import { useRef } from "react";
import { Link } from "react-router-dom";
import { motion, useScroll, useTransform, useMotionValue, useSpring } from "framer-motion";
import Tilt from "react-parallax-tilt";
import CyberBackground from "../components/CyberBackground";

function RevealSection({ children, image, title, subtitle, reverse }: any) {
    const ref = useRef(null);
    const { scrollYProgress } = useScroll({
        target: ref,
        offset: ["0 1", "1 0.5"]
    });

    const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0]);
    const y = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [150, 0, 0, -150]);
    const scale = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0.8, 1, 1, 0.8]);

    return (
        <motion.section
            ref={ref}
            style={{ opacity, y }}
            className={`min-h-[80vh] py-12 flex items-center justify-center relative w-full perspective-1000`}
        >
            <div className={`max-w-[1200px] mx-auto w-full px-8 flex flex-col ${reverse ? 'md:flex-row-reverse' : 'md:flex-row'} items-center gap-16`}>

                {/* Text Content */}
                <div className="flex-1 space-y-6 z-10">
                    <div className="flex items-center space-x-4 mb-2">
                        <div className="h-[1px] w-12 bg-neon-blue" />
                        <span className="text-neon-blue font-mono text-sm tracking-widest uppercase">{subtitle}</span>
                    </div>
                    <h2 className="text-4xl md:text-5xl font-display font-bold text-white neon-text glitch-hover" data-text={title}>{title}</h2>
                    <div className="text-cyber-gray text-lg leading-relaxed font-sans mt-6">
                        {children}
                    </div>
                </div>

                {/* 3D Holographic Image Parallax */}
                <motion.div
                    style={{ scale }}
                    className="flex-1 relative w-full"
                >
                    <Tilt
                        tiltMaxAngleX={15}
                        tiltMaxAngleY={15}
                        perspective={1000}
                        scale={1.05}
                        transitionSpeed={2000}
                        gyroscope={true}
                        glareEnable={true}
                        glareMaxOpacity={0.4}
                        glareColor="#00F0FF"
                        glarePosition="all"
                        className="glass-panel p-2 neon-border rounded-xl relative transform-style-3d interactive shadow-[0_0_50px_rgba(0,240,255,0.1)]"
                    >
                        <div className="absolute inset-0 bg-neon-blue/20 opacity-0 hover:opacity-100 transition-opacity duration-500 z-20 pointer-events-none mix-blend-overlay" />
                        <img
                            src={image}
                            alt={title}
                            className="w-full h-auto object-cover rounded-lg transform translate-z-12 brightness-[1.2] contrast-[1.1]"
                            style={{ transform: "translateZ(30px)" }}
                        />

                        {/* Sci-fi targeting UI overlays */}
                        <div className="absolute top-4 left-4 w-6 h-6 border-t-2 border-l-2 border-neon-blue z-30 pointer-events-none" style={{ transform: "translateZ(60px)" }} />
                        <div className="absolute top-4 right-4 w-6 h-6 border-t-2 border-r-2 border-neon-blue z-30 pointer-events-none" style={{ transform: "translateZ(60px)" }} />
                        <div className="absolute bottom-4 left-4 w-6 h-6 border-b-2 border-l-2 border-neon-blue z-30 pointer-events-none" style={{ transform: "translateZ(60px)" }} />
                        <div className="absolute bottom-4 right-4 w-6 h-6 border-b-2 border-r-2 border-neon-blue z-30 pointer-events-none" style={{ transform: "translateZ(60px)" }} />

                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 border border-neon-blue/30 rounded-full z-30 pointer-events-none" style={{ transform: "translateZ(90px)" }}>
                            <div className="absolute top-1/2 left-1/2 w-1 h-1 bg-neon-blue rounded-full -translate-x-1/2 -translate-y-1/2 shadow-[0_0_10px_rgba(0,240,255,1)]" />
                        </div>
                    </Tilt>
                </motion.div>

            </div>
        </motion.section>
    );
}

function MagneticButton({ children, to }: any) {
    const x = useMotionValue(0);
    const y = useMotionValue(0);
    const springX = useSpring(x, { stiffness: 150, damping: 15, mass: 0.1 });
    const springY = useSpring(y, { stiffness: 150, damping: 15, mass: 0.1 });

    const handleMouseMove = (e: React.MouseEvent<HTMLAnchorElement>) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        x.set(e.clientX - centerX);
        y.set(e.clientY - centerY);
    };

    const handleMouseLeave = () => {
        x.set(0);
        y.set(0);
    };

    return (
        <motion.div style={{ x: springX, y: springY }} className="inline-block relative z-50">
            <Link
                to={to}
                onMouseMove={handleMouseMove}
                onMouseLeave={handleMouseLeave}
                className="group relative inline-flex items-center justify-center px-10 py-5 font-mono font-bold tracking-[0.3em] text-white uppercase bg-page-bg border border-neon-blue overflow-hidden hover:bg-neon-blue/10 transition-colors duration-300 interactive shadow-[0_0_20px_rgba(0,240,255,0.2)]"
            >
                <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-neon-blue to-[#B026FF] opacity-0 group-hover:opacity-20 transition-opacity duration-500 pointer-events-none" />
                <span className="absolute inset-x-0 bottom-0 h-[3px] bg-neon-blue transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-300 pointer-events-none" />
                <span className="absolute inset-x-0 top-0 h-[1px] bg-neon-blue/50 transform scale-x-0 group-hover:scale-x-100 transition-transform origin-right duration-300 delay-100 pointer-events-none" />

                <span className="relative z-10 flex items-center glitch-hover pointer-events-none" data-text={children}>
                    {children}
                    <svg className="w-5 h-5 ml-4 transform group-hover:translate-x-2 transition-transform shadow-[0_0_10px_rgba(0,240,255,0.8)]" fill="none" stroke="#00F0FF" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path></svg>
                </span>
            </Link>
        </motion.div>
    );
}


export default function Home() {
    return (
        <div className="relative w-full text-white font-sans overflow-x-hidden">
            <CyberBackground />

            {/* Hero Intro */}
            <section className="min-h-[calc(100vh-72px)] flex flex-col items-center justify-center relative text-center px-4">

                {/* Background Glitch Rings */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] border border-neon-blue/10 rounded-full border-dashed animate-[spin_20s_linear_infinite] pointer-events-none" />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] border border-neon-purple/5 rounded-full border-dashed animate-[spin_30s_linear_infinite_reverse] pointer-events-none" />

                <motion.div
                    initial={{ opacity: 0, scale: 0.8, filter: "blur(10px)" }}
                    animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                    transition={{ duration: 1.5, type: "spring", bounce: 0.4 }}
                    className="relative z-10 flex flex-col items-center"
                >
                    <Tilt tiltMaxAngleX={20} tiltMaxAngleY={20} perspective={1000} scale={1.1} transitionSpeed={1000} className="w-[300px] h-[300px] relative mb-8 interactive transform-style-3d">
                        <img
                            src="/cyber_brain_hologram_1771740436825.png"
                            alt="Brain Hologram"
                            className="w-full h-full object-cover mix-blend-screen opacity-90 [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_70%)] drop-shadow-[0_0_30px_rgba(0,240,255,0.8)] pointer-events-none"
                            style={{ filter: 'hue-rotate(-15deg) contrast(1.2)' }}
                        />
                    </Tilt>

                    <h1 className="text-7xl md:text-[10rem] font-display font-black tracking-[0.1em] neon-text mb-2 uppercase select-none glitch-hover leading-none" data-text="KalpAI">KalpAI</h1>
                    <p className="text-xl md:text-2xl font-mono text-neon-blue tracking-[0.3em] mb-16 select-none opacity-80 uppercase font-light border-b border-neon-blue/30 pb-4 px-8">Cognitive Reasoning Engine</p>

                    <MagneticButton to="/capture">Initialize System</MagneticButton>
                </motion.div>

                <div className="absolute bottom-12 w-full flex justify-center pointer-events-none">
                    <motion.div
                        animate={{ y: [0, 15, 0], opacity: [0.3, 0.8, 0.3] }}
                        transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
                        className="flex flex-col items-center"
                    >
                        <span className="text-[0.65rem] font-mono tracking-[0.4em] text-cyan-500 mb-4 uppercase">SYSTEM_SCROLL</span>
                        <div className="w-[1px] h-16 bg-gradient-to-b from-[#00F0FF] to-transparent shadow-[0_0_10px_rgba(0,240,255,1)]" />
                    </motion.div>
                </div>
            </section>

            {/* Story Sections */}
            <RevealSection
                title="Telemetry Capture"
                subtitle="Phase 01_Ingestion"
                image="/cyber_pentest_nodes_1771740484041.png"
            >
                <p className="mb-4">
                    KalpAI begins by ingesting highly structured telemetry from the target environment. Advanced Rust parsers interface directly with standard security outputs (Nmap, Nikto, Gobuster) to extract deeply nested structured states.
                </p>
                <p>
                    Raw tool string noise is discarded. Only high-fidelity semantic data is preserved, transforming chaotic heterogeneous outputs into unified structural artifacts.
                </p>
            </RevealSection>

            <RevealSection
                title="Contextual Memory Matrix"
                subtitle="Phase 02_State Representation"
                image="/cyber_memory_graph_1771740896057.png"
                reverse
            >
                <p className="mb-4">
                    Abstracted entities are projected into a dynamic local memory graph instance. This forms the Security Output Semantic Model (SOSM).
                </p>
                <p>
                    KalpAI maps physical and logical relationships in real-time, holding Environmental, Operational, and Hypothesis context simultaneously across sessions without dropping the execution chain.
                </p>
            </RevealSection>

            <RevealSection
                title="SLM Cognitive Core"
                subtitle="Phase 03_Onnx Inference"
                image="/cyber_reasoning_core_1771740878463.png"
            >
                <p className="mb-4">
                    Operating independently of cloud APIs, the ONNX Runtime executes the Microsoft Phi-3-Mini SLM entirely locally at blazing native speeds.
                </p>
                <p className="mb-6">
                    The memory graph is serialized into a highly specific contextual prompt. The Cognitive Core generates probabilistic hypotheses, finding invisible correlations between isolated vulnerabilities.
                </p>

                <div className="inline-block p-[2px] rounded bg-gradient-to-r from-neon-blue to-[#B026FF] mt-4 shadow-[0_0_15px_rgba(176,38,255,0.4)]">
                    <div className="bg-black/90 px-6 py-3 text-sm font-mono text-white tracking-widest uppercase">
                        <span className="text-neon-blue font-bold mr-2 animate-pulse">&gt;</span> HYPOTHESIS_MATRIX_ONLINE
                    </div>
                </div>
            </RevealSection>

            <div className="h-32" />
        </div>
    );
}

import { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
// @ts-ignore
import * as random from 'maath/random/dist/maath-random.esm';

function StarField(props: any) {
    const ref = useRef<any>(null);

    // Create a sphere of random points, generating exactly once
    const [sphere] = useState(() => random.inSphere(new Float32Array(5000), { radius: 1.5 }));

    useFrame((_state, delta) => {
        if (ref.current) {
            ref.current.rotation.x -= delta / 10;
            ref.current.rotation.y -= delta / 15;
        }
    });

    return (
        <group rotation={[0, 0, Math.PI / 4]}>
            <Points ref={ref} positions={sphere} stride={3} frustumCulled={false} {...props}>
                <PointMaterial
                    transparent
                    color="#00f0ff"
                    size={0.005}
                    sizeAttenuation={true}
                    depthWrite={false}
                    opacity={0.6}
                />
            </Points>
        </group>
    );
}

export default function CyberBackground() {
    return (
        <div className="fixed inset-0 z-[-1] pointer-events-none bg-page-bg">
            <Canvas camera={{ position: [0, 0, 1] }}>
                <StarField />
            </Canvas>

            {/* Overlay Gradients to blend 3D canvas with Page Theme */}
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-page-bg/50 to-page-bg pointer-events-none" />
            <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-neon-purple-glow rounded-full blur-[150px] opacity-20 pointer-events-none mix-blend-screen" />
            <div className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-neon-blue-glow rounded-full blur-[150px] opacity-10 pointer-events-none mix-blend-screen" />
        </div>
    );
}

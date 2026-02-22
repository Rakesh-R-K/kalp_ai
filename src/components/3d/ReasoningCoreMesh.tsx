import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Torus, Octahedron, MeshWobbleMaterial } from '@react-three/drei';

export default function ReasoningCoreMesh({ color = "#FACC15" }: { color?: string }) {
    const outer = useRef<any>(null);
    const inner = useRef<any>(null);

    useFrame((state) => {
        if (outer.current && inner.current) {
            outer.current.rotation.x = state.clock.getElapsedTime() * 0.5;
            outer.current.rotation.y = state.clock.getElapsedTime() * 0.3;

            inner.current.rotation.y = -state.clock.getElapsedTime() * 0.8;
            inner.current.rotation.z = state.clock.getElapsedTime() * 0.5;

            const scale = 1 + Math.sin(state.clock.getElapsedTime() * 4) * 0.1;
            inner.current.scale.set(scale, scale, scale);
        }
    });

    return (
        <group>
            <ambientLight intensity={0.5} />
            <pointLight position={[0, 0, 0]} intensity={2} color={color} />

            {/* Outer spinning ring */}
            <Torus ref={outer} args={[1.5, 0.05, 16, 50]}>
                <meshBasicMaterial color={color} wireframe />
            </Torus>

            {/* Inner pulsing core */}
            <Octahedron ref={inner} args={[0.8, 0]}>
                <MeshWobbleMaterial
                    color={color}
                    envMapIntensity={1}
                    metalness={0.8}
                    roughness={0.2}
                    factor={0.5}
                    speed={2}
                    wireframe
                />
            </Octahedron>
        </group>
    );
}

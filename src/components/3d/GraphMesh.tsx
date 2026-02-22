import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export default function GraphMesh({ count = 50, color = "#B026FF" }: { count?: number, color?: string }) {
    const group = useRef<THREE.Group>(null);
    const linesRef = useRef<THREE.LineSegments>(null);

    // Generate random stable points for graph nodes
    const { positions, lines } = useMemo(() => {
        const pos = [];
        const lin = [];
        for (let i = 0; i < count; i++) {
            pos.push((Math.random() - 0.5) * 4);
            pos.push((Math.random() - 0.5) * 4);
            pos.push((Math.random() - 0.5) * 4);
        }

        // Connect arbitrary points to form a graph
        for (let i = 0; i < count; i++) {
            for (let j = i + 1; j < count; j++) {
                if (Math.random() > 0.85) { // 15% chance to connect
                    lin.push(
                        pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2],
                        pos[j * 3], pos[j * 3 + 1], pos[j * 3 + 2]
                    );
                }
            }
        }

        return {
            positions: new Float32Array(pos),
            lines: new Float32Array(lin)
        };
    }, [count]);

    useFrame((state) => {
        if (group.current) {
            group.current.rotation.y = state.clock.getElapsedTime() * 0.1;
            group.current.rotation.z = state.clock.getElapsedTime() * 0.05;
        }
    });

    return (
        <group ref={group}>
            <points>
                <bufferGeometry>
                    <bufferAttribute
                        attach="attributes-position"
                        count={positions.length / 3}
                        args={[positions, 3]}
                    />
                </bufferGeometry>
                <pointsMaterial size={0.08} color={color} transparent opacity={0.8} sizeAttenuation />
            </points>
            <lineSegments ref={linesRef}>
                <bufferGeometry>
                    <bufferAttribute
                        attach="attributes-position"
                        count={lines.length / 3}
                        args={[lines, 3]}
                    />
                </bufferGeometry>
                <lineBasicMaterial color={color} transparent opacity={0.2} />
            </lineSegments>
        </group>
    );
}

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Icosahedron, MeshDistortMaterial } from '@react-three/drei';

export default function TelemetryMesh({ color = "#00F0FF" }: { color?: string }) {
    const mesh = useRef<any>(null);

    useFrame((state) => {
        if (mesh.current) {
            mesh.current.rotation.x = state.clock.getElapsedTime() * 0.2;
            mesh.current.rotation.y = state.clock.getElapsedTime() * 0.3;
            mesh.current.position.y = Math.sin(state.clock.getElapsedTime() * 2) * 0.1;
        }
    });

    return (
        <group>
            <ambientLight intensity={0.5} />
            <directionalLight position={[10, 10, 10]} intensity={1} />
            <Icosahedron ref={mesh} args={[1.5, 0]}>
                <MeshDistortMaterial
                    color={color}
                    envMapIntensity={0.4}
                    clearcoat={1}
                    clearcoatRoughness={0.1}
                    metalness={0.9}
                    roughness={0.1}
                    wireframe
                    distort={0.4}
                    speed={2}
                />
            </Icosahedron>
        </group>
    );
}

import { Canvas, useFrame ,useLoader  } from "@react-three/fiber";
import {
  OrbitControls,
  Float,
  Html,
  Stars,
  Line,
} from "@react-three/drei";
import { useRef, useMemo } from "react";
import * as THREE from "three"; 
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";

/* ================================================= */
/* MAIN INFRASTRUCTURE */
/* ================================================= */
function Infrastructure() {
  return (
    <>
      <ambientLight intensity={0.4} />
      <pointLight position={[0, 3, 5]} intensity={18} distance={15} />
      <pointLight position={[-4, -2, 2]} intensity={8} distance={10} />

      {/* Background stars */}
      <Stars radius={18} depth={10} count={900} factor={1.8} saturation={0} fade />

      {/* CENTRAL AI CORE */}
      <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.5}>
        <AICore />
      </Float>

      {/* INFRASTRUCTURE NODES */}
      <InfrastructureNode position={[-2.7, 1.65, 0]} label="CPU" value="42.8%" type="PROCESSING" />
      <InfrastructureNode position={[2.7, 1.65, 0]} label="RAM" value="61.4%" type="MEMORY" />
      <InfrastructureNode position={[-2.7, -1.65, 0]} label="DISK" value="52.3%" type="STORAGE" />
      <InfrastructureNode position={[2.7, -1.65, 0]} label="NETWORK" value="124 KB/s" type="TRAFFIC" />

      {/* CONNECTIONS */}
      <DataConnection start={[-2.7, 1.65, 0]} end={[0, 0, 0]} />
      <DataConnection start={[2.7, 1.65, 0]} end={[0, 0, 0]} />
      <DataConnection start={[-2.7, -1.65, 0]} end={[0, 0, 0]} />
      <DataConnection start={[2.7, -1.65, 0]} end={[0, 0, 0]} />

      {/* DATA PARTICLES */}
      <DataParticle start={[-2.7, 1.65, 0]} end={[0, 0, 0]} speed={0.8} />
      <DataParticle start={[2.7, 1.65, 0]} end={[0, 0, 0]} speed={0.6} />
      <DataParticle start={[-2.7, -1.65, 0]} end={[0, 0, 0]} speed={0.5} />
      <DataParticle start={[2.7, -1.65, 0]} end={[0, 0, 0]} speed={0.7} />
    </>
  );
}

/* ================================================= */
/* AI CORE */
/* ================================================= */
function AICore() {
  const outer = useRef();
  const inner = useRef();

  useFrame(() => {
    if (outer.current) {
      outer.current.rotation.x += 0.002;
      outer.current.rotation.y += 0.004;
      outer.current.rotation.z += 0.001;
    }
    if (inner.current) {
      inner.current.rotation.y -= 0.008;
    }
  });

  return (
    <group>
      {/* Outer AI network */}
      <mesh ref={outer}>
        <icosahedronGeometry args={[0.9, 2]} />
        <meshStandardMaterial
          wireframe
          color="#8b5cf6"
          emissive="#5b21b6"
          emissiveIntensity={2}
        />
      </mesh>

      {/* Inner core matrix */}
      <mesh ref={inner}>
        <dodecahedronGeometry args={[0.4, 1]} />
        <meshStandardMaterial
          color="#ffffff"
          emissive="#a78bfa"
          emissiveIntensity={4}
        />
      </mesh>

      <Html center>
        <div className="core-label">
          <strong>AI</strong>
          <span>CORE</span>
        </div>
      </Html>
    </group>
  );
}

/* ================================================= */
/* INFRASTRUCTURE NODE */
/* ================================================= */
function InfrastructureNode({ position, label, value, type }) {
  const group = useRef();
  let gltf = null;

   try {
    gltf = useLoader(GLTFLoader, `/models/${label.toLowerCase()}.glb`);
  } catch (error) {
    console.error(`Asset Engine: Failed to resolve model pathway for ${label}:`, error);
  }


  useFrame((state) => {
    if (!group.current) return;
    group.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.05;
  });

  return (
    <group ref={group} position={position}>
      {gltf ? (
        <primitive object={gltf.scene.clone()} scale={0.5} />
      ) : (
         <>
      <mesh>
        <boxGeometry args={[1.15, 1.15, 1.15]} />
        <meshStandardMaterial
          color="#10152a"
          emissive="#6366f1"
          emissiveIntensity={1.2}
          metalness={0.9}
          roughness={0.1}
        />
      </mesh>

      <mesh scale={1.05}>
        <boxGeometry args={[1.15, 1.15, 1.15]} />
        <meshBasicMaterial color="#a78bfa" wireframe transparent opacity={0.6} />
      </mesh>
      </>
      )}

      <Html center>
        <div className="node-label">
          <span className="node-type">{type}</span>
          <strong>{label}</strong>
          <span className="node-value">{value}</span>
        </div>
      </Html>
    </group>
  );
}


/* ================================================= */
/* DATA CONNECTION */
/* ================================================= */
function DataConnection({ start, end }) {
  return (
    <Line
      points={[start, end]}
      color="#6366f1"
      lineWidth={1.5}
      transparent
      opacity={0.5}
    />
  );
}

/* ================================================= */
/* DATA PARTICLE ANIMATION */
/* ================================================= */
function DataParticle({ start, end, speed = 0.6 }) {
  const particleRef = useRef();
  
  const startVec = useMemo(() => new THREE.Vector3(...start), [start]);
  const endVec = useMemo(() => new THREE.Vector3(...end), [end]);

  useFrame((state) => {
    if (!particleRef.current) return;
    
    // Cycle progress loop from 0 to 1 based on elapsed time and speed
    const progress = (state.clock.elapsedTime * speed) % 1;
    
    // Linearly interpolate position along the connection path
    particleRef.current.position.lerpVectors(startVec, endVec, progress);
  });

  return (
    <mesh ref={particleRef}>
      <sphereGeometry args={[0.06, 16, 16]} />
      <meshBasicMaterial color="#60a5fa" toneMapped={false} />
    </mesh>
  );
}

/* ================================================= */
/* MAIN CANVAS EXPORT */
/* ================================================= */
export default function Infrastructure3D() {
  return (
    <Canvas
      camera={{ position: [0, 0, 13], fov: 50, near: 0.1, far: 100 }}
      dpr={[1, 2]}
    >
      <Infrastructure />
      <OrbitControls
        enableZoom={false}
        enablePan={false}
        autoRotate
        autoRotateSpeed={0.15}
      />
    </Canvas>
  );
}

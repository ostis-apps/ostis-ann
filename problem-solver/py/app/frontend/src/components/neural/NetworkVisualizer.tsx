
import React, { useRef, useEffect } from 'react';

interface NeuralNode {
  id: string;
  x: number;
  y: number;
  layer: number;
  type: 'input' | 'hidden' | 'output';
}

interface NeuralConnection {
  source: string;
  target: string;
  weight: number;
}

interface NetworkVisualizerProps {
  nodes: NeuralNode[];
  connections: NeuralConnection[];
  width?: number;
  height?: number;
  animated?: boolean;
}

const NetworkVisualizer: React.FC<NetworkVisualizerProps> = ({ 
  nodes, 
  connections, 
  width = 600, 
  height = 400,
  animated = true
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  
  useEffect(() => {
    if (!svgRef.current) return;
    
    // Animation effect for connections
    if (animated) {
      const connectionPaths = svgRef.current.querySelectorAll('.neural-connection');
      connectionPaths.forEach(path => {
        path.classList.add('animate-network-flow');
      });
    }
  }, [nodes, connections, animated]);

  // Function to create bezier curve path between nodes
  const createConnectionPath = (source: NeuralNode, target: NeuralNode, weight: number): string => {
    const controlPointX = (source.x + target.x) / 2;
    return `M ${source.x} ${source.y} C ${controlPointX} ${source.y}, ${controlPointX} ${target.y}, ${target.x} ${target.y}`;
  };

  // Get node opacity based on layer
  const getNodeOpacity = (layer: number, maxLayer: number): number => {
    return 0.5 + (layer / maxLayer) * 0.5;
  };
  
  // Get node size based on type
  const getNodeSize = (type: 'input' | 'hidden' | 'output'): number => {
    switch(type) {
      case 'input': return 8;
      case 'output': return 10;
      default: return 7;
    }
  };
  
  // Get connection opacity based on weight
  const getConnectionOpacity = (weight: number): number => {
    return Math.max(0.1, Math.min(0.9, Math.abs(weight)));
  };
  
  // Get connection width based on weight
  const getConnectionWidth = (weight: number): number => {
    return Math.max(0.5, Math.min(2.5, Math.abs(weight)));
  };
  
  // Find node by id
  const findNode = (id: string): NeuralNode | undefined => {
    return nodes.find(node => node.id === id);
  };
  
  // Get max layer
  const maxLayer = Math.max(...nodes.map(node => node.layer));

  return (
    <svg ref={svgRef} width={width} height={height} className="network-grid">
      {/* Draw connections first so they appear behind nodes */}
      {connections.map((connection, index) => {
        const source = findNode(connection.source);
        const target = findNode(connection.target);
        
        if (!source || !target) return null;
        
        const path = createConnectionPath(source, target, connection.weight);
        const opacity = getConnectionOpacity(connection.weight);
        const strokeWidth = getConnectionWidth(connection.weight);
        
        return (
          <path
            key={`connection-${index}`}
            d={path}
            className="neural-connection"
            style={{ 
              opacity,
              strokeWidth,
              strokeDasharray: strokeWidth * 4,
            }}
          />
        );
      })}
      
      {/* Draw nodes */}
      {nodes.map(node => {
        const nodeSize = getNodeSize(node.type);
        const opacity = getNodeOpacity(node.layer, maxLayer);
        
        return (
          <circle
            key={node.id}
            cx={node.x}
            cy={node.y}
            r={nodeSize}
            className="neural-node"
            style={{ opacity }}
          />
        );
      })}
    </svg>
  );
};

export default NetworkVisualizer;

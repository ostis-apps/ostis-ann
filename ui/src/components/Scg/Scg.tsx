import React from 'react';
import {NODE_TYPES} from './Node/types.ts';
import {EdgeSemanticTypes} from './Edge/types.ts';
import Node from './Node/Node.tsx';
import {Edge} from './Edge/Edge.tsx';

interface NodeDataProps {
    id: string;
    type: (typeof NODE_TYPES)[number] | 'node';
    text?: string;
    x: number;
    y: number;
}

interface EdgeDataProps {
    id: string;
    type: (typeof EdgeSemanticTypes)[number] | 'arc-const';
    sourceId: string;
    targetId: string;
}

interface FromNodeToEdgeDataProps {
    id: string;
    type: (typeof EdgeSemanticTypes)[number] | 'arc-const';
    sourceNodeId: string;
    targetEdgeId: string;
}

export interface ScgDataProps {
    nodes: NodeDataProps[];
    edges: EdgeDataProps[];
    fromNodeToEdge: FromNodeToEdgeDataProps[];
}

interface ScgProps {
    propData?: ScgDataProps;
}

const Scg = ({propData}: ScgProps) => {
    const [data] = React.useState<ScgDataProps | undefined>(propData);

    const [updateHandle, setUpdateHandle] = React.useState(true);
    const updateStateById = (newState: boolean) => {
        setUpdateHandle(newState);
    };

    if (data === undefined) return null;
    return (
        <div>
            <svg className={'canvas'} width={800} height={400}>
                {data.nodes.map((node, index) => (
                    <Node
                        key={index}
                        id={node.id}
                        x={node.x}
                        y={node.y}
                        type={node.type}
                        text={node.text}
                        nodeUpdate={updateStateById}
                    />
                ))}
                {data.edges.map((edge, index) => (
                    <Edge
                        key={index}
                        id={edge.id}
                        name={'aaa'}
                        type={edge.type}
                        sourceId={edge.sourceId}
                        targetId={edge.targetId}
                        updateState={updateHandle}
                    />
                ))}
                {data.fromNodeToEdge.map((edge, index) => (
                    <Edge
                        key={index}
                        id={edge.id}
                        name={'aaa'}
                        type={edge.type}
                        sourceId={edge.sourceNodeId}
                        targetId={edge.targetEdgeId}
                        updateState={updateHandle}
                    />
                ))}
            </svg>
        </div>
    );
};

export default Scg;

import React, {SVGProps} from 'react';

export interface NodeTypes extends SVGProps<SVGSVGElement> {
    rectRef: React.RefObject<SVGSVGElement>;
    x: number;
    y: number;
    text?: string;
}

export interface RectProps {
    id: string;
    x: number;
    y: number;
    type: (typeof NODE_TYPES)[number] | 'node';
    nodeUpdate: (state: boolean) => void;
    text?: string;
}

export const NODE_TYPES = [
    'const_node',
    'node',
    'var-group-node',
    'no-role-node',
    'link-node',
] as const;

import React from 'react';
import {ArcCommon, ArcConst, ArcConstPermPosAccess} from './EdgeTextures';

export type EdgeTypes = {
    id: string;
    name: string;
    type: (typeof EdgeSemanticTypes)[number] | 'none';
    sourceId: string;
    targetId: string;
    updateState: boolean;
};

export type EdgeSVGTypes = {
    id: string;
    name: string;
    type: (typeof EdgeSemanticTypes)[number] | 'none';
    x1: number;
    y1: number;
    x2: number;
    y2: number;
};

/*
    - <b>arc-const</b>: ArcConst.tsx
    - <b>arc-common</b>: ArcCommon.tsx
    - <b>arc-const-perm-fuz-access</b>: ArcConstPermFuzAccess.tsx
*/
export const EdgeSemanticTypes = [
    'arc-const',
    'arc-common',
    'arc-const-perm-fuz-access',
    'arc-const-perm-neg-access',
    'arc-const-perm-pos-access',
] as const;

export const EdgeComponentMap: Partial<
    Record<EdgeTypes['type'], React.ComponentType<EdgeSVGTypes>>
> = {
    'arc-const': ArcConst,
    'arc-common': ArcCommon,
    /*'arc-const-perm-fuz-access': ArcConstPermFuzAccess,
    'arc-const-perm-neg-access': ArcConstPermNegAccess,*/
    'arc-const-perm-pos-access': ArcConstPermPosAccess,
};

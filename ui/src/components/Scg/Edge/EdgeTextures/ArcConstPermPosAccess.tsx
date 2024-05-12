import React from 'react';
import {getUto} from './utils.ts';
import {EdgeSVGTypes} from '../types.ts';

export const ArcConstPermPosAccess = ({id, name, type, x1, y1, x2, y2}: EdgeSVGTypes) => {
    const [chords, setChords] = React.useState<{
        x1: string;
        y1: string;
        x2: string;
        y2: string;
    } | null>(null);

    React.useEffect(() => {
        setChords(getUto(x1, y1, x2, y2));
    }, [x1, y1, x2, y2]);
    if (chords === null || chords.x1 === '0' || isNaN(Number(chords.x1))) return null;
    else
        return (
            <svg x1={chords.x1} x2={chords.x2} y1={chords.y1} y2={chords.y2} id={String(id)} name={name} type={type} className={'edge'}>
                <defs>
                    <marker
                        id={'end-arrow-perm-pos'}
                        viewBox="0 -5 10 10"
                        refX="0"
                        markerWidth="5"
                        markerHeight="10"
                        orient="auto">
                        <path d="M0,-4L10,0L0,4"></path>
                    </marker>
                </defs>
                <path
                    className={'sh'}
                    d={`M${chords.x1},${chords.y1}L${chords.x2},${chords.y2}`}
                    stroke={'black'}
                    strokeWidth={2}
                    markerEnd="url(#end-arrow-perm-pos)"></path>
            </svg>
        );
};

export default ArcConstPermPosAccess;

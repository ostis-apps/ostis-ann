import React from 'react';
import {EdgeSVGTypes} from '../types.ts';

export const ArcConst = ({id, name, type, x1, y1, x2, y2}: EdgeSVGTypes) => {
    const [chords, setChords] = React.useState<{
        x1: string;
        y1: string;
        x2: string;
        y2: string;
    } | null>(null);
    React.useEffect(() => {
        const dx = x2 - x1;
        const dy = y2 - y1;
        // Находим длину этого вектора
        const length = Math.sqrt(dx * dx + dy * dy);

        setChords({
            x1: String(x1 + (dx / length) * 15),
            y1: String(y1 + (dy / length) * 15),
            x2: String(x2 - (dx / length) * 25),
            y2: String(y2 - (dy / length) * 25),
        });
    }, [x1, y1, x2, y2]);
    if (chords === null || chords.x1 === '0' || isNaN(Number(chords.x1))) return null;
    else
        return (
            <svg
                x1={chords.x1}
                x2={chords.x2}
                y1={chords.y1}
                y2={chords.y2}
                className={'edge'}
                id={String(id)}
                name={name}
                type={type}>
                <defs>
                    <marker
                        id={'end-arrow-const' + id}
                        viewBox="0 -5 10 10"
                        refX="0"
                        markerWidth="1.3"
                        markerHeight="4"
                        orient="auto">
                        <path d="M0,-4L10,0L0,4"></path>
                    </marker>
                </defs>
                <path
                    className={'sh'}
                    d={`M${chords.x1},${chords.y1}L${chords.x2},${chords.y2}`}
                    stroke={'black'}
                    strokeWidth={8}
                    markerEnd={`url(#end-arrow-const${id})`}></path>
                <path
                    className={'sh'}
                    d={`M${chords.x1},${chords.y1}L${chords.x2},${chords.y2}`}
                    stroke={'white'}
                    strokeWidth={6}></path>
            </svg>
        );
};

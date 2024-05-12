import React from 'react';
import * as d3 from 'd3';
import {EdgeComponentMap, EdgeTypes} from './types.ts';

export const Edge = ({...props}: EdgeTypes) => {
    const [lineCoords, setLineCoords] = React.useState<{
        x1: number;
        y1: number;
        x2: number;
        y2: number;
    } | null>(null);

    const updateLines = () => {
        const findCoordsById = (id: string) => {
            const rect = d3.select(`[id="${id}"]`);
            if (!rect.empty()) {
                if (rect.classed('edge') && rect.attr('id') === props.targetId) {
                    const x = (Number(rect.attr('x1')) + Number(rect.attr('x2'))) / 2;
                    const y = (Number(rect.attr('y1')) + Number(rect.attr('y2'))) / 2;
                    return {x, y};
                } else {
                    const x = Number(rect.attr('x')) + Number(rect.attr('width')) / 2;
                    const y = Number(rect.attr('y')) + Number(rect.attr('height')) / 2;
                    return {x, y};
                }
            }
            return null;
        };

        // Находим координаты для sourceId и targetId
        const sourceCoords = findCoordsById(props.sourceId);
        const targetCoords = findCoordsById(props.targetId);

        // Если удалось найти координаты для обоих узлов, устанавливаем их в state
        if (sourceCoords && targetCoords) {
            setLineCoords({
                x1: sourceCoords.x,
                y1: sourceCoords.y,
                x2: targetCoords.x,
                y2: targetCoords.y,
            });
        }
    };

    React.useEffect(() => {
        updateLines();
    }, [props.sourceId, props.targetId]);

    /*
        Реагирует на перемещение ноды
    */
    React.useEffect(() => {
        let intervalId: NodeJS.Timeout;

        if (props.updateState) {
            intervalId = setInterval(() => {
                if (props.updateState) updateLines();
                else clearInterval(intervalId); // остановка интервала
            }, 24);
        }

        return () => clearInterval(intervalId);
    }, [props.updateState]);

    const Component = EdgeComponentMap[props.type];
    if (lineCoords != null) {
        return Component ? (
            <Component
                id={props.id}
                type={props.type}
                name={props.name}
                x1={lineCoords.x1}
                y1={lineCoords.y1}
                x2={lineCoords.x2}
                y2={lineCoords.y2}
            />
        ) : null; // TODO create base or "none" edge
    } else {
        return null;
    }
};

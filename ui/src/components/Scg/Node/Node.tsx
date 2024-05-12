import * as d3 from 'd3';
import React from 'react';
import {NodeVar, ConstNode} from './NodeTextures';
import {RectProps} from './types.ts';
import VarGroupNode from './NodeTextures/VarGroupNode.tsx';
import NoRoleNode from './NodeTextures/NoRoleNode.tsx';
import LinkNode from './NodeTextures/LinkNode.tsx';

const Node = ({id, x, y, type = 'node', text, nodeUpdate}: RectProps) => {
    const rectRef = React.useRef<SVGSVGElement>(null);
    const handleClick = React.useCallback((event: React.MouseEvent<SVGSVGElement, MouseEvent>) => {
        event.preventDefault();
        switch (event.type) {
            case 'click':
                console.log('click');
                break;
            case 'contextmenu':
                console.log('contextmenu');
                break;
        }
    }, []);

    React.useEffect(() => {
        if (!rectRef.current) return;

        const drag = d3
            .drag()
            .subject(() => {
                const rect = d3.select(rectRef.current!);
                nodeUpdate(true);
                console.log(
                    'Current rect position:',
                    rect.attr('x'),
                    rect.attr('y'),
                    rect.attr('id'),
                ); //fixme удалить при билде
                return {x: rect.attr('x')!, y: rect.attr('y')!};
            })
            .on('drag', () => {
                const svgRect = document.querySelector('.canvas')!.getBoundingClientRect(); // Получаем координаты svg.canvas
                const rect = d3.select(rectRef.current!);

                const rectWidth = Number(rect.attr('width'));
                const rectHeight = Number(rect.attr('height'));
                console.log(svgRect.width);
                if (
                    (event as MouseEvent).clientX - svgRect.left - rectWidth / 2 >
                        svgRect.width - 42 ||
                    (event as MouseEvent).clientX - svgRect.left - rectWidth / 2 < -16
                )
                    return;

                if (
                    (event as MouseEvent).clientY - svgRect.top - rectHeight / 2 >
                        svgRect.height - rectHeight / 2 ||
                    (event as MouseEvent).clientY - svgRect.top - rectHeight / 2 < -16
                )
                    return;

                rect.attr('x', (event as MouseEvent).clientX - svgRect.left - rectWidth / 2); // учитываем положение холста и размеры ноды, некоторые с текстом
                rect.attr('y', (event as MouseEvent).clientY - svgRect.top - rectHeight / 2);
            })
            .on('end', () => {
                nodeUpdate(false);
            });

        drag(d3.select(rectRef.current as never));
    }, []);
    if (type === 'const_node') {
        return (
            <ConstNode
                text={text}
                id={String(id)}
                onContextMenu={(event) => handleClick(event)}
                x={x}
                y={y}
                rectRef={rectRef}
            />
        );
    } else if (type === 'node') {
        return (
            <NodeVar
                text={text}
                id={String(id)}
                onContextMenu={(event) => handleClick(event)}
                x={x}
                y={y}
                rectRef={rectRef}
            />
        );
    } else if (type === 'var-group-node') {
        return (
            <VarGroupNode
                text={text}
                id={String(id)}
                onContextMenu={(event) => handleClick(event)}
                x={x}
                y={y}
                rectRef={rectRef}
            />
        );
    } else if (type === 'no-role-node') {
        return (
            <NoRoleNode
                text={text}
                id={String(id)}
                onContextMenu={(event) => handleClick(event)}
                x={x}
                y={y}
                rectRef={rectRef}
            />
        );
    } else if (type === 'link-node') {
        return (
            <LinkNode
                text={text}
                id={String(id)}
                onContextMenu={(event) => handleClick(event)}
                x={x}
                y={y}
                rectRef={rectRef}
            />
        );
    }
};

export default Node;

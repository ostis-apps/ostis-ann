import {NodeTypes} from '../types.ts';

const LinkNode = ({rectRef, y, x, ...props}: NodeTypes) => {
    return (
        <svg
            width={21}
            height={21}
            viewBox={`0 0 ${21} ${21}`}
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            ref={rectRef}
            x={x}
            y={y}
            {...props}
            className={'node'}>
            {/* eslint-disable-next-line react/react-in-jsx-scope */}
            <rect width={21} height={21} fill="none" stroke={'black'} strokeWidth={2} />

            {/* Текст */}
            {props.text && (
                // eslint-disable-next-line react/react-in-jsx-scope
                <text className={'text'} x="70%" y="50%" fill="black" fontSize="14px">
                    'sdfh'
                </text>
            )}
        </svg>
    );
};

export default LinkNode;

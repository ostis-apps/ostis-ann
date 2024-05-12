import {NodeTypes} from '../types.ts';

export const NodeVar = ({rectRef, y, x, ...props}: NodeTypes) => {
    return (
        // eslint-disable-next-line react/react-in-jsx-scope
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="64"
            height="64"
            viewBox="0 0 64 64"
            fill="none"
            ref={rectRef}
            x={x}
            y={y}
            {...props}
            className={'node'}>
            {/* eslint-disable-next-line react/react-in-jsx-scope */}
            <circle cx="30.5" cy="30.5" r="10" fill="white" stroke="black" />
            {props.text ? (
                // eslint-disable-next-line react/react-in-jsx-scope
                <text className={'text'} x="70%" y="50%" fill="black" fontSize="14px">
                    {props.text}
                </text>
            ) : null}
        </svg>
    );
};

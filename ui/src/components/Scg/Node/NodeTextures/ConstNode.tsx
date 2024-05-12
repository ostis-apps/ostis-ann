import {NodeTypes} from '../types.ts';

export const ConstNode = ({rectRef, y, x, ...props}: NodeTypes) => {
    return (
        // eslint-disable-next-line react/react-in-jsx-scope
        <svg
            width="21"
            height="21"
            viewBox="0 0 21 21"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            ref={rectRef}
            x={x}
            y={y}
            {...props}
            className={'node'}>
            {/* eslint-disable-next-line react/react-in-jsx-scope */}
            <path
                className={'path'}
                d="M16 10.5C16 13.5376 13.5376 16 10.5 16C7.46243 16 5 13.5376 5 10.5C5 7.46243 7.46243 5 10.5 5C13.5376 5 16 7.46243 16 10.5Z"
                fill="black"
            />
            {/* eslint-disable-next-line react/react-in-jsx-scope */}
            <path
                fillRule="evenodd"
                clipRule="evenodd"
                className={'path'}
                d="M21 10.5C21 16.299 16.299 21 10.5 21C4.70101 21 0 16.299 0 10.5C0 4.70101 4.70101 0 10.5 0C16.299 0 21 4.70101 21 10.5ZM10.5 20C15.7467 20 20 15.7467 20 10.5C20 5.25329 15.7467 1 10.5 1C5.25329 1 1 5.25329 1 10.5C1 15.7467 5.25329 20 10.5 20Z"
                fill="black"
            />
            {/* eslint-disable-next-line react/react-in-jsx-scope */}
            <path
                fillRule="evenodd"
                clipRule="evenodd"
                className={'path'}
                d="M20 10.5C20 15.7467 15.7467 20 10.5 20C5.25329 20 1 15.7467 1 10.5C1 5.25329 5.25329 1 10.5 1C15.7467 1 20 5.25329 20 10.5ZM10.5 16C13.5376 16 16 13.5376 16 10.5C16 7.46243 13.5376 5 10.5 5C7.46243 5 5 7.46243 5 10.5C5 13.5376 7.46243 16 10.5 16Z"
                fill="white"
            />
            {props.text ? (
                // eslint-disable-next-line react/react-in-jsx-scope
                <text className={'text'} x="120%" y="100%" fill="black" fontSize="14px">
                    {props.text}
                </text>
            ) : null}
        </svg>
    );
};

import {NodeTypes} from '../types.ts';

const NoRoleNode = ({rectRef, y, x, ...props}: NodeTypes) => {
    return (
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
                d="M10.5 1C12.1281 1 13.6606 1.40957 15 2.13131C16.6375 3.01365 17.9863 4.36254 18.8687 6C19.5904 7.3394 20 8.87187 20 10.5C20 12.1281 19.5904 13.6606 18.8687 15C17.9863 16.6375 16.6375 17.9863 15 18.8687C13.6606 19.5904 12.1281 20 10.5 20C8.87187 20 7.3394 19.5904 6 18.8687C4.36254 17.9863 3.01365 16.6375 2.13131 15C1.40957 13.6606 1 12.1281 1 10.5C1 8.87187 1.40957 7.3394 2.13131 6C3.01365 4.36254 4.36254 3.01365 6 2.13131C7.3394 1.40957 8.87187 1 10.5 1Z"
                fill="white"
            />
            {/* eslint-disable-next-line react/react-in-jsx-scope */}
            <path
                className={'path'}
                d="M10.5 10.5L17.2175 3.78249M10.5 10.5L3.78249 17.2175M10.5 10.5L3.78249 3.78249M10.5 10.5L17.2175 17.2175M17.2175 3.78249C15.4984 2.06332 13.1234 1 10.5 1C7.87665 1 5.50165 2.06332 3.78249 3.78249M17.2175 3.78249C18.9367 5.50165 20 7.87665 20 10.5C20 13.1234 18.9367 15.4984 17.2175 17.2175M3.78249 17.2175C5.50165 18.9367 7.87665 20 10.5 20C13.1234 20 15.4984 18.9367 17.2175 17.2175M3.78249 17.2175C2.06332 15.4984 1 13.1234 1 10.5C1 7.87665 2.06332 5.50165 3.78249 3.78249"                stroke="black"
                strokeWidth="1.5"
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

export default NoRoleNode;

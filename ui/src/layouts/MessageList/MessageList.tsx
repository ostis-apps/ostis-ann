// import React from 'react';
import {block} from '../../utils';
import {Flex} from '@gravity-ui/uikit';
import './MessageList.scss';
import Message, {MessageProps} from '../../components/Message/Message.tsx';
const b = block('message-list');

export interface MessageListProps {
    messages: MessageProps[];
}

const MessageList = ({messages}: MessageListProps) => {
    return (
        <Flex direction={'column'} justifyContent={'end'} className={b()}>
            {messages.map((item, key) => {
                return <Message key={key} type={item.type} message={item.message} />;
            })}
        </Flex>
    );
};

export default MessageList;

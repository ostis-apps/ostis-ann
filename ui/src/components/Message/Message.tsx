import React from 'react';
import {Avatar, Flex, Text} from '@gravity-ui/uikit';
import {block} from '../../utils';
import './Message.scss';
import Scg from '../Scg/Scg.tsx';

const b = block('message');

export interface MessageProps {
    type: 'from' | 'to';
    message: string;
}

const Message = ({type = 'to', message}: MessageProps) => {
    const [time] = React.useState(new Date());

    return (
        <Flex gap={4} className={b(type)}>
            {type === 'to' ? <Avatar text={'Ann'} theme={'normal'} size="xl" /> : null}
            <Flex direction={'column'} maxWidth={'60%'} gap={1}>
                <Flex direction={'column'} className={b(type, 'message')}>
                    <Text variant={'body-2'}>{message}</Text>
                    <Scg />
                </Flex>
                <Text variant={'caption-2'} color={'secondary'}>
                    {('0' + time.getHours()).slice(-2)}:{('0' + time.getMinutes()).slice(-2)}
                </Text>
            </Flex>
            {type === 'from' ? <Avatar text={'You'} theme={'brand'} size="xl" /> : null}
        </Flex>
    );
};

export default Message;

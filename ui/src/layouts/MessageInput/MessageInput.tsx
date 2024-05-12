// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-expect-error
import React from 'react';
import {Button, Flex, Icon, TextArea} from '@gravity-ui/uikit';
import {ArrowUp, Microphone, FilePlus} from '@gravity-ui/icons';
import {block} from '../../utils';
import './MessageInput.scss';
const b = block('message-input');

interface MessageInputProps {
    setSendMessage: (msg: string) => void;
    value: string;
    sendMessage: () => void;
}

const MessageInput = ({setSendMessage, value, sendMessage}: MessageInputProps) => {
    return (
        <Flex className={b()} alignItems={'end'} gap={2}>
            <TextArea
                value={value}
                view={'clear'}
                onUpdate={(value) => setSendMessage(value)}
                size={'xl'}
                placeholder={'Cooбщение для OSTIS Ann...'}
                maxRows={5}
            />
            <Button size={'xl'} view={'flat'} onClick={() => sendMessage()}>
                <Icon data={FilePlus} />
            </Button>
            <Button
                size={'xl'}
                view={value !== '' ? 'action' : 'flat'}
                onClick={() => sendMessage()}>
                <Icon data={value === '' ? Microphone : ArrowUp} />
            </Button>
        </Flex>
    );
};

export default MessageInput;

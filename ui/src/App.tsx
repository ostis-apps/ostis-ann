import React from 'react';
import Header from './layouts/Header/Header.tsx';
import './styles/styles.scss';
import {Avatar, Button, Flex, Icon, Modal, Text, TextArea} from '@gravity-ui/uikit';
import {block} from './utils';
import {getMessageHistory} from './app/reader.ts';
import Scg, {ScgDataProps} from './components/Scg/Scg.tsx';
import {Microphone, ArrowUp, Picture} from '@gravity-ui/icons';
import 'regenerator-runtime/runtime';
import SpeechRecognition, {useSpeechRecognition} from 'react-speech-recognition';
import {MAIN_ID} from './app/common.ts';
import {createQuestion} from './app/index.ts';

const b = block('main');

function App() {
    const [messages, setMessages] = React.useState<
        {id: number; request: string; img: string; response: string; struct: ScgDataProps}[]
    >([]);

    const [inputMessage, setInputMessage] = React.useState('');
    const [inputImg, setInputImg] = React.useState('');
    const {transcript, resetTranscript} = useSpeechRecognition();
    const [isRecord, setIsRecord] = React.useState<boolean>(false);
    const inputFile: React.RefObject<HTMLInputElement> = React.useRef(null);
    const [isSending, setIsSending] = React.useState(false);
    const [scgModal, setScgModal] = React.useState({state: false, msgId: -1});

    React.useEffect(() => {
        getMessageHistory().then((r) => {
            setMessages(r);
            /*for(let i = 0; i< 10; i++){
                setMessages((prevMessages) => [...prevMessages, r[0]]);
            }*/
        });
    }, []);

    const onSend = async () => {
        setIsSending(true);
        console.log('Send');
        const resMessage: {
            id: number;
            request: string;
            img: string;
            response: string;
            struct: ScgDataProps;
        } = {
            id: messages.length + 1,
            request: inputMessage,
            img: '',
            response: '',
            struct: {nodes: [], edges: [], fromNodeToEdge: []},
        };
        const result = await createQuestion(messages.length + 1, inputMessage, inputImg);
        console.log(result);
        if (result.response !== '') {
            resMessage.response = result.response;
        }
        if (result.struct.nodes.length != 0) {
            resMessage.struct = result.struct;
        }
        if (inputImg !== '') {
            resMessage.img = inputImg;
        }
        setMessages((prevState) => [
            ...prevState,
            {
                id: resMessage.id,
                img: resMessage.img,
                response: resMessage.response,
                struct: resMessage.struct,
                request: resMessage.request,
            },
        ]);

        setInputMessage('');
        setInputImg('');
        setIsSending(false);
    };

    const handleListen = () => {
        if (!isRecord) {
            resetTranscript();
            SpeechRecognition.startListening({
                language: 'ru-RU',
            });
            setIsRecord(true);
        } else if (isRecord) {
            SpeechRecognition.stopListening();
            setIsRecord(false);
            setInputMessage(transcript);
        }
    };

    const handleOnChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
        e.preventDefault();

        const file: File | undefined = e.target.files?.[0];

        if (!file) {
            console.error('No file selected');
            return;
        }

        const reader = new FileReader();
        reader.onloadend = () => {
            const base64String: string | null = reader.result as string | null;
            if (base64String) {
                setInputImg(base64String);
                console.log(base64String);
            }
        };
        reader.readAsDataURL(file);
    };

    const onButtonSelectFile = () => {
        // `current` points to the mounted file input element
        if (inputFile.current) {
            // `current` points to the mounted file input element
            inputFile.current.click();
        }
    };

    return (
        <Flex className={b()} direction={'column'} justifyContent={'space-between'}>
            <Modal open={scgModal.state} onClose={() => setScgModal({state: false, msgId: -1})}>
                {scgModal.msgId != -1 ? (
                    <Flex direction={'column'} style={{padding: '24px'}}>
                        {messages[scgModal.msgId].struct.nodes.length != 0 ? (
                            <Scg propData={messages[scgModal.msgId].struct} />
                        ) : null}
                    </Flex>
                ) : null}
            </Modal>
            <Header />
            <Flex
                direction={'column'}
                overflow={'auto'}
                gap={4}
                style={{
                    overflowY: 'scroll',
                    height: '100%',
                    padding: '12px 12px',
                    borderTop: '1px var(--g-color-base-generic-medium) solid',
                }}>
                {messages.map((item, index) => {
                    return (
                        <Flex key={index} direction={'column'} gap={4}>
                            <Flex justifyContent={'end'} gap={2}>
                                <Flex
                                    direction={'column'}
                                    gap={2}
                                    style={{
                                        background: 'var(--g-color-base-misc-light)',
                                        padding: '12px',
                                        borderRadius: '12px 4px 12px 12px',
                                        maxWidth: '50%',
                                    }}>
                                    <Text>{item.request}</Text>
                                    {item.img !== ' ' && item.img !== '' && (
                                        <img
                                            src={`data:image/png;base64,${item.img}`}
                                            alt="Изображение"
                                        />
                                    )}
                                </Flex>
                                <Avatar text="You" theme={'normal'} size="xl" />
                            </Flex>
                            <Flex gap={2} style={{width: '100%'}}>
                                <Avatar text="Ann" theme={'brand'} size="xl" />
                                <Flex
                                    direction={'column'}
                                    gap={2}
                                    style={{
                                        background: 'var(--g-color-base-misc-light)',
                                        padding: '12px',
                                        borderRadius: '4px 12px 12px 12px',
                                        maxWidth: '100%',
                                    }}>
                                    <Text>
                                        {item.response === '' && item.struct.nodes.length != 0 ? (
                                            <>Ответ представлен в виде структуры:</>
                                        ) : (
                                            <>{item.response}</>
                                        )}
                                    </Text>
                                    <Flex justifyContent={'center'} alignItems={'center'} style={{cursor: 'pointer', padding: '12px', color: 'var(--g-color-text-dark-hint)'}} onClick={() => setScgModal({state: true, msgId: index})}>
                                        <Text variant={'display-4'} style={{textAlign: 'center'}}>SCG</Text>
                                    </Flex>
                                    {/*{item.struct.nodes.length > 0 && <Scg propData={item.struct} />}*/}
                                </Flex>
                            </Flex>
                        </Flex>
                    );
                })}
            </Flex>
            <Flex
                style={{
                    padding: '12px 12px',
                    borderTop: '1px var(--g-color-base-generic) solid',
                }}>
                <TextArea
                    maxRows={5}
                    disabled={isSending}
                    size={'xl'}
                    placeholder={'Введите запрос...'}
                    view={'clear'}
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                />
                <Flex gap={4}>
                    <Button
                        disabled={isSending}
                        size={'xl'}
                        view={'flat'}
                        onClick={onButtonSelectFile}>
                        <input
                            type="file"
                            id="file"
                            ref={inputFile}
                            accept={'image/*'}
                            onChange={(e) => handleOnChange(e)}
                            style={{display: 'none'}}
                        />
                        <Icon data={Picture} />
                    </Button>
                    <Button
                        disabled={isSending}
                        onClick={inputMessage === '' ? handleListen : onSend}
                        size={'xl'}
                        view={!isRecord ? 'flat' : 'action'}>
                        {inputMessage === '' ? <Icon data={Microphone} /> : <Icon data={ArrowUp} />}
                    </Button>
                </Flex>
            </Flex>
        </Flex>
    );
}

export default App;

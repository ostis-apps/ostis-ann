import {
    ScAddr,
    ScConstruction,
    ScLinkContent,
    ScLinkContentType,
    ScTemplate,
    ScType,
} from 'ts-sc-client';
import {client} from './common.ts';
import {getChatAddr, getElementName, getResponseStruct} from './reader.ts';
import {ScgDataProps} from '../components/Scg/Scg.tsx';

//const messageAddr: ScAddr[] = [];

export const createQuestion = async (index: number, prompt = 'Запрос', base64img?: string) => {
    const chatHistoryKeynode = await client.findKeynodes('ostis_ann_chats_history');
    const chatHistoryKeynodeAddr = new ScAddr(chatHistoryKeynode.ostisAnnChatsHistory.value); // Замените 123 на фактический адрес вашей ноды
    const chatAddr = await getChatAddr(chatHistoryKeynodeAddr);
    console.log(index, prompt, base64img);

    const nrelImageKeynode = await client.findKeynodes('nrel_image');
    const nrelImageKeynodeAddr = new ScAddr(nrelImageKeynode['nrelImage'].value);

    const nrelPromptKeynode = await client.findKeynodes('nrel_text_prompt');
    const nrelPromptKeynodeAddr = new ScAddr(nrelPromptKeynode['nrelTextPrompt'].value);

    const construction = new ScConstruction();

    construction.createNode(ScType.NodeConstTuple, 'edge_msg_tuple');
    construction.createEdge(
        ScType.EdgeAccessConstPosPerm,
        new ScAddr(chatAddr),
        'edge_msg_tuple',
        'edge_chat_to_tuple',
    );
    construction.createNode(ScType.NodeConstRole, 'node_role');
    construction.createLink(
        ScType.LinkConst,
        new ScLinkContent(String(index) + "'", ScLinkContentType.String),
        'link_msg_index',
    );
    construction.createEdge(ScType.EdgeDCommonConst, 'node_role', 'link_msg_index', 'idf');
    construction.createEdge(ScType.EdgeAccessConstPosPerm, 'node_role', 'edge_chat_to_tuple');
    construction.createLink(
        ScType.LinkConst,
        new ScLinkContent(prompt, ScLinkContentType.String),
        'link_prompt',
    );
    if (base64img !== undefined && base64img !== null && base64img !== '' && base64img !== ' ') {
        construction.createLink(
            ScType.LinkConst,
            new ScLinkContent(base64img, ScLinkContentType.String),
            'link_image',
        );
        construction.createEdge(
            ScType.EdgeDCommonConst,
            'edge_msg_tuple',
            'link_image',
            'edge_tuple_to_link_image',
        );
        construction.createEdge(
            ScType.EdgeAccessConstPosPerm,
            nrelImageKeynodeAddr,
            'edge_tuple_to_link_image',
        );
    }

    construction.createEdge(
        ScType.EdgeDCommonConst,
        'edge_msg_tuple',
        'link_prompt',
        'edge_tuple_to_link_prompt',
    );

    construction.createEdge(
        ScType.EdgeAccessConstPosPerm,
        nrelPromptKeynodeAddr,
        'edge_tuple_to_link_prompt',
    );

    const res1 = await client.createElements(construction);
    console.log(res1);
    const result: {response: string; struct: ScgDataProps} = {
        response: '',
        struct: {nodes: [], edges: [], fromNodeToEdge: []},
    };
    const intervalFunction = async () => {
        // Весь код внутри setInterval должен быть обернут в try-catch, чтобы обрабатывать ошибки
        try {
            const template = new ScTemplate();
            template.triple(res1[0], ScType.EdgeDCommonVar, ScType.NodeVarStruct);
            const res = await client.templateSearch(template);
            if (res.length != 0) {
                result.struct = await getResponseStruct(res[0].get(2));
            }

            const tempalte1 = new ScTemplate();
            tempalte1.tripleWithRelation(
                res1[0],
                ScType.EdgeDCommonVar,
                ScType.LinkVar,
                ScType.EdgeAccessVarPosPerm,
                ScType.NodeVarNoRole,
            );
            const res2 = await client.templateSearch(tempalte1);
            for (let j = 0; j < res2.length; j++) {
                if ((await getElementName(res2[j].get(3))) === 'nrel_text_response') {
                    const linkContent = (await client.getLinkContents([res2[j].get(2)]))[0].data;
                    if (linkContent) {
                        result.response = String(linkContent);
                    }
                }
            }
            console.log(i++);
            if (i > 50 || result.response) {
                console.log(result);
                clearInterval(intervalId);
            }
        } catch (error) {
            console.error('An error occurred inside setInterval:', error);
            clearInterval(intervalId); // Останавливаем setInterval в случае ошибки
        }
    };

    // Устанавливаем setInterval
    const intervalId = setInterval(intervalFunction, 1000);

    // Ждем, пока выполнится 50 итераций
    let i = 0;
    while (i <= 5 || result.struct.nodes.length == 0) {
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Ждем 2 секунды перед следующей итерацией
        i++;
    }

    clearInterval(intervalId); // Останавливаем setInterval после выполнения 50 итераций

    // Возвращаем результат
    return result;
};

import { client, EdgeTypes, NodeType} from './common.ts';
import {ScAddr, ScTemplate, ScTemplateResult, ScType} from 'ts-sc-client';
import {ScgDataProps} from '../components/Scg/Scg.tsx';

const randX = Math.random() * 800;
const randY = Math.random() * 400;

export const getMessageHistory = async () => {
    const result = [];
    const messageAddrs = await getMessageAddrs();
    console.log(messageAddrs);
    for (let i = 0; i < messageAddrs.length; i++) {
        const content = await getMessageContent(messageAddrs[i].addr);
        result.push({
            id: messageAddrs[i].id,
            request: content.request,
            img: content.img,
            response: content.response,
            struct: content.struct,
        });
    }
    console.log(result);
    return result;
};

const getMessageAddrs = async () => {
    const result = [];
    const mainNode = await client.findKeynodes('ostis_ann_chats_history');
    const mainNodeAddr = new ScAddr(mainNode.ostisAnnChatsHistory.value);
    const chatAddr = await getChatAddr(mainNodeAddr);

    const template = new ScTemplate();
    template.tripleWithRelation(
        new ScAddr(chatAddr),
        ScType.EdgeAccessVarPosPerm,
        ScType.NodeVarTuple,
        ScType.EdgeAccessVarPosPerm,
        ScType.NodeVarRole,
    );
    const searchResults: ScTemplateResult[] = await client.templateSearch(template);
    for (let i = 0; i < searchResults.length; i++) {
        result.push({
            id: Number((await getMessageId(searchResults[0].get(3)))[0]),
            addr: searchResults[i].get(2),
        });
    }
    return result;
};

export const getChatAddr = async (mainNodeAddr: ScAddr) => {
    const template = new ScTemplate();
    template.triple(mainNodeAddr, ScType.EdgeAccessVarPosPerm, ScType.NodeVarStruct);
    const searchResults = await client.templateSearch(template);
    /*
        If you need to add several chats, then you need to return an array of addresses.
    */
    return searchResults[0].get(2).value;
};

const getMessageId = async (messageRoleAddr: ScAddr) => {
    const template = new ScTemplate();
    template.triple(messageRoleAddr, ScType.EdgeDCommonVar, ScType.LinkVar);
    const searchResults = await client.templateSearch(template);
    const data = await client.getLinkContents([searchResults[0].get(2)]);
    return String(data[0].data);
};

const getMessageContent = async (msgAddr: ScAddr) => {
    const result: {request: string; img: string; response: string; struct: ScgDataProps} = {
        request: '',
        img: '',
        response: '',
        struct: {edges: [], fromNodeToEdge: [], nodes: []},
    };
    const template = new ScTemplate();
    template.tripleWithRelation(
        msgAddr,
        ScType.EdgeDCommonVar,
        ScType.Unknown,
        ScType.EdgeAccessVarPosPerm,
        ScType.NodeVarNoRole,
    );
    const searchResult = await client.templateSearch(template);
    for (let i = 0; i < searchResult.length; i++) {
        console.log(searchResult[i]);
        const roleName = await getMessageId(searchResult[i].get(3));
        if (roleName === 'nrel_image') {
            result.img = String((await client.getLinkContents([searchResult[i].get(2)]))[0].data);
        } else if (roleName === 'nrel_text_response') {
            result.response = String(
                (await client.getLinkContents([searchResult[i].get(2)]))[0].data,
            );
        } else if (roleName === 'nrel_text_prompt') {
            result.request = String(
                (await client.getLinkContents([searchResult[i].get(2)]))[0].data,
            );
        } else if (roleName === 'nrel_struct_pointer') {
            const addr = searchResult[i].get(2);
            const struct = await getResponseStruct(addr);
            result.struct = struct;
            console.log(struct);
        }
    }
    return result;
};

export const getResponseStruct = async (structAddr: ScAddr) => {
    console.log(structAddr);
    const elements = await getAllAddrsOfStruct(structAddr);
    console.log(elements);
    return await findInsideElements(elements);
};

const getAllAddrsOfStruct = async (structAddr: ScAddr) => {
    const result: ScAddr[] = [];
    const template = new ScTemplate();
    template.triple(structAddr, ScType.EdgeAccessVarPosPerm, ScType.Unknown);
    const templateResult = await client.templateSearch(template);
    templateResult.map((element) => {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-expect-error
        element.forEachTriple((structAddr: ScAddr, edge: ScAddr, target: ScAddr) => {
            result.push(target);
        });
    });
    return result;
};

const findInsideElements = async (elements: ScAddr[]) => {
    const result: ScgDataProps = {nodes: [], edges: [], fromNodeToEdge: []};
    for (let i = 0; i < elements.length; i++) {
        for (let j = 0; j < elements.length; j++) {
            if (j == i) continue;
            const template = new ScTemplate();
            template.triple(elements[i], ScType.Unknown, elements[j]);
            const templateResult = await client.templateSearch(template);
            if (templateResult.length != 0) {
                const edgeLinks = await getEdgeLinks(templateResult);
                if (edgeLinks !== undefined) {
                    edgeLinks.edges.map((item) => {
                        if (result.edges.find((itm) => itm.id === item.id) == undefined)
                            result.edges.push(item);
                    });
                    edgeLinks.nodes.map((item) => {
                        if (result.nodes.find((itm) => itm.id === item.id) == undefined)
                            result.nodes.push(item);
                    });
                    edgeLinks.fromNodeToEdge.map((item) => {
                        if (result.fromNodeToEdge.find((itm) => itm.id === item.id) == undefined)
                            result.fromNodeToEdge.push(item);
                    });
                }
            }
        }
    }
    return result;
};

const getEdgeLinks = async (templateResults: ScTemplateResult[]) => {
    const result: ScgDataProps = {nodes: [], edges: [], fromNodeToEdge: []};
    for (let i = 0; i < templateResults.length; i++) {
        const src = templateResults[i].get(0);
        const element = templateResults[i].get(1);
        const target = templateResults[i].get(2);

        const srcType = (await client.checkElements([src]))[0].value;
        const elementType = (await client.checkElements([element]))[0].value;
        const targetType = (await client.checkElements([target]))[0].value;
        const srcName = (await getElementName(src)) ? await getElementName(src) : '';
        const targetName = (await getElementName(target)) ? await getElementName(target) : '';
        if (srcName === 'идентификатор*') {
            console.log(srcType, elementType, new ScType(targetType).isEdge());
        }
        if (new ScType(targetType).isEdge()) {
            result.nodes.push({
                id: 'n' + src.value,
                text: srcName,
                type: NodeType[srcType],
                x: Math.random() * 700,
                y: Math.random() * 350,
            });
            result.fromNodeToEdge.push({
                id: 'e' + element.value,
                sourceNodeId: 'n' + src.value,
                targetEdgeId: 'e' + target.value,
                type: EdgeTypes[elementType],
            });
            console.log(result);
        } else if (new ScType(targetType).isNode()) {
            result.nodes.push({
                id: 'n' + src.value,
                text: srcName,
                type: NodeType[srcType],
                x: Math.random() * 700,
                y: Math.random() * 350,
            });
            result.nodes.push({
                id: 'n' + target.value,
                text: targetName,
                type: NodeType[targetType],
                x: Math.random() * 700,
                y: Math.random() * 350,
            });
            result.edges.push({
                id: 'e' + element.value,
                sourceId: 'n' + src.value,
                targetId: 'n' + target.value,
                type: EdgeTypes[elementType],
            });
        } else {
            result.nodes.push({
                id: 'n' + src.value,
                text: srcName,
                type: NodeType[srcType],
                x: Math.random() * 700,
                y: Math.random() * 350,
            });
            result.nodes.push({
                id: 'n' + target.value,
                text: targetName,
                type: NodeType[targetType],
                x: Math.random() * 700,
                y: Math.random() * 350,
            });
            result.edges.push({
                id: 'e' + element.value,
                sourceId: 'n' + src.value,
                targetId: 'n' + target.value,
                type: EdgeTypes[elementType],
            });
        }
    }
    return result;
};

export const getElementName = async (addr: ScAddr) => {
    const template = new ScTemplate();
    template.tripleWithRelation(
        addr,
        ScType.EdgeDCommonVar,
        ScType.LinkVar,
        ScType.EdgeAccessVarPosPerm,
        ScType.NodeVarNoRole,
    );
    const templateResult = await client.templateSearch(template);
    if (templateResult.length != 0) {
        return String((await client.getLinkContents([templateResult[0].get(2)]))[0].data);
    } else {
        return '';
    }
};

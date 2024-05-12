import {ScAddr, ScClient} from 'ts-sc-client';
import {NODE_TYPES} from '../components/Scg/Node/types.ts';
import {EdgeSemanticTypes} from '../components/Scg/Edge/types.ts';

export const client = new ScClient('ws://localhost:8090/ws_json');

export const CHAT_ADDRS: {id: number; addr: ScAddr}[] = [];

export const CHAT_HISTORY_ADDR = 'ostis_ann_chats_history';

export const SYSTEM_ID = (await client.findKeynodes('системный идентификатор*'))[
    'системный идентификатор*'
].value;

export const MAIN_ID = (await client.findKeynodes('основной идентификатор*'))[
    'основной идентификатор*'
].value;

export const NodeType: Record<number, (typeof NODE_TYPES)[number]> = {
    32: 'const_node',
    33: 'node',
    2081: 'var-group-node',
    1057: 'no-role-node',
};
export const EdgeTypes: Record<number, (typeof EdgeSemanticTypes)[number]> = {
    40: 'arc-const',
    2224: 'arc-const-perm-pos-access',
};

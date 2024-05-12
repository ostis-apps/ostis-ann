import {ScAddr, ScClient} from 'ts-sc-client';

/*
    As I understand it, overloading methods is an impossible task for a library...
*/
export const getLinkContent = async (client: ScClient, addr: ScAddr): Promise<string> => {
    try {
        const result = await client.getLinkContents([addr]); // Добавлено ключевое слово await
        if (result.length > 0 && typeof result[0].data === 'string') {
            return result[0].data;
        } else {
            return '';
        }
    } catch (error) {
        console.error('An error occurred while fetching link content:', error);
        return '';
    }
};

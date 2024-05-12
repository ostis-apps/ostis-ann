import React from 'react';
import {Avatar, Flex, Link, Text} from '@gravity-ui/uikit';
import {block} from '../../utils';
import './Header.scss';

const b = block('header');
const Header = () => {
    return (
        <Flex className={b()} justifyContent={'space-between'}>
            <Flex gap={2} alignItems={'center'}>
                <Avatar text="Ann" theme={'brand'} size="xl" />
                <Flex direction={'column'}>
                    <Text variant={'header-2'}>OSTIS ANN</Text>
                    <Text variant={'body-1'} color={'secondary'}>
                        AI чат бот на основе OSTIS
                    </Text>
                </Flex>
            </Flex>
            <Link href={'https://github.com/ostis-apps/ostis-ann'}>
                <img
                    width="48"
                    height="48"
                    src="https://img.icons8.com/glyph-neue/64/github.png"
                    alt="github"
                />
            </Link>
        </Flex>
    );
};

export default Header;

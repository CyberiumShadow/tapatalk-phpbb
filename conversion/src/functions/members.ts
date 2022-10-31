import { ttClient, phpbbClient } from '../lib/db'

import type { Member } from '../../prisma/generated/tt';

export default async function mapMembers() {
    const TTMembers: Member[] = await ttClient.member.findMany();

    for (const memberidx in TTMembers) {
        const member = TTMembers[memberidx]
        console.log(`ID: ${member.id} | Name: ${member.name}`)
        await phpbbClient.user.create({
            data: {
                user_id: member.id,
                username: member.name || undefined,
                username_clean: member.name || '',
                user_posts: member.numposts || 0,
                user_permissions: '',
                user_sig: '',
                user_regdate: member.joined || undefined,
                user_avatar: member.avatarremote || ''
            }
        })
    }
}
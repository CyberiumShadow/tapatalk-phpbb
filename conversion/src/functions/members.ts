import { ttClient, phpbbClient } from '../lib/db'

import type { Member } from '../../prisma/generated/tt';

export default async function mapMembers() {
    const TTMembers: Member[] = await ttClient.forum.findMany();

    for (const memberidx in TTMembers) {
        const member = TTMembers[memberidx]
        console.log(`ID: ${member.id} | Name: ${member.name}`)
        await phpbbClient.member.create({
            data: {
                forum_id: member.id,
                forum_name: member.name || undefined
            }
        })
    }
}
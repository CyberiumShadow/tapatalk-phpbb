import { ttClient, phpbbClient } from '../lib/db'

import type { Member } from '../../prisma/generated/tt';

export default async function mapMembers() {
    const TTMembers: Member[] = await ttClient.member.findMany();

    for (const memberidx in TTMembers) {
        const member = TTMembers[memberidx]
        const member_group: String[] = JSON.parse(member.group!)
        console.log(`ID: ${member.id} | Name: ${member.name}`)
        await phpbbClient.user.create({
            data: {
                user_id: member.id,
                username: member.name,
                user_posts: member.numposts || 0,
                user_regdate: member.joined || undefined,
                user_avatar: member.avatarremote || '',
                user_avatar_type: member.avatarremote ? 1 : 0,
                user_ip: member.ip || '',
                group_id: Number(member_group[member_group.length - 1])
            }
        })
        for (const groupidx in member_group) {
            const group = Number(member_group[groupidx])
            await phpbbClient.userGroup.create({
                data: {
                    group_id: group,
                    user_id: member.id,
                }
            })
        }
    }
}
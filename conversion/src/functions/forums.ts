import { ttClient, phpbbClient } from '../lib/db'

import type { Forum } from '../../prisma/generated/tt';

export default async function mapForums() {
    const TTForums: Forum[] = await ttClient.forum.findMany();

    for (const forumidx in TTForums) {
        const forum = TTForums[forumidx]
        console.log(`ID: ${forum.id} | Name: ${forum.name}`)
        await phpbbClient.forum.create({
            data: {
                forum_id: forum.id,
                forum_name: forum.name || undefined,
                forum_desc: forum.description || "",
                parent_id: forum.parent || undefined
            }
        })
    }
}
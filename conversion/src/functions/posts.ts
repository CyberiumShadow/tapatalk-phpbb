import { ttClient, phpbbClient } from '../lib/db'

import type { Post } from '../../prisma/generated/tt';

export default async function mapTopics() {
    const TTPosts: Post[] = await ttClient.post.findMany();

    for (const postidx in TTPosts) {
        const post = TTPosts[postidx]
        console.log(`ID: ${post.id}} | Topic ID: ${post.topic}`)
        await phpbbClient.post.create({
            data: {
                post_id: post.id,
                topic_id: post.topic || undefined,
                post_time: post.date || undefined,
                post_text: post.bbcode || '',
                post_username: post.guest || '',
                poster_id: post.member || undefined
            }
        })
    }
}
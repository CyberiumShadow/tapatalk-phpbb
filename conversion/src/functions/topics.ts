import { ttClient, phpbbClient } from '../lib/db'

import type { Topic } from '../../prisma/generated/tt';

export default async function mapTopics() {
    const TTTopics: Topic[] = await ttClient.topic.findMany();

    for (const topicidx in TTTopics) {
        const topic = TTTopics[topicidx]
        console.log(`ID: ${topic.id} | Name: ${topic.name}`)
        await phpbbClient.topic.create({
            data: {
                topic_id: topic.id,
                topic_title: topic.name || undefined,
                topic_views: topic.views || 0,
                forum_id: topic.forum || undefined
            }
        })
    }
}
import { PrismaClient as TapatalkClient } from '../prisma/generated/tt'
import { PrismaClient as PhpBBClient } from '../prisma/generated/php'

import type { Forum } from '../prisma/generated/tt';

const ttClient = new TapatalkClient();
const phpbbClient = new PhpBBClient();

async function mapForums() {
    const TTForums: Forum[] = await ttClient.forum.findMany();

    for (const forumidx in TTForums) {
       const forum = TTForums[forumidx]

       await phpbbClient.forum.create({
        data: {
            forum_id: forum.id,
            forum_desc: forum.description || "",
            parent_id: forum.parent || undefined,
            forum_parents: "",
            forum_rules: ""
        }
    })
    }
}

mapForums()
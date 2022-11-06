import { ttClient, phpbbClient } from '../lib/db'

import type { UserGroup } from '../../prisma/generated/tt';

export default async function mapGroups() {
    const TTGroups: UserGroup[] = await ttClient.userGroup.findMany();

    for (const groupidx in TTGroups) {
        const group = TTGroups[groupidx]
        console.log(`ID: ${group.id} | Name: ${group.name}`)
        await phpbbClient.group.create({
            data: {
                
            }
        })
    }
}
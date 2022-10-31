import { PrismaClient as TapatalkClient } from '../../prisma/generated/tt'
import { PrismaClient as PhpBBClient } from '../../prisma/generated/php'

export const ttClient = new TapatalkClient();
export const phpbbClient = new PhpBBClient();
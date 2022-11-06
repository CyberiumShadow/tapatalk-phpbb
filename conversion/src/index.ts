import {mapForums, mapMembers, mapTopics, mapPosts} from './functions'

async function main () {
    await mapForums();
    await mapMembers();
    await mapTopics();
    await mapPosts();
}

main()
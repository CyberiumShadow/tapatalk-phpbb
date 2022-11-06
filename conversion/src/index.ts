import {mapForums, mapMembers, mapTopics, mapPosts, mapGroups} from './functions'

async function main () {
    await mapForums();
    await mapGroups();
    await mapMembers();
    await mapTopics();
    await mapPosts();
}

main()
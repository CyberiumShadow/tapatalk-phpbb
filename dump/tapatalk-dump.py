# import xmlrpclib
import xmlrpc.client
import http.client
import ssl
import datetime
import sqlite3
# import urlparse
import urllib.parse
import os
import time
import json
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

chromeOptions = Options()
chromeOptions.add_argument("headless")
# chromeOptions.add_argument("no-sandbox")

FORUM_URL = "https://www.tapatalk.com/groups/FORUM_NAME/"
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"
SID = None
DRIVER = None
tt = None

doneForums = False
currentForumForTopics = False
currentTopicForPosts = False
largestProbedTopicNum = 0
largestTotalTopicNum = False
rescrapedPost = 0
largestTotalPostNum = False
doneMembers = False

if os.path.exists('status.json'):
    with open('status.json', mode='r') as f:
        status = json.load(f)
        doneForums = status.get('doneForums', False)
        currentForumForTopics = status.get('currentForumForTopics', False)
        currentTopicForPosts = status.get('currentTopicForPosts', False)
        largestProbedTopicNum = status.get('largestProbedTopicNum', 0)
        largestTotalTopicNum = status.get('largestTotalTopicNum', False)
        rescrapedPost = status.get('rescrapedPost', 0)
        doneMembers = status.get('doneMembers', False)


def saveStatus():
    status = {
        'doneForums': doneForums,
        'currentForumForTopics': currentForumForTopics,
        'currentTopicForPosts': currentTopicForPosts,
        'largestProbedTopicNum': largestProbedTopicNum,
        'largestTotalTopicNum': largestTotalTopicNum,
        'rescrapedPost': rescrapedPost,
        'doneMembers': doneMembers,
    }
    with open('status.json', 'w') as f:
        json.dump(status, f)


class CookiesTransportHttp(xmlrpc.client.Transport):
    """A Transport subclass that retains cookies over its lifetime."""

    def __init__(self):
        super().__init__()
        self._cookies = []

    def send_headers(self, connection, headers):
        if self._cookies:
            connection.putheader("Cookie", "; ".join(self._cookies))
        super().send_headers(connection, headers)

    def parse_response(self, response):
        for header in response.msg.get_all("Set-Cookie"):
            cookie = header.split(";", 1)[0]
            self._cookies.append(cookie)
        return super().parse_response(response)


class CookiesTransportHttps(xmlrpc.client.SafeTransport):
    """A SafeTransport (HTTPS) subclass that retains cookies over its lifetime."""

    # Note context option - it's required for success
    def __init__(self, context=None):
        super().__init__(context=context)
        self._cookies = []

    def send_headers(self, connection, headers):
        if self._cookies:
            connection.putheader("Cookie", "; ".join(self._cookies))
        super().send_headers(connection, headers)

    def parse_response(self, response):
        # This check is required if in some responses we receive no cookies at all
        if response.msg.get_all("Set-Cookie"):
            for header in response.msg.get_all("Set-Cookie"):
                cookie = header.split(";", 1)[0]
                self._cookies.append(cookie)
        return super().parse_response(response)


def apiLogin():
    global tt, DRIVER
    tt = None
    transport = None
    if FORUM_URL.startswith("https"):
        transport = CookiesTransportHttps(
            context=ssl._create_unverified_context())
    else:
        transport = CookiesTransportHttp()

    try:
        tt = xmlrpc.client.ServerProxy(
            FORUM_URL + "mobiquo/mobiquo.php", transport=transport)
        tt.login(USERNAME, PASSWORD)
    except:
        if DRIVER != None:
            DRIVER.Quit()


apiLogin()


def setupDatabase():
    print("(1/6) ########## SETTING UP SQL  ##########")
    # create board, forum, topic, post, poll, option and member tables
    # cursor.execute('''CREATE TABLE board (id integer, server integer, url text, name text)''')
    cursor.execute(
        '''CREATE TABLE forum (id integer PRIMARY KEY, parent integer, name text, description text, `order` integer)''')
    cursor.execute(
        '''CREATE TABLE topic (id integer PRIMARY KEY, forum integer, poll integer, name text, description text, tags text, views integer)''')
    cursor.execute(
        '''CREATE TABLE post (id integer PRIMARY KEY, topic integer, member integer, guest text, date integer, bbcode text, html text)''')
    cursor.execute(
        '''CREATE TABLE usergroup (id integer PRIMARY KEY, usergroup integer, name text, description text, color text)''')
    cursor.execute('''CREATE INDEX post_idx ON post (id)''')
    cursor.execute('''CREATE INDEX member_idx ON post (member)''')
    cursor.execute('''CREATE INDEX topic_idx ON post (topic)''')
    cursor.execute(
        '''CREATE TABLE poll (id integer PRIMARY KEY, question text, options integer)''')
    cursor.execute(
        '''CREATE TABLE option (id integer, poll integer, option text, votes integer, PRIMARY KEY (id, poll))''')
    cursor.execute('''CREATE TABLE member
    (id integer PRIMARY KEY, name text, password text, email text, birthday integer, number integer, joined integer, ip text, `group` text, title text, warning integer, pms integer, ipbans integer, photoremote text, photolocal text, avatarremote text, avatarlocal text, interests text, signaturebb text, signaturehtml text, location text, aol text, yahoo text, msn text, homepage text, lastactive integer, hourdifference real, numposts integer)''')
    cursor.execute(
        '''CREATE TABLE emoji (id integer PRIMARY KEY, code text, remote text, local text)''')
    cursor.execute(
        '''CREATE TABLE attachment (id integer PRIMARY KEY, url text, filename text, post integer)''')
    cursor.execute(
        '''CREATE TABLE logs (id integer PRIMARY KEY, `log` text, member integer, `date` integer, ip text)''')
    cursor.execute(
        '''CREATE TABLE modlogs (id integer PRIMARY KEY, `log` text, member integer, location text, `date` integer, ip text)''')
    # save the changes to the database
    conn.commit()


forumCount = 0


def scrapeForums():
    global doneForums
    if doneForums == True:
        return

    print("(2/6) ########## SCRAPING FORUMS  ##########")
    forums = tt.get_forum()
    insertCount = 0

    for forum in forums:
        processForums(forum)

    doneForums = True
    saveStatus()


def processSingleForum(forum):
    global forumCount
    ids = frozenset([i[0] for i in cursor.execute('SELECT id FROM forum')
                     .fetchall()])
    id = int(forum['forum_id'])
    parent = int(forum['parent_id'])
    name = forum['forum_name'].data.decode('utf8')
    description = forum['description'].data.decode('utf8')

    if 'is_protected' in forum and forum['is_protected']:
        print("The forum " + str(name) +
              " is password protected, please remove the password and restart the scraper if you want it to be scraped")
        time.sleep(10)
        return

    if 'url' in forum and forum['url'].strip() != '':
        # this is a redirect forum, don't save it
        return

    # insert it into the database
    if id not in ids:
        values = (id, parent, name, description, forumCount)
        cursor.execute('INSERT INTO forum VALUES (?,?,?,?,?)', values)
        conn.commit()
        print(values)
    forumCount = forumCount + 1


def processForums(forum):
    # process this forum first
    processSingleForum(forum)

    for f in forum['child']:
        processForums(f)


def scrapeTopics():
    global currentForumForTopics, largestTotalTopicNum
    if currentForumForTopics == True:
        return

    print("(3/6) ########## SCRAPING TOPICS ##########")

    if currentForumForTopics == False:
        forums = cursor.execute("SELECT id FROM forum").fetchall()
    else:
        forums = cursor.execute("SELECT id FROM forum WHERE id >= ?", [
                                currentForumForTopics]).fetchall()

    for forum in forums:
        forumID = forum[0]
        print("Scraping topic from forum " + str(forumID))

        start = 0
        end = 25
        firstIdInChunk = -1

        # need to grab topics in 25 topic chunks
        continueGrabbingTopics = True
        while continueGrabbingTopics:

            # do this because TT is awful
            chunk = False
            while chunk == False:
                try:
                    chunk = tt.get_topic(str(forumID), start, end-1)
                except xmlrpc.client.ProtocolError:
                    print("Yay, TT is awful")
                    time.sleep(10)
                    apiLogin()
                    time.sleep(10)

            # if 'topics' in chunk:
            #    chunk = chunk['topics']
            # else:
            #    chunk = []
            print(chunk)
            if 'result' in chunk and chunk['result'] == False:
                print("OH NO, Tapatalk error")
                print(chunk['result_text'].data.decode('utf8'))
                print(chunk['error'].data.decode('utf8'))
                if str(chunk['error']) == "The forum you selected does not exist.":
                    print("Abort!")
                    break
                sys.exit(0)
            if 'total_topic_num' in chunk:
                largestTotalTopicNum = max(
                    largestTotalTopicNum, int(chunk['total_topic_num']))

            chunk = chunk['topics']

            # if len(chunk) != 25:
            if len(chunk) != 25 or firstIdInChunk == chunk[0]['topic_id']:
                # this is the last chunk
                continueGrabbingTopics = False

            if len(chunk) > 0:
                firstIdInChunk = chunk[0]['topic_id']

            for topic in chunk:
                id = int(topic['topic_id'])
                forum = forumID
                poll = None
                name = topic['topic_title'].data.decode('utf8')
                description = ''
                tags = ''
                views = topic['view_number']

                if topic['has_poll']:
                    # TODO - do poll stuff here, might not be possible with TT api?
                    pass

                # insert to database
                values = (id, forum, poll, name, description, tags, views)
                print(values)
                try:
                    cursor.execute(
                        'INSERT INTO topic VALUES (?,?,?,?,?,?,?)', values)
                except sqlite3.IntegrityError:
                    print("SQLITE3 INTEGRITY ERROR - inserting topic into database\n")
                conn.commit()

            start = start + 25
            end = end + 25

        currentForumForTopics = forumID
        saveStatus()

    currentForumForTopics = True
    saveStatus()


def scrapeMissingTopics():
    global largestProbedTopicNum
    if largestProbedTopicNum == True:
        return
    topics = cursor.execute("SELECT id FROM topic").fetchall()

    ids = frozenset(t[0] for t in topics)

    starting = largestProbedTopicNum
    ending = largestTotalTopicNum + 10

    for i in range(starting, ending):
        if i in ids:
            continue

        print("probing topic id " + str(i))

        topic = False
        while topic == False:
            try:
                topic = tt.get_thread(str(i), 0, 0)
            except (xmlrpc.client.ProtocolError, http.client.ResponseNotReady) as err:
                print('tt.get_thread(' + str(i) + ',0 ,0 )')
                print("Yay, TT is awful")
                time.sleep(10)
                apiLogin()
                time.sleep(10)

        if 'result' in topic and topic['result'] == False:
            print("no topic found, continuing")
            largestProbedTopicNum = i
            saveStatus()
            continue

        print("we got a topic! yay!")

        id = i
        forum = topic['forum_id']
        poll = None
        name = topic['topic_title'].data.decode('utf8')
        description = ''
        tags = ''
        views = topic['view_number']

        # insert to database
        values = (id, forum, poll, name, description, tags, views)
        print(values)
        try:
            cursor.execute('INSERT INTO topic VALUES (?,?,?,?,?,?,?)', values)
        except sqlite3.IntegrityError:
            print("SQLITE3 INTEGRITY ERROR - inserting topic into database\n")
        conn.commit()
        largestProbedTopicNum = i
        saveStatus()
    largestProbedTopicNum = True
    saveStatus()


POST_PAGESIZE = 50


def scrapePosts():
    global currentTopicForPosts, POST_PAGESIZE
    if currentTopicForPosts == True:
        return

    print("(4/6) ########## SCRAPING POSTS  ##########")

    if currentTopicForPosts == False:
        topics = cursor.execute("SELECT id FROM topic").fetchall()
    else:
        topics = cursor.execute("SELECT id FROM topic WHERE id >= ?", [
                                currentTopicForPosts]).fetchall()

    for topic in topics:
        topicID = topic[0]
        print("Scraping topic " + str(topicID))
        if (int(topicID) == 1283):
            global _pagesize
            _pagesize = POST_PAGESIZE
            POST_PAGESIZE = 10
        elif '_pagesize' in globals():
            POST_PAGESIZE = _pagesize
            del _pagesize

        start = 0
        end = POST_PAGESIZE
        firstIdInChunk = -1

        # need to grab posts in POST_PAGESIZE post chunks
        continueGrabbingPosts = True
        while continueGrabbingPosts:

            # do this because TT is awful
            chunk = False
            while chunk == False:
                try:
                    chunk = tt.get_thread(str(topicID), start, end-1)
                    chunk = chunk['posts']
                except (xmlrpc.client.ProtocolError, http.client.ResponseNotReady) as e:
                    print('tt.get_thread(' + str(topicID) + ',' +
                          str(start) + ' ,' + str(end-1) + ' )[\'posts\']')
                    print("Yay, TT is awful")
                    time.sleep(10)
                    apiLogin()
                    time.sleep(10)
                except KeyError:
                    print('tt.get_thread(' + str(topicID) + ',' +
                          str(start) + ' ,' + str(end-1) + ' )[\'posts\']')
                    print("Yay, TT is terrible")
                    print(chunk)

            if len(chunk) != POST_PAGESIZE or firstIdInChunk == chunk[0]['post_id']:
                # this is the last chunk
                continueGrabbingPosts = False

            if len(chunk) > 0:
                firstIdInChunk = chunk[0]['post_id']

            for post in chunk:
                id = int(post['post_id'])
                topic = topicID
                member = post['post_author_id']
                guest = post['post_author_name'].data.decode('utf8')
                date = int((datetime.datetime.strptime(str(
                    post['post_time']), '%Y%m%dT%H:%M:%S+00:00') - datetime.datetime(1970, 1, 1)).total_seconds())
                bbcode = post['post_content'].data.decode('utf8')
                html = ''

                values = (id, topic, member, guest, date, bbcode, html)
                print(values)
                try:
                    cursor.execute(
                        'INSERT INTO post VALUES (?,?,?,?,?,?,?)', values)
                except sqlite3.IntegrityError:
                    print("SQLITE3 INTEGRITY ERROR - inserting post into database\n")
                    print("start: " + str(start))
                    print("end:   " + str(end))
                    print("chunk: " + str(len(chunk)))
                conn.commit()

            start = start + POST_PAGESIZE
            end = end + POST_PAGESIZE

        currentTopicForPosts = topicID
        saveStatus()

    currentTopicForPosts = True
    saveStatus()


def rescrapePosts():
    global rescrapedPost, POST_PAGESIZE
    if rescrapedPost == True:
        return

    print("(5/6) ########## RESCRAPING POSTS  ##########")

    ids_to_scrape = json.load(open("rescrape_us.json", "r"))
    for id in filter(ids_to_scrape, lambda i: i > rescrapedPost):
        post = False
        while post == False:
            try:
                post = tt.get_raw_post(id)
            except (xmlrpc.client.ProtocolError, http.client.ResponseNotReady) as e:
                print('tt.get_raw_post('+str(id)+')')
                print("Yah, TT is awful")
                time.sleep(10)
                apiLogin()
                time.sleep(10)
        assert (id == int(post['post_id']))
        topic = int(post['topic_id'])
        member = post['post_author_id']
        guest = post['post_author_name'].data.decode('utf8')
        date = int((datetime.datetime.strptime(str(
            post['post_time']), '%Y%m%dT%H:%M:%S+00:00') - datetime.datetime(1970, 1, 1)).total_seconds())
        bbcode = post['post_content'].data.decode('utf8')
        html = ''

        values = (id, topic, member, guest, date, bbcode, html)
        print(values)
        cursor.execute(
            'INSERT OR REPLACE INTO post VALUES (?,?,?,?,?,?,?)', values)
        rescrapedPost = id


def checkForMissing(table):
    ids = frozenset(row[0] for row in cursor.execute("SELECT id FROM %s" % table)
                    .fetchall())
    max_ids = max(ids)

    missing = max_ids - len(ids)

    if missing > 0:
        print("WARNING: missing {} of {} {} ids ({:.2f}%)".format(missing,
                                                                  max_ids, table, 100*missing/float(max_ids)))


def get_first_key(dictionary):
    for key in dictionary:
        return key
    raise IndexError


def scrapeMembers():
    global doneMembers
    if doneMembers == True:
        return

    print("(6/6) ########## SCRAPING MEMBERS  ##########")

    continueGrabbingMembers = True

    members = cursor.execute("SELECT id FROM member").fetchall()

    scraped = frozenset(int(m[0]) for m in members)

    if doneMembers == False:
        chunkCount = 1
    else:
        chunkCount = doneMembers

    firstIdInChunk = -1

    while continueGrabbingMembers:

        # do this because TT is awful
        chunk = False
        while chunk == False:
            try:
                chunk = tt.get_member_list(chunkCount)['list']
            except xmlrpc.client.ProtocolError:
                print("Yay, TT is awful")
                time.sleep(10)
                apiLogin()
                time.sleep(10)

        # if len(chunk) != 20:
        if len(chunk) != 20 or firstIdInChunk == chunk[get_first_key(chunk)]['user_id']:
            continueGrabbingMembers = False

        if len(chunk) > 0:
            firstIdInChunk = chunk[get_first_key(chunk)]['user_id']

        for member in chunk.values():
            id = member['user_id']

            if int(id) in scraped:
                continue

            name = member['user_name'].data.decode('utf8')
            password = ''
            email = None  # getEmail(id)
            birthday = 0
            number = 0
            joined = int(member['timestamp_reg'])
            ip = None
            group = json.dumps(member['usergroup_id'])
            title = ''
            warning = 0
            pms = 0
            ipbans = 0
            photoremote = None
            photolocal = None
            avatarremote = member['icon_url']
            avatarlocal = None
            interests = None
            signaturebb = ''
            signaturehtml = ''
            location = ''
            aol = ''
            yahoo = ''
            msn = ''
            homepage = ''
            if type(member['timestamp']) == int:
                lastactive = int(member['timestamp'])
            else:
                lastactive = 0
            hourdifference = 0
            numposts = member['post_count']

            values = (id, name, password, email, birthday, number, joined, ip, group, title, warning, pms, ipbans, photoremote, photolocal, avatarremote,
                      avatarlocal, interests, signaturebb, signaturehtml, location, aol, yahoo, msn, homepage, lastactive, hourdifference, numposts)
            print(values)
            try:
                cursor.execute(
                    'INSERT INTO member VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', values)
            except sqlite3.IntegrityError:
                print(
                    "SQLITE3 INTEGRITY ERROR - inserting member #{} into database\n".format(chunkCount))
                print("chunkCount: " + str(len(chunkCount)))
            conn.commit()

        chunkCount = chunkCount + 1

        doneMembers = chunkCount
        saveStatus()

    doneMembers = True
    saveStatus()


def scrapeMissingMembers():
    members = cursor.execute("SELECT id FROM member").fetchall()

    ids = [m[0] for m in members]

    starting = 1
    ending = ids[len(ids)-1] + 10

    for i in range(starting, ending):
        if i in ids:
            continue

        print("probing member id " + str(i))

        member = False
        while member == False:
            try:
                member = tt.get_user_info("", str(i))
            except (xmlrpc.client.ProtocolError, http.client.ResponseNotReady) as err:
                print('tt.get_user_info("",' + str(i) + ')')
                print("Yay, TT is awful")
                time.sleep(10)
                apiLogin()
                time.sleep(10)

        if 'result' in member and member['result'] == False:
            print("no member found, continuing")
            continue

        print("we got a member! yay!")

        if (str(member['user_name']).endswith(' [Bot]') or str(member['user_name']).endswith(' [Spider]') or str(member['user_name']).endswith(' [Google]')):
            cf = dict((str(x['name']), str(x['value']))
                      for x in member['custom_fields_list'])
            if 'Groups' in cf and cf['Groups'] == 'Bots':
                print(('bot member', member['user_name'].data.decode('utf8')))
                continue

        if (int(member['user_id']) != i):
            print("i", i, "member", member)
            assert (member['user_id'] == i)
        id = member['user_id']
        name = member['user_name'].data.decode('utf8')
        password = ''
        email = None  # getEmail(id)
        birthday = 0
        number = 0
        joined = int(member['timestamp_reg'])
        ip = None
        group = json.dumps(member['usergroup_id'])
        title = ''
        warning = 0
        pms = 0
        ipbans = 0
        photoremote = None
        photolocal = None
        avatarremote = member['icon_url']
        avatarlocal = None
        interests = None
        signaturebb = ''
        signaturehtml = ''
        location = ''
        aol = ''
        yahoo = ''
        msn = ''
        homepage = ''
        if type(member['timestamp']) == int:
            lastactive = int(member['timestamp'])
        else:
            lastactive = 0
        hourdifference = 0
        numposts = member['post_count']

        # try and get email

        values = (id, name, password, email, birthday, number, joined, ip, group, title, warning, pms, ipbans, photoremote, photolocal, avatarremote,
                  avatarlocal, interests, signaturebb, signaturehtml, location, aol, yahoo, msn, homepage, lastactive, hourdifference, numposts)
        print(values)
        cursor.execute(
            'INSERT INTO member VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', values)
        conn.commit()


def scrapeMemberEmails():
    try:
        ttlogin()
        # and *now* do the emails
        members = cursor.execute(
            "SELECT id FROM member where email is null").fetchall()
        for member in members:
            memberID = member[0]
            email = getEmail(memberID)
            cursor.execute(
                'UPDATE member SET email = ? WHERE id = ?', (email, memberID))
            conn.commit()
    finally:
        DRIVER.quit()
        print("Shutting down chromedriver...")


def ttlogin():
    global SID, DRIVER
    if DRIVER != None:
        return

    DRIVER = webdriver.Chrome(service=ChromiumService(
        ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()), options=chromeOptions)

    # do login
    DRIVER.maximize_window()
    DRIVER.get(FORUM_URL + "ucp.php?mode=login")
    DRIVER.find_element(By.NAME, "username").send_keys(USERNAME)
    DRIVER.find_element(By.NAME, "password").send_keys(PASSWORD)
    DRIVER.find_element(By.NAME, "submit").click()

    # get rid of the new tapatalk iframe
    DRIVER.implicitly_wait(15)
    DRIVER.switch_to.frame("dot-com-frame")
    DRIVER.find_element(By.CLASS_NAME, "close").click()
    DRIVER.switch_to.default_content()
    DRIVER.refresh()

    # oops GDPR because european server...
    DRIVER.switch_to.frame("gdpr-consent-notice")
    DRIVER.find_element(By.ID, "save").click()
    DRIVER.switch_to.default_content()

    # click the acp button
    settings = DRIVER.find_element(
        By.CSS_SELECTOR, "#navbar_home > div.cl-af.inner > div > div.nv-l-b.manage-settings > div > a")
    settings.click()
    link = DRIVER.find_element(
        By.CSS_SELECTOR, "#navbar_home > div.cl-af.inner > div > div.nv-l-b.manage-settings > div > div > ul > li:nth-child(1) > a").click()
    DRIVER.find_element(
        By.CSS_SELECTOR, "#page-body > div > div > div > div > div").click()

    # login to the acp
    DRIVER.find_element(By.NAME, "username").send_keys(USERNAME)
    DRIVER.find_element(By.NAME, "password").send_keys(PASSWORD)
    DRIVER.find_element(By.NAME, "submit").click()
    DRIVER.implicitly_wait(15)

    # go to the user details page
    SID = urllib.parse.parse_qs(urllib.parse.urlparse(
        DRIVER.current_url).query)['sid'][0]


def getEmail(userId):
    print(userId)
    url = FORUM_URL + "adm/index.php?i=users&mode=overview&sid=" + \
        SID + "&u=" + str(userId)
    DRIVER.get(url)

    try:
        warning = DRIVER.find_element(
            By.CLASS_NAME, "warningbox").find_element(By.CSS_SELECTOR, "p")
        print("Uh oh, this is a founder email, we can't get them.")
        return None
    except:
        pass

    email = DRIVER.find_element(
        By.ID, "user_email_search").get_attribute("value")
    print(email)
    return email


def getGroup(groupId):
    return


def scrapeGroups():
    return


if __name__ == '__main__':
    createDatabase = (not os.path.exists('database.db'))

    # create sqlite database connection
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if createDatabase:
        setupDatabase()

    scrapeForums()
    scrapeTopics()
    scrapeMissingTopics()
    scrapePosts()
    scrapeMembers()
    scrapeMissingMembers()
    scrapeMemberEmails()
    checkForMissing("forum")
    checkForMissing("topic")
    checkForMissing("post")
    checkForMissing("member")

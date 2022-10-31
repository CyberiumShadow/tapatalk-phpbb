-- CreateTable
CREATE TABLE "attachment" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "url" TEXT,
    "filename" TEXT,
    "post" INTEGER
);

-- CreateTable
CREATE TABLE "emoji" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "code" TEXT,
    "remote" TEXT,
    "local" TEXT
);

-- CreateTable
CREATE TABLE "forum" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "parent" INTEGER,
    "name" TEXT,
    "description" TEXT,
    "order" INTEGER
);

-- CreateTable
CREATE TABLE "logs" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "log" TEXT,
    "member" INTEGER,
    "date" INTEGER,
    "ip" TEXT
);

-- CreateTable
CREATE TABLE "member" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT,
    "password" TEXT,
    "email" TEXT,
    "birthday" INTEGER,
    "number" INTEGER,
    "joined" INTEGER,
    "ip" TEXT,
    "group" TEXT,
    "title" TEXT,
    "warning" INTEGER,
    "pms" INTEGER,
    "ipbans" INTEGER,
    "photoremote" TEXT,
    "photolocal" TEXT,
    "avatarremote" TEXT,
    "avatarlocal" TEXT,
    "interests" TEXT,
    "signaturebb" TEXT,
    "signaturehtml" TEXT,
    "location" TEXT,
    "aol" TEXT,
    "yahoo" TEXT,
    "msn" TEXT,
    "homepage" TEXT,
    "lastactive" INTEGER,
    "hourdifference" REAL,
    "numposts" INTEGER
);

-- CreateTable
CREATE TABLE "modlogs" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "log" TEXT,
    "member" INTEGER,
    "location" TEXT,
    "date" INTEGER,
    "ip" TEXT
);

-- CreateTable
CREATE TABLE "option" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "poll" INTEGER,
    "option" TEXT,
    "votes" INTEGER
);

-- CreateTable
CREATE TABLE "poll" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "question" TEXT,
    "options" INTEGER
);

-- CreateTable
CREATE TABLE "post" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "topic" INTEGER,
    "member" INTEGER,
    "guest" TEXT,
    "date" INTEGER,
    "bbcode" TEXT,
    "html" TEXT
);

-- CreateTable
CREATE TABLE "topic" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "forum" INTEGER,
    "poll" INTEGER,
    "name" TEXT,
    "description" TEXT,
    "tags" TEXT,
    "views" INTEGER
);

-- CreateTable
CREATE TABLE "usergroup" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "usergroup" INTEGER,
    "name" TEXT,
    "description" TEXT,
    "color" TEXT
);

-- CreateIndex
CREATE INDEX "topic_idx" ON "post"("topic");

-- CreateIndex
CREATE INDEX "member_idx" ON "post"("member");

-- CreateIndex
CREATE INDEX "post_idx" ON "post"("id");

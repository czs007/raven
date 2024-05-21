# raven
Raven is a tool designed to assist in generating Milvus Release Notes.

## Usage

The contents of the .git/config file in my milvus working directory are as follows:


[remote "origin"]
        url = git@github.com:czs007/milvus.git
        fetch = +refs/heads/:refs/remotes/origin/

[branch "master"]
        remote = origin
        merge = refs/heads/master

[remote "milvus"]
        url = git@github.com:milvus-io/milvus.git
        fetch = +refs/heads/*:refs/remotes/milvus/



The initial and final commit messages are as follows:

Initial commit: commit 39b07adff1eec54de3f9f6690ed1a31e42d3cfd0 (tag: v2.3.15)
Final commit for upcoming version 2.3.16: commit 23e7155a48bcd0e73c520280f17837ad5d75af62 (milvus/2.3)

To generate the ReleaseNote for milvus verion 2.3.16, execute the following command:

git log --oneline v2.3.15..milvus/2.3 | python raven.py > rn.md
THE JAVA TORCTL PROJECT HAS MOVED TO GIT
========================================

The rest of this file explains where to find the Git repository for
the Java Tor controller, and what to do with it when you find it.


How to use Git to work on Jtorctl
================================

Before you start
----------------

First, read and understand the Git Tutorial (man gittutorial) and maybe
gittutorial-2.  It is very short and helpful.

If you have more time, read the Git user manual.



If you know how to use Git
--------------------------

If you know how to use Git, all you need to know is that the official
jtorctl repository is at
        git://git.torproject.org/git/jtorctl
and that if you're updating the official repository (we will tell you
if you're such a person), ssh access is at:
        ssh://git.torproject.org/git/jtorctl

There.  Done.  Go use git; you know how.

If you don't know how to use Git: Setting up your git
-----------------------------------------------------

First, make sure you have Git 1.5.x or later installed.  Using earlier
versions should probably still work, but I don't have experience with them,
so I can't help you.

Second, edit your ~/.gitconfig file so that Git commits from you have a
useful name attached.  It should look something like

------------------------------
[user]
        name = Nick Mathewson
        email = nickm@torproject.org
------------------------------

except that you shouldn't claim to be me. Make sure to tell us what you
set there if you have ever committed to svn, so we can attribute those svn
commits to you.


If you don't know how to use Git: Getting started
-------------------------------------------------

Now we can fetch the repository!  I like to do all my development under
~/src/projectname, so I'll start with:

-----
% cd src
% git clone git://git.torproject.org/git/jtorctl
-----

There's now a '~/src/jtorctl' directory with the latest jtorctl in it.  I
can build and edit and mess with this source to my heart's content.

All the Git metadata for my project lives in ~/src/jtorctl/.git , so it's
safe to move your checkout around wherever or rename it if you don't
like it.

Let's mess around with the repository a bit.

-----
% git status
# On branch master
nothing to commit (working directory clean)
-----

This means we're on the 'master' branch, with no local changes.  The
master branch of a repository is like the 'trunk' branch in Subversion.

In Git, branches are cheap and local.  It's good practice to start a new
cheap local branch whenever you start working on a new feature or set of
features.  This makes our commits neater, and makes it easier to hold
off on pushing work into the mainline.

Let's pretend we're adding FTP support to jtorctl.  We'll want to make a
new branch to work on it, like this:

-----
% git checkout -b ftp
-----

The checkout command switches branches.  Using the '-b' switch makes it
create a new branch.  By default, it starts the branch based on the
current branch.  We could also have said 'git checkout -b ftp master' to
make it start at the master branch explicitly.

Anyway, let's see if it worked!

-----
% git branch
* ftp
  master
-----

Yup.  There are two branches, and we're on a branch called 'ftp'.

You can do a lot of other things with the 'git branch' command.  For
more information on git branch, just type 'git help branch'.  For that
matter, you can get help on any git command with 'git help commandname'.

Now let's say we have work to commit on our branch.  The easiest way to
commit all of our changes is to say:

-----
% git commit -a
-----

This asks us for a commit message, and commits every changed file.

If we only want to commit some files, or if we want to add new files
that were not previously in the repository, we use the 'git add' command
to tell Git what to commit, and then we use 'git commit' without the
'-a' flag to commit them.

-----
% git add changedFile1
% git add changedFile2
% git add newfile
% git commit
-----

The files that have been added but not yet committed are in a structure
called the "index".  You can change your mind about a file you have
added to the index with 'git reset'.  You can throw away all local
non-added changes to a file with 'git checkout'.


----
% git add file1
% git add file2

  (Oh wait, I don't want to commit file2!)
% git reset file2
file2: needs update
% git commit
% git status
# On branch ftp
# Changed but not updated:
#   (use "git add <file>..." to update what will be committed)
#
#       modified:   file2
#
no changes added to commit (use "git add" and/or "git commit -a")


  (On second thought, I don't want my changes to file2 at all.)
% git checkout file2
----

There are more options to reset, add, and checkout that you will
eventually want to know about, but that should be enough for now.

To see what changes you've made on the ftp branch, you can do

----
% git log master..ftp
----

You can just say "git log master.." if you're on the ftp branch.  If you
want to see the associated patches one by one, along with the log, say
'git log -p master..".  (The 'master..ftp' notation means, "Show me
every commit that's in ftp but not in master.")

If you say 'git diff master' instead of 'git log master..', you can
see the changes you've made in unified diff format.  You can also say
'git diff' to see the changes that are in your working directory but not
in your index,
'git diff --cached' to see the changes in your index, and
'git diff HEAD' to see all the changes since your last commit.

If you want to generate a set of patches to mail to the maintainer,
use 'git format-patch' instead of diff or log.

A NOTE ON COMMIT MESSAGES: Many Git tools (like the commit emails, and
the shortlogs) will give better output if commit messages come in a
special format.  The first line of the commit message should be a short
"Subject", summarizing the contents of the commit.  There should then be
a blank line, and the rest of your commit message, in as many paragraphs
as you want.


Staying up to date.
-------------------


While you work, there's an upstream repository that's changing too.
You can update your copy of it with

-----
% git fetch git://git.torproject.org/git/jtorctl
-----

That's pretty verbose.  Fortunately, since you started by cloning from
that URL, it has the alias "origin":

-----
% git fetch origin
-----

You can use the 'git remote' command to create aliases for other remote
repositories.  Run 'git help remote' to learn more.

You might have noticed that after you fetched the origin, you didn't
see any changes in your branches.  That's because "fetch" by default
only downloads things; it doesn't merge them.  To fetch and merge at the
same time, use "git pull" in the master branch:

----
% git checkout master
% git pull
----

Assuming there are no changes in your master branch, this will cause a
'fast-forward' merge: all the changes from upstream get appended to your
history, and the head of the 'master' branch now just points at them.

If there are changes, git will try to merge for you.

Now, what should we do about our local ftp branch?  It's still based on
the pre-pull  version.  We have a few choices.

1. We could let it stay based on the old version until we're ready to
   merge it into our master branch, or send it in as a patch, or
   whatever.

2. We could merge in changes from the master branch:

-----
% git checkout ftp
% git merge master
-----

   This might create a new merge commit, as appropriate.

3. We could "rebase" the ftp branch to the head of the master.  This, in
   effect, makes a new ftp branch against the head of master, and copies
   over all the commits from the old ftp branch into new commits onto
   the new ftp branch.

-----
% git checkout ftp
% git rebase master
-----

   This is a fine thing to do on a _local_ branch, but you should never
   do it (or any other kind of "history rewriting") on a branch you have
   published to others.



Sharing with others.
--------------------

It's nice to have a public repository that other people can pull from.
You can set one up pretty easily if you have a Unix machine, or an
account on Moria.

The writeup in the Git manual at:

http://www.kernel.org/pub/software/scm/git/docs/user-manual.html#public-repositories

is really all you need to read here.  If you have an account on Moria,
just do:

-----
% mkdir ~/git
% cd ~/git
% git clone --bare /git/jtorctl.git jtorctl.git
% touch jtorctl.git/git-daemon-export-ok
-----

And now you have a new Git repository that other people can fetch from
git://git.torproject.org/~USERNAME/git/jtorctl

For you, that's ssh://git.torproject.org/~USERNAME/git/jtorctl : you can
follow the instructions at

http://www.kernel.org/pub/software/scm/git/docs/user-manual.html#pushing-changes-to-a-public-repository

to push branches to your public repository.


If you don't have an account on Moria, see the rest of the documentation
in that part of the Git manual.  Or go use github: it's pretty neat.


Merging from others
-------------------

As mentioned above, you can specify additional remotes for your git
repository. Let's say Nick has published his ftp branch, and you want to
give it a shot. It is not yet ready to be merged to the master branch, so
you cannot just pull from the master branch. Nick tells you his branch is
called master, and his repository lives at
git://git.torproject.org/~nickm/git/jtorctl.

Now it's time for you to add a remote for nicks repository, get his
published branches, and make a local branch that tracks his ftp branch:

-----
%git remote add nick git://git.torproject.org/~nickm/git/jtorctl
%git fetch nickm
%git checkout -b nick_ftp nick/ftp
-----

This will have switched you to your new local branch nick_ftp, and you can
build and test the ftp stuff that nick made. If you're done with testing,
just type

-----
%git checkout master
-----

to go back to your master branch. Maybe, a few days later, Nick has made
some changes that you would like to look at. First, you fetch his stuff
again and switch to your local branch that tracks his ftp branch:

-----
%git fetch nick
%git checkout nick_ftp
-----

git will tell you that there has been an update to the branch that you
checked out. To get the new stuff in, and rebase any changes that you may
have made in the meantime, type:

-----
%git rebase
-----

This fast-forwards the branch if you haven't made changes, or first
applies the changes from nick's repository and the replays your changes on
top of the result. If you then want to make a patch based on your changes
to send to nick, it's easy. Use git format-patch (see above).

If you want to actually merge his ftp branch into one of your other local
branches, do this:

-----
%git checkout branch
%git merge nick_ftp
-----

Git will automatically merge into nick_ftp.

Further reading
---------------

To see how the git folks do it:

http://www.kernel.org/pub/software/scm/git/docs/howto/maintain-git.txt


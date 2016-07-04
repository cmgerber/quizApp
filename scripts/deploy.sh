#!/bin/bash

set -x

if [ $TRAVIS_BRANCH == 'develop' ] ; then
    chmod 600 deploy_key

    mv deploy_key ~/.ssh/id_rsa

    git remote add deploy "deploy@104.236.112.22:/home/www/quizApp"
    git config user.name "Travis CI"
    git config user.email "alexeibendebury+travis@gmail.com"

    # This may seem bad, but since this is a public repo I am not concerned
    # about MITM attacks.
    yes | git push --force deploy develop 
else
    echo "Not deploying"
fi

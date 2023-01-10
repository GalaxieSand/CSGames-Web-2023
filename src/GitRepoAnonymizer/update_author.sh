#!/bin/sh


ENV_FILTER='
if [ "$GIT_COMMITTER_EMAIL" = "'"$OLD_EMAIL"'" || "$GIT_AUTHOR_EMAIL" = "'"$OLD_EMAIL"'" ];
then
    export GIT_COMMITTER_NAME="'"$CORRECT_NAME"'" && export GIT_COMMITTER_EMAIL="'"$CORRECT_EMAIL"'"
    export GIT_AUTHOR_NAME="'"$CORRECT_NAME"'" && export GIT_AUTHOR_EMAIL="'"$CORRECT_EMAIL"'"
fi


git filter-branch -f --env-filter "$ENV_FILTER" --tag-name-filter cat -- --branches --tags

#!/usr/bin/env bash
set -e

GIT_MESSAGE=$(git log --format=%B -n 1 $CIRCLE_SHA1)

echo "git message is:"
echo "$GIT_MESSAGE"

if [[ $GIT_MESSAGE == "Merge pull request #"* ]]
then
  MERGED_BRANCH=$(echo $GIT_MESSAGE | sed -n "s/^.*from ministryofjustice\/\s*\(\S*\).*$/\1/p")
  RELEASE_NAME=$(echo $MERGED_BRANCH | sed 's/^feature[-/]//' | sed 's:^\w*\/::' | tr -s ' _/[]().' '-' | tr '[:upper:]' '[:lower:]' | cut -c1-28 | sed 's/-$//')

  echo "Attempting to delete release $RELEASE_NAME"

  RELEASES=$(helm list --all)

  echo "Current releases:"
  echo "$RELEASES"

  if [[ $RELEASES == *"$RELEASE_NAME"* ]]
  then
    echo "Deleting release $RELEASE_NAME"
    helm delete $RELEASE_NAME
  else
    echo "Release $RELEASE_NAME was not found"
  fi

else
  echo "This commit is not a merged pull request"
fi
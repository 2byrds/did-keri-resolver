#!/bin/bash

echo "Fetching latest changes from origin..."
git fetch origin

echo "Unique emails of contributors with commits missing DCO signatures on origin/main:"
# List authors' emails with missing DCO signatures
MISSING_DCO_EMAILS=$(git log origin/main --no-merges --grep="^Signed-off-by: " --invert-grep --pretty="%ae" | sort -u)
echo "$MISSING_DCO_EMAILS"

read -p "Which contributor's email commits would you like to sign? " AUTHOR_EMAIL

# Create or switch to the temporary branch
git branch -D temp_dco_check &> /dev/null
git checkout -b temp_dco_check origin/main

# Find and amend commits by the author missing the DCO signature
COMMITS_TO_AMEND=$(git log --no-merges --author="$AUTHOR_EMAIL" --pretty="%H %s" | grep -v "^Signed-off-by: " | awk '{print $1}')

for COMMIT in $COMMITS_TO_AMEND; do
    git checkout $COMMIT
    echo "Original Commit:"
    git show --pretty=medium --no-patch
    git commit --amend --no-edit --signoff
    echo "Amended Commit:"
    git show --pretty=medium --no-patch
done

git rebase origin/main

echo "Review the changes between origin/main and the temporary branch:"
git log origin/main..temp_dco_check --oneline
read -p "Press enter to continue..."

read -p "Do you want to update the main branch with these changes? (y/n) " UPDATE_MAIN

if [[ "$UPDATE_MAIN" == "y" ]]; then
    git checkout main
    git rebase temp_dco_check

    echo "Review the changes on the main branch before pushing:"
    git log origin/main..main --oneline
    read -p "Press enter to continue..."

    read -p "Do you want to push the changes to origin/main? (y/n) " PUSH_CHANGES
    if [[ "$PUSH_CHANGES" == "y" ]]; then
        git push origin main
    else
        echo "Changes are not pushed. You can push later if you wish."
    fi
else
    git checkout main
    git branch -D temp_dco_check
    echo "Reverted to state of origin/main."
fi

echo "Process completed."

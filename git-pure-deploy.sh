#!/bin/sh

#### Deploy dashboard ####
# check if data folder in gitignore
if grep -R "data/" .gitignore
then # if so, remove from file
    sed -i "" "s%\ndata/%%" .gitignore && printf 'DATA REMOVED FROM .gitignore\n'
else # else print confirm message
    printf "DATA LOADED"
fi
# check if secrets file in .gitignore
if grep -R "juicy_secrets.py" .gitignore
then # if so, print confirm message
    printf "SECRETS PROTECTED"
else # else add file to .gitignore
    printf "\njuicy_secrets.py" >> .gitignore && printf 'SECRETS ADDED TO .gitignore\n'
fi
git add .
git commit -m "deploy"
git push origin main
git push -f heroku main

#### Re-push repo w/ data folder in .gitignore ####
printf "\ndata/" >> .gitignore # add ./data to .gitignore
git rm -r --cached . # remove files in index
git add . # add all files
git commit -m "remove data from index" # commit changes
git push origin main # push to origin

# Reset commit history and delete orphaned files
git checkout --orphan newBranch # new branch
git add -A # add all to new branch
git commit -m "reset commit history" # commit changes
git branch -D main  # Delete main branch
git branch -m main  # Rename current branch to main
git push -f -u origin main  # Force push main branch to github
git gc --auto --prune=all # remove orphaned files
cat ./images/update_done.txt 
printf '\n'
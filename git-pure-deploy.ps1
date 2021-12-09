#### Deploy dashboard ####
# check if data folder in gitignore

"C:\Users\spenc\Desktop\PureSolutionsDash\juicy_secrets.py" | Out-File -FilePath "C:\Users\spenc\Desktop\PureSolutionsDash\.gitignore"

git add .
git commit -m "deploy"
git push origin main
git push -f heroku main

#### Re-push repo w/ data folder in .gitignore ####
"C:\Users\spenc\Desktop\PureSolutionsDash\juicy_secrets.py`nC:\Users\spenc\Desktop\PureSolutionsDash\data" | Out-File -FilePath "C:\Users\spenc\Desktop\PureSolutionsDash\.gitignore"
git rm -r --cached C:\Users\spenc\Desktop\PureSolutionsDash\juicy_secrets.py # remove files in index
git rm -r --cached C:\Users\spenc\Desktop\PureSolutionsDash\data # remove files in index
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
Write-Host "Done!"